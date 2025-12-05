import os
import sys
from pathlib import Path
from typing import List

from PySide6.QtCore import Qt, QRect, QPoint, Signal, QObject, QSize, QThread
from PySide6.QtGui import QAction, QPixmap, QPainter, QPen, QGuiApplication, QCursor
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QFileDialog, QVBoxLayout, QHBoxLayout,
    QLabel, QSplitter, QTableWidget, QTableWidgetItem, QToolBar, QPushButton,
    QStatusBar, QMessageBox, QSizePolicy, QTextEdit, QComboBox, QCheckBox
)

from config import Config, OCRRect
from utils import FileUtils, ImageUtils, ExcelExporter
from PIL import Image
from cache_manager_wrapper import CacheManagerWrapper
from dependency_manager import DependencyManager
from optimized_image_loader import OptimizedImageLoader
from ocr_engine_downloader import OCREngineDownloader
from ocr_engine_download_dialog import OCREngineDownloadDialog
import gc


class OCRInitWorker(QThread):
    """后台线程：初始化OCR引擎（不阻塞UI）"""
    finished = Signal(object)  # 全部初始化完成，传递OCREngineManager实例
    primary_init_finished = Signal(object)  # 首选引擎初始化完成，传递OCREngineManager实例
    error = Signal(str)  # 初始化失败，传递错误消息
    
    def run(self):
        """在后台线程中初始化OCR引擎"""
        try:
            # 使用DependencyManager延迟导入OCR引擎管理器
            OCREngineManager = DependencyManager.load_ocr_engine()
            if not OCREngineManager:
                self.error.emit("OCR引擎管理器不可用")
                return
            
            # 检查是否已请求中断
            if self.isInterruptionRequested():
                return
            
            # 创建引擎管理器（只初始化首选引擎）
            manager = OCREngineManager()
            
            # 检查是否已请求中断
            if self.isInterruptionRequested():
                return
            
            # 发送首选引擎就绪信号
            self.primary_init_finished.emit(manager)
            
            # 检查是否已请求中断
            if self.isInterruptionRequested():
                return
            
            # 继续在后台初始化其他引擎
            manager.init_background_engines()
            
            # 检查是否已请求中断
            if self.isInterruptionRequested():
                return
            
            # 发送全部完成信号
            self.finished.emit(manager)
        except Exception as e:
            # 发送错误信号
            self.error.emit(str(e))


