"""
缓存管理器鲁棒性属性测试
使用hypothesis进行属性测试，验证错误处理和安全性
"""

import os
import sys
import tempfile
import shutil
import ctypes
from unittest.mock import Mock, patch, MagicMock
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from hypothesis import Phase

# 导入被测试的模块
try:
    from ocr_cache_manager import OCRCacheManager, CacheInitError
    from config import OCRRect
except ImportError as e:
    print(f"导入失败: {e}")
    print("请确保在项目根目录运行测试")
    sys.exit(1)


# ============================================================
# 属性测试 1.1: NULL指针安全检测
# **Feature: cache-engine-robustness, Property 4: NULL指针安全检测**
# **Validates: Requirements 4.1**
# ============================================================

@settings(
    max_examples=20,  # 减少测试用例数量
    deadline=5000,    # 5秒超时
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    phases=[Phase.generate, Phase.target]  # 跳过shrink阶段以加快速度
)
@given(
    db_path=st.one_of(
        st.none(),
        st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126), min_size=1, max_size=20),
        st.just("")
    )
)
def test_property_null_pointer_safety(db_path):
    """
    属性4: NULL指针安全检测
    
    对于任何C++引擎返回NULL指针的情况，Python层应该在使用前检测并抛出明确的异常，
    而不是导致访问违规错误。
    
    测试策略：
    1. Mock C++引擎使其返回NULL (0)
    2. 尝试初始化OCRCacheManager
    3. 验证抛出CacheInitError而不是访问违规
    4. 验证错误信息包含"null_pointer"类型
    """
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 如果db_path为None，使用临时目录
        if db_path is None:
            test_db_path = None
        elif db_path == "":
            # 空字符串应该被处理
            test_db_path = ""
        else:
            # 使用临时目录中的路径
            safe_path = db_path.replace("/", "_").replace("\\", "_").replace(":", "_")[:50]
            test_db_path = os.path.join(temp_dir, safe_path + ".db")
        
        # Mock get_resource_path and file system checks
        with patch('ocr_cache_manager.get_resource_path') as mock_get_resource:
            mock_get_resource.return_value = "fake_lib.dll"
            
            with patch('ocr_cache_manager.os.path.exists') as mock_exists:
                mock_exists.return_value = True
                
                with patch('ocr_cache_manager.os.access') as mock_access:
                    mock_access.return_value = True
                    
                    # Mock C++库，使ocr_engine_init返回NULL
                    with patch('ocr_cache_manager.ctypes.CDLL') as mock_cdll:
                        # 创建特殊的Mock类
                        class MockCLib:
                            def __init__(self):
                                self.ocr_engine_init = Mock(return_value=0)  # NULL指针
                                self.ocr_engine_has_cache = Mock(return_value=0)
                                self.ocr_engine_get_error = Mock(return_value=None)
                                self.ocr_engine_get_last_error = Mock(return_value=None)
                                self.ocr_engine_destroy = Mock()
                                self.ocr_engine_save_result = Mock(return_value=0)
                                self.ocr_engine_load_all = Mock(return_value=None)
                                self.ocr_engine_save_session = Mock(return_value=0)
                                self.ocr_engine_load_session = Mock(return_value=None)
                                self.ocr_engine_clear = Mock()
                                self.ocr_engine_free_string = Mock()
                            
                            def __getattr__(self, name):
                                # 返回一个Mock而不是None，这样可以设置argtypes等属性
                                return Mock()
                        
                        mock_cdll.return_value = MockCLib()
                        
                        # 尝试初始化，应该抛出CacheInitError而不是访问违规
                        try:
                            manager = OCRCacheManager(test_db_path)
                            # 如果没有抛出异常，这是一个bug
                            assert False, "应该抛出CacheInitError，但没有抛出任何异常"
                        except CacheInitError as e:
                            # 验证错误类型
                            assert e.error_type == "null_pointer", f"错误类型应该是'null_pointer'，实际是'{e.error_type}'"
                            # 验证错误信息不为空
                            assert e.error_message, "错误信息不应为空"
                            # 验证有建议
                            assert len(e.suggestions) > 0, "应该提供解决建议"
                        except Exception as e:
                            # 其他异常类型表示测试失败
                            assert False, f"应该抛出CacheInitError，但抛出了{type(e).__name__}: {e}"
    
    finally:
        # 清理临时目录
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


# ============================================================
# 属性测试 1.2: ctypes调用安全性
# **Feature: cache-engine-robustness, Property 5: ctypes调用安全性**
# **Validates: Requirements 4.2**
# ============================================================

