import os
import sys
from pathlib import Path
from typing import List

from PySide6.QtCore import Qt, QRect, QPoint, Signal, QObject, QSize, QThread
from PySide6.QtGui import QAction, QPixmap, QPainter, QPen, QGuiApplication
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QSplitter, QTableWidget, QTableWidgetItem, QToolBar, QPushButton,
    QStatusBar, QMessageBox, QSizePolicy, QTextEdit, QComboBox
)

from config import Config, OCRRect
# 延迟导入重型库，加快启动速度并减小打包体积
# OCR引擎管理器在后台线程中按需导入
# from ocr_engine_manager import OCREngineManager
from utils import FileUtils, ImageUtils, ExcelExporter
from PIL import Image


class OCRInitWorker(QThread):
    """后台线程：初始化OCR引擎（不阻塞UI）"""
    finished = Signal(object)  # 全部初始化完成，传递OCREngineManager实例
    primary_init_finished = Signal(object)  # 首选引擎初始化完成，传递OCREngineManager实例
    error = Signal(str)  # 初始化失败，传递错误消息
    
    def run(self):
        """在后台线程中初始化OCR引擎"""
        try:
            # 延迟导入（在工作线程中）
            from ocr_engine_manager import OCREngineManager
            
            # 创建引擎管理器（只初始化首选引擎）
            manager = OCREngineManager()
            
            # 发送首选引擎就绪信号
            self.primary_init_finished.emit(manager)
            
            # 继续在后台初始化其他引擎
            manager.init_background_engines()
            
            # 发送全部完成信号
            self.finished.emit(manager)
        except Exception as e:
            # 发送错误信号
            self.error.emit(str(e))


