"""
数据库自动恢复单元测试
测试需求 3.1, 3.2, 3.3, 3.4, 3.5
"""

import os
import sys
import tempfile
import shutil
import sqlite3
from unittest.mock import Mock, patch

# 导入被测试的模块
try:
    from ocr_cache_manager import OCRCacheManager, CacheInitError
except ImportError as e:
    print(f"导入失败: {e}")
    print("请确保在项目根目录运行测试")
    sys.exit(1)


def test_database_health_check_healthy():
    """测试健康数据库的检查"""
    temp_dir = tempfile.mkdtemp()
    
    try:
        test_db_path = os.path.join(temp_dir, "test.db")
        
        # 创建一个健康的数据库
        conn = sqlite3.connect(test_db_path)
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, data TEXT)")
        conn.execute("INSERT INTO test VALUES (1, 'test data')")
        conn.commit()
        conn.close()
        
        # Mock库加载和引擎初始化
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
                        manager = OCRCacheManager(test_db_path)
                        
                        # 验证健康检查通过
                        is_healthy = manager._check_database_health()
                        assert is_healthy, "健康的数据库应该通过检查"
                        
                        del manager
    
    finally:
        shutil.rmtree(temp_dir)


def test_database_health_check_corrupted():
    """测试损坏数据库的检查"""
    temp_dir = tempfile.mkdtemp()
    
    try:
        test_db_path = os.path.join(temp_dir, "corrupted.db")
        
        # 创建一个损坏的数据库文件（写入随机数据）
        with open(test_db_path, 'wb') as f:
            f.write(b'This is not a valid SQLite database file!')
        
        # Mock库加载
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
                        
                        # 验证健康检查失败
                        is_healthy = manager._check_database_health()
                        assert not is_healthy, "损坏的数据库应该检查失败"
    
    finally:
        shutil.rmtree(temp_dir)


def test_database_backup():
    """测试数据库备份功能"""
    temp_dir = tempfile.mkdtemp()
    
    try:
        test_db_path = os.path.join(temp_dir, "test.db")
        
        # 创建一个数据库
        conn = sqlite3.connect(test_db_path)
        conn.execute("CREATE TABLE test (id INTEGER PRIMARY KEY, data TEXT)")
        conn.execute("INSERT INTO test VALUES (1, 'test data')")
        conn.commit()
        conn.close()
        
        # Mock库加载
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
                        
                        # 执行备份
                        backup_path = manager._backup_database()
                        
                        # 验证备份文件存在
                        assert backup_path is not None, "备份应该成功"
                        assert os.path.exists(backup_path), "备份文件应该存在"
                        assert backup_path.startswith(test_db_path), "备份文件应该在同一目录"
                        
                        # 验证备份文件内容
                        backup_conn = sqlite3.connect(backup_path)
                        cursor = backup_conn.execute("SELECT * FROM test")
                        rows = cursor.fetchall()
                        backup_conn.close()
                        
                        assert len(rows) == 1, "备份应该包含原始数据"
                        assert rows[0] == (1, 'test data'), "备份数据应该正确"
    
    finally:
        shutil.rmtree(temp_dir)


def test_database_rebuild():
    """测试数据库重建功能"""
    temp_dir = tempfile.mkdtemp()
    
    try:
        test_db_path = os.path.join(temp_dir, "corrupted.db")
        
        # 创建一个损坏的数据库
        with open(test_db_path, 'wb') as f:
            f.write(b'Corrupted database content')
        
        # 验证损坏的数据库存在
        assert os.path.exists(test_db_path), "损坏的数据库应该存在"
        
        # Mock库加载
        with patch('ocr_cache_manager.get_resource_path') as mock_get_resource:
            mock_get_resource.return_value = "fake_lib.dll"
            
            # Don't mock os.path.exists - we need real file system operations
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
                    
                    # 执行重建
                    success = manager._rebuild_database()
                    
                    # 验证重建成功
                    assert success, "重建应该成功"
                    
                    # 验证旧数据库被删除
                    assert not os.path.exists(test_db_path), "损坏的数据库应该被删除"
                    
                    # 验证备份文件存在
                    backup_files = [f for f in os.listdir(temp_dir) if f.startswith("corrupted.db.backup_")]
                    assert len(backup_files) > 0, "应该创建备份文件"
    
    finally:
        shutil.rmtree(temp_dir)