@settings(
    max_examples=20,
    deadline=5000,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    phases=[Phase.generate, Phase.target]
)
@given(
    error_type=st.sampled_from([
        OSError("Library load failed"),
        OSError("Function not found"),
        AttributeError("Function does not exist"),
        RuntimeError("Unexpected error")
    ])
)
def test_property_ctypes_call_safety(error_type):
    """
    属性5: ctypes调用安全性
    
    对于任何ctypes函数调用，如果发生OSError或其他异常，系统应该捕获并提供
    包含函数名、参数和上下文的详细错误信息。
    
    测试策略：
    1. Mock ctypes.CDLL使其抛出各种异常
    2. 尝试初始化OCRCacheManager
    3. 验证抛出CacheInitError
    4. 验证错误信息包含详细的上下文
    """
    temp_dir = tempfile.mkdtemp()
    
    try:
        test_db_path = os.path.join(temp_dir, "test.db")
        
        # Mock get_resource_path and file system checks
        with patch('ocr_cache_manager.get_resource_path') as mock_get_resource:
            mock_get_resource.return_value = "fake_lib.dll"
            
            with patch('ocr_cache_manager.os.path.exists') as mock_exists:
                mock_exists.return_value = True
                
                with patch('ocr_cache_manager.os.access') as mock_access:
                    mock_access.return_value = True
                    
                    # Mock C++库加载失败
                    with patch('ocr_cache_manager.ctypes.CDLL') as mock_cdll:
                        # 使CDLL抛出异常
                        mock_cdll.side_effect = error_type
                        
                        # 尝试初始化
                        try:
                            manager = OCRCacheManager(test_db_path)
                            assert False, "应该抛出CacheInitError"
                        except CacheInitError as e:
                            # 验证错误类型相关
                            assert e.error_type in ["library_load_failed", "library_load_unexpected", 
                                                   "function_not_found", "signature_definition_failed"], \
                                f"错误类型应该与库加载相关，实际是'{e.error_type}'"
                            # 验证错误详情包含有用信息
                            assert e.error_details, "错误详情不应为空"
                            # 验证有建议
                            assert len(e.suggestions) > 0, "应该提供解决建议"
                        except Exception as e:
                            assert False, f"应该抛出CacheInitError，但抛出了{type(e).__name__}: {e}"
    
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


# ============================================================
# 属性测试 1.3: 编码处理正确性
# **Feature: cache-engine-robustness, Property 6: 编码处理正确性**
# **Validates: Requirements 4.3**
# ============================================================

