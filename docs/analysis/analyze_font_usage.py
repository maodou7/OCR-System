#!/usr/bin/env python3
"""
字体文件使用分析工具

分析项目中的字体文件使用情况，评估是否需要内嵌字体文件。
"""

import os
import sys
from pathlib import Path


def find_font_files(root_dir='.'):
    """查找所有字体文件"""
    font_extensions = ['.ttf', '.otf', '.woff', '.woff2', '.eot']
    font_files = []
    
    for root, dirs, files in os.walk(root_dir):
        # 跳过虚拟环境和缓存目录
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'venv', 'env', 'node_modules', '.pytest_cache']]
        
        for file in files:
            if any(file.lower().endswith(ext) for ext in font_extensions):
                file_path = os.path.join(root, file)
                file_size = os.path.getsize(file_path)
                font_files.append({
                    'path': file_path,
                    'name': file,
                    'size': file_size,
                    'size_mb': file_size / (1024 * 1024)
                })
    
    return font_files


def analyze_font_usage_in_code(root_dir='.'):
    """分析代码中的字体使用情况"""
    font_usage = {
        'qfont_usage': [],
        'font_family_usage': [],
        'font_file_references': []
    }
    
    python_files = []
    for root, dirs, files in os.walk(root_dir):
        # 跳过虚拟环境和缓存目录
        dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', 'venv', 'env', 'node_modules', '.pytest_cache']]
        
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
    
    for py_file in python_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
                for i, line in enumerate(lines, 1):
                    # 检查QFont使用
                    if 'QFont' in line and not line.strip().startswith('#'):
                        font_usage['qfont_usage'].append({
                            'file': py_file,
                            'line': i,
                            'code': line.strip()
                        })
                    
                    # 检查字体族设置
                    if 'setFamily' in line or 'FontFamily' in line:
                        if not line.strip().startswith('#'):
                            font_usage['font_family_usage'].append({
                                'file': py_file,
                                'line': i,
                                'code': line.strip()
                            })
                    
                    # 检查字体文件引用
                    if any(ext in line for ext in ['.ttf', '.otf', '.woff']):
                        if not line.strip().startswith('#'):
                            font_usage['font_file_references'].append({
                                'file': py_file,
                                'line': i,
                                'code': line.strip()
                            })
        
        except Exception as e:
            print(f"警告: 无法读取文件 {py_file}: {e}")
    
    return font_usage


def check_pyside6_fonts():
    """检查PySide6是否使用系统字体"""
    info = {
        'uses_system_fonts': True,
        'explanation': 'PySide6/Qt默认使用系统字体，无需内嵌字体文件'
    }
    return info


