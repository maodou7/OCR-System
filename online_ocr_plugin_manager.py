"""
在线OCR插件管理器 - GUI版本

提供图形界面用于管理在线OCR插件的安装和配置。
"""

import sys
import subprocess
from typing import Dict, Optional
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTextEdit, QGroupBox, QMessageBox, QProgressDialog
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QFont


class PluginInstallThread(QThread):
    """插件安装线程"""
    
    progress = Signal(str)  # 进度信息
    finished = Signal(bool, str)  # 完成信号 (成功, 消息)
    
    def __init__(self, plugin_id: str, packages: list):
        super().__init__()
        self.plugin_id = plugin_id
        self.packages = packages
        self.python_cmd = sys.executable
    
    def run(self):
        """执行安装"""
        try:
            for package in self.packages:
                self.progress.emit(f"正在安装 {package}...")
                
                result = subprocess.run(
                    [self.python_cmd, '-m', 'pip', 'install', package],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                self.progress.emit(f"✓ {package} 安装成功")
            
            self.finished.emit(True, "安装成功！")
        
        except subprocess.CalledProcessError as e:
            error_msg = f"安装失败: {e.stderr}"
            self.finished.emit(False, error_msg)
        
        except Exception as e:
            self.finished.emit(False, f"安装失败: {str(e)}")


class OnlineOCRPluginManagerDialog(QDialog):
    """在线OCR插件管理器对话框"""
    
    # 插件定义
    PLUGINS = {
        'aliyun': {
            'name': '阿里云OCR',
            'description': '阿里云在线OCR服务，支持多种特殊证件识别',
            'packages': [
                'alibabacloud-ocr-api20210707>=1.0.0',
                'alibabacloud-tea-openapi>=0.3.0',
                'alibabacloud-tea-util>=0.3.0',
                'alibabacloud-openapi-util>=0.2.0',
            ],
            'config_hint': (
                "配置步骤：\n"
                "1. 在 config.py 中设置：\n"
                "   ALIYUN_ENABLED = True\n"
                "   ALIYUN_ACCESS_KEY_ID = 'your_key_id'\n"
                "   ALIYUN_ACCESS_KEY_SECRET = 'your_key_secret'\n\n"
                "2. 或使用环境变量（推荐）：\n"
                "   export ALIYUN_ACCESS_KEY_ID='your_key_id'\n"
                "   export ALIYUN_ACCESS_KEY_SECRET='your_key_secret'"
            )
        },
        'deepseek': {
            'name': 'DeepSeek OCR',
            'description': '硅基流动DeepSeek-OCR服务，AI大模型驱动',
            'packages': [
                'openai>=1.0.0',
            ],
            'config_hint': (
                "配置步骤：\n"
                "1. 在 config.py 中设置：\n"
                "   DEEPSEEK_ENABLED = True\n"
                "   DEEPSEEK_API_KEY = 'your_api_key'\n\n"
                "2. 或使用环境变量（推荐）：\n"
                "   export DEEPSEEK_API_KEY='your_api_key'"
            )
        }
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("在线OCR插件管理器")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        
        self.install_thread = None
        
        self.init_ui()
        self.check_plugin_status()
    
    def init_ui(self):
        """初始化UI"""
        layout = QVBoxLayout()
        
        # 标题
        title_label = QLabel("在线OCR插件管理")
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        layout.addWidget(title_label)
        
        # 说明
        info_label = QLabel(
            "在线OCR是可选插件，需要单独安装依赖包。\n"
            "核心版本不包含这些依赖，以减小程序体积。"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addSpacing(10)
        
        # 插件列表
        for plugin_id, plugin_info in self.PLUGINS.items():
            plugin_group = self.create_plugin_group(plugin_id, plugin_info)
            layout.addWidget(plugin_group)
        
        layout.addStretch()
        
        # 关闭按钮
        close_btn = QPushButton("关闭")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def create_plugin_group(self, plugin_id: str, plugin_info: Dict) -> QGroupBox:
        """
        创建插件组
        
        :param plugin_id: 插件ID
        :param plugin_info: 插件信息
        :return: QGroupBox
        """
        group = QGroupBox(plugin_info['name'])
        layout = QVBoxLayout()
        
        # 描述
        desc_label = QLabel(plugin_info['description'])
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # 状态和按钮
        btn_layout = QHBoxLayout()
        
        # 状态标签
        status_label = QLabel()
        status_label.setObjectName(f"status_{plugin_id}")
        btn_layout.addWidget(status_label)
        
        btn_layout.addStretch()
        
        # 安装按钮
        install_btn = QPushButton("安装")
        install_btn.setObjectName(f"install_{plugin_id}")
        install_btn.clicked.connect(lambda: self.install_plugin(plugin_id))
        btn_layout.addWidget(install_btn)
        
        # 配置说明按钮
        config_btn = QPushButton("配置说明")
        config_btn.clicked.connect(lambda: self.show_config_hint(plugin_id))
        btn_layout.addWidget(config_btn)
        
        layout.addLayout(btn_layout)
        
        group.setLayout(layout)
        return group
    
    def check_plugin_status(self):
        """检查所有插件的安装状态"""
        for plugin_id in self.PLUGINS.keys():
            installed = self.is_plugin_installed(plugin_id)
            self.update_plugin_status(plugin_id, installed)
    
    def is_plugin_installed(self, plugin_id: str) -> bool:
        """
        检查插件是否已安装
        
        :param plugin_id: 插件ID
        :return: 是否已安装
        """
        if plugin_id not in self.PLUGINS:
            return False
        
        packages = self.PLUGINS[plugin_id]['packages']
        
        for package in packages:
            # 提取包名（去除版本号）
            package_name = package.split('>=')[0].split('==')[0].split('<')[0]
            
            try:
                # 尝试导入包
                __import__(package_name.replace('-', '_'))
            except ImportError:
                return False
        
        return True
    
    def update_plugin_status(self, plugin_id: str, installed: bool):
        """
        更新插件状态显示
        
        :param plugin_id: 插件ID
        :param installed: 是否已安装
        """
        status_label = self.findChild(QLabel, f"status_{plugin_id}")
        install_btn = self.findChild(QPushButton, f"install_{plugin_id}")
        
        if status_label:
            if installed:
                status_label.setText("✓ 已安装")
                status_label.setStyleSheet("color: green; font-weight: bold;")
            else:
                status_label.setText("✗ 未安装")
                status_label.setStyleSheet("color: red;")
        
        if install_btn:
            install_btn.setEnabled(not installed)
            if installed:
                install_btn.setText("已安装")
    
    def install_plugin(self, plugin_id: str):
        """
        安装插件
        
        :param plugin_id: 插件ID
        """
        if plugin_id not in self.PLUGINS:
            return
        
        plugin_info = self.PLUGINS[plugin_id]
        
        # 确认安装
        reply = QMessageBox.question(
            self,
            "确认安装",
            f"确定要安装 {plugin_info['name']} 吗？\n\n"
            f"将安装 {len(plugin_info['packages'])} 个依赖包。",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # 创建进度对话框
        progress_dialog = QProgressDialog(
            f"正在安装 {plugin_info['name']}...",
            "取消",
            0, 0,
            self
        )
        progress_dialog.setWindowTitle("安装插件")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setCancelButton(None)  # 禁用取消按钮
        progress_dialog.show()
        
        # 创建安装线程
        self.install_thread = PluginInstallThread(
            plugin_id,
            plugin_info['packages']
        )
        
        # 连接信号
        self.install_thread.progress.connect(
            lambda msg: progress_dialog.setLabelText(msg)
        )
        self.install_thread.finished.connect(
            lambda success, msg: self.on_install_finished(
                plugin_id, success, msg, progress_dialog
            )
        )
        
        # 启动安装
        self.install_thread.start()
    
    def on_install_finished(self, plugin_id: str, success: bool, 
                           message: str, progress_dialog: QProgressDialog):
        """
        安装完成回调
        
        :param plugin_id: 插件ID
        :param success: 是否成功
        :param message: 消息
        :param progress_dialog: 进度对话框
        """
        progress_dialog.close()
        
        if success:
            QMessageBox.information(
                self,
                "安装成功",
                f"{self.PLUGINS[plugin_id]['name']} 安装成功！\n\n"
                f"请点击"配置说明"按钮查看配置方法。"
            )
            
            # 更新状态
            self.update_plugin_status(plugin_id, True)
            
            # 显示配置说明
            self.show_config_hint(plugin_id)
        else:
            QMessageBox.critical(
                self,
                "安装失败",
                f"{self.PLUGINS[plugin_id]['name']} 安装失败：\n\n{message}"
            )
    
    def show_config_hint(self, plugin_id: str):
        """
        显示配置说明
        
        :param plugin_id: 插件ID
        """
        if plugin_id not in self.PLUGINS:
            return
        
        plugin_info = self.PLUGINS[plugin_id]
        
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(f"{plugin_info['name']} - 配置说明")
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(f"{plugin_info['name']} 配置说明")
        msg_box.setInformativeText(plugin_info['config_hint'])
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec()


def show_plugin_manager(parent=None):
    """
    显示插件管理器对话框
    
    :param parent: 父窗口
    :return: 对话框结果
    """
    dialog = OnlineOCRPluginManagerDialog(parent)
    return dialog.exec()


if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    
    app = QApplication(sys.argv)
    dialog = OnlineOCRPluginManagerDialog()
    dialog.show()
    sys.exit(app.exec())