@settings(
    max_examples=20,
    deadline=5000,
    suppress_health_check=[HealthCheck.function_scoped_fixture],
    phases=[Phase.generate, Phase.target]
)
@given(
    path_component=st.text(
        alphabet=st.characters(
            min_codepoint=32,
            max_codepoint=0x10000,  # 限制Unicode范围
            blacklist_categories=('Cs',),  # 排除代理字符
            blacklist_characters='\x00<>:"/\\|?*'  # 排除NULL和文件系统非法字符
        ),
        min_size=1,
        max_size=20
    )
)
def test_property_encoding_correctness(path_component):
    """
    属性6: 编码处理正确性
    
    对于任何包含非ASCII字符（中文、日文、特殊符号等）的数据库路径，
    系统应该正确处理UTF-8编码转换，不产生编码错误。
    
    测试策略：
    1. 生成包含各种Unicode字符的路径
    2. 尝试初始化OCRCacheManager
    3. 验证不会因为编码问题崩溃
    4. 如果路径无效，应该抛出明确的CacheInitError
    """
    temp_dir = tempfile.mkdtemp()
    
    try:
        # 使用path_component作为文件名（已经过滤了非法字符）
        assume(len(path_component) > 0)
        
        # 构建测试路径
        test_db_path = os.path.join(temp_dir, path_component + ".db")
        
        # 验证路径可以编码为UTF-8
        try:
            test_db_path.encode('utf-8')
        except UnicodeEncodeError:
            # 如果无法编码，跳过这个测试用例
            assume(False)
        
        # Mock get_resource_path and file system checks
        with patch('ocr_cache_manager.get_resource_path') as mock_get_resource:
            mock_get_resource.return_value = "fake_lib.dll"
            
            with patch('ocr_cache_manager.os.path.exists') as mock_exists:
                mock_exists.return_value = True
                
                with patch('ocr_cache_manager.os.access') as mock_access:
                    mock_access.return_value = True
                    
                    # Mock C++库以避免实际初始化
                    with patch('ocr_cache_manager.ctypes.CDLL') as mock_cdll:
                        # 创建特殊的Mock类
                        class MockCLib:
                            def __init__(self):
                                self.ocr_engine_init = Mock(return_value=12345)  # 非NULL指针
                                self.ocr_engine_has_cache = Mock(return_value=0)
                                self.ocr_engine_destroy = Mock()
                                self.ocr_engine_save_result = Mock(return_value=0)
                                self.ocr_engine_load_all = Mock(return_value=None)
                                self.ocr_engine_save_session = Mock(return_value=0)
                                self.ocr_engine_load_session = Mock(return_value=None)
                                self.ocr_engine_clear = Mock()
                                self.ocr_engine_free_string = Mock()
                            
                            def __getattr__(self, name):
                                return Mock()
                        
                        mock_cdll.return_value = MockCLib()
                        
                        # 尝试初始化
                        try:
                            manager = OCRCacheManager(test_db_path)
                            
                            # 验证路径被正确处理
                            assert manager.db_path is not None, "数据库路径不应为None"
                            
                            # 验证路径可以编码
                            encoded_path = manager.db_path.encode('utf-8')
                            assert isinstance(encoded_path, bytes), "路径应该可以编码为bytes"
                            
                            # 验证引擎已初始化
                            assert manager.engine is not None, "引擎应该已初始化"
                            assert manager.engine != 0, "引擎指针不应为0"
                            
                            # 清理
                            del manager
                            
                        except CacheInitError as e:
                            # 如果抛出CacheInitError，验证是路径相关的错误
                            assert e.error_type in ["path_validation_failed", "path_creation_failed", 
                                                   "permission_denied", "encoding_error"], \
                                f"编码相关错误类型应该是路径或编码错误，实际是'{e.error_type}'"
                            # 验证错误信息提到了编码或路径
                            assert any(keyword in e.error_message.lower() 
                                      for keyword in ["编码", "路径", "encode", "path"]), \
                                "错误信息应该提到编码或路径问题"
                        except UnicodeEncodeError as e:
                            # 不应该抛出UnicodeEncodeError，应该被包装为CacheInitError
                            assert False, f"不应该抛出UnicodeEncodeError，应该被包装为CacheInitError: {e}"
                        except Exception as e:
                            # 其他异常也不应该发生
                            assert False, f"不应该抛出{type(e).__name__}异常: {e}"
    
    finally:
        try:
            shutil.rmtree(temp_dir)
        except Exception:
            pass


# ============================================================
# 辅助函数：运行所有属性测试
# ============================================================

def run_all_property_tests():
    """运行所有属性测试"""
    print("=" * 80)
    print("缓存管理器鲁棒性属性测试")
    print("=" * 80)
    
    tests = [
        ("属性4: NULL指针安全检测", test_property_null_pointer_safety),
        ("属性5: ctypes调用安全性", test_property_ctypes_call_safety),
        ("属性6: 编码处理正确性", test_property_encoding_correctness),
    ]
    
    passed = []
    failed = []
    
    for test_name, test_func in tests:
        print(f"\n运行测试: {test_name}")
        print("-" * 60)
        try:
            # 运行hypothesis测试
            # 使用.hypothesis.fuzz_one_input()来运行单个测试
            import sys
            import io
            
            # 捕获输出
            old_stdout = sys.stdout
            sys.stdout = io.StringIO()
            
            try:
                test_func()
                output = sys.stdout.getvalue()
            finally:
                sys.stdout = old_stdout
            
            if output:
                print(output)
            
            print(f"[PASS] {test_name} 通过")
            passed.append(test_name)
        except Exception as e:
            import traceback
            print(f"[FAIL] {test_name} 失败")
            print(f"错误: {e}")
            print(traceback.format_exc())
            failed.append((test_name, str(e)))
    
    # 打印总结
    print("\n" + "=" * 80)
    print("测试总结")
    print("=" * 80)
    print(f"通过: {len(passed)}/{len(tests)}")
    print(f"失败: {len(failed)}/{len(tests)}")
    
    if passed:
        print("\n通过的测试:")
        for test_name in passed:
            print(f"  [PASS] {test_name}")
    
    if failed:
        print("\n失败的测试:")
        for test_name, error in failed:
            print(f"  [FAIL] {test_name}")
            print(f"    错误: {error[:200]}")  # 限制错误信息长度
    
    return len(failed) == 0


if __name__ == "__main__":
    try:
        success = run_all_property_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n测试执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


# ============================================================
# 单元测试：数据库自动恢复机制
# 测试需求 3.1, 3.2, 3.3, 3.4, 3.5
# ============================================================

import sqlite3


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
                        
                        # 验证损坏的数据库存在
                        assert os.path.exists(test_db_path), "损坏的数据库应该存在"
                        
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
    
    # 运行属性测试
    run_all_property_tests()
