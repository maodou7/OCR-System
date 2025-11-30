#!/usr/bin/env python3
"""
启动时模块检查工具

监控启动时加载的模块，识别不应在启动时加载的模块
验证需求: 8.4
"""

import sys
import os

# 确保导入路径正确
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def check_startup_modules():
    """
    检查启动时加载的模块
    
    记录启动时加载的所有模块，识别不应在启动时加载的模块
    """
    print("=" * 60)
    print("启动时模块检查")
    print("=" * 60)
    print()
    
    # 记录启动前的模块
    initial_modules = set(sys.modules.keys())
    print(f"启动前已加载模块数: {len(initial_modules)}")
    print()
    
    # 导入主模块
    print("正在导入主模块...")
    from qt_main import MainWindow
    from PySide6.QtWidgets import QApplication
    
    # 记录导入后的模块
    after_import_modules = set(sys.modules.keys())
    new_modules = after_import_modules - initial_modules
    print(f"导入后新增模块数: {len(new_modules)}")
    print()
    
    # 创建应用和窗口
    print("正在创建应用和窗口...")
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.processEvents()
    
    # 记录创建后的模块
    after_create_modules = set(sys.modules.keys())
    create_new_modules = after_create_modules - after_import_modules
    print(f"创建后新增模块数: {len(create_new_modules)}")
    print()
    
    # 分析不应在启动时加载的模块
    print("=" * 60)
    print("模块加载分析")
    print("=" * 60)
    print()
    
    # 定义不应在启动时加载的模块
    should_not_load = {
        'openpyxl': 'Excel导出库（应在导出时加载）',
        'fitz': 'PyMuPDF PDF处理库（应在打开PDF时加载）',
        'numpy': 'NumPy数值计算库（检查是否必需）',
        'pandas': 'Pandas数据分析库（检查是否必需）',
        'matplotlib': 'Matplotlib绘图库（检查是否必需）',
        'scipy': 'SciPy科学计算库（检查是否必需）',
        'requests': 'HTTP请求库（应在需要时加载）',
        'urllib3': 'HTTP客户端库（应在需要时加载）',
        'certifi': 'SSL证书库（应在需要时加载）',
        'charset_normalizer': '字符编码检测库（应在需要时加载）',
    }
    
    # 检查不应加载的模块
    loaded_should_not = []
    for module_name, description in should_not_load.items():
        if module_name in after_create_modules:
            loaded_should_not.append((module_name, description))
    
    if loaded_should_not:
        print("⚠ 发现不应在启动时加载的模块:")
        print()
        for module_name, description in loaded_should_not:
            print(f"  • {module_name}")
            print(f"    说明: {description}")
            print()
    else:
        print("✓ 未发现不应在启动时加载的模块")
        print()
    
    # 分析关键模块
    print("=" * 60)
    print("关键模块加载状态")
    print("=" * 60)
    print()
    
    key_modules = {
        'PySide6': '必需（GUI框架）',
        'PIL': '必需（图像处理）',
        'config': '必需（配置管理）',
        'utils': '必需（工具函数）',
        'ocr_cache_manager': '必需（缓存管理）',
        'dependency_manager': '必需（依赖管理）',
        'optimized_image_loader': '必需（图像加载）',
        'ocr_engine_downloader': '必需（引擎下载）',
        'ocr_engine_manager': '延迟加载（OCR引擎管理）',
        'ocr_engine_paddle': '延迟加载（PaddleOCR引擎）',
        'ocr_engine_rapid': '延迟加载（RapidOCR引擎）',
        'ocr_engine_aliyun_new': '延迟加载（阿里云OCR）',
        'ocr_engine_deepseek': '延迟加载（DeepSeek OCR）',
    }
    
    for module_name, status in key_modules.items():
        if module_name in after_create_modules:
            print(f"  ✓ {module_name:<30} {status}")
        else:
            print(f"  ✗ {module_name:<30} {status}")
    print()
    
    # 统计模块类型
    print("=" * 60)
    print("模块类型统计")
    print("=" * 60)
    print()
    
    stdlib_count = 0
    third_party_count = 0
    local_count = 0
    
    for module_name in after_create_modules:
        if module_name.startswith('_') or '.' in module_name:
            continue
        
        try:
            module = sys.modules[module_name]
            if hasattr(module, '__file__') and module.__file__:
                module_path = module.__file__
                if 'site-packages' in module_path or 'dist-packages' in module_path:
                    third_party_count += 1
                elif sys.prefix in module_path:
                    stdlib_count += 1
                else:
                    local_count += 1
            else:
                stdlib_count += 1
        except:
            pass
    
    total_modules = len(after_create_modules)
    print(f"总模块数: {total_modules}")
    print(f"  标准库: {stdlib_count} ({stdlib_count/total_modules*100:.1f}%)")
    print(f"  第三方库: {third_party_count} ({third_party_count/total_modules*100:.1f}%)")
    print(f"  本地模块: {local_count} ({local_count/total_modules*100:.1f}%)")
    print()
    
    # 列出所有第三方模块
    print("=" * 60)
    print("第三方模块列表")
    print("=" * 60)
    print()
    
    third_party_modules = []
    for module_name in sorted(after_create_modules):
        if '.' in module_name:
            continue
        
        try:
            module = sys.modules[module_name]
            if hasattr(module, '__file__') and module.__file__:
                module_path = module.__file__
                if 'site-packages' in module_path or 'dist-packages' in module_path:
                    third_party_modules.append(module_name)
        except:
            pass
    
    if third_party_modules:
        for i, module_name in enumerate(third_party_modules, 1):
            print(f"  {i}. {module_name}")
    else:
        print("  (无)")
    print()
    
    # 保存报告
    report_path = os.path.join(os.path.dirname(__file__), "startup_modules_report.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("=" * 60 + "\n")
        f.write("启动时模块检查报告\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"启动前已加载模块数: {len(initial_modules)}\n")
        f.write(f"导入后新增模块数: {len(new_modules)}\n")
        f.write(f"创建后新增模块数: {len(create_new_modules)}\n")
        f.write(f"总模块数: {total_modules}\n\n")
        
        f.write("=" * 60 + "\n")
        f.write("不应在启动时加载的模块\n")
        f.write("=" * 60 + "\n\n")
        
        if loaded_should_not:
            for module_name, description in loaded_should_not:
                f.write(f"• {module_name}\n")
                f.write(f"  说明: {description}\n\n")
        else:
            f.write("✓ 未发现不应在启动时加载的模块\n\n")
        
        f.write("=" * 60 + "\n")
        f.write("关键模块加载状态\n")
        f.write("=" * 60 + "\n\n")
        
        for module_name, status in key_modules.items():
            if module_name in after_create_modules:
                f.write(f"✓ {module_name:<30} {status}\n")
            else:
                f.write(f"✗ {module_name:<30} {status}\n")
        f.write("\n")
        
        f.write("=" * 60 + "\n")
        f.write("模块类型统计\n")
        f.write("=" * 60 + "\n\n")
        
        f.write(f"总模块数: {total_modules}\n")
        f.write(f"  标准库: {stdlib_count} ({stdlib_count/total_modules*100:.1f}%)\n")
        f.write(f"  第三方库: {third_party_count} ({third_party_count/total_modules*100:.1f}%)\n")
        f.write(f"  本地模块: {local_count} ({local_count/total_modules*100:.1f}%)\n\n")
        
        f.write("=" * 60 + "\n")
        f.write("第三方模块列表\n")
        f.write("=" * 60 + "\n\n")
        
        if third_party_modules:
            for i, module_name in enumerate(third_party_modules, 1):
                f.write(f"{i}. {module_name}\n")
        else:
            f.write("(无)\n")
        f.write("\n")
        
        f.write("=" * 60 + "\n")
        f.write("所有加载的模块\n")
        f.write("=" * 60 + "\n\n")
        
        for i, module_name in enumerate(sorted(after_create_modules), 1):
            f.write(f"{i}. {module_name}\n")
    
    print(f"✓ 详细报告已保存到: {report_path}")
    print()
    
    # 优化建议
    print("=" * 60)
    print("优化建议")
    print("=" * 60)
    print()
    
    if loaded_should_not:
        print("建议优化以下模块的加载方式:")
        print()
        for module_name, description in loaded_should_not:
            print(f"  • {module_name}: 改为按需导入")
        print()
    else:
        print("✓ 模块加载策略良好")
        print()
    
    print("=" * 60)
    
    # 关闭应用
    app.quit()


if __name__ == "__main__":
    check_startup_modules()
