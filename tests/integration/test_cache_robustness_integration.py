#!/usr/bin/env python3
"""
缓存引擎鲁棒性集成测试

测试完整的应用启动流程、缓存失败时的OCR工作流、以及在各种环境下的行为

验证需求: 所有需求 (1.1-5.5)
"""

import os
import sys
import tempfile
import shutil
import sqlite3
import unittest
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from qt_main import MainWindow
    from cache_manager_wrapper import CacheManagerWrapper
    from ocr_cache_manager import OCRCacheManager, CacheInitError
    from config import OCRRect
except ImportError as e:
    print(f"导入失败: {e}")
    print("请确保在项目根目录运行测试")
    sys.exit(1)


class TestApplicationStartupFlow(unittest.TestCase):
    """
    测试完整的应用启动流程
    
    验证需求: 1.1, 1.2, 1.3, 5.1
    """
    
    @classmethod
    def setUpClass(cls):
        """设置测试类"""
        # 创建QApplication（如果还没有）
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)
    
    def test_app_starts_with_valid_cache(self):
        """
        测试应用在缓存引擎正常时启动
        
        验证需求: 1.1
        """
        print("\n测试: 应用在缓存引擎正常时启动")
        
        # 创建主窗口
        window = MainWindow()
        
        # 验证窗口创建成功
        self.assertIsNotNone(window)
        
        # 验证缓存管理器存在
        self.assertIsNotNone(window.cache_manager)
        self.assertIsInstance(window.cache_manager, CacheManagerWrapper)
        
        # 验证缓存可用（至少有内存缓存）
        self.assertTrue(window.cache_manager.is_cache_available())
        
        # 清理
        window.close()
        
        print("✓ 应用在缓存引擎正常时启动成功")
    
    def test_app_starts_with_invalid_cache_path(self):
        """
        测试应用在缓存路径无效时启动（应该降级到内存缓存）
        
        验证需求: 1.1, 1.2
        """
        print("\n测试: 应用在缓存路径无效时启动")
        
        # 模拟无效的缓存路径
        with patch('cache_manager_wrapper.OCRCacheManager') as mock_manager:
            # 模拟初始化失败
            mock_manager.side_effect = CacheInitError(
                error_type="invalid_path",
                error_message="无效的数据库路径",
                error_details={},
                suggestions=["检查路径是否正确"]
            )
            
            # 创建主窗口
            window = MainWindow()
            
            # 验证窗口创建成功（即使缓存失败）
            self.assertIsNotNone(window)
            
            # 验证缓存管理器存在
            self.assertIsNotNone(window.cache_manager)
            
            # 验证已降级到内存缓存
            status = window.cache_manager.get_status()
            self.assertEqual(status.backend_type, "memory")
            
            # 清理
            window.close()
        
        print("✓ 应用在缓存路径无效时成功降级到内存缓存")
    
    def test_app_starts_with_missing_library(self):
        """
        测试应用在C++库文件缺失时启动（应该降级到内存缓存）
        
        验证需求: 1.1, 1.2, 2.1
        """
        print("\n测试: 应用在C++库文件缺失时启动")
        
        # 模拟库文件不存在
        with patch('ocr_cache_manager.os.path.exists') as mock_exists:
            mock_exists.return_value = False
            
            # 创建主窗口
            window = MainWindow()
            
            # 验证窗口创建成功
            self.assertIsNotNone(window)
            
            # 验证缓存管理器存在
            self.assertIsNotNone(window.cache_manager)
            
            # 验证缓存可用（内存缓存）
            self.assertTrue(window.cache_manager.is_cache_available())
            
            # 清理
            window.close()
        
        print("✓ 应用在C++库文件缺失时成功启动")
    
    def test_app_ui_elements_initialized(self):
        """
        测试应用UI元素正确初始化
        
        验证需求: 1.5
        """
        print("\n测试: 应用UI元素正确初始化")
        
        # 创建主窗口
        window = MainWindow()
        
        # 验证关键UI元素存在
        self.assertIsNotNone(window.image_label)
        self.assertIsNotNone(window.result_text)
        self.assertIsNotNone(window.table)
        self.assertIsNotNone(window.cache_status_label)
        
        # 验证缓存状态标签有内容
        label_text = window.cache_status_label.text()
        self.assertIsNotNone(label_text)
        self.assertGreater(len(label_text), 0)
        
        # 清理
        window.close()
        
        print("✓ 应用UI元素正确初始化")


