#!/usr/bin/env python3
"""
缓存引擎单元测试
测试OCRCacheManager和CacheManagerWrapper的各种场景

测试需求: 所有需求 (1.1-5.5)
"""

import os
import sys
import tempfile
import shutil
import sqlite3
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from ocr_cache_manager import OCRCacheManager, CacheInitError
    from cache_manager_wrapper import CacheManagerWrapper, CacheStatus
    from config import OCRRect
except ImportError as e:
    print(f"导入失败: {e}")
    print("请确保在项目根目录运行测试")
    sys.exit(1)


class TestOCRCacheManagerInitialization(unittest.TestCase):
    """测试OCRCacheManager的各种初始化场景"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """清理测试环境"""
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass
    
    def test_init_with_valid_path(self):
        """测试使用有效路径初始化"""
        test_db_path = os.path.join(self.temp_dir, "test.db")
        
        with patch('ocr_cache_manager.get_resource_path') as mock_get_resource:
            mock_get_resource.return_value = "fake_lib.dll"
            
            with patch('ocr_cache_manager.os.path.exists') as mock_exists:
                mock_exists.return_value = True
                
                with patch('ocr_cache_manager.os.access') as mock_access:
                    mock_access.return_value = True
                    
                    with patch('ocr_cache_manager.ctypes.CDLL') as mock_cdll:
                        class MockCLib:
                            def __init__(self):
                                self.ocr_engine_init = Mock(return_value=12345)
                                self.ocr_engine_has_cache = Mock(return_value=1)
                                self.ocr_engine_destroy = Mock()
                            
                            def __getattr__(self, name):
                                return Mock()
                        
                        mock_cdll.return_value = MockCLib()
                        
                        # 初始化应该成功
                        manager = OCRCacheManager(test_db_path)
                        
                        self.assertIsNotNone(manager)
                        self.assertIsNotNone(manager.engine)
                        self.assertEqual(manager.db_path, test_db_path)
                        
                        del manager
    
    def test_init_with_none_path(self):
        """测试使用None路径初始化（应使用默认路径）"""
        with patch('ocr_cache_manager.get_resource_path') as mock_get_resource:
            mock_get_resource.return_value = "fake_lib.dll"
            
            with patch('ocr_cache_manager.os.path.exists') as mock_exists:
                mock_exists.return_value = True
                
                with patch('ocr_cache_manager.os.access') as mock_access:
                    mock_access.return_value = True
                    
                    with patch('ocr_cache_manager.ctypes.CDLL') as mock_cdll:
                        class MockCLib:
                            def __init__(self):
                                self.ocr_engine_init = Mock(return_value=12345)
                                self.ocr_engine_has_cache = Mock(return_value=1)
                                self.ocr_engine_destroy = Mock()
                            
                            def __getattr__(self, name):
                                return Mock()
                        
                        mock_cdll.return_value = MockCLib()
                        
                        # 初始化应该成功，使用默认路径
                        manager = OCRCacheManager(None)
                        
                        self.assertIsNotNone(manager)
                        self.assertIsNotNone(manager.db_path)
                        
                        del manager
    
    def test_init_with_library_not_found(self):
        """测试库文件不存在的情况"""
        test_db_path = os.path.join(self.temp_dir, "test.db")
        
        with patch('ocr_cache_manager.get_resource_path') as mock_get_resource:
            mock_get_resource.return_value = "nonexistent_lib.dll"
            
            with patch('ocr_cache_manager.os.path.exists') as mock_exists:
                mock_exists.return_value = False
                
                # 应该抛出CacheInitError
                with self.assertRaises(CacheInitError) as context:
                    manager = OCRCacheManager(test_db_path)
                
                error = context.exception
                self.assertEqual(error.error_type, "library_not_found")
                # 检查错误消息包含相关关键词
                self.assertTrue(
                    "库文件" in error.error_message or "找不到" in error.error_message,
                    f"错误消息应包含库文件相关信息: {error.error_message}"
                )
                self.assertGreater(len(error.suggestions), 0)
    
    def test_init_with_null_pointer(self):
        """测试C++引擎返回NULL指针"""
        test_db_path = os.path.join(self.temp_dir, "test.db")
        
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
                        
                        # 应该抛出CacheInitError
                        with self.assertRaises(CacheInitError) as context:
                            manager = OCRCacheManager(test_db_path)
                        
                        error = context.exception
                        self.assertEqual(error.error_type, "null_pointer")
                        self.assertIn("NULL", error.error_message)
    
    def test_init_with_permission_denied(self):
        """测试权限不足的情况"""
        test_db_path = os.path.join(self.temp_dir, "test.db")
        
        with patch('ocr_cache_manager.get_resource_path') as mock_get_resource:
            mock_get_resource.return_value = "fake_lib.dll"
            
            with patch('ocr_cache_manager.os.path.exists') as mock_exists:
                mock_exists.return_value = True
                
                with patch('ocr_cache_manager.os.access') as mock_access:
                    # 模拟没有写权限
                    mock_access.return_value = False
                    
                    # 应该抛出CacheInitError
                    with self.assertRaises(CacheInitError) as context:
                        manager = OCRCacheManager(test_db_path)
                    
                    error = context.exception
                    self.assertEqual(error.error_type, "permission_denied")
                    # 检查错误消息包含权限相关关键词
                    self.assertTrue(
                        "权限" in error.error_message or "不可写" in error.error_message,
                        f"错误消息应包含权限相关信息: {error.error_message}"
                    )


class TestCacheManagerWrapperDegradation(unittest.TestCase):
    """测试CacheManagerWrapper的降级策略"""
    
    def test_wrapper_init_with_invalid_path(self):
        """测试使用无效路径初始化包装器"""
        # 包装器应该成功创建（即使路径无效）
        wrapper = CacheManagerWrapper("/nonexistent/path/to/cache.db")
        
        # 包装器应该成功创建
        self.assertIsNotNone(wrapper)
        
        # 获取状态
        status = wrapper.get_status()
        self.assertIsNotNone(status)
        
        # 如果C++引擎初始化失败，应该降级到内存缓存
        # 如果成功（因为C++引擎会创建目录），也是正常的
        self.assertIn(status.backend_type, ["cpp_engine", "memory"])
        
        # 应该有状态消息
        message = wrapper.get_status_message()
        self.assertIsInstance(message, str)
        self.assertGreater(len(message), 0)
    
    def test_wrapper_save_result_with_fallback(self):
        """测试降级模式下保存结果"""
        wrapper = CacheManagerWrapper("/invalid/path.db")
        
        # 创建测试数据
        rects = [
            OCRRect(0, 0, 100, 100),
            OCRRect(100, 100, 200, 200)
        ]
        rects[0].text = "测试文本1"
        rects[1].text = "测试文本2"
        
        # 保存应该成功（使用内存缓存）
        result = wrapper.save_result("test.png", rects, "完成")
        self.assertTrue(result)
        
        # 应该能够加载回来
        all_results = wrapper.load_all_results()
        self.assertIn("test.png", all_results)
        
        loaded_rects = all_results["test.png"]["rects"]
        self.assertEqual(len(loaded_rects), 2)
        self.assertEqual(loaded_rects[0].text, "测试文本1")
        self.assertEqual(loaded_rects[1].text, "测试文本2")
    
    def test_wrapper_save_session_with_fallback(self):
        """测试降级模式下保存会话"""
        wrapper = CacheManagerWrapper("/invalid/path.db")
        
        files = ["file1.png", "file2.png", "file3.png"]
        cur_index = 1
        
        # 保存会话应该成功
        result = wrapper.save_session(files, cur_index)
        self.assertTrue(result)
        
        # 应该能够加载回来
        session = wrapper.load_session()
        self.assertIsNotNone(session)
        self.assertEqual(session["files"], files)
        self.assertEqual(session["cur_index"], cur_index)
    
    def test_wrapper_clear_cache_with_fallback(self):
        """测试降级模式下清除缓存"""
        wrapper = CacheManagerWrapper("/invalid/path.db")
        
        # 先保存一些数据
        rects = [OCRRect(0, 0, 100, 100)]
        wrapper.save_result("test.png", rects, "完成")
        
        # 验证数据存在
        results = wrapper.load_all_results()
        self.assertIn("test.png", results)
        
        # 清除缓存
        wrapper.clear_cache()
        
        # 验证数据被清除
        results = wrapper.load_all_results()
        self.assertEqual(len(results), 0)
    
    def test_wrapper_health_check(self):
        """测试健康检查功能"""
        wrapper = CacheManagerWrapper("/invalid/path.db")
        
        health = wrapper.health_check()
        
        # 验证健康检查返回字典
        self.assertIsInstance(health, dict)
        
        # 验证包含必要的字段
        self.assertIn("cache_available", health)
        self.assertIn("backend_type", health)
        self.assertIn("message", health)
        self.assertIn("timestamp", health)
        
        # 验证值的类型
        self.assertIsInstance(health["cache_available"], bool)
        self.assertIn(health["backend_type"], ["cpp_engine", "memory"])


class TestErrorHandlingAndResourceCleanup(unittest.TestCase):
    """测试错误处理和资源清理"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """清理测试环境"""
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass
    
    def test_error_info_completeness(self):
        """测试错误信息的完整性"""
        test_db_path = os.path.join(self.temp_dir, "test.db")
        
        with patch('ocr_cache_manager.get_resource_path') as mock_get_resource:
            mock_get_resource.return_value = "fake_lib.dll"
            
            with patch('ocr_cache_manager.os.path.exists') as mock_exists:
                mock_exists.return_value = False
                
                # 捕获错误
                try:
                    manager = OCRCacheManager(test_db_path)
                    self.fail("应该抛出CacheInitError")
                except CacheInitError as e:
                    # 验证错误信息完整性
                    self.assertIsNotNone(e.error_type)
                    self.assertIsNotNone(e.error_message)
                    self.assertIsNotNone(e.error_details)
                    self.assertIsNotNone(e.suggestions)
                    
                    # 验证错误类型不为空
                    self.assertGreater(len(e.error_type), 0)
                    
                    # 验证错误消息不为空
                    self.assertGreater(len(e.error_message), 0)
                    
                    # 验证有建议
                    self.assertGreater(len(e.suggestions), 0)
    
    def test_resource_cleanup_on_failure(self):
        """测试初始化失败时的资源清理"""
        test_db_path = os.path.join(self.temp_dir, "test.db")
        
        with patch('ocr_cache_manager.get_resource_path') as mock_get_resource:
            mock_get_resource.return_value = "fake_lib.dll"
            
            with patch('ocr_cache_manager.os.path.exists') as mock_exists:
                mock_exists.return_value = True
                
                with patch('ocr_cache_manager.os.access') as mock_access:
                    mock_access.return_value = True
                    
                    with patch('ocr_cache_manager.ctypes.CDLL') as mock_cdll:
                        destroy_mock = Mock()
                        
                        class MockCLib:
                            def __init__(self):
                                self.ocr_engine_init = Mock(return_value=12345)
                                self.ocr_engine_has_cache = Mock(side_effect=Exception("测试异常"))
                                self.ocr_engine_destroy = destroy_mock
                            
                            def __getattr__(self, name):
                                return Mock()
                        
                        mock_cdll.return_value = MockCLib()
                        
                        # 初始化应该失败
                        try:
                            manager = OCRCacheManager(test_db_path)
                            self.fail("应该抛出异常")
                        except Exception:
                            pass
                        
                        # 验证destroy被调用（资源被清理）
                        self.assertTrue(destroy_mock.called)
    
    def test_wrapper_exception_isolation(self):
        """测试包装器的异常隔离"""
        wrapper = CacheManagerWrapper("/invalid/path.db")
        
        # 即使后端失败，所有操作都应该正常返回
        try:
            # 这些操作都不应该抛出异常
            wrapper.save_result("test.png", [], "完成")
            wrapper.load_all_results()
            wrapper.save_session([], 0)
            wrapper.load_session()
            wrapper.has_cache()
            wrapper.clear_cache()
            wrapper.get_status()
            wrapper.get_status_message()
            wrapper.health_check()
            
            # 如果到这里，说明所有操作都没有抛出异常
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"包装器操作抛出异常: {e}")


class TestDatabaseRecovery(unittest.TestCase):
    """测试数据库自动恢复"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """清理测试环境"""
        try:
            shutil.rmtree(self.temp_dir)
        except Exception:
            pass
    
    def test_corrupted_database_detection(self):
        """测试损坏数据库的检测"""
        test_db_path = os.path.join(self.temp_dir, "corrupted.db")
        
        # 创建损坏的数据库文件
        with open(test_db_path, 'wb') as f:
            f.write(b'This is not a valid SQLite database!')
        
        with patch('ocr_cache_manager.get_resource_path') as mock_get_resource:
            mock_get_resource.return_value = "fake_lib.dll"
            
            with patch('ocr_cache_manager.os.path.exists') as mock_exists:
                mock_exists.return_value = True
                
                with patch('ocr_cache_manager.os.access') as mock_access:
                    mock_access.return_value = True
                    
                    with patch('ocr_cache_manager.ctypes.CDLL') as mock_cdll:
                        class MockCLib:
                            def __init__(self):
                                self.ocr_engine_init = Mock(return_value=12345)
                                self.ocr_engine_has_cache = Mock(return_value=0)
                                self.ocr_engine_destroy = Mock()
                            
                            def __getattr__(self, name):
                                return Mock()
                        
                        mock_cdll.return_value = MockCLib()
                        
                        # 创建管理器实例
                        manager = OCRCacheManager.__new__(OCRCacheManager)
                        manager.db_path = test_db_path
                        manager.engine = None
                        manager._lib = None
                        manager._last_init_error = None
                        
                        # 检查数据库健康状态
                        is_healthy = manager._check_database_health()
                        
                        # 损坏的数据库应该被检测到
                        self.assertFalse(is_healthy)
    
    def test_database_backup_creation(self):
        """测试数据库备份创建"""
        test_db_path = os.path.join(self.temp_dir, "test.db")
        
        # 创建一个有效的数据库
        conn = sqlite3.connect(test_db_path)
        conn.execute("CREATE TABLE test (id INTEGER, data TEXT)")
        conn.execute("INSERT INTO test VALUES (1, 'test data')")
        conn.commit()
        conn.close()
        
        with patch('ocr_cache_manager.get_resource_path') as mock_get_resource:
            mock_get_resource.return_value = "fake_lib.dll"
            
            with patch('ocr_cache_manager.os.path.exists') as mock_exists:
                mock_exists.return_value = True
                
                with patch('ocr_cache_manager.os.access') as mock_access:
                    mock_access.return_value = True
                    
                    with patch('ocr_cache_manager.ctypes.CDLL') as mock_cdll:
                        class MockCLib:
                            def __init__(self):
                                self.ocr_engine_init = Mock(return_value=12345)
                                self.ocr_engine_has_cache = Mock(return_value=0)
                                self.ocr_engine_destroy = Mock()
                            
                            def __getattr__(self, name):
                                return Mock()
                        
                        mock_cdll.return_value = MockCLib()
                        
                        # 创建管理器实例
                        manager = OCRCacheManager.__new__(OCRCacheManager)
                        manager.db_path = test_db_path
                        manager.engine = None
                        manager._lib = None
                        manager._last_init_error = None
                        
                        # 创建备份
                        backup_path = manager._backup_database()
                        
                        # 验证备份文件存在
                        self.assertIsNotNone(backup_path)
                        self.assertTrue(os.path.exists(backup_path))
                        
                        # 验证备份内容
                        backup_conn = sqlite3.connect(backup_path)
                        cursor = backup_conn.execute("SELECT * FROM test")
                        rows = cursor.fetchall()
                        backup_conn.close()
                        
                        self.assertEqual(len(rows), 1)
                        self.assertEqual(rows[0], (1, 'test data'))


def run_all_tests():
    """运行所有单元测试"""
    print("=" * 80)
    print("缓存引擎单元测试")
    print("=" * 80)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestOCRCacheManagerInitialization))
    suite.addTests(loader.loadTestsFromTestCase(TestCacheManagerWrapperDegradation))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandlingAndResourceCleanup))
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseRecovery))
    
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