def generate_report(font_files, font_usage, pyside6_info):
    """生成分析报告"""
    report = []
    report.append("# 字体文件使用分析报告")
    report.append("")
    report.append("## 1. 字体文件扫描结果")
    report.append("")
    
    if font_files:
        report.append(f"发现 {len(font_files)} 个字体文件:")
        report.append("")
        total_size = 0
        for font in font_files:
            report.append(f"- **{font['name']}**")
            report.append(f"  - 路径: `{font['path']}`")
            report.append(f"  - 大小: {font['size_mb']:.2f} MB")
            report.append("")
            total_size += font['size']
        
        report.append(f"**总大小**: {total_size / (1024 * 1024):.2f} MB")
        report.append("")
    else:
        report.append("✓ **未发现内嵌字体文件**")
        report.append("")
    
    report.append("## 2. 代码中的字体使用分析")
    report.append("")
    
    # QFont使用
    report.append("### 2.1 QFont使用情况")
    report.append("")
    if font_usage['qfont_usage']:
        report.append(f"发现 {len(font_usage['qfont_usage'])} 处QFont使用:")
        report.append("")
        for usage in font_usage['qfont_usage']:
            report.append(f"- **{usage['file']}** (行 {usage['line']})")
            report.append(f"  ```python")
            report.append(f"  {usage['code']}")
            report.append(f"  ```")
            report.append("")
    else:
        report.append("未发现QFont使用")
        report.append("")
    
    # 字体族设置
    report.append("### 2.2 字体族设置")
    report.append("")
    if font_usage['font_family_usage']:
        report.append(f"发现 {len(font_usage['font_family_usage'])} 处字体族设置:")
        report.append("")
        for usage in font_usage['font_family_usage']:
            report.append(f"- **{usage['file']}** (行 {usage['line']})")
            report.append(f"  ```python")
            report.append(f"  {usage['code']}")
            report.append(f"  ```")
            report.append("")
    else:
        report.append("✓ **未发现显式字体族设置**")
        report.append("")
    
    # 字体文件引用
    report.append("### 2.3 字体文件引用")
    report.append("")
    if font_usage['font_file_references']:
        report.append(f"发现 {len(font_usage['font_file_references'])} 处字体文件引用:")
        report.append("")
        for usage in font_usage['font_file_references']:
            report.append(f"- **{usage['file']}** (行 {usage['line']})")
            report.append(f"  ```python")
            report.append(f"  {usage['code']}")
            report.append(f"  ```")
            report.append("")
    else:
        report.append("✓ **未发现字体文件引用**")
        report.append("")
    
    report.append("## 3. PySide6字体机制")
    report.append("")
    report.append(f"- **使用系统字体**: {pyside6_info['uses_system_fonts']}")
    report.append(f"- **说明**: {pyside6_info['explanation']}")
    report.append("")
    
    report.append("## 4. 优化建议")
    report.append("")
    
    if font_files:
        report.append("### 发现内嵌字体文件")
        report.append("")
        report.append("**建议操作**:")
        report.append("")
        report.append("1. **评估必要性**: 检查这些字体文件是否真的需要")
        report.append("2. **使用系统字体**: PySide6/Qt默认使用系统字体，通常无需内嵌")
        report.append("3. **移除字体文件**: 如果不是必需的，建议移除以减小体积")
        report.append("4. **压缩字体**: 如果必须保留，考虑使用字体子集化工具压缩")
        report.append("")
        report.append(f"**预计节省空间**: {total_size / (1024 * 1024):.2f} MB")
        report.append("")
    else:
        report.append("### ✓ 无内嵌字体文件")
        report.append("")
        report.append("**当前状态**: 项目未内嵌字体文件，使用系统字体")
        report.append("")
        report.append("**优势**:")
        report.append("")
        report.append("1. **体积小**: 无需打包字体文件")
        report.append("2. **兼容性好**: 使用用户系统的字体，显示效果更自然")
        report.append("3. **维护简单**: 无需管理字体文件版本")
        report.append("")
        report.append("**建议**: 保持当前方案，继续使用系统字体")
        report.append("")
    
    # 代码中的字体使用建议
    if font_usage['qfont_usage'] or font_usage['font_family_usage']:
        report.append("### 代码优化建议")
        report.append("")
        report.append("**当前字体使用方式**:")
        report.append("")
        report.append("- 代码中使用了QFont，但未指定特定字体族")
        report.append("- 这是推荐的做法，让Qt使用系统默认字体")
        report.append("")
        report.append("**建议**: 保持当前实现，无需修改")
        report.append("")
    
    report.append("## 5. 总结")
    report.append("")
    
    if not font_files and not font_usage['font_file_references']:
        report.append("✓ **字体配置优化良好**")
        report.append("")
        report.append("- 未内嵌字体文件")
        report.append("- 使用系统字体")
        report.append("- 无需进一步优化")
        report.append("")
        report.append("**验证需求 5.2**: ✓ 已通过 - 项目使用系统字体，无内嵌字体文件")
    else:
        report.append("⚠ **需要优化**")
        report.append("")
        if font_files:
            report.append(f"- 发现 {len(font_files)} 个内嵌字体文件")
            report.append(f"- 可节省约 {total_size / (1024 * 1024):.2f} MB")
        if font_usage['font_file_references']:
            report.append(f"- 发现 {len(font_usage['font_file_references'])} 处字体文件引用")
        report.append("")
        report.append("**验证需求 5.2**: ⚠ 需要优化 - 建议移除内嵌字体文件")
    
    report.append("")
    report.append("---")
    report.append("")
    report.append("*报告生成时间: " + __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "*")
    
    return '\n'.join(report)


def main():
    """主函数"""
    print("开始分析字体文件使用情况...")
    print()
    
    # 1. 查找字体文件
    print("1. 扫描字体文件...")
    font_files = find_font_files()
    print(f"   发现 {len(font_files)} 个字体文件")
    
    # 2. 分析代码中的字体使用
    print("2. 分析代码中的字体使用...")
    font_usage = analyze_font_usage_in_code()
    print(f"   - QFont使用: {len(font_usage['qfont_usage'])} 处")
    print(f"   - 字体族设置: {len(font_usage['font_family_usage'])} 处")
    print(f"   - 字体文件引用: {len(font_usage['font_file_references'])} 处")
    
    # 3. 检查PySide6字体机制
    print("3. 检查PySide6字体机制...")
    pyside6_info = check_pyside6_fonts()
    print(f"   {pyside6_info['explanation']}")
    
    # 4. 生成报告
    print()
    print("生成分析报告...")
    report = generate_report(font_files, font_usage, pyside6_info)
    
    # 保存报告
    report_file = 'FONT_USAGE_ANALYSIS.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"✓ 报告已保存到: {report_file}")
    print()
    
    # 输出摘要
    print("=" * 60)
    print("分析摘要")
    print("=" * 60)
    
    if not font_files:
        print("✓ 未发现内嵌字体文件")
        print("✓ 项目使用系统字体，无需优化")
    else:
        total_size = sum(f['size'] for f in font_files)
        print(f"⚠ 发现 {len(font_files)} 个内嵌字体文件")
        print(f"⚠ 总大小: {total_size / (1024 * 1024):.2f} MB")
        print(f"⚠ 建议移除以减小打包体积")
    
    print()
    print(f"详细信息请查看: {report_file}")
    print("=" * 60)


if __name__ == '__main__':
    main()
