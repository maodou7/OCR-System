"""
OCR引擎下载对话框

提供用户友好的引擎下载界面，支持：
- 引擎选择
- 下载进度显示
- 取消下载功能

验证需求: 6.2
"""

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QComboBox, QTextEdit, QMessageBox, QGroupBox
)

from ocr_engine_downloader import OCREngineDownloader


class DownloadWorker(QThread):
    """后台下载线程"""
    
    # 信号
    download_progress = Signal(int, int, str)  # (downloaded_mb, total_mb, message)
    extract_progress = Signal(str)  # (message)
    finished = Signal(bool, str)  # (success, message)
    
    def __init__(self, downloader: OCREngineDownloader, engine_type: str):
        super().__init__()
        self.downloader = downloader
        self.engine_type = engine_type
        self._cancelled = False
    
    def run(self):
        """执行下载和安装"""
        try:
            # 下载
            success, msg = self.downloader.download(
                self.engine_type,
                progress_callback=self._on_download_progress
            )
            
            if not success or self._cancelled:
                self.finished.emit(False, msg if not self._cancelled else "下载已取消")
                return
            
            # 解压
            success, msg = self.downloader.extract(
                self.engine_type,
                progress_callback=self._on_extract_progress
            )
            
            if not success or self._cancelled:
                self.finished.emit(False, msg if not self._cancelled else "安装已取消")
                return
            
            # 完成
            self.finished.emit(True, msg)
        
        except Exception as e:
            self.finished.emit(False, f"下载失败: {str(e)}")
    
    def _on_download_progress(self, downloaded_mb: int, total_mb: int, message: str):
        """下载进度回调"""
        if not self._cancelled:
            self.download_progress.emit(downloaded_mb, total_mb, message)
    
    def _on_extract_progress(self, message: str):
        """解压进度回调"""
        if not self._cancelled:
            self.extract_progress.emit(message)
    
    def cancel(self):
        """取消下载"""
        self._cancelled = True
        self.requestInterruption()