def test_auto_recovery_with_corrupted_database():
    """测试自动恢复损坏的数据库"""
    temp_dir = tempfile.mkdtemp()
    
    try:
        test_db_path = os.path.join(temp_dir, "test.db")
        
        # 创建一个损坏的数据库
        with open(test_db_path, 'wb') as f:
            f.write(b'Corrupted database')
        
        # Mock库加载和引擎初始化
        with patch('ocr_cache_manager.get_resource_path') as mock_get_resource:
            mock_get_resource.return_value = "fake_lib.dll"
            
            with patch('ocr_cache_manager.os.path.exists') as mock_exists:
                # 第一次调用检查库文件，返回True
                # 后续调用检查数据库文件
                mock_exists.side_effect = lambda path: True
                
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
                        
                        # 初始化应该触发自动恢复
                        manager = OCRCacheManager(test_db_path)
                        
                        # 验证管理器成功初始化
                        assert manager.engine is not None, "引擎应该已初始化"
                        assert manager.db_path == test_db_path, "数据库路径应该正确"
                        
                        # 验证备份文件被创建
                        backup_files = [f for f in os.listdir(temp_dir) if f.startswith("test.db.backup_")]
                        assert len(backup_files) > 0, "应该创建备份文件"
                        
                        del manager
    
    finally:
        shutil.rmtree(temp_dir)


def test_disk_space_check():
    """测试磁盘空间检查"""
    temp_dir = tempfile.mkdtemp()
    
    try:
        test_db_path = os.path.join(temp_dir, "test.db")
        
        # Mock库加载
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
                        
                        # 检查磁盘空间（应该有足够空间）
                        has_space = manager._check_disk_space()
                        assert has_space, "临时目录应该有足够的磁盘空间"
    
    finally:
        shutil.rmtree(temp_dir)


def test_insufficient_disk_space():
    """测试磁盘空间不足的情况"""
    temp_dir = tempfile.mkdtemp()
    
    try:
        test_db_path = os.path.join(temp_dir, "test.db")
        
        # Mock库加载
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
                        
                        # Mock磁盘空间检查返回False
                        with patch.object(manager, '_check_disk_space', return_value=False):
                            # 尝试自动恢复应该抛出错误
                            try:
                                manager._auto_recover_database()
                                assert False, "应该抛出CacheInitError"
                            except CacheInitError as e:
                                assert e.error_type == "insufficient_disk_space", \
                                    f"错误类型应该是'insufficient_disk_space'，实际是'{e.error_type}'"
                                assert "磁盘空间不足" in e.error_message, "错误信息应该提到磁盘空间"
    
    finally:
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    # 运行所有测试
    print("\n" + "=" * 80)
    print("运行数据库自动恢复单元测试")
    print("=" * 80)
    
    unit_tests = [
        ("健康数据库检查", test_database_health_check_healthy),
        ("损坏数据库检查", test_database_health_check_corrupted),
        ("数据库备份", test_database_backup),
        ("数据库重建", test_database_rebuild),
        ("自动恢复损坏数据库", test_auto_recovery_with_corrupted_database),
        ("磁盘空间检查", test_disk_space_check),
        ("磁盘空间不足", test_insufficient_disk_space),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in unit_tests:
        print(f"\n运行测试: {test_name}")
        print("-" * 60)
        try:
            test_func()
            print(f"[PASS] {test_name}")
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test_name}")
            print(f"错误: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 80)
    print(f"单元测试总结: 通过 {passed}/{len(unit_tests)}, 失败 {failed}/{len(unit_tests)}")
    print("=" * 80)
    
    if failed == 0:
        print("\n✓ 所有测试通过!")
        sys.exit(0)
    else:
        print(f"\n✗ {failed} 个测试失败")
        sys.exit(1)
