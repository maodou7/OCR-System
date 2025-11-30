"""
测试CacheManagerWrapper与qt_main.py的集成

验证需求: 1.1, 1.5, 5.1
"""

import sys
from PySide6.QtWidgets import QApplication


def test_main_window_starts_with_cache_wrapper():
    """
    测试主窗口能够使用CacheManagerWrapper正常启动
    
    验证:
    - 主窗口能够成功创建
    - cache_manager是CacheManagerWrapper实例
    - 缓存管理器不为None
    - 应用程序不会因为缓存初始化失败而崩溃
    
    验证需求: 1.1, 5.1
    """
    # 创建QApplication（如果还没有）
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        # 导入并创建主窗口
        from qt_main import MainWindow
        from cache_manager_wrapper import CacheManagerWrapper
        
        # 创建主窗口
        window = MainWindow()
        
        # 验证cache_manager存在且是CacheManagerWrapper实例
        assert window.cache_manager is not None, "cache_manager不应该为None"
        assert isinstance(window.cache_manager, CacheManagerWrapper), \
            f"cache_manager应该是CacheManagerWrapper实例，实际是{type(window.cache_manager)}"
        
        # 验证缓存管理器可用（即使C++引擎失败，也应该有内存缓存）
        assert window.cache_manager.is_cache_available(), \
            "缓存管理器应该可用（至少有内存缓存）"
        
        # 验证缓存状态标签存在
        assert hasattr(window, 'cache_status_label'), "应该有cache_status_label"
        
        # 清理
        window.close()
        
        print("✓ 主窗口成功使用CacheManagerWrapper启动")
        
    except Exception as e:
        pytest.fail(f"主窗口启动失败: {e}")


def test_cache_operations_dont_crash_app():
    """
    测试缓存操作不会导致应用崩溃
    
    验证:
    - save_result不会抛出异常
    - load_all_results不会抛出异常
    - save_session不会抛出异常
    - load_session不会抛出异常
    - has_cache不会抛出异常
    - clear_cache不会抛出异常
    
    验证需求: 1.1, 1.3, 5.1
    """
    # 创建QApplication（如果还没有）
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        from qt_main import MainWindow
        from config import OCRRect
        
        # 创建主窗口
        window = MainWindow()
        
        # 测试save_result（不应该抛出异常）
        test_rect = OCRRect(0, 0, 100, 100, "测试文本")
        result = window.cache_manager.save_result("test.png", [test_rect], "已识别")
        assert isinstance(result, bool), "save_result应该返回bool"
        
        # 测试load_all_results（不应该抛出异常）
        results = window.cache_manager.load_all_results()
        assert isinstance(results, dict), "load_all_results应该返回dict"
        
        # 测试save_session（不应该抛出异常）
        result = window.cache_manager.save_session(["test1.png", "test2.png"], 0)
        assert isinstance(result, bool), "save_session应该返回bool"
        
        # 测试load_session（不应该抛出异常）
        session = window.cache_manager.load_session()
        # session可能是None或dict
        assert session is None or isinstance(session, dict), \
            "load_session应该返回None或dict"
        
        # 测试has_cache（不应该抛出异常）
        has_cache = window.cache_manager.has_cache()
        assert isinstance(has_cache, bool), "has_cache应该返回bool"
        
        # 测试clear_cache（不应该抛出异常）
        window.cache_manager.clear_cache()
        
        # 清理
        window.close()
        
        print("✓ 所有缓存操作都不会导致应用崩溃")
        
    except Exception as e:
        pytest.fail(f"缓存操作测试失败: {e}")


def test_cache_status_display():
    """
    测试缓存状态显示功能
    
    验证:
    - 缓存状态标签存在
    - 状态标签有文本
    - 状态标签有样式
    
    验证需求: 1.5
    """
    # 创建QApplication（如果还没有）
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    try:
        from qt_main import MainWindow
        
        # 创建主窗口
        window = MainWindow()
        
        # 验证缓存状态标签存在
        assert hasattr(window, 'cache_status_label'), "应该有cache_status_label"
        
        # 验证标签有文本
        label_text = window.cache_status_label.text()
        assert label_text, "缓存状态标签应该有文本"
        assert "缓存" in label_text, "标签文本应该包含'缓存'"
        
        # 验证标签有样式
        style = window.cache_status_label.styleSheet()
        assert style, "缓存状态标签应该有样式"
        
        # 验证get_status方法可用
        status = window.cache_manager.get_status()
        assert status is not None, "get_status应该返回状态对象"
        assert hasattr(status, 'backend_type'), "状态对象应该有backend_type属性"
        
        # 清理
        window.close()
        
        print("✓ 缓存状态显示功能正常")
        
    except Exception as e:
        pytest.fail(f"缓存状态显示测试失败: {e}")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "-s"])