class TestOCRWorkflowWithCacheFailure(unittest.TestCase):
    """
    测试缓存失败时的OCR工作流
    
    验证需求: 5.1, 5.2, 5.3, 5.4, 5.5
    """
    
    @classmethod
    def setUpClass(cls):
        """设置测试类"""
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """清理测试环境"""
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass
    
    def test_cache_save_failure_does_not_affect_ocr(self):
        """
        测试缓存保存失败不影响OCR功能
        
        验证需求: 5.2
        """
        print("\n测试: 缓存保存失败不影响OCR功能")
        
        # 创建包装器
        wrapper = CacheManagerWrapper("/invalid/path.db")
        
        # 创建测试数据
        rects = [OCRRect(0, 0, 100, 100)]
        rects[0].text = "测试文本"
        
        # 保存应该成功（使用内存缓存）
        result = wrapper.save_result("test.png", rects, "完成")
        self.assertTrue(result)
        
        # 验证可以加载回来
        all_results = wrapper.load_all_results()
        self.assertIn("test.png", all_results)
        
        print("✓ 缓存保存失败不影响OCR功能")
    
    def test_cache_load_failure_does_not_crash(self):
        """
        测试缓存加载失败不导致崩溃
        
        验证需求: 5.3
        """
        print("\n测试: 缓存加载失败不导致崩溃")
        
        # 创建包装器
        wrapper = CacheManagerWrapper("/invalid/path.db")
        
        # 加载应该成功（返回空字典）
        try:
            results = wrapper.load_all_results()
            self.assertIsInstance(results, dict)
            print("✓ 缓存加载失败不导致崩溃")
        except Exception as e:
            self.fail(f"缓存加载失败导致异常: {e}")
    
    def test_session_save_failure_allows_continued_work(self):
        """
        测试会话保存失败允许继续工作
        
        验证需求: 5.4
        """
        print("\n测试: 会话保存失败允许继续工作")
        
        # 创建包装器
        wrapper = CacheManagerWrapper("/invalid/path.db")
        
        # 保存会话应该成功（使用内存缓存）
        files = ["file1.png", "file2.png"]
        result = wrapper.save_session(files, 0)
        self.assertTrue(result)
        
        # 验证可以加载回来
        session = wrapper.load_session()
        self.assertIsNotNone(session)
        self.assertEqual(session["files"], files)
        
        print("✓ 会话保存失败允许继续工作")
    
    def test_cache_clear_failure_does_not_block_operations(self):
        """
        测试缓存清除失败不阻止其他操作
        
        验证需求: 5.5
        """
        print("\n测试: 缓存清除失败不阻止其他操作")
        
        # 创建包装器
        wrapper = CacheManagerWrapper("/invalid/path.db")
        
        # 先保存一些数据
        rects = [OCRRect(0, 0, 100, 100)]
        wrapper.save_result("test.png", rects, "完成")
        
        # 清除缓存应该成功
        try:
            wrapper.clear_cache()
            
            # 验证数据被清除
            results = wrapper.load_all_results()
            self.assertEqual(len(results), 0)
            
            print("✓ 缓存清除失败不阻止其他操作")
        except Exception as e:
            self.fail(f"缓存清除失败导致异常: {e}")


