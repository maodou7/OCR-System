"""
OCR缓存引擎DLL诊断工具
用于检测和诊断DLL加载和函数导出问题
"""

import os
import sys
import ctypes
import platform
from pathlib import Path

def check_dll_exists():
    """检查DLL文件是否存在"""
    print("=" * 60)
    print("1. 检查DLL文件")
    print("=" * 60)
    
    dll_path = os.path.join("models", "ocr_cache.dll")
    if os.path.exists(dll_path):
        size = os.path.getsize(dll_path)
        print(f"✓ DLL文件存在: {dll_path}")
        print(f"  文件大小: {size:,} 字节 ({size/1024:.2f} KB)")
        return dll_path
    else:
        print(f"✗ DLL文件不存在: {dll_path}")
        print("\n建议:")
        print("  1. 运行 models/cpp_engine/rebuild_dll.bat 重新编译DLL")
        print("  2. 确保已安装MinGW编译器")
        return None

def check_dll_dependencies(dll_path):
    """检查DLL依赖"""
    print("\n" + "=" * 60)
    print("2. 检查DLL依赖")
    print("=" * 60)
    
    try:
        # 尝试加载DLL
        lib = ctypes.CDLL(dll_path)
        print("✓ DLL加载成功")
        return lib
    except OSError as e:
        print(f"✗ DLL加载失败: {e}")
        print("\n可能的原因:")
        print("  1. 缺少Visual C++ Redistributable运行时")
        print("  2. DLL依赖的其他库不存在")
        print("  3. DLL文件损坏")
        print("\n建议:")
        print("  1. 安装 Visual C++ Redistributable:")
        print("     https://aka.ms/vs/17/release/vc_redist.x64.exe")
        print("  2. 使用 Dependency Walker 检查缺少的依赖:")
        print("     http://www.dependencywalker.com/")
        return None

def check_function_exports(lib):
    """检查函数导出"""
    print("\n" + "=" * 60)
    print("3. 检查函数导出")
    print("=" * 60)
    
    functions = [
        "ocr_engine_init",
        "ocr_engine_save_result",
        "ocr_engine_load_all",
        "ocr_engine_save_session",
        "ocr_engine_load_session",
        "ocr_engine_has_cache",
        "ocr_engine_clear",
        "ocr_engine_destroy",
        "ocr_engine_free_string",
        "ocr_engine_get_error"
    ]
    
    all_ok = True
    for func_name in functions:
        try:
            func = getattr(lib, func_name)
            print(f"✓ {func_name}")
        except AttributeError:
            print(f"✗ {func_name} - 未导出")
            all_ok = False
    
    if not all_ok:
        print("\n问题: 部分函数未正确导出")
        print("建议:")
        print("  1. 检查 ocr_cache_engine.h 中是否所有函数都有 OCR_CACHE_API 宏")
        print("  2. 检查 CMakeLists.txt 中是否定义了 OCR_CACHE_EXPORTS")
        print("  3. 重新编译DLL: models/cpp_engine/rebuild_dll.bat")
    
    return all_ok

def test_basic_functionality(lib):
    """测试基本功能"""
    print("\n" + "=" * 60)
    print("4. 测试基本功能")
    print("=" * 60)
    
    try:
        # 定义函数签名
        lib.ocr_engine_init.argtypes = [ctypes.c_char_p]
        lib.ocr_engine_init.restype = ctypes.c_void_p
        
        lib.ocr_engine_has_cache.argtypes = [ctypes.c_void_p]
        lib.ocr_engine_has_cache.restype = ctypes.c_int
        
        lib.ocr_engine_destroy.argtypes = [ctypes.c_void_p]
        lib.ocr_engine_destroy.restype = None
        
        # 测试初始化
        test_db = b"test_cache.db"
        print(f"  测试初始化引擎...")
        engine = lib.ocr_engine_init(test_db)
        
        if not engine or engine == 0:
            print("✗ 引擎初始化失败 - 返回NULL指针")
            return False
        
        print(f"✓ 引擎初始化成功 (指针: {hex(engine)})")
        
        # 测试has_cache
        print(f"  测试has_cache...")
        result = lib.ocr_engine_has_cache(engine)
        print(f"✓ has_cache返回: {result}")
        
        # 清理
        print(f"  清理资源...")
        lib.ocr_engine_destroy(engine)
        print("✓ 资源清理成功")
        
        # 删除测试数据库
        if os.path.exists("test_cache.db"):
            os.remove("test_cache.db")
        if os.path.exists("test_cache.db-wal"):
            os.remove("test_cache.db-wal")
        if os.path.exists("test_cache.db-shm"):
            os.remove("test_cache.db-shm")
        
        return True
        
    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "=" * 60)
    print("OCR缓存引擎DLL诊断工具")
    print("=" * 60)
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    
    # 步骤1: 检查DLL文件
    dll_path = check_dll_exists()
    if not dll_path:
        print("\n" + "=" * 60)
        print("诊断结果: DLL文件不存在")
        print("=" * 60)
        return
    
    # 步骤2: 检查DLL依赖
    lib = check_dll_dependencies(dll_path)
    if not lib:
        print("\n" + "=" * 60)
        print("诊断结果: DLL加载失败")
        print("=" * 60)
        return
    
    # 步骤3: 检查函数导出
    exports_ok = check_function_exports(lib)
    if not exports_ok:
        print("\n" + "=" * 60)
        print("诊断结果: 函数导出不完整")
        print("=" * 60)
        return
    
    # 步骤4: 测试基本功能
    test_ok = test_basic_functionality(lib)
    
    print("\n" + "=" * 60)
    if test_ok:
        print("诊断结果: ✓ 所有检查通过，DLL工作正常")
    else:
        print("诊断结果: ✗ 功能测试失败")
    print("=" * 60)

if __name__ == "__main__":
    main()
