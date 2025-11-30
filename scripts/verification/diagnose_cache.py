"""
缓存引擎诊断脚本

用于诊断缓存引擎的问题，提供详细的系统信息和错误报告。
"""

import os
import sys
import platform
import json
from datetime import datetime


def diagnose():
    """运行完整的诊断流程"""
    print("=" * 70)
    print("缓存引擎诊断报告".center(70))
    print("=" * 70)
    print()
    
    # 系统信息
    print_section("系统信息")
    print(f"操作系统: {platform.system()} {platform.release()} ({platform.version()})")
    print(f"Python版本: {sys.version}")
    print(f"Python路径: {sys.executable}")
    print(f"工作目录: {os.getcwd()}")
    print(f"诊断时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 检查库文件
    print_section("库文件检查")
    check_library_files()
    print()
    
    # 检查数据库目录
    print_section("数据库目录检查")
    check_database_directory()
    print()
    
    # 检查依赖
    print_section("Python依赖检查")
    check_python_dependencies()
    print()
    
    # 测试缓存初始化
    print_section("缓存初始化测试")
    test_cache_initialization()
    print()
    
    print("=" * 70)
    print("诊断完成".center(70))
    print("=" * 70)
    print()
    print("如果问题仍未解决，请参考:")
    print("  - 故障排除指南: CACHE_TROUBLESHOOTING.md")
    print("  - 错误消息参考: CACHE_ERROR_MESSAGES.md")
    print("  - 提交Issue: https://github.com/maodou7/OCR-System/issues")


def print_section(title):
    """打印章节标题"""
    print(f"[{title}]")
    print("-" * 70)


def check_library_files():
    """检查库文件"""
    if platform.system() == "Windows":
        lib_path = "models/ocr_cache.dll"
    else:
        lib_path = "models/libocr_cache.so"
    
    if os.path.exists(lib_path):
        file_size = os.path.getsize(lib_path)
        print(f"✓ 库文件存在: {lib_path}")
        print(f"  文件大小: {file_size:,} 字节 ({file_size / 1024:.2f} KB)")
        
        # 检查文件权限
        if os.access(lib_path, os.R_OK):
            print(f"  可读: 是")
        else:
            print(f"  可读: 否 ⚠️")
        
        if os.access(lib_path, os.X_OK):
            print(f"  可执行: 是")
        else:
            print(f"  可执行: 否 ⚠️")
    else:
        print(f"✗ 库文件不存在: {lib_path}")
        print(f"  建议: 重新下载或安装应用程序")
    
    # 检查models目录
    models_dir = "models"
    if os.path.exists(models_dir):
        print(f"✓ models目录存在")
        files = os.listdir(models_dir)
        print(f"  包含文件: {len(files)} 个")
    else:
        print(f"✗ models目录不存在")


def check_database_directory():
    """检查数据库目录"""
    db_dir = ".ocr_cache"
    db_file = os.path.join(db_dir, "ocr_cache.db")
    
    if os.path.exists(db_dir):
        print(f"✓ 数据库目录存在: {db_dir}")
        
        # 检查目录权限
        if os.access(db_dir, os.W_OK):
            print(f"  可写: 是")
        else:
            print(f"  可写: 否 ⚠️")
            print(f"  建议: 修改目录权限或以管理员身份运行")
        
        # 检查数据库文件
        if os.path.exists(db_file):
            file_size = os.path.getsize(db_file)
            print(f"✓ 数据库文件存在: {db_file}")
            print(f"  文件大小: {file_size:,} 字节 ({file_size / 1024:.2f} KB)")
            
            # 检查备份文件
            backup_file = f"{db_file}.backup"
            if os.path.exists(backup_file):
                backup_size = os.path.getsize(backup_file)
                print(f"  备份文件: {backup_file} ({backup_size / 1024:.2f} KB)")
        else:
            print(f"  数据库文件不存在（首次运行正常）")
    else:
        print(f"  数据库目录不存在（首次运行正常）")
        print(f"  程序首次运行时会自动创建")


def check_python_dependencies():
    """检查Python依赖"""
    dependencies = [
        "ctypes",
        "threading",
        "logging",
        "dataclasses",
        "datetime"
    ]
    
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✓ {dep}")
        except ImportError:
            print(f"✗ {dep} (缺失)")


def test_cache_initialization():
    """测试缓存初始化"""
    try:
        # 尝试导入
        from cache_manager_wrapper import CacheManagerWrapper
        print("✓ 成功导入 CacheManagerWrapper")
        
        # 尝试初始化
        print("\n正在初始化缓存管理器...")
        wrapper = CacheManagerWrapper()
        print("✓ 缓存管理器初始化成功")
        
        # 获取健康检查信息
        health = wrapper.health_check()
        
        print("\n[缓存状态]")
        print(f"缓存可用: {health['cache_available']}")
        print(f"后端类型: {health['backend_type']}")
        print(f"降级模式: {health['fallback_active']}")
        print(f"状态消息: {health['message']}")
        
        if 'init_error' in health:
            print("\n[初始化错误]")
            error = health['init_error']
            print(f"错误类型: {error['type']}")
            print(f"错误消息: {error['message']}")
            print(f"建议:")
            for i, suggestion in enumerate(error['suggestions'], 1):
                print(f"  {i}. {suggestion}")
        
        # 内存缓存统计
        if 'memory_cache' in health:
            print("\n[内存缓存统计]")
            mem_cache = health['memory_cache']
            print(f"结果数量: {mem_cache['results_count']}")
            print(f"会话数据: {'有' if mem_cache['has_session'] else '无'}")
        
        # 测试基本操作
        print("\n[功能测试]")
        try:
            # 测试保存
            from config import OCRRect
            test_rect = OCRRect(x=0, y=0, w=100, h=100, text="测试")
            success = wrapper.save_result("test.png", [test_rect], "测试")
            print(f"保存测试: {'✓ 成功' if success else '✗ 失败'}")
            
            # 测试加载
            results = wrapper.load_all_results()
            print(f"加载测试: ✓ 成功 (加载了 {len(results)} 条记录)")
            
            # 清理测试数据
            wrapper.clear_cache()
            print(f"清理测试: ✓ 成功")
            
        except Exception as e:
            print(f"功能测试失败: {e}")
    
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        print(f"  建议: 确认所有必需的文件都存在")
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
        print(f"  异常类型: {type(e).__name__}")
        
        # 尝试获取更多信息
        import traceback
        print("\n[详细错误信息]")
        print(traceback.format_exc())


if __name__ == "__main__":
    try:
        diagnose()
    except KeyboardInterrupt:
        print("\n\n诊断被用户中断")
    except Exception as e:
        print(f"\n\n诊断过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
