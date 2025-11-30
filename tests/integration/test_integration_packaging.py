#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试 - 打包流程测试

测试优化后的打包流程，生成体积分析报告，记录打包效果。
验证需求: 所有

使用方法:
    python test_integration_packaging.py
"""

import os
import sys
import time
import subprocess
import json
from pathlib import Path
from collections import defaultdict


def format_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def run_cleanup():
    """运行打包前清理"""
    print("=" * 80)
    print("步骤 1: 执行打包前清理")
    print("=" * 80)
    print()
    
    try:
        result = subprocess.run(
            [sys.executable, 'cleanup_before_packaging.py', '--auto'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ 清理完成")
            print(result.stdout)
        else:
            print("⚠️  清理脚本返回非零状态码")
            print(result.stderr)
        
        print()
        return True
        
    except subprocess.TimeoutExpired:
        print("❌ 清理超时")
        return False
    except Exception as e:
        print(f"❌ 清理失败: {e}")
        return False


def run_packaging(spec_file='Pack/Pyinstaller/ocr_system_core.spec'):
    """运行PyInstaller打包"""
    print("=" * 80)
    print("步骤 2: 执行PyInstaller打包")
    print("=" * 80)
    print()
    
    if not os.path.exists(spec_file):
        print(f"❌ Spec文件不存在: {spec_file}")
        return False
    
    print(f"使用spec文件: {spec_file}")
    print("开始打包...")
    print()
    
    start_time = time.time()
    
    try:
        # 运行PyInstaller
        result = subprocess.run(
            [sys.executable, '-m', 'PyInstaller', '--clean', spec_file],
            capture_output=True,
            text=True,
            timeout=600  # 10分钟超时
        )
        
        elapsed_time = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ 打包成功 (耗时: {elapsed_time:.1f}秒)")
            print()
            return True
        else:
            print(f"❌ 打包失败 (耗时: {elapsed_time:.1f}秒)")
            print()
            print("错误输出:")
            print(result.stderr[-2000:])  # 只显示最后2000字符
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ 打包超时 (>10分钟)")
        return False
    except Exception as e:
        print(f"❌ 打包异常: {e}")
        return False


def analyze_package_size(dist_path='Pack/Pyinstaller/dist/OCR-System-Core'):
    """分析打包后的体积"""
    print("=" * 80)
    print("步骤 3: 分析打包体积")
    print("=" * 80)
    print()
    
    if not os.path.exists(dist_path):
        print(f"❌ 打包目录不存在: {dist_path}")
        return None
    
    print(f"分析目录: {dist_path}")
    print()
    
    # 收集文件信息
    files_info = []
    total_size = 0
    
    for root, dirs, files in os.walk(dist_path):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                size = os.path.getsize(file_path)
                rel_path = os.path.relpath(file_path, dist_path)
                ext = Path(file).suffix.lower() or '(no ext)'
                
                files_info.append({
                    'path': rel_path,
                    'size': size,
                    'ext': ext,
                })
                
                total_size += size
            except OSError:
                pass
    
    # 统计信息
    print(f"📊 总体统计:")
    print(f"   文件总数: {len(files_info)}")
    print(f"   总体积: {format_size(total_size)}")
    print()
    
    # 按类型统计
    type_stats = defaultdict(lambda: {'count': 0, 'size': 0})
    for f in files_info:
        type_stats[f['ext']]['count'] += 1
        type_stats[f['ext']]['size'] += f['size']
    
    print("📁 按文件类型统计 (前10):")
    sorted_types = sorted(type_stats.items(), key=lambda x: x[1]['size'], reverse=True)
    for ext, stats in sorted_types[:10]:
        percentage = (stats['size'] / total_size * 100) if total_size > 0 else 0
        print(f"   {ext:15s} {stats['count']:4d}个  {format_size(stats['size']):>10s}  ({percentage:5.1f}%)")
    print()
    
    # 最大文件
    print("📦 最大的10个文件:")
    sorted_files = sorted(files_info, key=lambda x: x['size'], reverse=True)
    for f in sorted_files[:10]:
        print(f"   {format_size(f['size']):>10s}  {f['path']}")
    print()
    
    return {
        'total_size': total_size,
        'total_count': len(files_info),
        'files': files_info,
        'type_stats': dict(type_stats),
    }


def check_optimization_goals(analysis_result):
    """检查优化目标是否达成"""
    print("=" * 80)
    print("步骤 4: 验证优化目标")
    print("=" * 80)
    print()
    
    if not analysis_result:
        print("❌ 无法验证 - 缺少分析结果")
        return False
    
    total_size = analysis_result['total_size']
    total_size_mb = total_size / (1024 * 1024)
    
    goals = {
        '核心程序体积 < 100MB': total_size_mb < 100,
        '核心程序体积 < 250MB (含RapidOCR)': total_size_mb < 250,
    }
    
    all_passed = True
    
    for goal, passed in goals.items():
        status = "✅" if passed else "❌"
        print(f"{status} {goal}")
        if not passed:
            all_passed = False
    
    print()
    print(f"实际体积: {format_size(total_size)} ({total_size_mb:.1f} MB)")
    print()
    
    return all_passed


def generate_report(analysis_result, output_file='INTEGRATION_TEST_PACKAGING_REPORT.md'):
    """生成测试报告"""
    print("=" * 80)
    print("步骤 5: 生成测试报告")
    print("=" * 80)
    print()
    
    if not analysis_result:
        print("❌ 无法生成报告 - 缺少分析结果")
        return
    
    total_size = analysis_result['total_size']
    total_count = analysis_result['total_count']
    files = analysis_result['files']
    type_stats = analysis_result['type_stats']
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 集成测试报告 - 打包流程\n\n")
        f.write(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 测试概述\n\n")
        f.write("本测试验证优化后的打包流程，包括:\n")
        f.write("1. 打包前清理\n")
        f.write("2. PyInstaller打包\n")
        f.write("3. 体积分析\n")
        f.write("4. 优化目标验证\n\n")
        
        f.write("## 打包结果\n\n")
        f.write(f"- **文件总数**: {total_count}\n")
        f.write(f"- **总体积**: {format_size(total_size)} ({total_size / (1024 * 1024):.1f} MB)\n\n")
        
        f.write("## 优化目标验证\n\n")
        total_size_mb = total_size / (1024 * 1024)
        
        if total_size_mb < 100:
            f.write("✅ **核心程序体积 < 100MB** - 达成\n\n")
        elif total_size_mb < 250:
            f.write("✅ **核心程序体积 < 250MB (含RapidOCR)** - 达成\n\n")
        else:
            f.write("❌ **体积优化目标** - 未达成\n\n")
        
        f.write("## 文件类型统计\n\n")
        f.write("| 文件类型 | 数量 | 总大小 | 占比 |\n")
        f.write("|----------|------|--------|------|\n")
        
        sorted_types = sorted(type_stats.items(), key=lambda x: x[1]['size'], reverse=True)
        for ext, stats in sorted_types[:15]:
            percentage = (stats['size'] / total_size * 100) if total_size > 0 else 0
            f.write(f"| {ext} | {stats['count']} | {format_size(stats['size'])} | {percentage:.2f}% |\n")
        
        f.write("\n## 最大文件 (前20)\n\n")
        f.write("| 大小 | 文件路径 |\n")
        f.write("|------|----------|\n")
        
        sorted_files = sorted(files, key=lambda x: x['size'], reverse=True)
        for f_info in sorted_files[:20]:
            f.write(f"| {format_size(f_info['size'])} | {f_info['path']} |\n")
        
        f.write("\n## 优化建议\n\n")
        
        # Qt文件
        qt_files = [f for f in files if 'PySide6' in f['path'] or 'Qt6' in f['path']]
        if qt_files:
            qt_total = sum(f['size'] for f in qt_files)
            qt_percentage = (qt_total / total_size * 100) if total_size > 0 else 0
            f.write(f"### Qt/PySide6 文件\n\n")
            f.write(f"- 文件数: {len(qt_files)}\n")
            f.write(f"- 总大小: {format_size(qt_total)} ({qt_percentage:.1f}%)\n")
            f.write(f"- 建议: 继续排除未使用的Qt模块\n\n")
        
        # 模型文件
        model_files = [f for f in files if 'models' in f['path'].lower()]
        if model_files:
            model_total = sum(f['size'] for f in model_files)
            model_percentage = (model_total / total_size * 100) if total_size > 0 else 0
            f.write(f"### OCR模型文件\n\n")
            f.write(f"- 文件数: {len(model_files)}\n")
            f.write(f"- 总大小: {format_size(model_total)} ({model_percentage:.1f}%)\n")
            f.write(f"- 建议: 考虑模型压缩或可选下载\n\n")
        
        # DLL文件
        dll_files = [f for f in files if f['ext'] == '.dll']
        if dll_files:
            dll_total = sum(f['size'] for f in dll_files)
            dll_percentage = (dll_total / total_size * 100) if total_size > 0 else 0
            large_dlls = [f for f in dll_files if f['size'] > 5 * 1024 * 1024]
            
            f.write(f"### DLL文件\n\n")
            f.write(f"- 文件数: {len(dll_files)}\n")
            f.write(f"- 总大小: {format_size(dll_total)} ({dll_percentage:.1f}%)\n")
            
            if large_dlls:
                f.write(f"- 大型DLL (>5MB): {len(large_dlls)}个\n")
                for dll in sorted(large_dlls, key=lambda x: x['size'], reverse=True)[:5]:
                    f.write(f"  - {format_size(dll['size'])} - {dll['path']}\n")
            f.write("\n")
    
    print(f"✅ 报告已保存: {output_file}")
    print()


def main():
    """主测试流程"""
    print()
    print("=" * 80)
    print("集成测试 - 打包流程")
    print("=" * 80)
    print()
    
    # 步骤1: 清理
    if not run_cleanup():
        print("⚠️  清理失败，但继续执行")
        print()
    
    # 步骤2: 打包
    if not run_packaging():
        print()
        print("=" * 80)
        print("❌ 测试失败 - 打包失败")
        print("=" * 80)
        print()
        sys.exit(1)
    
    # 步骤3: 分析
    analysis_result = analyze_package_size()
    
    if not analysis_result:
        print()
        print("=" * 80)
        print("❌ 测试失败 - 无法分析打包结果")
        print("=" * 80)
        print()
        sys.exit(1)
    
    # 步骤4: 验证目标
    goals_met = check_optimization_goals(analysis_result)
    
    # 步骤5: 生成报告
    generate_report(analysis_result)
    
    # 总结
    print("=" * 80)
    if goals_met:
        print("✅ 测试通过 - 所有优化目标达成")
    else:
        print("⚠️  测试完成 - 部分优化目标未达成")
    print("=" * 80)
    print()
    
    return 0 if goals_met else 1


if __name__ == '__main__':
    sys.exit(main())
