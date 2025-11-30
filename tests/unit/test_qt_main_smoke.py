"""
快速烟雾测试：验证qt_main.py能够正常启动
"""

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer


def test_smoke():
    """快速烟雾测试"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    from qt_main import MainWindow
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 验证基本属性
    print(f"✓ 主窗口创建成功")
    print(f"✓ 缓存管理器类型: {type(window.cache_manager).__name__}")
    print(f"✓ 缓存可用: {window.cache_manager.is_cache_available()}")
    
    status = window.cache_manager.get_status()
    print(f"✓ 缓存后端类型: {status.backend_type}")
    print(f"✓ 缓存状态消息: {status.message}")
    
    # 使用定时器关闭窗口
    QTimer.singleShot(100, window.close)
    QTimer.singleShot(200, app.quit)
    
    # 运行事件循环
    app.exec()
    
    print("✓ 应用程序正常启动和关闭")


if __name__ == "__main__":
    test_smoke()