class TestVariousEnvironments(unittest.TestCase):
    """
    测试在各种环境下的行为
    
    验证需求: 1.1, 2.1, 2.2, 3.1, 3.3, 4.1, 4.2
    """
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """清理测试环境"""
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass
    
    def test_no_library_environment(self):
        """
        测试无库文件环境
        
        验证需求: 2.1
        """
        print("\n测试: 无库文件环境")
        
        with patch('ocr_cache_manager.get_resource_path') as mock_get_resource:
            mock_get_resource.return_value = "nonexistent_lib.dll"
            
            with patch('ocr_cache_manager.os.path.exists') as mock_exists:
                mock_exists.return_value = False
                
                # 创建包装器应该成功（降级到内存缓存）
                wrapper = CacheManagerWrapper(os.path.join(self.temp_dir, "test.db"))
                
                # 验证包装器可用
                self.assertIsNotNone(wrapper)
                self.assertTrue(wrapper.is_cache_available())
                
                # 验证已降级到内存缓存
                status = wrapper.get_status()
                self.assertEqual(status.backend_type, "memory")
                
                # 验证有错误信息
                self.assertIsNotNone(status.init_error)
                self.assertEqual(status.init_error.error_type, "library_not_found")
        
        print("✓ 无库文件环境测试通过")
    
    def test_readonly_filesystem_environment(self):
        """
        测试只读文件系统环境
        
        验证需求: 3.3, 4.2
        """
        print("\n测试: 只读文件系统环境")
        
        # 创建一个只读目录（模拟）
        readonly_dir = os.path.join(self.temp_dir, "readonly")
        os.makedirs(readonly_dir, exist_ok=True)
        
        with patch('ocr_cache_manager.os.access') as mock_access:
            # 模拟没有写权限
            mock_access.return_value = False
            
            # 创建包装器应该成功（降级到内存缓存）
            wrapper = CacheManagerWrapper(os.path.join(readonly_dir, "test.db"))
            
            # 验证包装器可用
            self.assertIsNotNone(wrapper)
            self.assertTrue(wrapper.is_cache_available())
            
            # 验证已降级到内存缓存
            status = wrapper.get_status()
            self.assertEqual(status.backend_type, "memory")
        
        print("✓ 只读文件系统环境测试通过")
    
    def test_corrupted_database_environment(self):
        """
        测试损坏的数据库环境
        
        验证需求: 3.1
        """
        print("\n测试: 损坏的数据库环境")
        
        # 创建损坏的数据库文件
        corrupted_db = os.path.join(self.temp_dir, "corrupted.db")
        with open(corrupted_db, 'wb') as f:
            f.write(b'This is not a valid SQLite database!')
        
        # 创建包装器应该成功（自动恢复或降级）
        wrapper = CacheManagerWrapper(corrupted_db)
        
        # 验证包装器可用
        self.assertIsNotNone(wrapper)
        self.assertTrue(wrapper.is_cache_available())
        
        print("✓ 损坏的数据库环境测试通过")
    
    def test_null_pointer_environment(self):
        """
        测试C++引擎返回NULL指针的环境
        
        验证需求: 4.1
        """
        print("\n测试: C++引擎返回NULL指针的环境")
        
        with patch('ocr_cache_manager.get_resource_path') as mock_get_resource:
            mock_get_resource.return_value = "fake_lib.dll"
            
            with patch('ocr_cache_manager.os.path.exists') as mock_exists:
                mock_exists.return_value = True
                
                with patch('ocr_cache_manager.os.access') as mock_access:
                    mock_access.return_value = True
                    
                    with patch('ocr_cache_manager.ctypes.CDLL') as mock_cdll:
                        class MockCLib:
                            def __init__(self):
                                self.ocr_engine_init = Mock(return_value=0)  # NULL
                                self.ocr_engine_get_error = Mock(return_value=None)
                                self.ocr_engine_get_last_error = Mock(return_value=None)
                                self.ocr_engine_destroy = Mock()
                            
                            def __getattr__(self, name):
                                return Mock()
                        
                        mock_cdll.return_value = MockCLib()
                        
                        # 创建包装器应该成功（降级到内存缓存）
                        wrapper = CacheManagerWrapper(os.path.join(self.temp_dir, "test.db"))
                        
                        # 验证包装器可用
                        self.assertIsNotNone(wrapper)
                        self.assertTrue(wrapper.is_cache_available())
                        
                        # 验证已降级到内存缓存
                        status = wrapper.get_status()
                        self.assertEqual(status.backend_type, "memory")
        
        print("✓ C++引擎返回NULL指针的环境测试通过")
    
    def test_ctypes_exception_environment(self):
        """
        测试ctypes调用异常的环境
        
        验证需求: 4.2
        """
        print("\n测试: ctypes调用异常的环境")
        
        with patch('ocr_cache_manager.get_resource_path') as mock_get_resource:
            mock_get_resource.return_value = "fake_lib.dll"
            
            with patch('ocr_cache_manager.os.path.exists') as mock_exists:
                mock_exists.return_value = True
                
                with patch('ocr_cache_manager.ctypes.CDLL') as mock_cdll:
                    # 模拟ctypes加载失败
                    mock_cdll.side_effect = OSError("无法加载库")
                    
                    # 创建包装器应该成功（降级到内存缓存）
                    wrapper = CacheManagerWrapper(os.path.join(self.temp_dir, "test.db"))
                    
                    # 验证包装器可用
                    self.assertIsNotNone(wrapper)
                    self.assertTrue(wrapper.is_cache_available())
                    
                    # 验证已降级到内存缓存
                    status = wrapper.get_status()
                    self.assertEqual(status.backend_type, "memory")
        
        print("✓ ctypes调用异常的环境测试通过")


