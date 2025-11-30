#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
打包体积分析工具

分析PyInstaller打包后的dist目录，生成详细的体积分析报告。
识别大文件，按文件类型、大小排序，提供优化建议。

使用方法:
    python analyze_package_size.py [dist_path]
    
    默认分析: Pack/Pyinstaller/dist/OCR-System/
"""

import os
import sys
from pathlib import Path
from collections import defaultdict


def format_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def get_file_extension(file_path):
    """获取文件扩展名"""
    ext = Path(file_path).suffix.lower()
    if not ext:
        return '(no extension)'
    return ext


def analyze_directory(dist_path):
    """分析目录中的所有文件"""
    if not os.path.exists(dist_path):
        print(f"错误: 目录不存在: {dist_path}")
        return None
    
    print(f"正在分析: {dist_path}")
    print()
    
    # 收集所有文件信息
    files_info = []
    total_size = 0
    
    for root, dirs, files in os.walk(dist_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                rel_path = os.path.relpath(file_path, dist_path)
                
                files_info.append({
                    'path': rel_path,
                    'size': size,
                    'ext': get_file_extension(file),
                })
                
                total_size += size
            except OSError as e:
                print(f"警告: 无法读取文件 {file_path}: {e}")
    
    return {
        'files': files_info,
        'total_size': total_size,
        'total_count': len(files_info),
    }


def generate_report(analysis_result, output_file='package_size_report.md'):
    """生成分析报告"""
    if not analysis_result:
        return
    
    files = analysis_result['files']
    total_size = analysis_result['total_size']
    total_count = analysis_result['total_count']
    
    print("=" * 80)
    print("打包体积分析报告")
    print("=" * 80)
    print()
    
    print(f"📊 总体统计:")
    print(f"   文件总数: {total_count}")
    print(f"   总体积: {format_size(total_size)}")
    print()
    
    # 按大小排序（前20个最大文件）
    print("=" * 80)
    print("📦 最大的20个文件")
    print("=" * 80)
    print()
    
    sorted_by_size = sorted(files, key=lambda x: x['size'], reverse=True)
    
    print(f"{'大小':>12s}  {'文件路径'}")
    print("-" * 80)
    
    for i, file_info in enumerate(sorted_by_size[:20], 1):
        size_str = format_size(file_info['size'])
        print(f"{size_str:>12s}  {file_info['path']}")
    
    print()
    
    # 按文件类型统计
    print("=" * 80)
    print("📁 按文件类型统计")
    print("=" * 80)
    print()
    
    type_stats = defaultdict(lambda: {'count': 0, 'size': 0, 'files': []})
    
    for file_info in files:
        ext = file_info['ext']
        type_stats[ext]['count'] += 1
        type_stats[ext]['size'] += file_info['size']
        type_stats[ext]['files'].append(file_info)
    
    # 按总大小排序
    sorted_types = sorted(type_stats.items(), key=lambda x: x[1]['size'], reverse=True)
    
    print(f"{'文件类型':20s} {'数量':>8s} {'总大小':>12s} {'占比':>8s}")
    print("-" * 80)
    
    for ext, stats in sorted_types:
        count = stats['count']
        size = stats['size']
        percentage = (size / total_size * 100) if total_size > 0 else 0
        
        print(f"{ext:20s} {count:8d} {format_size(size):>12s} {percentage:7.2f}%")
    
    print()
    
    # 识别可优化的大文件
    print("=" * 80)
    print("💡 优化建议")
    print("=" * 80)
    print()
    
    # 1. 大型DLL文件
    large_dlls = [f for f in files if f['ext'] == '.dll' and f['size'] > 5 * 1024 * 1024]
    if large_dlls:
        print("1. 大型DLL文件 (>5MB):")
        for dll in sorted(large_dlls, key=lambda x: x['size'], reverse=True)[:10]:
            print(f"   • {format_size(dll['size']):>10s}  {dll['path']}")
        print()
    
    # 2. 大型PYD文件
    large_pyds = [f for f in files if f['ext'] == '.pyd' and f['size'] > 1 * 1024 * 1024]
    if large_pyds:
        print("2. 大型PYD文件 (>1MB):")
        for pyd in sorted(large_pyds, key=lambda x: x['size'], reverse=True)[:10]:
            print(f"   • {format_size(pyd['size']):>10s}  {pyd['path']}")
        print()
    
    # 3. Qt插件
    qt_plugins = [f for f in files if 'PySide6' in f['path'] or 'Qt6' in f['path']]
    if qt_plugins:
        qt_total = sum(f['size'] for f in qt_plugins)
        print(f"3. Qt/PySide6相关文件:")
        print(f"   总数: {len(qt_plugins)}")
        print(f"   总大小: {format_size(qt_total)}")
        print(f"   占比: {(qt_total / total_size * 100):.2f}%")
        
        # 按子目录分组
        qt_dirs = defaultdict(lambda: {'count': 0, 'size': 0})
        for f in qt_plugins:
            dir_name = Path(f['path']).parts[0] if Path(f['path']).parts else 'root'
            qt_dirs[dir_name]['count'] += 1
            qt_dirs[dir_name]['size'] += f['size']
        
        print("   按目录分组:")
        for dir_name, stats in sorted(qt_dirs.items(), key=lambda x: x[1]['size'], reverse=True):
            print(f"     • {dir_name:30s} {stats['count']:4d}个文件  {format_size(stats['size']):>10s}")
        print()
    
    # 4. 模型文件
    model_files = [f for f in files if 'models' in f['path'].lower()]
    if model_files:
        model_total = sum(f['size'] for f in model_files)
        print(f"4. OCR模型文件:")
        print(f"   总数: {len(model_files)}")
        print(f"   总大小: {format_size(model_total)}")
        print(f"   占比: {(model_total / total_size * 100):.2f}%")
        print()
    
    # 5. Python库
    python_libs = [f for f in files if f['ext'] in ['.pyc', '.pyd', '.py']]
    if python_libs:
        py_total = sum(f['size'] for f in python_libs)
        print(f"5. Python库文件:")
        print(f"   总数: {len(python_libs)}")
        print(f"   总大小: {format_size(py_total)}")
        print(f"   占比: {(py_total / total_size * 100):.2f}%")
        print()
    
    # 保存报告
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 打包体积分析报告\n\n")
        
        f.write("## 总体统计\n\n")
        f.write(f"- 文件总数: {total_count}\n")
        f.write(f"- 总体积: {format_size(total_size)}\n\n")
        
        f.write("## 最大的20个文件\n\n")
        f.write("| 大小 | 文件路径 |\n")
        f.write("|------|----------|\n")
        for file_info in sorted_by_size[:20]:
            f.write(f"| {format_size(file_info['size'])} | {file_info['path']} |\n")
        f.write("\n")
        
        f.write("## 按文件类型统计\n\n")
        f.write("| 文件类型 | 数量 | 总大小 | 占比 |\n")
        f.write("|----------|------|--------|------|\n")
        for ext, stats in sorted_types:
            count = stats['count']
            size = stats['size']
            percentage = (size / total_size * 100) if total_size > 0 else 0
            f.write(f"| {ext} | {count} | {format_size(size)} | {percentage:.2f}% |\n")
        f.write("\n")
        
        f.write("## 优化建议\n\n")
        
        if large_dlls:
            f.write("### 大型DLL文件\n\n")
            for dll in sorted(large_dlls, key=lambda x: x['size'], reverse=True)[:10]:
                f.write(f"- {format_size(dll['size'])} - {dll['path']}\n")
            f.write("\n")
        
        if qt_plugins:
            f.write("### Qt/PySide6优化\n\n")
            f.write(f"- 总大小: {format_size(qt_total)}\n")
            f.write(f"- 占比: {(qt_total / total_size * 100):.2f}%\n")
            f.write("- 建议: 排除未使用的Qt模块和插件\n\n")
        
        if model_files:
            f.write("### OCR模型优化\n\n")
            f.write(f"- 总大小: {format_size(model_total)}\n")
            f.write(f"- 占比: {(model_total / total_size * 100):.2f}%\n")
            f.write("- 建议: 移除非中英文模型，或设为可选下载\n\n")
    
    print(f"✅ 报告已保存到: {output_file}")
    print()


def main():
    # 获取dist路径
    if len(sys.argv) > 1:
        dist_path = sys.argv[1]
    else:
        # 默认路径
        dist_path = 'Pack/Pyinstaller/dist/OCR-System'
    
    # 检查路径是否存在
    if not os.path.exists(dist_path):
        print(f"❌ 错误: 目录不存在: {dist_path}")
        print()
        print("请先执行打包:")
        print("  cd Pack/Pyinstaller")
        print("  python -m PyInstaller ocr_system.spec")
        print()
        print("或指定其他dist目录:")
        print(f"  python {sys.argv[0]} <dist_path>")
        sys.exit(1)
    
    # 分析目录
    result = analyze_directory(dist_path)
    
    if result:
        # 生成报告
        generate_report(result)


if __name__ == '__main__':
    main()