class RectSelectionLabel(QLabel):
    """可框选的图片显示控件，支持缩放、平移和边缘自动滚动"""
    rect_finished = Signal(QRect)
    rect_removed = Signal(int)  # 发送被删除矩形的索引

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMouseTracking(True)  # 启用鼠标追踪
        
        self._pix: QPixmap | None = None
        self._display_size: QSize | None = None
        self._scale = 1.0  # 显示缩放比例（显示/原图）
        self._origin_img_size: QSize | None = None
        self._rubber_origin: QPoint | None = None
        self._rubber_rect: QRect | None = None
        self._drawing = False
        self._rects: List[QRect] = []
        
        # 缩放和平移相关
        self._zoom_level = 1.0  # 用户缩放级别（1.0 = 适应窗口）
        self._min_zoom = 0.5
        self._max_zoom = 5.0
        self._pan_offset = QPoint(0, 0)  # 平移偏移量
        self._panning = False  # 是否正在平移
        self._pan_start = QPoint(0, 0)  # 平移起始点
        self._last_pan_offset = QPoint(0, 0)  # 上次平移偏移
        
        # 边缘自动滚动相关
        self._edge_scroll_margin = 50  # 边缘触发区域（像素）
        self._edge_scroll_speed = 15  # 滚动速度（像素/帧）
        self._scroll_timer = None  # 滚动定时器
        
        # 初始化滚动定时器
        from PySide6.QtCore import QTimer
        self._scroll_timer = QTimer()
        self._scroll_timer.timeout.connect(self._on_edge_scroll)
        self._scroll_timer.setInterval(30)  # 约33fps

    def load_image(self, pix: QPixmap, origin_w: int, origin_h: int):
        self._pix = pix
        self._origin_img_size = QSize(origin_w, origin_h)
        # 重置缩放和平移
        self._zoom_level = 1.0
        self._pan_offset = QPoint(0, 0)
        self._update_scaled_pix()
        self._rects.clear()
        self.update()

    def _update_scaled_pix(self):
        if not self._pix:
            return
        # 根据label大小和缩放级别计算显示大小
        label_w = max(1, self.width())
        label_h = max(1, self.height())
        
        # 先计算适应窗口的基础缩放
        base_scaled = self._pix.scaled(label_w, label_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        base_w = base_scaled.width()
        base_h = base_scaled.height()
        
        # 应用用户缩放级别
        final_w = int(base_w * self._zoom_level)
        final_h = int(base_h * self._zoom_level)
        
        # 缩放图片
        scaled = self._pix.scaled(final_w, final_h, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self._display_size = scaled.size()
        
        # 计算缩放比例（显示/原图）
        if self._origin_img_size and self._origin_img_size.width() > 0:
            self._scale = self._display_size.width() / self._origin_img_size.width()
        
        # 限制平移范围
        self._clamp_pan_offset()
        
        # 不再使用setPixmap，改为手动绘制
        self.update()

    def _clamp_pan_offset(self):
        """限制平移偏移量，确保图片不会移出可视区域太多"""
        if not self._display_size:
            return
        
        label_w = self.width()
        label_h = self.height()
        img_w = self._display_size.width()
        img_h = self._display_size.height()
        
        # 如果图片小于等于窗口，不允许平移
        if img_w <= label_w:
            self._pan_offset.setX(0)
        else:
            max_x = (img_w - label_w) // 2 + 50
            self._pan_offset.setX(max(-max_x, min(max_x, self._pan_offset.x())))
        
        if img_h <= label_h:
            self._pan_offset.setY(0)
        else:
            max_y = (img_h - label_h) // 2 + 50
            self._pan_offset.setY(max(-max_y, min(max_y, self._pan_offset.y())))

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self._update_scaled_pix()

    def wheelEvent(self, e):
        """鼠标滚轮缩放"""
        if not self._pix:
            return
        
        # 获取鼠标位置（用于以鼠标为中心缩放）
        mouse_pos = e.position().toPoint()
        
        # 计算缩放前鼠标在图片上的位置
        old_img_pos = self._widget_to_image_pos(mouse_pos)
        
        # 计算新的缩放级别
        delta = e.angleDelta().y()
        zoom_factor = 1.15 if delta > 0 else 1 / 1.15
        new_zoom = self._zoom_level * zoom_factor
        new_zoom = max(self._min_zoom, min(self._max_zoom, new_zoom))
        
        if new_zoom != self._zoom_level:
            self._zoom_level = new_zoom
            self._update_scaled_pix()
            
            # 调整平移偏移，使鼠标位置保持在图片同一点上
            new_img_pos = self._widget_to_image_pos(mouse_pos)
            if old_img_pos and new_img_pos:
                # 计算需要的偏移调整
                dx = (new_img_pos.x() - old_img_pos.x()) * self._scale
                dy = (new_img_pos.y() - old_img_pos.y()) * self._scale
                self._pan_offset = QPoint(
                    self._pan_offset.x() + int(dx),
                    self._pan_offset.y() + int(dy)
                )
                self._clamp_pan_offset()
            
            self.update()
        
        e.accept()

    def _widget_to_image_pos(self, widget_pos: QPoint) -> QPoint | None:
        """将控件坐标转换为图片坐标"""
        if not self._display_size or self._scale <= 0:
            return None
        
        # 计算图片在控件中的位置
        img_x = (self.width() - self._display_size.width()) // 2 - self._pan_offset.x()
        img_y = (self.height() - self._display_size.height()) // 2 - self._pan_offset.y()
        
        # 计算相对于图片的位置
        rel_x = widget_pos.x() - img_x
        rel_y = widget_pos.y() - img_y
        
        # 转换为原图坐标
        img_x = int(rel_x / self._scale)
        img_y = int(rel_y / self._scale)
        
        return QPoint(img_x, img_y)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton and self._pix is not None:
            # 检查是否按住Ctrl键进行平移
            if e.modifiers() & Qt.ControlModifier:
                self._panning = True
                self._pan_start = e.position().toPoint()
                self._last_pan_offset = QPoint(self._pan_offset)
                self.setCursor(Qt.ClosedHandCursor)
            else:
                # 开始框选
                self._drawing = True
                self._rubber_origin = e.position().toPoint()
                self._rubber_rect = QRect(self._rubber_origin, QSize(0, 0))
                self.update()
        elif e.button() == Qt.MiddleButton and self._pix is not None:
            # 中键平移
            self._panning = True
            self._pan_start = e.position().toPoint()
            self._last_pan_offset = QPoint(self._pan_offset)
            self.setCursor(Qt.ClosedHandCursor)
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
        pos = e.position().toPoint()
        
        if self._panning:
            # 平移模式
            delta = pos - self._pan_start
            self._pan_offset = QPoint(
                self._last_pan_offset.x() - delta.x(),
                self._last_pan_offset.y() - delta.y()
            )
            self._clamp_pan_offset()
            self.update()
        elif self._drawing and self._rubber_origin is not None:
            # 框选模式
            self._rubber_rect = QRect(self._rubber_origin, pos).normalized()
            self.update()
            
            # 检查是否需要边缘滚动
            self._check_edge_scroll(pos)
        else:
            # 更新鼠标样式
            if e.modifiers() & Qt.ControlModifier:
                self.setCursor(Qt.OpenHandCursor)
            else:
                self.setCursor(Qt.CrossCursor)
        
        super().mouseMoveEvent(e)

    def _check_edge_scroll(self, pos: QPoint):
        """检查是否需要边缘自动滚动"""
        if not self._drawing or self._zoom_level <= 1.0:
            self._scroll_timer.stop()
            return
        
        # 检查是否在边缘区域
        margin = self._edge_scroll_margin
        at_edge = (pos.x() < margin or pos.x() > self.width() - margin or
                   pos.y() < margin or pos.y() > self.height() - margin)
        
        if at_edge:
            if not self._scroll_timer.isActive():
                self._scroll_timer.start()
        else:
            self._scroll_timer.stop()

    def _on_edge_scroll(self):
        """边缘滚动定时器回调"""
        if not self._drawing:
            self._scroll_timer.stop()
            return
        
        # 获取当前鼠标位置
        cursor_pos = self.mapFromGlobal(QCursor.pos())
        
        margin = self._edge_scroll_margin
        speed = self._edge_scroll_speed
        
        dx, dy = 0, 0
        
        # 计算滚动方向和速度
        if cursor_pos.x() < margin:
            dx = -speed * (1 - cursor_pos.x() / margin)
        elif cursor_pos.x() > self.width() - margin:
            dx = speed * (1 - (self.width() - cursor_pos.x()) / margin)
        
        if cursor_pos.y() < margin:
            dy = -speed * (1 - cursor_pos.y() / margin)
        elif cursor_pos.y() > self.height() - margin:
            dy = speed * (1 - (self.height() - cursor_pos.y()) / margin)
        
        if dx != 0 or dy != 0:
            # 更新平移偏移
            self._pan_offset = QPoint(
                self._pan_offset.x() + int(dx),
                self._pan_offset.y() + int(dy)
            )
            self._clamp_pan_offset()
            
            # 更新框选矩形的起点（保持相对位置）
            if self._rubber_origin:
                self._rubber_origin = QPoint(
                    self._rubber_origin.x() - int(dx),
                    self._rubber_origin.y() - int(dy)
                )
            
            # 更新框选矩形
            if self._rubber_rect and self._rubber_origin:
                self._rubber_rect = QRect(self._rubber_origin, cursor_pos).normalized()
            
            self.update()

    def mouseReleaseEvent(self, e):
        if e.button() == Qt.LeftButton:
            if self._panning:
                self._panning = False
                self.setCursor(Qt.CrossCursor)
            elif self._drawing:
                self._drawing = False
                self._scroll_timer.stop()
                if self._rubber_rect and self._rubber_rect.width() > 5 and self._rubber_rect.height() > 5:
                    # 记录显示坐标的矩形
                    self._rects.append(self._rubber_rect)
                    self.rect_finished.emit(self._rubber_rect)
                self._rubber_rect = None
                self.update()
        elif e.button() == Qt.MiddleButton:
            self._panning = False
            self.setCursor(Qt.CrossCursor)
        super().mouseReleaseEvent(e)
    
    def reset_zoom(self):
        """重置缩放和平移"""
        self._zoom_level = 1.0
        self._pan_offset = QPoint(0, 0)
        self._update_scaled_pix()
        self.update()
    
    def mouseDoubleClickEvent(self, e):
        """双击重置缩放"""
        if e.button() == Qt.LeftButton and self._pix is not None:
            self.reset_zoom()
        super().mouseDoubleClickEvent(e)
    
    def keyPressEvent(self, e):
        """键盘快捷键"""
        if e.key() == Qt.Key_0 or e.key() == Qt.Key_Home:
            # 按0或Home键重置缩放
            self.reset_zoom()
        elif e.key() == Qt.Key_Plus or e.key() == Qt.Key_Equal:
            # 按+键放大
            self._zoom_level = min(self._max_zoom, self._zoom_level * 1.2)
            self._update_scaled_pix()
        elif e.key() == Qt.Key_Minus:
            # 按-键缩小
            self._zoom_level = max(self._min_zoom, self._zoom_level / 1.2)
            self._update_scaled_pix()
        else:
            super().keyPressEvent(e)

    def paintEvent(self, e):
        # 不调用super().paintEvent()，完全自定义绘制
        if not self._pix or not self._display_size:
            super().paintEvent(e)
            return
        
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # 填充背景
        painter.fillRect(self.rect(), self.palette().window())
        
        # 计算图片绘制位置（居中 + 平移偏移）
        img_x = (self.width() - self._display_size.width()) // 2 - self._pan_offset.x()
        img_y = (self.height() - self._display_size.height()) // 2 - self._pan_offset.y()
        
        # 绘制缩放后的图片
        scaled_pix = self._pix.scaled(
            self._display_size.width(), 
            self._display_size.height(),
            Qt.KeepAspectRatio, 
            Qt.SmoothTransformation
        )
        painter.drawPixmap(img_x, img_y, scaled_pix)
        
        # 绘制缩放提示（当缩放不为1时）
        if self._zoom_level != 1.0:
            from PySide6.QtGui import QFont, QColor
            font = QFont()
            font.setPointSize(10)
            painter.setFont(font)
            painter.setPen(QColor(100, 100, 100))
            zoom_text = f"缩放: {self._zoom_level:.1f}x (滚轮缩放, Ctrl+拖动/中键平移, 双击重置)"
            painter.drawText(10, 20, zoom_text)
        
        # 绘制已存在的矩形
        from PySide6.QtGui import QFont, QBrush, QColor
        for idx, r in enumerate(self._rects):
            # 设置框的颜色（第1个框用红色，其他用绿色）
            if idx == 0:
                pen = QPen(Qt.red, 3, Qt.SolidLine)  # 第1个框：红色粗线（重命名用）
            else:
                pen = QPen(Qt.green, 2, Qt.SolidLine)  # 其他框：绿色
            painter.setPen(pen)
            painter.drawRect(r)
            
            # 绘制序号标签
            label_text = str(idx + 1)
            
            # 设置字体和颜色
            font = QFont()
            font.setPointSize(14)
            font.setBold(True)
            painter.setFont(font)
            
            # 第1个框用红色字体，其他用白色字体
            if idx == 0:
                text_color = QColor(255, 0, 0)  # 红色
                bg_color = QColor(255, 255, 0, 200)  # 黄色半透明背景
            else:
                text_color = QColor(255, 255, 255)  # 白色
                bg_color = QColor(0, 128, 0, 200)  # 绿色半透明背景
            
            # 计算文本位置（左上角）
            text_x = r.x() + 5
            text_y = r.y() + 20
            
            # 绘制背景矩形
            metrics = painter.fontMetrics()
            text_width = metrics.horizontalAdvance(label_text)
            text_height = metrics.height()
            bg_rect = QRect(text_x - 3, text_y - text_height + 3, text_width + 6, text_height + 2)
            
            painter.fillRect(bg_rect, QBrush(bg_color))
            
            # 绘制序号文本
            painter.setPen(text_color)
            painter.drawText(text_x, text_y, label_text)
        
        # 绘制正在框选的矩形
        if self._rubber_rect:
            pen = QPen(Qt.blue, 2, Qt.DashLine)
            painter.setPen(pen)
            painter.drawRect(self._rubber_rect)

    def display_to_image_rect(self, r: QRect) -> QRect:
        """将显示坐标矩形转换为原图坐标矩形（考虑缩放和平移）"""
        if self._scale <= 0 or not self._display_size:
            return QRect()
        # 计算图片在控件中的位置（居中 + 平移偏移）
        off_x = (self.width() - self._display_size.width()) // 2 - self._pan_offset.x()
        off_y = (self.height() - self._display_size.height()) // 2 - self._pan_offset.y()
        
        # 计算相对于图片的位置
        x = max(0, r.x() - off_x)
        y = max(0, r.y() - off_y)
        w = r.width()
        h = r.height()
        
        # 反缩放到原图坐标
        ix = int(x / self._scale)
        iy = int(y / self._scale)
        iw = int(w / self._scale)
        ih = int(h / self._scale)
        return QRect(ix, iy, iw, ih)
    
    def image_to_display_rect(self, ix: int, iy: int, iw: int, ih: int) -> QRect:
        """将原图坐标矩形转换为显示坐标矩形（考虑缩放和平移）"""
        if self._scale <= 0 or not self._display_size:
            return QRect()
        # 缩放到显示大小
        x = int(ix * self._scale)
        y = int(iy * self._scale)
        w = int(iw * self._scale)
        h = int(ih * self._scale)
        # 计算图片在控件中的位置（居中 + 平移偏移）
        off_x = (self.width() - self._display_size.width()) // 2 - self._pan_offset.x()
        off_y = (self.height() - self._display_size.height()) // 2 - self._pan_offset.y()
        return QRect(x + off_x, y + off_y, w, h)
    
    def set_rects(self, rects: List[QRect]):
        """设置显示的矩形列表（用于切换文件时恢复框选）"""
        self._rects = rects.copy()
        self.update()
    
    def clear_rects(self):
        """清空所有矩形"""
        self._rects.clear()
        self.update()


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
        self.rects: List[OCRRect] = []  # 当前图片的区域
        self.all_ocr_results: dict = {}  # 所有文件的OCR结果 {file_path: {"rects": [OCRRect], "status": str}}
        
        # 延迟初始化OCR引擎（加快启动速度）
        self.ocr_manager = None
        self.ocr = None
        self._ocr_initialized = False
        self._ocr_worker = None  # 后台初始化线程
        self._ocr_tasks = []     # OCR识别任务列表（防止线程被垃圾回收）
        
        # 初始化缓存管理器（使用安全包装层）
        # CacheManagerWrapper会自动处理初始化失败，不会抛出异常
        self.cache_manager = CacheManagerWrapper()

        # UI
        self._init_ui()
        
        # 初始化引擎下载器
        self.engine_downloader = OCREngineDownloader()
        
        # 在后台线程中异步初始化OCR引擎（不阻塞UI）
        from PySide6.QtCore import QTimer
        QTimer.singleShot(100, self._check_and_init_engines)
        
        # 延迟检查是否恢复会话
        QTimer.singleShot(500, self._check_restore_session)
        
        # 设置空闲时内存释放定时器（验证需求: 9.4）
        self._idle_timer = QTimer()
        self._idle_timer.timeout.connect(self._on_idle_timeout)
        self._idle_timer.start(30000)  # 每30秒检查一次

    def _init_ui(self):
        """
        初始化UI（优化版）
        
        只创建关键组件，延迟创建非关键组件以加快启动速度
        验证需求: 8.3
        """
        # 工具栏 - 关键组件，立即创建
        tb = QToolBar("Main")
        self.addToolBar(tb)

        act_open_files = QAction("\ud83d\udcc2 \u6253\u5f00\u6587\u4ef6", self)
        act_open_files.triggered.connect(self.open_files)
        tb.addAction(act_open_files)

        act_open_folder = QAction("📁 打开文件夹", self)
        act_open_folder.triggered.connect(self.open_folder)
        tb.addAction(act_open_folder)

        act_rename_next = QAction("✏️ 改名并下一张", self)
        act_rename_next.triggered.connect(self.rename_and_next)
        tb.addAction(act_rename_next)

        act_export = QAction("💾 导出Excel", self)
        act_export.triggered.connect(self.export_excel)
        tb.addAction(act_export)
        
        # 添加分隔符
        tb.addSeparator()
        
        # 添加重置缩放按钮
        act_reset_zoom = QAction("🔍 重置缩放", self)
        act_reset_zoom.triggered.connect(self._reset_image_zoom)
        tb.addAction(act_reset_zoom)
        
        # 添加分隔符
        tb.addSeparator()
        
        # 添加下载引擎按钮
        act_download_engine = QAction("⬇️ 下载引擎", self)
        act_download_engine.triggered.connect(lambda: self._show_download_dialog())
        tb.addAction(act_download_engine)
        
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
        
        # 添加缓存状态标签（可选）
        tb.addSeparator()
        self.cache_status_label = QLabel()
        self._update_cache_status_label()
        tb.addWidget(self.cache_status_label)
        
        # 初始化下拉框（OCR引擎未初始化时的占位）
        self.engine_combo.addItem("初始化中...")
        self.engine_combo.setEnabled(False)  # 初始化完成前禁用
        
        # 绑定信号（初始化完成后才会生效）
        self.engine_combo.currentTextChanged.connect(self.on_engine_changed)

        # 中心布局 - 关键组件，立即创建
        central = QWidget(self)
        self.setCentralWidget(central)
        h = QHBoxLayout(central)

        splitter = QSplitter(Qt.Horizontal)
        h.addWidget(splitter)

        # 左侧：图片+结果
        left = QWidget()
        left_v = QVBoxLayout(left)
        self.image_label = RectSelectionLabel()
        self.image_label.setFocusPolicy(Qt.StrongFocus)  # 允许接收键盘焦点
        left_v.addWidget(self.image_label, stretch=1)
        self.image_label.rect_finished.connect(self.on_rect_finished)
        self.image_label.rect_removed.connect(self.on_rect_removed)

        left_v.addWidget(QLabel("识别结果（可编辑）:"))
        self.result_text = QTextEdit()
        self.result_text.setPlaceholderText("OCR识别结果将显示在此，支持手动编辑修正...")
        # 延迟连接信号（使用QTimer）
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, lambda: self.result_text.textChanged.connect(self.on_result_text_changed))
        left_v.addWidget(self.result_text, stretch=0)

        # 右侧：文件表 - 延迟初始化表格内容
        right = QWidget()
        right_v = QVBoxLayout(right)
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["序号", "文件名", "状态"])
        
        # 设置列宽
        self.table.setColumnWidth(0, 50)   # 序号列：50px
        self.table.setColumnWidth(1, 250)  # 文件名列：250px
        self.table.setColumnWidth(2, 80)   # 状态列：80px
        
        # 延迟设置列的拉伸模式（使用QTimer）
        from PySide6.QtCore import QTimer
        QTimer.singleShot(0, self._init_table_header)
        
        self.table.cellClicked.connect(self.on_table_clicked)  # 单击切换
        self.table.cellDoubleClicked.connect(self.on_table_double_clicked)  # 双击（保留）
        right_v.addWidget(self.table)

        splitter.addWidget(left)
        splitter.addWidget(right)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 2)

        # 状态栏 - 关键组件，立即创建
        sb = QStatusBar()
        self.setStatusBar(sb)
    
    def _init_table_header(self):
        """
        延迟初始化表格头部（非关键组件）
        
        验证需求: 8.3
        """
        from PySide6.QtWidgets import QHeaderView
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)      # 序号固定宽度
        header.setSectionResizeMode(1, QHeaderView.Stretch)    # 文件名自适应拉伸
        header.setSectionResizeMode(2, QHeaderView.Fixed)      # 状态固定宽度
    
    def _check_and_init_engines(self):
        """
        检查OCR引擎是否已安装，如果没有则提示下载
        
        验证需求: 6.1
        """
        # 检查是否有任何引擎已安装
        has_any_engine = False
        for engine_type in ['paddle', 'rapid']:
            if self.engine_downloader.is_installed(engine_type):
                has_any_engine = True
                break
        
        if not has_any_engine:
            # 没有任何引擎，提示用户下载
            reply = QMessageBox.question(
                self,
                "首次启动",
                "检测到您是首次使用本程序，需要下载OCR引擎才能使用识别功能。\n\n"
                "推荐下载 RapidOCR（轻量级，45MB）\n"
                "或 PaddleOCR（高精度，562MB）\n\n"
                "是否现在下载？\n\n"
                "点击 Yes 立即下载\n"
                "点击 No 稍后下载（可在菜单中手动下载）",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # 打开下载对话框，默认选择RapidOCR
                self._show_download_dialog('rapid')
            else:
                self.statusBar().showMessage("提示: 请在工具栏中下载OCR引擎后使用识别功能", 5000)
        else:
            # 有引擎，正常初始化
            self._start_ocr_init_thread()
    
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
        """
        更新引擎下拉框菜单
        
        显示所有引擎（包括未安装的），未安装的引擎标记为"未安装"
        
        验证需求: 6.5
        """
        # 暂时阻塞信号，避免触发on_engine_changed
        self.engine_combo.blockSignals(True)
        self.engine_combo.clear()
        
        if not self.ocr_manager:
            self.engine_combo.addItem("初始化中...")
            self.engine_combo.setEnabled(False)
            self.engine_combo.blockSignals(False)
            return
        
        # 获取所有引擎（包括未安装的）
        all_engines = {
            'paddle': 'PaddleOCR（高精度C++版）',
            'rapid': 'RapidOCR（轻量级C++版）',
            'aliyun': '阿里云OCR',
            'deepseek': 'DeepSeek OCR'
        }
        
        available = self.ocr_manager.get_available_engines()
        available_types = {engine_type for engine_type, _, _, _ in available}
        
        # 添加所有引擎到下拉框
        for engine_type, display_name in all_engines.items():
            if engine_type in available_types:
                # 已安装且可用
                display_text = f"{display_name}"
                self.engine_combo.addItem(display_text, engine_type)
            else:
                # 未安装或不可用
                # 检查是否是本地引擎（可下载）
                if engine_type in ['paddle', 'rapid']:
                    if not self.engine_downloader.is_installed(engine_type):
                        display_text = f"{display_name} [未安装 - 点击下载]"
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
        """
        处理引擎选择变化
        
        如果选择的是未安装的引擎，触发下载流程
        
        验证需求: 6.5
        """
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
        
        # 检查引擎是否已安装
        if engine_type in ['paddle', 'rapid'] and not self.engine_downloader.is_installed(engine_type):
            # 未安装的本地引擎，提示下载
            engine_name = self.engine_downloader.ENGINES[engine_type]['display_name']
            size_mb = self.engine_downloader.ENGINES[engine_type]['size_mb']
            
            reply = QMessageBox.question(
                self,
                "下载引擎",
                f"{engine_name} 尚未安装\n\n"
                f"大小: {size_mb} MB\n\n"
                f"是否现在下载？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # 打开下载对话框
                self._show_download_dialog(engine_type)
            
            # 恢复之前的选择
            if self.ocr_manager.current_engine_type:
                for i in range(self.engine_combo.count()):
                    if self.engine_combo.itemData(i) == self.ocr_manager.current_engine_type.value:
                        self.engine_combo.blockSignals(True)
                        self.engine_combo.setCurrentIndex(i)
                        self.engine_combo.blockSignals(False)
                        break
            
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
            engine_mode = "在线" if info['is_online'] else "本地"
            engine_name = info['name']
            self.engine_status_label.setText(f"引擎: [{engine_mode}] {engine_name} {status}")
            self.engine_status_label.setStyleSheet(f"color: {color}; font-weight: bold;")
        else:
            self.engine_status_label.setText("引擎: 未初始化")
            self.engine_status_label.setStyleSheet("color: gray; font-weight: bold;")
    
    def _reset_image_zoom(self):
        """重置图片缩放"""
        if hasattr(self, 'image_label'):
            self.image_label.reset_zoom()
            self.statusBar().showMessage("已重置缩放", 2000)
    
    def _update_cache_status_label(self):
        """更新缓存状态标签"""
        if not self.cache_manager:
            self.cache_status_label.setText("缓存: 未初始化")
            self.cache_status_label.setStyleSheet("color: gray;")
            return
        
        status = self.cache_manager.get_status()
        
        if status.backend_type == "cpp_engine":
            self.cache_status_label.setText("缓存: ✓ C++引擎")
            self.cache_status_label.setStyleSheet("color: green;")
        elif status.backend_type == "memory":
            self.cache_status_label.setText("缓存: ⚠ 内存模式")
            self.cache_status_label.setStyleSheet("color: orange;")
            # 设置工具提示显示详细信息
            if status.init_error:
                tooltip = f"C++引擎不可用，已降级到内存缓存\n错误: {status.init_error.error_type}"
                if status.init_error.suggestions:
                    tooltip += f"\n建议: {status.init_error.suggestions[0]}"
                self.cache_status_label.setToolTip(tooltip)
        else:
            self.cache_status_label.setText("缓存: 已禁用")
            self.cache_status_label.setStyleSheet("color: gray;")
    
    def _show_download_dialog(self, engine_type: str = None):
        """
        显示引擎下载对话框
        
        :param engine_type: 预选的引擎类型（可选）
        
        验证需求: 6.2
        """
        dialog = OCREngineDownloadDialog(self, engine_type)
        dialog.download_completed.connect(self._on_engine_downloaded)
        dialog.exec()
    
    def _on_engine_downloaded(self, engine_type: str):
        """
        引擎下载完成回调
        
        自动配置引擎：
        1. 更新配置文件启用引擎
        2. 重新检测引擎可用性
        3. 初始化引擎实例
        
        :param engine_type: 下载完成的引擎类型
        
        验证需求: 6.4
        """
        self.statusBar().showMessage(f"✓ {engine_type} 引擎下载完成，正在配置...", 3000)
        
        # 步骤1: 更新配置文件启用引擎
        from config import Config
        config_key = f"{engine_type.upper()}_ENABLED"
        Config.set_config_value(config_key, True)
        
        # 步骤2: 如果OCR管理器还未初始化，现在初始化
        if not self._ocr_initialized:
            self._start_ocr_init_thread()
        else:
            # 步骤3: 如果已初始化，重新检查引擎可用性
            self.ocr_manager._check_engine_availability()
            
            # 步骤4: 更新UI
            self._update_engine_combo()
            self._update_engine_status_label()
            
            # 步骤5: 如果当前没有可用引擎，自动切换到新下载的引擎
            if not self.ocr_manager.current_engine or not self.ocr_manager.is_ready():
                if self.ocr_manager.set_engine(engine_type):
                    self.ocr = self.ocr_manager.current_engine
                    self._update_engine_combo()
                    self._update_engine_status_label()
                    self.statusBar().showMessage(f"✓ 已自动切换到 {engine_type} 引擎", 3000)
        
        QMessageBox.information(
            self,
            "配置完成",
            f"{engine_type.upper()} 引擎已下载并配置完成，可以开始使用了！"
        )

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
            
            # 序号
            self.table.setItem(row, 0, QTableWidgetItem(str(i)))
            
            # 文件名（只显示文件名，不显示完整路径）
            filename = os.path.basename(p)
            filename_item = QTableWidgetItem(filename)
            filename_item.setToolTip(p)  # 鼠标悬停显示完整路径
            self.table.setItem(row, 1, filename_item)
            
            # 状态
            self.table.setItem(row, 2, QTableWidgetItem("待处理"))

    def on_table_clicked(self, row, col):
        """单击文件列表切换图片"""
        if row != self.cur_index:
            self.load_index(row)
    
    def on_table_double_clicked(self, row, col):
        """双击文件列表（保留兼容）"""
        self.load_index(row)

    # ---- 加载显示 ----
    def load_index(self, idx: int):
        if idx < 0 or idx >= len(self.files):
            return
        
        # 保存当前图片的结果
        if self.cur_index >= 0 and self.cur_index < len(self.files):
            old_file = self.files[self.cur_index]
            self.all_ocr_results[old_file] = {
                "rects": self.rects.copy(),
                "status": self.table.item(self.cur_index, 2).text() if self.table.item(self.cur_index, 2) else "待处理"
            }
            
            # 释放前一个图像的内存（验证需求: 9.1, 9.3）
            if self.cur_pil:
                OptimizedImageLoader.release_image(self.cur_pil)
                self.cur_pil = None
            if self.cur_pix:
                self.cur_pix = None
            
            # 触发垃圾回收（验证需求: 9.4）
            OptimizedImageLoader.trigger_gc()
        
        self.cur_index = idx
        path = self.files[idx]
        try:
            pil = ImageUtils.load_image(path)
            self.cur_pil = pil
            # 转 QPixmap 显示
            qimg = self._pil_to_qpixmap(pil)
            self.cur_pix = qimg
            self.image_label.load_image(qimg, pil.width, pil.height)
            
            # 从all_ocr_results恢复区域（如果有）
            # 临时断开信号，避免触发文本同步
            try:
                self.result_text.textChanged.disconnect(self.on_result_text_changed)
            except (RuntimeError, TypeError):
                pass  # 信号未连接或其他问题时忽略
            
            if path in self.all_ocr_results:
                self.rects = self.all_ocr_results[path]["rects"].copy()
                
                # 🔑 关键：将OCRRect转换为显示坐标的QRect，恢复显示层的矩形
                display_rects = []
                for rect in self.rects:
                    # OCRRect 使用 x1, y1, x2, y2，需要转换为 x, y, width, height
                    width = rect.x2 - rect.x1
                    height = rect.y2 - rect.y1
                    display_rect = self.image_label.image_to_display_rect(
                        rect.x1, rect.y1, width, height
                    )
                    display_rects.append(display_rect)
                self.image_label.set_rects(display_rects)
                
                # 恢复文本显示
                self.result_text.clear()
                for rect in self.rects:
                    if rect.text:
                        self.append_result(rect.text)
            else:
                self.rects = []
                self.image_label.clear_rects()
                self.result_text.clear()
            
            # 重新连接信号
            self.result_text.textChanged.connect(self.on_result_text_changed)
            
            # 高亮显示当前文件
            self.table.selectRow(idx)
            
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
        
        # 保存到all_ocr_results字典
        if self.cur_index >= 0 and self.cur_index < len(self.files):
            current_file = self.files[self.cur_index]
            self.all_ocr_results[current_file] = {
                "rects": self.rects.copy(),
                "status": "已识别"
            }
            # 自动保存到缓存
            self._auto_save_cache()
        
        # OCR完成后清理临时数据（验证需求: 9.3）
        OptimizedImageLoader.trigger_gc()
            
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
            
            # 临时断开信号，避免在刷新时触发文本同步
            self.result_text.textChanged.disconnect(self.on_result_text_changed)
            
            # 刷新结果显示
            self.result_text.clear()
            for rect in self.rects:
                if rect.text:
                    self.append_result(rect.text)
            
            # 重新连接信号
            self.result_text.textChanged.connect(self.on_result_text_changed)
            
            # 更新all_ocr_results
            if self.files and self.cur_index < len(self.files):
                current_file = self.files[self.cur_index]
                self.all_ocr_results[current_file] = {
                    'rects': [rect for rect in self.rects],
                    'status': self.table.item(self.cur_index, 2).text() if self.table.item(self.cur_index, 2) else '未识别'
                }
                # 自动保存到缓存
                self._auto_save_cache()
            
            self.statusBar().showMessage(f"已删除区域 {index + 1}")

    def append_result(self, text: str):
        """
        添加识别结果到文本框
        将多行文本合并为一行显示，提升可读性
        """
        if not text:
            text = "(空)"
        else:
            # 将多行文本合并为一行，用空格连接
            text = text.replace('\n', ' ').replace('\r', ' ')
            # 去除多余的空格
            text = ' '.join(text.split())
        
        self.result_text.append(text)
    
    def on_result_text_changed(self):
        """
        文本框内容变化时，同步到区域对象
        将文本框的每一行对应到各个区域
        """
        if not self.rects:
            return
        
        # 获取文本框内容并按行分割
        text_content = self.result_text.toPlainText()
        lines = text_content.split('\n')
        
        # 将每行同步到对应的区域
        for i, rect in enumerate(self.rects):
            if i < len(lines):
                rect.text = lines[i]
            else:
                rect.text = ""  # 如果行数不足，设为空

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
        
        # 获取文本框内容（支持用户编辑后的内容）
        text_content = self.result_text.toPlainText().strip()
        if not text_content:
            QMessageBox.information(self, "提示", "没有可用于重命名的识别结果。")
            return
        
        # 使用第一行作为文件名（如果有多行）
        first_line = text_content.split('\n')[0].strip()
        if not first_line:
            QMessageBox.information(self, "提示", "识别结果为空，无法重命名。")
            return
        
        src = self.files[self.cur_index]
        directory = str(Path(src).parent)
        base = FileUtils.clean_filename(first_line)
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
        
        # 保存当前图片的结果
        if self.cur_index >= 0 and self.cur_index < len(self.files):
            current_file = self.files[self.cur_index]
            self.all_ocr_results[current_file] = {
                "rects": self.rects.copy(),
                "status": self.table.item(self.cur_index, 2).text() if self.table.item(self.cur_index, 2) else "待处理"
            }
        
        # 第一步：让用户选择导出模式
        reply = QMessageBox.question(
            self,
            "选择导出模式",
            "请选择Excel导出方式：\n\n"
            "• 追加模式：将数据追加到已有Excel文件\n"
            "• 新建模式：创建新的Excel文件（如文件存在则自动重命名）\n",
            QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel,
            QMessageBox.Yes
        )
        
        # 用户取消
        if reply == QMessageBox.Cancel:
            return
        
        # 根据用户选择确定模式
        append_mode = (reply == QMessageBox.Yes)
        
        # 第二步：根据模式选择文件
        if append_mode:
            # 追加模式：选择已存在的Excel文件
            save_path, _ = QFileDialog.getOpenFileName(
                self,
                "选择要追加的Excel文件",
                str(Path.cwd()),
                "Excel文件 (*.xlsx)"
            )
            if not save_path:
                return
        else:
            # 新建模式：保存新文件
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "保存为新Excel文件",
                str(Path.cwd() / "ocr结果.xlsx"),
                "Excel文件 (*.xlsx)"
            )
            if not save_path:
                return
        
        # 汇总结果：使用all_ocr_results而非仅当前rects
        results = {}
        for p in self.files:
            if p in self.all_ocr_results:
                results[p] = self.all_ocr_results[p]
            else:
                # 未识别的文件
                idx = self.files.index(p)
                results[p] = {
                    "rects": [],
                    "status": self.table.item(idx, 2).text() if self.table.item(idx, 2) else "待处理"
                }
        
        # 导出Excel
        ok = ExcelExporter.export_results(results, save_path, append_mode=append_mode)
        if ok:
            mode_text = "追加" if append_mode else "新建"
            QMessageBox.information(self, "成功", f"Excel导出完成（{mode_text}模式）。")
        else:
            QMessageBox.warning(self, "失败", "导出失败。")

    def update_current_status(self, text: str):
        if 0 <= self.cur_index < self.table.rowCount():
            self.table.setItem(self.cur_index, 2, QTableWidgetItem(text))


    def _auto_save_cache(self):
        """
        自动保存缓存
        
        使用CacheManagerWrapper，不会抛出异常
        验证需求: 1.1, 5.1
        """
        if not self.cache_manager:
            return
        
        # 保存当前文件的结果
        if self.cur_index >= 0 and self.cur_index < len(self.files):
            current_file = self.files[self.cur_index]
            if current_file in self.all_ocr_results:
                result = self.all_ocr_results[current_file]
                # CacheManagerWrapper.save_result 不会抛出异常
                self.cache_manager.save_result(
                    current_file,
                    result["rects"],
                    result["status"]
                )
        
        # 保存会话信息
        # CacheManagerWrapper.save_session 不会抛出异常
        self.cache_manager.save_session(self.files, self.cur_index)
    
    def _check_restore_session(self):
        """
        检查是否恢复会话
        
        使用CacheManagerWrapper，不会抛出异常
        验证需求: 1.1, 5.1
        """
        if not self.cache_manager:
            return
        
        # CacheManagerWrapper.has_cache 不会抛出异常
        if self.cache_manager.has_cache():
            reply = QMessageBox.question(
                self,
                "发现未完成任务",
                "检测到上次未完成的识别任务，是否继续？\n\n"
                "点击 Yes 继续上次任务\n"
                "点击 No 开始新任务（清除缓存）",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            
            if reply == QMessageBox.Yes:
                # 恢复会话
                # CacheManagerWrapper.load_session 不会抛出异常
                session = self.cache_manager.load_session()
                if session:
                    self.files = session.get("files", [])
                    cur_index = session.get("cur_index", 0)
                    
                    # 加载所有OCR结果
                    # CacheManagerWrapper.load_all_results 不会抛出异常
                    self.all_ocr_results = self.cache_manager.load_all_results()
                    
                    # 刷新表格
                    self.refresh_table()
                    
                    # 更新状态
                    for i, file_path in enumerate(self.files):
                        if file_path in self.all_ocr_results:
                            status = self.all_ocr_results[file_path].get("status", "待处理")
                            self.table.setItem(i, 2, QTableWidgetItem(status))
                    
                    # 加载当前索引的图片
                    if 0 <= cur_index < len(self.files):
                        self.load_index(cur_index)
                        self.table.selectRow(cur_index)
                    
                    self.statusBar().showMessage("✓ 已恢复上次会话", 3000)
            else:
                # 清除缓存
                # CacheManagerWrapper.clear_cache 不会抛出异常
                self.cache_manager.clear_cache()
                self.statusBar().showMessage("已清除旧缓存", 2000)
    
    def _on_idle_timeout(self):
        """
        空闲定时器回调
        
        定期触发垃圾回收以释放内存
        验证需求: 9.4
        """
        # 检查是否有正在进行的OCR任务
        has_active_tasks = any(worker.isRunning() for worker in self._ocr_tasks)
        
        # 如果没有活动任务，触发垃圾回收
        if not has_active_tasks:
            OptimizedImageLoader.trigger_gc()
    
    def release_memory(self):
        """
        主动释放内存
        
        在空闲时调用，释放不必要的内存占用
        验证需求: 9.1, 9.4
        """
        # 触发垃圾回收
        OptimizedImageLoader.trigger_gc()
    
    def closeEvent(self, event):
        """
        窗口关闭事件：保存缓存并清理线程资源
        """
        # 停止空闲定时器
        if hasattr(self, '_idle_timer'):
            self._idle_timer.stop()
        
        # 释放图像内存
        if self.cur_pil:
            OptimizedImageLoader.release_image(self.cur_pil)
            self.cur_pil = None
        if self.cur_pix:
            self.cur_pix = None
        
        # 保存当前状态到缓存
        if self.cur_index >= 0 and self.cur_index < len(self.files):
            current_file = self.files[self.cur_index]
            self.all_ocr_results[current_file] = {
                "rects": self.rects.copy(),
                "status": self.table.item(self.cur_index, 2).text() if self.table.item(self.cur_index, 2) else "待处理"
            }
        
        # 保存所有结果到缓存
        # CacheManagerWrapper 不会抛出异常，无需try-except
        if self.cache_manager:
            for file_path, result in self.all_ocr_results.items():
                self.cache_manager.save_result(
                    file_path,
                    result["rects"],
                    result["status"]
                )
            self.cache_manager.save_session(self.files, self.cur_index)
        
        # 先关闭所有OCR引擎（关键！防止子进程残留）
        if self.ocr_manager:
            try:
                print("正在关闭OCR引擎...")
                # 关闭所有已初始化的引擎实例
                for engine_type, engine_instance in self.ocr_manager._engine_instances.items():
                    try:
                        # 调用引擎的析构方法关闭子进程
                        if hasattr(engine_instance, '__del__'):
                            engine_instance.__del__()
                        elif hasattr(engine_instance, 'close'):
                            engine_instance.close()
                    except Exception as e:
                        print(f"关闭引擎 {engine_type} 失败: {e}")
                print("OCR引擎已关闭")
            except Exception as e:
                print(f"关闭OCR引擎失败: {e}")
        
        # 停止初始化线程（这是崩溃的主要原因）
        if hasattr(self, '_ocr_worker') and self._ocr_worker:
            if self._ocr_worker.isRunning():
                print("正在停止OCR初始化线程...")
                self._ocr_worker.requestInterruption()  # 请求中断
                self._ocr_worker.quit()  # 请求线程退出
                if not self._ocr_worker.wait(3000):  # 等待3秒
                    print("强制终止OCR初始化线程...")
                    self._ocr_worker.terminate()  # 强制终止
                    self._ocr_worker.wait()
                print("OCR初始化线程已停止")
        
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