class TestCacheOperationsIntegration(unittest.TestCase):
    """
    测试缓存操作的集成
    
    验证需求: 1.3, 5.1, 5.2, 5.3, 5.4, 5.5
    """
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """清理测试环境"""
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass
    
    def test_save_and_load_results(self):
        """
        测试保存和加载结果的完整流程
        
        验证需求: 5.2, 5.3
        """
        print("\n测试: 保存和加载结果的完整流程")
        
        # 创建包装器
        wrapper = CacheManagerWrapper(os.path.join(self.temp_dir, "test.db"))
        
        # 创建测试数据
        rects1 = [OCRRect(0, 0, 100, 100), OCRRect(100, 100, 200, 200)]
        rects1[0].text = "文本1"
        rects1[1].text = "文本2"
        
        rects2 = [OCRRect(50, 50, 150, 150)]
        rects2[0].text = "文本3"
        
        # 保存结果
        self.assertTrue(wrapper.save_result("file1.png", rects1, "完成"))
        self.assertTrue(wrapper.save_result("file2.png", rects2, "完成"))
        
        # 加载所有结果
        all_results = wrapper.load_all_results()
        
        # 验证结果
        self.assertIn("file1.png", all_results)
        self.assertIn("file2.png", all_results)
        self.assertEqual(len(all_results["file1.png"]["rects"]), 2)
        self.assertEqual(len(all_results["file2.png"]["rects"]), 1)
        self.assertEqual(all_results["file1.png"]["rects"][0].text, "文本1")
        self.assertEqual(all_results["file2.png"]["rects"][0].text, "文本3")
        
        print("✓ 保存和加载结果的完整流程测试通过")
    
    def test_save_and_load_session(self):
        """
        测试保存和加载会话的完整流程
        
        验证需求: 5.4
        """
        print("\n测试: 保存和加载会话的完整流程")
        
        # 创建包装器
        wrapper = CacheManagerWrapper(os.path.join(self.temp_dir, "test.db"))
        
        # 保存会话
        files = ["file1.png", "file2.png", "file3.png"]
        cur_index = 1
        self.assertTrue(wrapper.save_session(files, cur_index))
        
        # 加载会话
        session = wrapper.load_session()
        
        # 验证会话
        self.assertIsNotNone(session)
        self.assertEqual(session["files"], files)
        self.assertEqual(session["cur_index"], cur_index)
        
        print("✓ 保存和加载会话的完整流程测试通过")
    
    def test_clear_cache_operation(self):
        """
        测试清除缓存操作
        
        验证需求: 5.5
        """
        print("\n测试: 清除缓存操作")
        
        # 创建包装器
        wrapper = CacheManagerWrapper(os.path.join(self.temp_dir, "test.db"))
        
        # 保存一些数据
        rects = [OCRRect(0, 0, 100, 100)]
        rects[0].text = "测试"
        wrapper.save_result("test.png", rects, "完成")
        wrapper.save_session(["test.png"], 0)
        
        # 验证数据存在
        self.assertTrue(wrapper.has_cache())
        
        # 清除缓存
        wrapper.clear_cache()
        
        # 验证数据被清除
        results = wrapper.load_all_results()
        self.assertEqual(len(results), 0)
        session = wrapper.load_session()
        # 会话可能是None或空字典
        if session is not None:
            self.assertEqual(len(session.get("files", [])), 0)
        
        print("✓ 清除缓存操作测试通过")


