#!/usr/bin/env python3
"""
导入语句审查工具
检查所有Python文件的顶层import，识别应该延迟导入的模块
"""

import ast
import os
from pathlib import Path

# 核心模块（应该保持顶层导入）
CORE_MODULES = {
    'PySide6', 'PIL', 'config', 'pathlib', 'typing',
    'enum', 'dataclasses', 'dependency_manager'
}

# 标准库模块（可以顶层导入）
STDLIB_MODULES = {
    'os', 'sys', 'json', 're', 'time', 'datetime', 'collections',
    'subprocess', 'ctypes', 'base64', 'socket', 'threading', 'gc',
    'ast', 'io', 'atexit', 'importlib', 'platform', 'shutil',
    'tempfile', 'traceback', 'unittest'
}

# 应该延迟导入的模块
LAZY_LOAD_MODULES = {
    'openpyxl': 'Excel导出功能',
    'fitz': 'PDF处理功能',
    'alibabacloud_ocr_api20210707': '阿里云OCR',
    'alibabacloud_tea_openapi': '阿里云SDK',
    'alibabacloud_tea_util': '阿里云SDK',
    'openai': 'DeepSeek OCR',
    'numpy': 'numpy数组处理',
    'ocr_engine_manager': 'OCR引擎管理器',
}

def get_top_level_imports(file_path):
    """提取文件的顶层import语句"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        top_level_imports = []
        
        for node in tree.body:
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top_level = alias.name.split('.')[0]
                    top_level_imports.append({
                        'type': 'import',
                        'module': top_level,
                        'line': node.lineno,
                        'full': alias.name
                    })
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    top_level = node.module.split('.')[0]
                    top_level_imports.append({
                        'type': 'from',
                        'module': top_level,
                        'line': node.lineno,
                        'full': node.module
                    })
        
        return top_level_imports
    
    except Exception as e:
        print(f"警告: 解析 {file_path} 失败: {e}")
        return []

def analyze_file(file_path):
    """分析单个文件的导入"""
    imports = get_top_level_imports(file_path)
    
    issues = []
    
    for imp in imports:
        module = imp['module']
        
        # 检查是否应该延迟导入
        if module in LAZY_LOAD_MODULES:
            issues.append({
                'severity': 'warning',
                'line': imp['line'],
                'module': module,
                'message': f"建议延迟导入 {module} ({LAZY_LOAD_MODULES[module]})",
                'suggestion': f"使用 DependencyManager.load_xxx() 在需要时加载"
            })
    
    return imports, issues

def main():
    print("=" * 80)
    print("导入语句审查报告")
    print("=" * 80)
    print()
    
    # 获取所有Python文件
    python_files = []
    exclude_dirs = {'.venv', 'venv', 'env', '__pycache__', '.git', 'build', 'dist',
                   'portable_python', 'models', 'Pack', 'Env-Config'}
    
    for root, dirs, files in os.walk('.'):
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file.endswith('.py') and not file.startswith('test_'):
                python_files.append(os.path.join(root, file))
    
    print(f"📁 扫描 {len(python_files)} 个Python文件\n")
    
    all_issues = []
    files_with_issues = []
    
    for file_path in sorted(python_files):
        imports, issues = analyze_file(file_path)
        
        if issues:
            files_with_issues.append((file_path, imports, issues))
            all_issues.extend(issues)
    
    # 打印结果
    if files_with_issues:
        print("⚠️  发现需要优化的文件:\n")
        
        for file_path, imports, issues in files_with_issues:
            print(f"📄 {file_path}")
            
            for issue in issues:
                print(f"   行 {issue['line']:4d}: {issue['message']}")
                print(f"            {issue['suggestion']}")
            
            print()
    else:
        print("✅ 所有文件的导入语句都已优化！\n")
    
    # 统计
    print("=" * 80)
    print("📊 统计")
    print("=" * 80)
    print(f"总文件数: {len(python_files)}")
    print(f"需要优化的文件: {len(files_with_issues)}")
    print(f"需要优化的导入: {len(all_issues)}")
    print()
    
    # 按模块分组统计
    if all_issues:
        print("按模块分组:")
        module_count = {}
        for issue in all_issues:
            module = issue['module']
            module_count[module] = module_count.get(module, 0) + 1
        
        for module, count in sorted(module_count.items(), key=lambda x: -x[1]):
            print(f"  • {module:30s} {count} 处")
    
    print()
    
    # 生成报告
    with open('import_review_report.md', 'w', encoding='utf-8') as f:
        f.write("# 导入语句审查报告\n\n")
        
        f.write("## 概述\n\n")
        f.write(f"- 总文件数: {len(python_files)}\n")
        f.write(f"- 需要优化的文件: {len(files_with_issues)}\n")
        f.write(f"- 需要优化的导入: {len(all_issues)}\n\n")
        
        if files_with_issues:
            f.write("## 需要优化的文件\n\n")
            
            for file_path, imports, issues in files_with_issues:
                f.write(f"### {file_path}\n\n")
                
                for issue in issues:
                    f.write(f"- **行 {issue['line']}**: {issue['message']}\n")
                    f.write(f"  - 建议: {issue['suggestion']}\n")
                
                f.write("\n")
        else:
            f.write("## ✅ 所有导入已优化\n\n")
    
    print("✅ 报告已保存到: import_review_report.md")

if __name__ == '__main__':
    main()
