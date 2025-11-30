"""
Task 1 验证测试：验证OCRCacheManager增强的错误处理和验证
"""

import os
import sys
import tempfile
import shutil
import logging
from unittest.mock import Mock, patch, MagicMock

# 配置日志以避免输出干扰
logging.basicConfig(level=logging.CRITICAL)

try:
    from ocr_cache_manager import OCRCacheManager, CacheInitError
except ImportError as e:
    print(f"导入失败: {e}")
    sys.exit(1)


def test_null_pointer_detection():
    """测试NULL指针检测"""
    print("测试1: NULL指针检测...")
    
    temp_dir = tempfile.mkdtemp()
    try:
        test_db_path = os.path.join(temp_dir, "test.db")
        
        with patch('ocr_cache_manager.get_executable_dir', return_value=temp_dir):
            with patch('ocr_cache_manager.get_resource_path', return_value="fake_lib.dll"):
                with patch('ocr_cache_manager.os.path.exists', return_value=True):
                    with patch('ocr_cache_manager.os.access', return_value=True):
                        with patch('ocr_cache_manager.os.makedirs'):
                            with patch('ocr_cache_manager.ctypes.CDLL') as mock_cdll:
                                # Mock返回NULL指针
                                mock_lib = MagicMock()
                                mock_lib.ocr_engine_init = MagicMock(return_value=0)  # NULL
                                mock_lib.ocr_engine_destroy = MagicMock()
                                mock_lib.ocr_engine_has_cache = MagicMock(return_value=0)
                                mock_cdll.return_value = mock_lib
                                
                                try:
                                    manager = OCRCacheManager(test_db_path)
                                    print("  ❌ 失败: 应该抛出CacheInitError")
                                    return False
                                except CacheInitError as e:
                                    if e.error_type == "null_pointer":
                                        print(f"  ✅ 通过: 正确检测到NULL指针")
                                        print(f"     错误信息: {e.error_message[:50]}...")
                                        return True
                                    else:
                                        print(f"  ❌ 失败: 错误类型不正确: {e.error_type}")
                                        return False
                                except Exception as e:
                                    print(f"  ❌ 失败: 抛出了意外异常: {type(e).__name__}: {e}")
                                    import traceback
                                    traceback.print_exc()
                                    return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_ctypes_error_handling():
    """测试ctypes调用错误处理"""
    print("\n测试2: ctypes调用错误处理...")
    
    temp_dir = tempfile.mkdtemp()
    try:
        test_db_path = os.path.join(temp_dir, "test.db")
        
        with patch('ocr_cache_manager.get_executable_dir', return_value=temp_dir):
            with patch('ocr_cache_manager.get_resource_path', return_value="fake_lib.dll"):
                with patch('ocr_cache_manager.os.path.exists', return_value=True):
                    with patch('ocr_cache_manager.os.access', return_value=True):
                        with patch('ocr_cache_manager.os.makedirs'):
                            with patch('ocr_cache_manager.ctypes.CDLL') as mock_cdll:
                                # Mock抛出OSError
                                mock_cdll.side_effect = OSError("Library load failed")
                                
                                try:
                                    manager = OCRCacheManager(test_db_path)
                                    print("  ❌ 失败: 应该抛出CacheInitError")
                                    return False
                                except CacheInitError as e:
                                    if "library_load" in e.error_type:
                                        print(f"  ✅ 通过: 正确捕获ctypes错误")
                                        print(f"     错误类型: {e.error_type}")
                                        print(f"     建议数量: {len(e.suggestions)}")
                                        return True
                                    else:
                                        print(f"  ❌ 失败: 错误类型不正确: {e.error_type}")
                                        return False
                                except Exception as e:
                                    print(f"  ❌ 失败: 抛出了意外异常: {type(e).__name__}: {e}")
                                    return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_encoding_handling():
    """测试编码处理"""
    print("\n测试3: 编码处理...")
    
    temp_dir = tempfile.mkdtemp()
    try:
        # 使用包含中文的路径
        test_db_path = os.path.join(temp_dir, "测试数据库.db")
        
        with patch('ocr_cache_manager.get_resource_path', return_value="fake_lib.dll"):
            with patch('ocr_cache_manager.os.path.exists', return_value=True):
                with patch('ocr_cache_manager.os.access', return_value=True):
                    with patch('ocr_cache_manager.os.makedirs'):
                        with patch('ocr_cache_manager.ctypes.CDLL') as mock_cdll:
                            mock_lib = MagicMock()
                            mock_lib.ocr_engine_init = MagicMock(return_value=12345)  # 非NULL
                            mock_lib.ocr_engine_has_cache = MagicMock(return_value=0)
                            mock_lib.ocr_engine_destroy = MagicMock()
                            mock_cdll.return_value = mock_lib
                            
                            try:
                                manager = OCRCacheManager(test_db_path)
                                # 验证路径可以编码
                                encoded = manager.db_path.encode('utf-8')
                                print(f"  ✅ 通过: 正确处理中文路径")
                                print(f"     路径: {manager.db_path}")
                                del manager
                                return True
                            except UnicodeEncodeError as e:
                                print(f"  ❌ 失败: 编码错误未被正确处理: {e}")
                                return False
                            except CacheInitError as e:
                                # 如果是路径相关错误，也算通过（因为被正确包装了）
                                if "encoding" in e.error_type or "path" in e.error_type:
                                    print(f"  ✅ 通过: 编码错误被正确包装为CacheInitError")
                                    return True
                                else:
                                    print(f"  ❌ 失败: 错误类型不正确: {e.error_type}")
                                    return False
                            except Exception as e:
                                print(f"  ❌ 失败: 抛出了意外异常: {type(e).__name__}: {e}")
                                return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_detailed_error_logging():
    """测试详细的错误日志"""
    print("\n测试4: 详细错误日志...")
    
    temp_dir = tempfile.mkdtemp()
    try:
        test_db_path = os.path.join(temp_dir, "test.db")
        
        with patch('ocr_cache_manager.get_resource_path', return_value="fake_lib.dll"):
            with patch('ocr_cache_manager.os.path.exists', return_value=False):
                with patch('ocr_cache_manager.os.makedirs'):
                    try:
                        manager = OCRCacheManager(test_db_path)
                        print("  ❌ 失败: 应该抛出CacheInitError")
                        return False
                    except CacheInitError as e:
                        # 验证错误信息的完整性
                        has_error_type = e.error_type is not None
                        has_error_message = len(e.error_message) > 0
                        has_error_details = len(e.error_details) > 0
                        has_suggestions = len(e.suggestions) > 0
                        
                        if all([has_error_type, has_error_message, has_error_details, has_suggestions]):
                            print(f"  ✅ 通过: 错误信息完整")
                            print(f"     错误类型: {e.error_type}")
                            print(f"     详情字段数: {len(e.error_details)}")
                            print(f"     建议数量: {len(e.suggestions)}")
                            return True
                        else:
                            print(f"  ❌ 失败: 错误信息不完整")
                            print(f"     has_error_type: {has_error_type}")
                            print(f"     has_error_message: {has_error_message}")
                            print(f"     has_error_details: {has_error_details}")
                            print(f"     has_suggestions: {has_suggestions}")
                            return False
                    except Exception as e:
                        print(f"  ❌ 失败: 抛出了意外异常: {type(e).__name__}: {e}")
                        return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_path_validation():
    """测试路径验证"""
    print("\n测试5: 路径验证...")
    
    temp_dir = tempfile.mkdtemp()
    try:
        # 测试只读目录
        test_db_path = os.path.join(temp_dir, "test.db")
        
        with patch('ocr_cache_manager.os.makedirs'):
            with patch('ocr_cache_manager.os.access', return_value=False):
                try:
                    manager = OCRCacheManager(test_db_path)
                    print("  ❌ 失败: 应该抛出CacheInitError")
                    return False
                except CacheInitError as e:
                    if e.error_type == "permission_denied":
                        print(f"  ✅ 通过: 正确检测权限问题")
                        print(f"     错误信息: {e.error_message}")
                        return True
                    else:
                        print(f"  ❌ 失败: 错误类型不正确: {e.error_type}")
                        return False
                except Exception as e:
                    print(f"  ❌ 失败: 抛出了意外异常: {type(e).__name__}: {e}")
                    return False
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def main():
    """运行所有验证测试"""
    print("=" * 70)
    print("Task 1 验证测试：OCRCacheManager错误处理和验证增强")
    print("=" * 70)
    
    tests = [
        test_null_pointer_detection,
        test_ctypes_error_handling,
        test_encoding_handling,
        test_detailed_error_logging,
        test_path_validation,
    ]
    
    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"  ❌ 测试执行失败: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    # 打印总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    print(f"失败: {total - passed}/{total}")
    
    if passed == total:
        print("\n✅ 所有测试通过！Task 1 实现完成。")
        return True
    else:
        print(f"\n❌ {total - passed} 个测试失败")
        return False


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n测试执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