class TestHealthCheckAndDiagnostics(unittest.TestCase):
    """
    测试健康检查和诊断功能
    
    验证需求: 1.4, 2.4, 2.5
    """
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """清理测试环境"""
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass
    
    def test_health_check_with_cpp_engine(self):
        """
        测试C++引擎可用时的健康检查
        
        验证需求: 1.4
        """
        print("\n测试: C++引擎可用时的健康检查")
        
        # 创建包装器
        wrapper = CacheManagerWrapper(os.path.join(self.temp_dir, "test.db"))
        
        # 执行健康检查
        health = wrapper.health_check()
        
        # 验证健康检查结果
        self.assertIsInstance(health, dict)
        self.assertIn("cache_available", health)
        self.assertIn("backend_type", health)
        self.assertIn("message", health)
        self.assertIn("timestamp", health)
        
        # 验证缓存可用
        self.assertTrue(health["cache_available"])
        
        print("✓ C++引擎可用时的健康检查测试通过")
    
    def test_health_check_with_memory_fallback(self):
        """
        测试降级到内存缓存时的健康检查
        
        验证需求: 1.4, 2.5
        """
        print("\n测试: 降级到内存缓存时的健康检查")
        
        # 使用mock强制降级到内存缓存
        with patch('cache_manager_wrapper.OCRCacheManager') as mock_manager:
            # 模拟初始化失败
            mock_manager.side_effect = CacheInitError(
                error_type="test_error",
                error_message="测试错误",
                error_details={},
                suggestions=["这是测试"]
            )
            
            # 创建包装器（会降级到内存缓存）
            wrapper = CacheManagerWrapper("/test/path.db")
            
            # 执行健康检查
            health = wrapper.health_check()
            
            # 验证健康检查结果
            self.assertIsInstance(health, dict)
            self.assertTrue(health["cache_available"])
            self.assertEqual(health["backend_type"], "memory")
            
            # 验证有错误信息
            self.assertIn("init_error", health)
            self.assertIn("type", health["init_error"])
            self.assertIn("message", health["init_error"])
            self.assertIn("suggestions", health["init_error"])
        
        print("✓ 降级到内存缓存时的健康检查测试通过")
    
    def test_status_message_completeness(self):
        """
        测试状态消息的完整性
        
        验证需求: 2.4, 2.5
        """
        print("\n测试: 状态消息的完整性")
        
        # 创建包装器（使用无效路径触发错误）
        wrapper = CacheManagerWrapper("/invalid/path.db")
        
        # 获取状态
        status = wrapper.get_status()
        
        # 验证状态对象
        self.assertIsNotNone(status)
        self.assertIsNotNone(status.message)
        self.assertGreater(len(status.message), 0)
        
        # 获取状态消息
        message = wrapper.get_status_message()
        self.assertIsNotNone(message)
        self.assertGreater(len(message), 0)
        
        print("✓ 状态消息的完整性测试通过")


def run_all_tests():
    """运行所有集成测试"""
    print("=" * 80)
    print("缓存引擎鲁棒性集成测试")
    print("=" * 80)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestApplicationStartupFlow))
    suite.addTests(loader.loadTestsFromTestCase(TestOCRWorkflowWithCacheFailure))
    suite.addTests(loader.loadTestsFromTestCase(TestVariousEnvironments))
    suite.addTests(loader.loadTestsFromTestCase(TestCacheOperationsIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestHealthCheckAndDiagnostics))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 打印总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
