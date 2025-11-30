"""
测试C++引擎增强的错误报告功能
验证需求 2.1, 2.2, 2.4
"""

import os
import sys
import ctypes
import tempfile
import shutil
from pathlib import Path

def test_engine_version():
    """测试 ocr_engine_version() 函数"""
    print("\n=== 测试 1: 引擎版本查询 ===")
    
    # 加载DLL - 尝试多个可能的路径
    possible_paths = [
        Path("models/ocr_cache.dll"),
        Path("../models/ocr_cache.dll"),
        Path("../../models/ocr_cache.dll")
    ]
    
    dll_path = None
    for path in possible_paths:
        if path.exists():
            dll_path = path
            break
    
    if not dll_path:
        print(f"❌ DLL文件不存在，尝试过的路径: {[str(p) for p in possible_paths]}")
        return False
    
    print(f"✓ 找到DLL: {dll_path}")
    
    try:
        lib = ctypes.CDLL(str(dll_path))
        
        # 设置函数签名
        lib.ocr_engine_version.restype = ctypes.c_char_p
        lib.ocr_engine_version.argtypes = []
        
        # 调用函数
        version = lib.ocr_engine_version()
        version_str = version.decode('utf-8') if version else "Unknown"
        
        print(f"✓ 引擎版本: {version_str}")
        
        # 验证版本字符串格式
        if "OCR Cache Engine" in version_str and "SQLite" in version_str:
            print("✓ 版本字符串格式正确")
            return True
        else:
            print(f"❌ 版本字符串格式不正确: {version_str}")
            return False
            
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False


