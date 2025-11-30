#!/usr/bin/env python3
"""
依赖分析工具
扫描所有Python文件的import语句，对比requirements.txt，生成使用情况报告
"""

import os
import re
import ast
from pathlib import Path
from collections import defaultdict

def parse_requirements(req_file='requirements.txt'):
    """解析requirements.txt文件"""
    requirements = {}
    try:
        with open(req_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                # 跳过注释和空行
                if not line or line.startswith('#'):
                    continue
                
                # 解析包名（处理版本号）
                match = re.match(r'^([a-zA-Z0-9_-]+)', line)
                if match:
                    package = match.group(1).lower()
                    requirements[package] = line
    except FileNotFoundError:
        print(f"错误: 找不到 {req_file}")
        return {}
    
    return requirements

def get_python_files(root_dir='.'):
    """获取所有Python文件"""
    python_files = []
    exclude_dirs = {'.venv', 'venv', 'env', '__pycache__', '.git', 'build', 'dist', 
                   'portable_python', 'models', 'Pack', 'Env-Config'}
    
    for root, dirs, files in os.walk(root_dir):
        # 排除特定目录
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    return python_files

def extract_imports(file_path):
    """从Python文件中提取import语句"""
    imports = set()
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 使用AST解析
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    # 获取顶层包名
                    top_level = alias.name.split('.')[0]
                    imports.add(top_level)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    # 获取顶层包名
                    top_level = node.module.split('.')[0]
                    imports.add(top_level)
    
    except Exception as e:
        print(f"警告: 解析 {file_path} 失败: {e}")
    
    return imports

def map_import_to_package(import_name):
    """将import名称映射到requirements.txt中的包名"""
    # 常见的映射关系
    mapping = {
        'PIL': 'pillow',
        'cv2': 'opencv-python',
        'fitz': 'pymupdf',
        'openpyxl': 'openpyxl',
        'PySide6': 'pyside6',
        'alibabacloud_ocr_api20210707': 'alibabacloud-ocr-api20210707',
        'alibabacloud_tea_openapi': 'alibabacloud-tea-openapi',
        'alibabacloud_tea_util': 'alibabacloud-tea-util',
        'openai': 'openai',
        'numpy': 'numpy',
        'paddleocr': 'paddleocr',
        'rapidocr_onnxruntime': 'rapidocr-onnxruntime',
    }
    
    return mapping.get(import_name, import_name.lower())

def analyze_dependencies():
    """分析依赖使用情况"""
    print("=" * 80)
    print("依赖分析报告")
    print("=" * 80)
    print()
    
    # 1. 解析requirements.txt
    print("📋 解析 requirements.txt...")
    requirements = parse_requirements()
    print(f"   找到 {len(requirements)} 个依赖包")
    print()
    
    # 2. 扫描Python文件
    print("🔍 扫描Python文件...")
    python_files = get_python_files()
    print(f"   找到 {len(python_files)} 个Python文件")
    print()
    
    # 3. 提取所有import
    print("📦 提取import语句...")
    all_imports = set()
    file_imports = {}
    
    for file_path in python_files:
        imports = extract_imports(file_path)
        file_imports[file_path] = imports
        all_imports.update(imports)
    
    print(f"   找到 {len(all_imports)} 个不同的import")
    print()
    
    # 4. 映射import到包名
    print("🔗 映射import到requirements包名...")
    used_packages = defaultdict(list)
    
    for import_name in all_imports:
        package_name = map_import_to_package(import_name)
        if package_name in requirements:
            used_packages[package_name].append(import_name)
    
    print(f"   匹配到 {len(used_packages)} 个使用的包")
    print()
    
    # 5. 生成报告
    print("=" * 80)
    print("📊 分析结果")
    print("=" * 80)
    print()
    
    # 5.1 使用的依赖
    print("✅ 使用的依赖 ({} 个):".format(len(used_packages)))
    print("-" * 80)
    for package, imports in sorted(used_packages.items()):
        req_line = requirements[package]
        print(f"  • {package:30s} <- {', '.join(imports)}")
        print(f"    {req_line}")
    print()
    
    # 5.2 未使用的依赖
    unused_packages = set(requirements.keys()) - set(used_packages.keys())
    print("❌ 未使用的依赖 ({} 个):".format(len(unused_packages)))
    print("-" * 80)
    if unused_packages:
        for package in sorted(unused_packages):
            req_line = requirements[package]
            print(f"  • {package:30s}")
            print(f"    {req_line}")
    else:
        print("  （无）")
    print()
    
    # 5.3 未在requirements.txt中的import
    unmapped_imports = []
    for import_name in all_imports:
        package_name = map_import_to_package(import_name)
        if package_name not in requirements:
            unmapped_imports.append(import_name)
    
    print("⚠️  未在requirements.txt中的import ({} 个):".format(len(unmapped_imports)))
    print("-" * 80)
    if unmapped_imports:
        # 过滤标准库
        stdlib_modules = {'os', 'sys', 'json', 'pathlib', 'typing', 'enum', 'dataclasses',
                         'collections', 'time', 'datetime', 're', 'subprocess', 'ctypes',
                         'base64', 'socket', 'threading', 'gc', 'ast', 'io'}
        
        non_stdlib = [imp for imp in unmapped_imports if imp not in stdlib_modules]
        
        if non_stdlib:
            for import_name in sorted(non_stdlib):
                print(f"  • {import_name}")
        else:
            print("  （都是标准库模块）")
    else:
        print("  （无）")
    print()
    
    # 6. 详细使用情况
    print("=" * 80)
    print("📁 各文件的import详情")
    print("=" * 80)
    print()
    
    for file_path, imports in sorted(file_imports.items()):
        if imports:
            print(f"📄 {file_path}")
            for imp in sorted(imports):
                package = map_import_to_package(imp)
                status = "✓" if package in requirements else "?"
                print(f"   {status} {imp}")
            print()
    
    # 7. 优化建议
    print("=" * 80)
    print("💡 优化建议")
    print("=" * 80)
    print()
    
    if unused_packages:
        print("1. 可以移除以下未使用的依赖:")
        for package in sorted(unused_packages):
            print(f"   - {package}")
        print()
    
    # 检查大型依赖
    large_packages = {
        'paddleocr': '~300MB',
        'paddlepaddle': '~500MB+',
        'rapidocr-onnxruntime': '~100MB',
        'opencv-python': '~80MB',
        'numpy': '~20MB',
    }
    
    print("2. 大型依赖检查:")
    for package, size in large_packages.items():
        if package in used_packages:
            print(f"   ✓ {package:30s} {size:10s} (使用中)")
        elif package in requirements:
            print(f"   ❌ {package:30s} {size:10s} (未使用，建议移除)")
    print()
    
    print("3. 按需加载建议:")
    optional_packages = {
        'openpyxl': 'Excel导出功能',
        'pymupdf': 'PDF处理功能',
        'alibabacloud-ocr-api20210707': '阿里云OCR（在线）',
        'openai': 'DeepSeek OCR（在线）',
    }
    
    for package, feature in optional_packages.items():
        if package in used_packages:
            print(f"   • {package:30s} -> {feature}")
    print()
    
    # 8. 保存报告
    report_file = 'dependency_analysis_report.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 依赖分析报告\n\n")
        f.write(f"生成时间: {Path.cwd()}\n\n")
        
        f.write("## 使用的依赖\n\n")
        for package, imports in sorted(used_packages.items()):
            f.write(f"- **{package}**: {', '.join(imports)}\n")
        
        f.write("\n## 未使用的依赖\n\n")
        if unused_packages:
            for package in sorted(unused_packages):
                f.write(f"- {package}\n")
        else:
            f.write("（无）\n")
        
        f.write("\n## 优化建议\n\n")
        if unused_packages:
            f.write("### 可移除的依赖\n\n")
            for package in sorted(unused_packages):
                f.write(f"- {package}\n")
    
    print(f"✅ 报告已保存到: {report_file}")
    print()

if __name__ == '__main__':
    analyze_dependencies()