class RectSelectionLabel(QLabel):
    """可框选的图片显示控件，使用橡皮筋绘制选区"""
    rect_finished = Signal(QRect)
    rect_removed = Signal(int)  # 发送被删除矩形的索引

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._pix: QPixmap | None = None
        self._display_size: QSize | None = None
        self._scale = 1.0
        self._origin_img_size: QSize | None = None
        self._rubber_origin: QPoint | None = None
        self._rubber_rect: QRect | None = None
        self._drawing = False
        self._rects: List[QRect] = []

    def load_image(self, pix: QPixmap, origin_w: int, origin_h: int):
        self._pix = pix
        self._origin_img_size = QSize(origin_w, origin_h)
        self._update_scaled_pix()
        self._rects.clear()
        self.update()

    def _update_scaled_pix(self):
        if not self._pix:
            return
        # 根据label大小计算缩放
        label_w = max(1, self.width())
        label_h = max(1, self.height())
        scaled = self._pix.scaled(label_w, label_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._display_size = scaled.size()
        # 计算缩放比例（显示/原图）
        if self._origin_img_size:
            self._scale = self._display_size.width() / self._origin_img_size.width()
        self.setPixmap(scaled)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._update_scaled_pix()

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and self._pix is not None:
            self._drawing = True
            self._rubber_origin = e.position().toPoint()
            self._rubber_rect = QRect(self._rubber_origin, QSize(0, 0))
            self.update()
        elif e.button() == Qt.RightButton and self._pix is not None:
            # 右键删除矩形
            click_pos = e.position().toPoint()
            for i, rect in enumerate(self._rects):
                if rect.contains(click_pos):
                    self._rects.pop(i)
                    self.rect_removed.emit(i)
                    self.update()
                    break
        super().mousePressEvent(e)

    def mouseMoveEvent(self, e):
        if self._drawing and self._rubber_origin is not None:
            self._rubber_rect = QRect(self._rubber_origin, e.position().toPoint()).normalized()
            self.update()
        super().mouseMoveEvent(e)

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton and self._drawing:
            self._drawing = False
            if self._rubber_rect and self._rubber_rect.width() > 5 and self._rubber_rect.height() > 5:
                # 记录显示坐标的矩形
                self._rects.append(self._rubber_rect)
                self.rect_finished.emit(self._rubber_rect)
            self._rubber_rect = None
            self.update()
        super().mouseReleaseEvent(e)

    def paintEvent(self, e):
        super().paintEvent(e)
        if not self._pix:
            return
        painter = QPainter(self)
        pen = QPen(Qt.red, 2, Qt.SolidLine)
        painter.setPen(pen)
        # 绘制已存在的矩形
        for r in self._rects:
            painter.drawRect(r)
        # 绘制正在框选的矩形
        if self._rubber_rect:
            pen = QPen(Qt.blue, 2, Qt.DashLine)
            painter.setPen(pen)
            painter.drawRect(self._rubber_rect)

    def display_to_image_rect(self, r: QRect) -> QRect:
        """将显示坐标矩形转换为原图坐标矩形"""
        if self._scale <= 0:
            return QRect()
        # 计算label居中造成的偏移
        off_x = (self.width() - (self._display_size.width() if self._display_size else 0)) // 2
        off_y = (self.height() - (self._display_size.height() if self._display_size else 0)) // 2
        x = max(0, r.x() - off_x)
        y = max(0, r.y() - off_y)
        w = r.width()
        h = r.height()
        # 反缩放
        ix = int(x / self._scale)
        iy = int(y / self._scale)
        iw = int(w / self._scale)
        ih = int(h / self._scale)
        return QRect(ix, iy, iw, ih)


class OCRWorker(QThread):
    """后台线程：执行OCR识别任务"""
    finished = Signal(object, str)  # 识别完成，传递(rect, text)
    error = Signal(str)
    
    def __init__(self, ocr_engine, image, rect, is_full_image=False):
        super().__init__()
        self.ocr = ocr_engine
        self.image = image
        self.rect = rect  # OCRRect对象 或 None(全图)
        self.is_full_image = is_full_image
        
    def run(self):
        try:
            if self.is_full_image:
                # 识别全图
                res = self.ocr.recognize_image(self.image)
                lines = []
                if res and isinstance(res, list) and len(res) > 0:
                    # 处理RapidOCR格式
                    if isinstance(res[0], list):
                        for item in res[0]:
                            if isinstance(item, (list, tuple)) and len(item) >= 2:
                                text = item[1][0] if isinstance(item[1], (list, tuple)) else item[1]
                                lines.append(text)
                    # 处理EasyOCR格式
                    elif isinstance(res[0], dict) and 'text' in res[0]:
                        for item in res:
                            if isinstance(item, dict) and 'text' in item:
                                lines.append(item['text'])
                
                text = " ".join(lines) if lines else "(未识别到文字)"
                self.finished.emit(None, text)
            else:
                # 识别区域
                if self.rect:
                    text = self.ocr.recognize_region(self.image, (self.rect.x1, self.rect.y1, self.rect.x2, self.rect.y2))
                    self.finished.emit(self.rect, text or "")
        except Exception as e:
            self.error.emit(str(e))


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(Config.APP_NAME + " (Qt)")
        self.resize(Config.WINDOW_WIDTH, Config.WINDOW_HEIGHT)

        # 状态
        self.files: List[str] = []
        self.cur_index = -1
        self.cur_pil: Image.Image | None = None
        self.cur_pix: QPixmap | None = None
        self.rects: List[OCRRect] = []
        self.ocr_results = {}
        
        # 延迟初始化OCR引擎（加快启动速度）
        self.ocr_manager = None
        self.ocr = None
        self._ocr_initialized = False
        self._ocr_worker = None  # 后台初始化线程
        self._ocr_tasks = []     # OCR识别任务列表（防止线程被垃圾回收）

        # UI
        self._init_ui()
        
        # 在后台线程中异步初始化OCR引擎（不阻塞UI）
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, self._start_ocr_init_thread)

    def _init_ui(self):
        # 工具栏
        tb = QToolBar("Main")
        self.addToolBar(tb)

        act_open_files = QAction("\ud83d\udcc2 \u6253\u5f00\u6587\u4ef6", self)
        act_open_files.triggered.connect(self.open_files)
        tb.addAction(act_open_files)

        act_open_folder = QAction("📁 打开文件夹", self)
        act_open_folder.triggered.connect(self.open_folder)
        tb.addAction(act_open_folder)

        act_ocr = QAction("🔍 开始识别", self)
        act_ocr.triggered.connect(self.start_ocr_current)
        tb.addAction(act_ocr)

        act_rename_next = QAction("✏️ 改名并下一张", self)
        act_rename_next.triggered.connect(self.rename_and_next)
        tb.addAction(act_rename_next)

        act_export = QAction("💾 导出Excel", self)
        act_export.triggered.connect(self.export_excel)
        tb.addAction(act_export)
        
        # 添加分隔符
        tb.addSeparator()
        
        # 添加引擎选择下拉框
        tb.addWidget(QLabel("OCR引擎:"))
        self.engine_combo = QComboBox()
        self.engine_combo.setMinimumWidth(120)
        tb.addWidget(self.engine_combo)
        
        # 添加状态标签
        self.engine_status_label = QLabel("引擎: 初始化中...")
        self.engine_status_label.setStyleSheet("color: orange; font-weight: bold;")
        tb.addWidget(self.engine_status_label)
        
        # 初始化下拉框（OCR引擎未初始化时的占位）
        self.engine_combo.addItem("初始化中...")
        self.engine_combo.setEnabled(False)  # 初始化完成前禁用
        
        # 绑定信号（初始化完成后才会生效）
        self.engine_combo.currentTextChanged.connect(self.on_engine_changed)

        # 中心布局
        central = QWidget(self)
        self.setCentralWidget(central)
        h = QHBoxLayout(central)

        splitter = QSplitter(Qt.Horizontal)
        h.addWidget(splitter)

        # 左侧：图片+结果
        left = QWidget()
        left_v = QVBoxLayout(left)
        self.image_label = RectSelectionLabel()
        left_v.addWidget(self.image_label, stretch=1)
        self.image_label.rect_finished.connect(self.on_rect_finished)
        self.image_label.rect_removed.connect(self.on_rect_removed)

        left_v.addWidget(QLabel("识别结果:"))
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        left_v.addWidget(self.result_text, stretch=0)

        # 右侧：文件表
        right = QWidget()
        right_v = QVBoxLayout(right)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["序号", "路径", "状态"])
        self.table.cellDoubleClicked.connect(self.on_table_double_clicked)
        right_v.addWidget(self.table)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        # 状态栏
        sb = QStatusBar()
        self.setStatusBar(sb)
    
    def _start_ocr_init_thread(self):
        """启动后台线程初始化OCR引擎（不阻塞UI）"""
        if self._ocr_initialized or self._ocr_worker is not None:
            return
        
        self.statusBar().showMessage("正在后台初始化OCR引擎...")
        
        # 创建并启动工作线程
        self._ocr_worker = OCRInitWorker()
        self._ocr_worker.primary_init_finished.connect(self._on_primary_ocr_ready)
        self._ocr_worker.finished.connect(self._on_ocr_init_finished)
        self._ocr_worker.error.connect(self._on_ocr_init_error)
        self._ocr_worker.start()
    
    def _on_primary_ocr_ready(self, manager):
        """首选OCR引擎初始化完成的回调"""
        self.ocr_manager = manager
        self.ocr = self.ocr_manager.current_engine
        self._ocr_initialized = True
        
        # 更新UI
        self._update_engine_combo()
        self._update_engine_status()
        
        self.statusBar().showMessage("✓ 默认OCR引擎已就绪", 3000)
    
    def _on_ocr_init_finished(self, manager):
        """所有OCR引擎初始化完成的回调"""
        # 再次更新UI以显示所有可用引擎
        self._update_engine_combo()
        self.statusBar().showMessage("✓ 所有OCR引擎初始化完成", 3000)
        
        # 清理工作线程
        if self._ocr_worker:
            self._ocr_worker.deleteLater()
            self._ocr_worker = None
    
    def _on_ocr_init_error(self, error_msg: str):
        """OCR引擎初始化失败的回调"""
        self.statusBar().showMessage(f"✗ OCR引擎初始化失败: {error_msg}")
        QMessageBox.warning(
            self, 
            "初始化失败", 
            f"OCR引擎初始化失败:\n{error_msg}\n\n程序将继续运行，但OCR功能不可用。"
        )
        
        # 清理工作线程
        if self._ocr_worker:
            self._ocr_worker.deleteLater()
            self._ocr_worker = None
    
    def _ensure_ocr_ready(self) -> bool:
        """确保OCR引擎已初始化"""
        if not self._ocr_initialized:
            # 如果正在初始化，提示用户等待
            if self._ocr_worker and self._ocr_worker.isRunning():
                QMessageBox.information(
                    self, 
                    "正在初始化", 
                    "OCR引擎正在后台初始化中，请稍后再试。"
                )
                return False
            # 如果还没开始初始化，立即开始
            self._start_ocr_init_thread()
            QMessageBox.information(
                self, 
                "正在初始化", 
                "OCR引擎正在后台初始化中，请稍后再试。"
            )
            return False
        
        if not self.ocr or not self.ocr.is_ready():
            QMessageBox.warning(self, "OCR未就绪", "OCR引擎未就绪，请稍后再试。")
            return False
        return True

    def _update_engine_status(self):
        if self.ocr and self.ocr.is_ready():
            self.statusBar().showMessage("正在初始化OCR引擎...")
        else:
            self.statusBar().showMessage("警告：OCR引擎未就绪")
    
    def _update_engine_combo(self):
        """更新引擎下拉框菜单"""
        # 暂时阻塞信号，避免触发on_engine_changed
        self.engine_combo.blockSignals(True)
        self.engine_combo.clear()
        
        if not self.ocr_manager:
            self.engine_combo.addItem("初始化中...")
            self.engine_combo.setEnabled(False)
            self.engine_combo.blockSignals(False)
            return
        
        available = self.ocr_manager.get_available_engines()
        
        if not available:
            self.engine_combo.addItem("没有可用引擎")
            self.engine_combo.setEnabled(False)
            self.engine_combo.blockSignals(False)
            return
        
        # 添加可用引擎
        for engine_type, name, description, specs in available:
            display_text = f"{name} ({specs})"
            self.engine_combo.addItem(display_text, engine_type)
        
        # 设置当前引擎为下拉框的值
        if self.ocr_manager.current_engine_type:
            current_type = self.ocr_manager.current_engine_type.value
            for i in range(self.engine_combo.count()):
                if self.engine_combo.itemData(i) == current_type:
                    self.engine_combo.setCurrentIndex(i)
                    break
        
        # 启用下拉框（初始化完成）
        self.engine_combo.setEnabled(True)
        self.engine_combo.blockSignals(False)
        
        self._update_engine_status_label()
    
    def on_engine_changed(self, display_text: str):
        """处理引擎选择变化"""
        if not display_text or display_text == "没有可用引擎" or display_text == "初始化中...":
            return
        
        # 确保OCR管理器已初始化
        if not self.ocr_manager:
            return
        
        # 获取选中的引擎类型
        index = self.engine_combo.currentIndex()
        if index < 0:
            return
        
        engine_type = self.engine_combo.itemData(index)
        if not engine_type:  # 无效的引擎类型
            return
        
        # 切换引擎
        self.statusBar().showMessage(f"正在切换到 {display_text}...")
        
        try:
            if self.ocr_manager.set_engine(engine_type):
                self.ocr = self.ocr_manager.current_engine
                self._update_engine_status_label()
                self.statusBar().showMessage(f"已切换到 {display_text}")
            else:
                QMessageBox.warning(self, "切换失败", f"無法切换到 {display_text}")
                # 恢复之前的選擇
                for i in range(self.engine_combo.count()):
                    if self.engine_combo.itemData(i) == self.ocr_manager.current_engine_type.value:
                        self.engine_combo.blockSignals(True)
                        self.engine_combo.setCurrentIndex(i)
                        self.engine_combo.blockSignals(False)
                        break
        except Exception as e:
            QMessageBox.warning(self, "错誤", f"切换引擎失败: {str(e)}")
    
    def _update_engine_status_label(self):
        """更新引擎状态标签"""
        if not self.ocr_manager:
            self.engine_status_label.setText("引擎: 初始化中...")
            self.engine_status_label.setStyleSheet("color: orange; font-weight: bold;")
            return
        
        if self.ocr_manager.current_engine_type:
            info = self.ocr_manager.get_current_engine_info()
            status = "✓ 就绪" if info['is_ready'] else "✗ 未就绪"
            color = "green" if info['is_ready'] else "red"
            engine_name = info['name']
            self.engine_status_label.setText(f"引擎: {engine_name} {status}")
            self.engine_status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        else:
            self.engine_status_label.setText("引擎: 未初始化")
            self.engine_status_label.setStyleSheet("color: gray; font-weight: bold;")

    # ---- 文件操作 ----
    def open_files(self):
        paths, _ = QFileDialog.getOpenFileNames(self, "选择文件", str(Path.cwd()),
                                                "图片/PDF (*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.tif *.pdf)")
        if paths:
            self.files = [p for p in paths if FileUtils.is_supported_file(p)]
            self.refresh_table()
            self.load_index(0)

    def open_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹", str(Path.cwd()))
        if folder:
            self.files = FileUtils.get_files_from_folder(folder, recursive=False)
            self.refresh_table()
            self.load_index(0)

    def refresh_table(self):
        self.table.setRowCount(0)
        for i, p in enumerate(self.files, 1):
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(i)))
            self.table.setItem(row, 1, QTableWidgetItem(p))
            self.table.setItem(row, 2, QTableWidgetItem("待处理"))

    def on_table_double_clicked(self, row, col):
        self.load_index(row)

    # ---- 加载显示 ----
    def load_index(self, idx: int):
        if idx < 0 or idx >= len(self.files):
            return
        self.cur_index = idx
        path = self.files[idx]
        try:
            pil = ImageUtils.load_image(path)
            self.cur_pil = pil
            # 转 QPixmap 显示
            qimg = self._pil_to_qpixmap(pil)
            self.cur_pix = qimg
            self.image_label.load_image(qimg, pil.width, pil.height)
            self.rects = []
            self.result_text.clear()
            self.statusBar().showMessage(f"已加载: {os.path.basename(path)}")
        except Exception as e:
            QMessageBox.warning(self, "加载失败", str(e))

    @staticmethod
    def _pil_to_qpixmap(pil: Image.Image) -> QPixmap:
        if pil.mode != "RGB":
            pil = pil.convert("RGB")
        data = pil.tobytes("raw", "RGB")
        from PySide6.QtGui import QImage
        qimg = QImage(data, pil.width, pil.height, pil.width * 3, QImage.Format_RGB888)
        return QPixmap.fromImage(qimg)

    # ---- 选区与OCR ----
    def on_rect_finished(self, display_rect: QRect):
        if not self.cur_pil:
            return
        
        # 确保OCR引擎已就绪
        if not self._ensure_ocr_ready():
            return
        
        img_rect = self.image_label.display_to_image_rect(display_rect)
        if img_rect.width() < Config.MIN_RECT_SIZE or img_rect.height() < Config.MIN_RECT_SIZE:
            return
        ocr_rect = OCRRect(img_rect.x(), img_rect.y(), img_rect.x()+img_rect.width(), img_rect.y()+img_rect.height())
        self.rects.append(ocr_rect)
        
        # 异步识别
        self.statusBar().showMessage("正在识别...")
        self.update_current_status("识别中...")
        
        worker = OCRWorker(self.ocr, self.cur_pil, ocr_rect, is_full_image=False)
        worker.finished.connect(self._on_ocr_finished)
        worker.error.connect(self._on_ocr_error)
        
        # 保存引用防止被垃圾回收
        self._ocr_tasks.append(worker)
        # 任务完成后清理引用
        worker.finished.connect(lambda: self._cleanup_ocr_task(worker))
        worker.error.connect(lambda: self._cleanup_ocr_task(worker))
        
        worker.start()
        
    def _on_ocr_finished(self, rect, text):
        """OCR识别完成回调"""
        if rect:
            # 区域识别
            rect.text = text or ""
            self.append_result(text)
        else:
            # 全图识别
            self.append_result(text)
            
        self.statusBar().showMessage("✓ 识别完成", 2000)
        self.update_current_status("已识别")
        
    def _on_ocr_error(self, error_msg):
        """OCR识别错误回调"""
        self.statusBar().showMessage(f"✗ 识别失败: {error_msg}")
        QMessageBox.warning(self, "识别失败", error_msg)
        self.update_current_status("识别失败")
        
    def _cleanup_ocr_task(self, worker):
        """清理已完成的OCR任务"""
        if worker in self._ocr_tasks:
            self._ocr_tasks.remove(worker)
        worker.deleteLater()
    
    def on_rect_removed(self, index: int):
        """处理右键删除框选区域"""
        if 0 <= index < len(self.rects):
            removed_rect = self.rects.pop(index)
            # 刷新结果显示
            self.result_text.clear()
            for rect in self.rects:
                if rect.text:
                    self.append_result(rect.text)
            self.statusBar().showMessage(f"已删除区域 {index + 1}")

    def append_result(self, text: str):
        if not text:
            text = "(空)"
        self.result_text.append(text)

    def start_ocr_current(self):
        if not self.cur_pil:
            return
        
        # 确保OCR引擎已就绪
        if not self._ensure_ocr_ready():
            return
        
        self.statusBar().showMessage("正在识别...")
        self.update_current_status("识别中...")
        
        if not self.rects:
            # 没有区域则识别整图
            worker = OCRWorker(self.ocr, self.cur_pil, None, is_full_image=True)
            worker.finished.connect(self._on_ocr_finished)
            worker.error.connect(self._on_ocr_error)
            
            self._ocr_tasks.append(worker)
            worker.finished.connect(lambda: self._cleanup_ocr_task(worker))
            worker.error.connect(lambda: self._cleanup_ocr_task(worker))
            
            worker.start()
        else:
            # 批量识别所有区域
            # 为简单起见，这里我们对每个区域启动一个任务，或者可以修改Worker支持批量
            # 考虑到区域通常不多，逐个启动是可以的，但更好的方式是Worker支持列表
            # 这里为了保持改动最小，我们循环启动
            for r in self.rects:
                worker = OCRWorker(self.ocr, self.cur_pil, r, is_full_image=False)
                worker.finished.connect(self._on_ocr_finished)
                worker.error.connect(self._on_ocr_error)
                
                self._ocr_tasks.append(worker)
                worker.finished.connect(lambda: self._cleanup_ocr_task(worker))
                worker.error.connect(lambda: self._cleanup_ocr_task(worker))
                
                worker.start()

    # ---- 重命名并下一张 ----
    def rename_and_next(self):
        if self.cur_index < 0 or self.cur_index >= len(self.files):
            return
        if not self.rects or not (self.rects[0].text or "").strip():
            QMessageBox.information(self, "提示", "没有可用于重命名的识别结果。")
            return
        src = self.files[self.cur_index]
        directory = str(Path(src).parent)
        base = FileUtils.clean_filename(self.rects[0].text.strip())
        ext = Path(src).suffix
        dst = FileUtils.get_unique_filename(directory, base, ext)
        try:
            os.rename(src, dst)
            self.files[self.cur_index] = dst
            self.table.item(self.cur_index, 1).setText(dst)
            self.update_current_status("已重命名")
        except Exception as e:
            QMessageBox.warning(self, "重命名失败", str(e))
            return
        # 下一张
        next_idx = self.cur_index + 1
        if next_idx < len(self.files):
            self.load_index(next_idx)
            self.table.selectRow(next_idx)
        else:
            QMessageBox.information(self, "完成", "已处理到最后一张。")

    # ---- Excel 导出 ----
    def export_excel(self):
        if not self.files:
            QMessageBox.information(self, "提示", "没有数据可导出。")
            return
        save_path, _ = QFileDialog.getSaveFileName(self, "保存为Excel", str(Path.cwd() / "ocr结果.xlsx"), "Excel (*.xlsx)")
        if not save_path:
            return
        # 汇总结果
        results = {}
        for i, p in enumerate(self.files):
            results[p] = {
                "rects": self.rects if i == self.cur_index else [],
                "status": self.table.item(i, 2).text() if self.table.item(i, 2) else ""
            }
        ok = ExcelExporter.export_results(results, save_path)
        if ok:
            QMessageBox.information(self, "成功", "导出完成。")
        else:
            QMessageBox.warning(self, "失败", "导出失败。")

    def update_current_status(self, text: str):
        if 0 <= self.cur_index < self.table.rowCount():
            self.table.setItem(self.cur_index, 2, QTableWidgetItem(text))


    def closeEvent(self, event):
        """
        窗口关闭事件：清理线程资源
        """
        # 停止初始化线程
        if self._ocr_worker and self._ocr_worker.isRunning():
            self._ocr_worker.quit()
            self._ocr_worker.wait(1000)  # 等待1秒
            if self._ocr_worker.isRunning():
                self._ocr_worker.terminate()  # 强制终止
                self._ocr_worker.wait()
        
        # 停止所有OCR任务线程
        for worker in self._ocr_tasks:
            if worker.isRunning():
                worker.quit()
                worker.wait(500)
                if worker.isRunning():
                    worker.terminate()
                    worker.wait()
        
        event.accept()

def main():
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()