class OCREngineDownloadDialog(QDialog):
    """
    OCR引擎下载对话框
    
    功能:
    - 显示可用引擎列表
    - 显示下载进度
    - 支持取消下载
    
    验证需求: 6.2
    """
    
    # 信号：下载完成
    download_completed = Signal(str)  # engine_type
    
    def __init__(self, parent=None, engine_type: str = None):
        """
        初始化对话框
        
        :param parent: 父窗口
        :param engine_type: 预选的引擎类型（可选）
        """
        super().__init__(parent)
        
        self.downloader = OCREngineDownloader()
        self.download_worker = None
        self.selected_engine = engine_type
        
        self._init_ui()
        self._update_engine_list()
        
        # 如果指定了引擎类型，自动选择
        if engine_type:
            self._select_engine(engine_type)
    
    def _init_ui(self):
        """初始化UI"""
        self.setWindowTitle("下载OCR引擎")
        self.setMinimumWidth(500)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout(self)
        
        # 引擎选择区域
        engine_group = QGroupBox("选择引擎")
        engine_layout = QVBoxLayout(engine_group)
        
        # 引擎下拉框
        engine_select_layout = QHBoxLayout()
        engine_select_layout.addWidget(QLabel("OCR引擎:"))
        
        self.engine_combo = QComboBox()
        self.engine_combo.currentTextChanged.connect(self._on_engine_changed)
        engine_select_layout.addWidget(self.engine_combo, stretch=1)
        
        engine_layout.addLayout(engine_select_layout)
        
        # 引擎信息显示
        self.engine_info_label = QLabel()
        self.engine_info_label.setWordWrap(True)
        self.engine_info_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        engine_layout.addWidget(self.engine_info_label)
        
        layout.addWidget(engine_group)
        
        # 进度区域
        progress_group = QGroupBox("下载进度")
        progress_layout = QVBoxLayout(progress_group)
        
        # 进度条
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        # 状态标签
        self.status_label = QLabel("准备就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        progress_layout.addWidget(self.status_label)
        
        # 日志文本框
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        progress_layout.addWidget(self.log_text)
        
        layout.addWidget(progress_group)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        self.download_button = QPushButton("开始下载")
        self.download_button.clicked.connect(self._start_download)
        button_layout.addWidget(self.download_button)
        
        self.cancel_button = QPushButton("取消")
        self.cancel_button.clicked.connect(self._cancel_download)
        self.cancel_button.setEnabled(False)
        button_layout.addWidget(self.cancel_button)
        
        self.close_button = QPushButton("关闭")
        self.close_button.clicked.connect(self.close)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
    
    def _update_engine_list(self):
        """更新引擎列表"""
        self.engine_combo.clear()
        
        # 获取所有引擎状态
        engines_status = self.downloader.get_all_engines_status()
        
        for engine_type, info in engines_status.items():
            display_text = f"{info['display_name']} ({info['size_mb']} MB)"
            if info['installed']:
                display_text += " [已安装]"
            
            self.engine_combo.addItem(display_text, engine_type)
    
    def _select_engine(self, engine_type: str):
        """选择指定的引擎"""
        for i in range(self.engine_combo.count()):
            if self.engine_combo.itemData(i) == engine_type:
                self.engine_combo.setCurrentIndex(i)
                break
    
    def _on_engine_changed(self, display_text: str):
        """引擎选择变化"""
        index = self.engine_combo.currentIndex()
        if index < 0:
            return
        
        engine_type = self.engine_combo.itemData(index)
        self.selected_engine = engine_type
        
        # 更新引擎信息显示
        info = self.downloader.get_engine_info(engine_type)
        if info:
            info_text = f"<b>{info['display_name']}</b><br>"
            info_text += f"大小: {info['size_mb']} MB<br>"
            info_text += f"状态: {'已安装 ✓' if info['installed'] else '未安装'}<br>"
            
            self.engine_info_label.setText(info_text)
            
            # 如果已安装，禁用下载按钮
            if info['installed']:
                self.download_button.setEnabled(False)
                self.download_button.setText("已安装")
            else:
                self.download_button.setEnabled(True)
                self.download_button.setText("开始下载")
    
    def _start_download(self):
        """开始下载"""
        if not self.selected_engine:
            QMessageBox.warning(self, "提示", "请选择要下载的引擎")
            return
        
        # 检查是否已安装
        if self.downloader.is_installed(self.selected_engine):
            QMessageBox.information(self, "提示", "该引擎已安装")
            return
        
        # 禁用控件
        self.engine_combo.setEnabled(False)
        self.download_button.setEnabled(False)
        self.cancel_button.setEnabled(True)
        self.close_button.setEnabled(False)
        
        # 清空日志
        self.log_text.clear()
        self.progress_bar.setValue(0)
        
        # 创建并启动下载线程
        self.download_worker = DownloadWorker(self.downloader, self.selected_engine)
        self.download_worker.download_progress.connect(self._on_download_progress)
        self.download_worker.extract_progress.connect(self._on_extract_progress)
        self.download_worker.finished.connect(self._on_download_finished)
        self.download_worker.start()
        
        self._log(f"开始下载 {self.downloader.ENGINES[self.selected_engine]['display_name']}...")
    
    def _cancel_download(self):
        """取消下载"""
        if self.download_worker and self.download_worker.isRunning():
            reply = QMessageBox.question(
                self,
                "确认取消",
                "确定要取消下载吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                self._log("正在取消下载...")
                self.download_worker.cancel()
                self.download_worker.quit()
                self.download_worker.wait()
                
                self._log("下载已取消")
                self._reset_ui()
    
    def _on_download_progress(self, downloaded_mb: int, total_mb: int, message: str):
        """下载进度更新"""
        # 更新进度条
        if total_mb > 0:
            percent = int((downloaded_mb / total_mb) * 100)
            self.progress_bar.setValue(percent)
        
        # 更新状态标签
        self.status_label.setText(message)
        
        # 记录日志
        self._log(message)
    
    def _on_extract_progress(self, message: str):
        """解压进度更新"""
        # 更新状态标签
        self.status_label.setText(message)
        
        # 记录日志
        self._log(message)
        
        # 解压阶段设置进度条为不确定状态
        self.progress_bar.setRange(0, 0)
    
    def _on_download_finished(self, success: bool, message: str):
        """下载完成"""
        # 恢复进度条
        self.progress_bar.setRange(0, 100)
        
        if success:
            self.progress_bar.setValue(100)
            self.status_label.setText("✓ 安装完成")
            self._log(f"✓ {message}")
            
            # 发送完成信号
            self.download_completed.emit(self.selected_engine)
            
            QMessageBox.information(self, "成功", message)
        else:
            self.status_label.setText("✗ 安装失败")
            self._log(f"✗ {message}")
            
            QMessageBox.warning(self, "失败", message)
        
        # 重置UI
        self._reset_ui()
        
        # 更新引擎列表
        self._update_engine_list()
    
    def _reset_ui(self):
        """重置UI状态"""
        self.engine_combo.setEnabled(True)
        self.download_button.setEnabled(True)
        self.cancel_button.setEnabled(False)
        self.close_button.setEnabled(True)
        
        # 更新引擎信息
        self._on_engine_changed(self.engine_combo.currentText())
    
    def _log(self, message: str):
        """添加日志"""
        self.log_text.append(message)
        # 自动滚动到底部
        self.log_text.verticalScrollBar().setValue(
            self.log_text.verticalScrollBar().maximum()
        )
    
    def closeEvent(self, event):
        """关闭事件"""
        # 如果正在下载，提示用户
        if self.download_worker and self.download_worker.isRunning():
            reply = QMessageBox.question(
                self,
                "确认关闭",
                "下载正在进行中，确定要关闭吗？",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # 取消下载
                self.download_worker.cancel()
                self.download_worker.quit()
                self.download_worker.wait()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    """测试对话框"""
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    
    dialog = OCREngineDownloadDialog()
    dialog.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