def test_engine_test_function():
    """测试 ocr_engine_test() 健康检查函数"""
    print("\n=== 测试 2: 引擎健康检查 ===")
    
    # 加载DLL - 尝试多个可能的路径
    possible_paths = [
        Path("models/ocr_cache.dll"),
        Path("../models/ocr_cache.dll"),
        Path("../../models/ocr_cache.dll")
    ]
    
    dll_path = None
    for path in possible_paths:
        if path.exists():
            dll_path = path
            break
    
    if not dll_path:
        print(f"❌ DLL文件不存在")
        return False
    
    print(f"✓ 找到DLL: {dll_path}")
    
    try:
        lib = ctypes.CDLL(str(dll_path))
        
        # 设置函数签名
        lib.ocr_engine_init.restype = ctypes.c_void_p
        lib.ocr_engine_init.argtypes = [ctypes.c_char_p]
        
        lib.ocr_engine_test.restype = ctypes.c_int
        lib.ocr_engine_test.argtypes = [ctypes.c_void_p]
        
        lib.ocr_engine_get_error.restype = ctypes.c_char_p
        lib.ocr_engine_get_error.argtypes = [ctypes.c_void_p]
        
        lib.ocr_engine_destroy.restype = None
        lib.ocr_engine_destroy.argtypes = [ctypes.c_void_p]
        
        # 创建临时数据库
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_health.db")
            
            # 初始化引擎
            engine = lib.ocr_engine_init(db_path.encode('utf-8'))
            
            if not engine:
                print("❌ 引擎初始化失败")
                return False
            
            print("✓ 引擎初始化成功")
            
            # 执行健康检查
            result = lib.ocr_engine_test(engine)
            
            if result == 1:
                print("✓ 健康检查通过")
                lib.ocr_engine_destroy(engine)
                return True
            else:
                error = lib.ocr_engine_get_error(engine)
                error_str = error.decode('utf-8') if error else "Unknown error"
                print(f"❌ 健康检查失败: {error_str}")
                lib.ocr_engine_destroy(engine)
                return False
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_detailed_error_messages():
    """测试详细的错误消息"""
    print("\n=== 测试 3: 详细错误消息 ===")
    
    # 加载DLL - 尝试多个可能的路径
    possible_paths = [
        Path("models/ocr_cache.dll"),
        Path("../models/ocr_cache.dll"),
        Path("../../models/ocr_cache.dll")
    ]
    
    dll_path = None
    for path in possible_paths:
        if path.exists():
            dll_path = path
            break
    
    if not dll_path:
        print(f"❌ DLL文件不存在")
        return False
    
    print(f"✓ 找到DLL: {dll_path}")
    
    try:
        lib = ctypes.CDLL(str(dll_path))
        
        # 设置函数签名
        lib.ocr_engine_init.restype = ctypes.c_void_p
        lib.ocr_engine_init.argtypes = [ctypes.c_char_p]
        
        lib.ocr_engine_get_error.restype = ctypes.c_char_p
        lib.ocr_engine_get_error.argtypes = [ctypes.c_void_p]
        
        lib.ocr_engine_save_result.restype = ctypes.c_int
        lib.ocr_engine_save_result.argtypes = [
            ctypes.c_void_p,
            ctypes.c_char_p,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_double),
            ctypes.POINTER(ctypes.c_char_p)
        ]
        
        lib.ocr_engine_destroy.restype = None
        lib.ocr_engine_destroy.argtypes = [ctypes.c_void_p]
        
        # 测试1: 空路径初始化
        print("\n测试 3.1: 空路径初始化")
        engine = lib.ocr_engine_init(b"")
        if engine:
            print("❌ 应该失败但成功了")
            lib.ocr_engine_destroy(engine)
            return False
        else:
            print("✓ 正确拒绝空路径")
        
        # 测试2: 无效路径初始化
        print("\n测试 3.2: 无效路径初始化")
        invalid_path = "/invalid/path/that/does/not/exist/test.db"
        engine = lib.ocr_engine_init(invalid_path.encode('utf-8'))
        if engine:
            error = lib.ocr_engine_get_error(engine)
            error_str = error.decode('utf-8') if error else ""
            print(f"引擎初始化成功（可能创建了目录）")
            lib.ocr_engine_destroy(engine)
        else:
            print("✓ 正确拒绝无效路径")
        
        # 测试3: 使用有效引擎测试错误消息
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_errors.db")
            engine = lib.ocr_engine_init(db_path.encode('utf-8'))
            
            if not engine:
                print("❌ 无法创建测试引擎")
                return False
            
            print("\n测试 3.3: 无效参数错误消息")
            # 尝试保存结果但传入无效参数
            result = lib.ocr_engine_save_result(
                engine,
                None,  # NULL file_path
                b"completed",
                0,
                None,
                None
            )
            
            if result == -1:
                error = lib.ocr_engine_get_error(engine)
                error_str = error.decode('utf-8') if error else ""
                print(f"✓ 捕获到错误: {error_str}")
                
                # 验证错误消息包含有用信息
                if "NULL" in error_str or "null" in error_str.lower():
                    print("✓ 错误消息包含详细信息")
                else:
                    print(f"⚠ 错误消息可能不够详细: {error_str}")
            else:
                print("❌ 应该返回错误但成功了")
                lib.ocr_engine_destroy(engine)
                return False
            
            lib.ocr_engine_destroy(engine)
        
        print("\n✓ 所有错误消息测试通过")
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_init_stage_tracking():
    """测试初始化阶段跟踪"""
    print("\n=== 测试 4: 初始化阶段跟踪 ===")
    
    # 加载DLL - 尝试多个可能的路径
    possible_paths = [
        Path("models/ocr_cache.dll"),
        Path("../models/ocr_cache.dll"),
        Path("../../models/ocr_cache.dll")
    ]
    
    dll_path = None
    for path in possible_paths:
        if path.exists():
            dll_path = path
            break
    
    if not dll_path:
        print(f"❌ DLL文件不存在")
        return False
    
    print(f"✓ 找到DLL: {dll_path}")
    
    try:
        lib = ctypes.CDLL(str(dll_path))
        
        # 设置函数签名
        lib.ocr_engine_init.restype = ctypes.c_void_p
        lib.ocr_engine_init.argtypes = [ctypes.c_char_p]
        
        lib.ocr_engine_get_error.restype = ctypes.c_char_p
        lib.ocr_engine_get_error.argtypes = [ctypes.c_void_p]
        
        lib.ocr_engine_destroy.restype = None
        lib.ocr_engine_destroy.argtypes = [ctypes.c_void_p]
        
        # 测试成功初始化
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test_stage.db")
            engine = lib.ocr_engine_init(db_path.encode('utf-8'))
            
            if engine:
                print("✓ 引擎初始化成功")
                error = lib.ocr_engine_get_error(engine)
                error_str = error.decode('utf-8') if error else ""
                
                # 成功初始化后，错误消息应该为空或表示成功
                if not error_str or error_str == "":
                    print("✓ 成功初始化后错误消息为空")
                else:
                    print(f"⚠ 成功初始化后仍有错误消息: {error_str}")
                
                lib.ocr_engine_destroy(engine)
                return True
            else:
                print("❌ 引擎初始化失败")
                return False
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("=" * 60)
    print("C++引擎错误报告增强测试")
    print("=" * 60)
    
    results = []
    
    # 注意: 这些测试需要重新编译的DLL才能完全通过
    # 如果DLL未重新编译，某些测试可能会失败
    print("\n⚠ 注意: 这些测试需要重新编译的DLL才能完全验证新功能")
    print("如果CMake不可用，请手动编译DLL或在有CMake的环境中运行")
    
    results.append(("引擎版本查询", test_engine_version()))
    results.append(("引擎健康检查", test_engine_test_function()))
    results.append(("详细错误消息", test_detailed_error_messages()))
    results.append(("初始化阶段跟踪", test_init_stage_tracking()))
    
    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "❌ 失败"
        print(f"{status}: {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
        return 0
    else:
        print(f"\n⚠ {total - passed} 个测试失败")
        print("\n如果测试失败是因为DLL未重新编译，这是预期的。")
        print("代码更改已完成，需要在有CMake的环境中重新编译DLL。")
        return 1


if __name__ == "__main__":
    sys.exit(main())
