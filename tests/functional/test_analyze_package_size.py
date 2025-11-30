#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试打包体积分析工具

验证analyze_package_size.py的功能正确性
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# 设置UTF-8编码输出
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 导入被测试的模块
import analyze_package_size


def create_test_directory():
    """创建测试目录结构"""
    test_dir = tempfile.mkdtemp(prefix='test_package_')
    
    # 创建各种类型的测试文件
    test_files = [
        ('app.exe', 10 * 1024 * 1024),  # 10MB
        ('python311.dll', 5 * 1024 * 1024),  # 5MB
        ('Qt6Core.dll', 8 * 1024 * 1024),  # 8MB
        ('_ssl.pyd', 2 * 1024 * 1024),  # 2MB
        ('config.json', 1024),  # 1KB
        ('README.txt', 512),  # 512B
    ]
    
    # 创建PySide6子目录
    pyside_dir = os.path.join(test_dir, 'PySide6')
    os.makedirs(pyside_dir, exist_ok=True)
    
    pyside_files = [
        ('Qt6Widgets.dll', 6 * 1024 * 1024),  # 6MB
        ('Qt6Gui.dll', 7 * 1024 * 1024),  # 7MB
    ]
    
    # 创建models子目录
    models_dir = os.path.join(test_dir, 'models')
    os.makedirs(models_dir, exist_ok=True)
    
    model_files = [
        ('model_det.pdmodel', 3 * 1024 * 1024),  # 3MB
        ('model_rec.pdmodel', 4 * 1024 * 1024),  # 4MB
    ]
    
    # 写入测试文件
    for filename, size in test_files:
        filepath = os.path.join(test_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(b'0' * size)
    
    for filename, size in pyside_files:
        filepath = os.path.join(pyside_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(b'0' * size)
    
    for filename, size in model_files:
        filepath = os.path.join(models_dir, filename)
        with open(filepath, 'wb') as f:
            f.write(b'0' * size)
    
    return test_dir


def test_format_size():
    """测试文件大小格式化"""
    print("测试: format_size()")
    
    assert analyze_package_size.format_size(0) == "0.00 B"
    assert analyze_package_size.format_size(1024) == "1.00 KB"
    assert analyze_package_size.format_size(1024 * 1024) == "1.00 MB"
    assert analyze_package_size.format_size(1024 * 1024 * 1024) == "1.00 GB"
    
    print("  ✅ 文件大小格式化正确")


def test_get_file_extension():
    """测试文件扩展名获取"""
    print("测试: get_file_extension()")
    
    assert analyze_package_size.get_file_extension("test.dll") == ".dll"
    assert analyze_package_size.get_file_extension("test.pyd") == ".pyd"
    assert analyze_package_size.get_file_extension("test") == "(no extension)"
    assert analyze_package_size.get_file_extension("test.TXT") == ".txt"
    
    print("  ✅ 文件扩展名获取正确")


def test_analyze_directory():
    """测试目录分析功能"""
    print("测试: analyze_directory()")
    
    # 创建测试目录
    test_dir = create_test_directory()
    
    try:
        # 分析目录
        result = analyze_package_size.analyze_directory(test_dir)
        
        # 验证结果
        assert result is not None, "分析结果不应为None"
        assert 'files' in result, "结果应包含files字段"
        assert 'total_size' in result, "结果应包含total_size字段"
        assert 'total_count' in result, "结果应包含total_count字段"
        
        # 验证文件数量
        expected_count = 6 + 2 + 2  # 根目录6个 + PySide6 2个 + models 2个
        assert result['total_count'] == expected_count, \
            f"文件数量应为{expected_count}，实际为{result['total_count']}"
        
        # 验证总大小
        expected_size = (10 + 5 + 8 + 2 + 6 + 7 + 3 + 4) * 1024 * 1024 + 1024 + 512
        assert result['total_size'] == expected_size, \
            f"总大小应为{expected_size}，实际为{result['total_size']}"
        
        # 验证文件信息
        dll_files = [f for f in result['files'] if f['ext'] == '.dll']
        # 应该有4个DLL文件: python311.dll, Qt6Core.dll, Qt6Widgets.dll, Qt6Gui.dll
        assert len(dll_files) == 4, f"DLL文件应有4个，实际为{len(dll_files)}"
        
        pyd_files = [f for f in result['files'] if f['ext'] == '.pyd']
        assert len(pyd_files) == 1, f"PYD文件应有1个，实际为{len(pyd_files)}"
        
        model_files = [f for f in result['files'] if 'models' in f['path']]
        assert len(model_files) == 2, f"模型文件应有2个，实际为{len(model_files)}"
        
        print("  ✅ 目录分析功能正确")
        
    finally:
        # 清理测试目录
        shutil.rmtree(test_dir)


def test_generate_report():
    """测试报告生成功能"""
    print("测试: generate_report()")
    
    # 创建测试目录
    test_dir = create_test_directory()
    
    try:
        # 分析目录
        result = analyze_package_size.analyze_directory(test_dir)
        
        # 生成报告
        report_file = os.path.join(test_dir, 'test_report.md')
        analyze_package_size.generate_report(result, report_file)
        
        # 验证报告文件存在
        assert os.path.exists(report_file), "报告文件应该被创建"
        
        # 验证报告内容
        with open(report_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert '# 打包体积分析报告' in content, "报告应包含标题"
        assert '## 总体统计' in content, "报告应包含总体统计"
        assert '## 最大的20个文件' in content, "报告应包含最大文件列表"
        assert '## 按文件类型统计' in content, "报告应包含文件类型统计"
        assert '## 优化建议' in content, "报告应包含优化建议"
        
        # 验证报告包含关键数据
        assert '.dll' in content, "报告应包含DLL文件统计"
        assert 'Qt6Core.dll' in content, "报告应包含大型DLL文件"
        
        print("  ✅ 报告生成功能正确")
        
    finally:
        # 清理测试目录
        shutil.rmtree(test_dir)


def test_nonexistent_directory():
    """测试不存在的目录"""
    print("测试: 不存在的目录处理")
    
    result = analyze_package_size.analyze_directory('/nonexistent/path')
    assert result is None, "不存在的目录应返回None"
    
    print("  ✅ 不存在目录处理正确")


def main():
    """运行所有测试"""
    print("=" * 80)
    print("打包体积分析工具测试")
    print("=" * 80)
    print()
    
    try:
        test_format_size()
        test_get_file_extension()
        test_nonexistent_directory()
        test_analyze_directory()
        test_generate_report()
        
        print()
        print("=" * 80)
        print("✅ 所有测试通过!")
        print("=" * 80)
        
    except AssertionError as e:
        print()
        print("=" * 80)
        print(f"❌ 测试失败: {e}")
        print("=" * 80)
        sys.exit(1)
    except Exception as e:
        print()
        print("=" * 80)
        print(f"❌ 测试错误: {e}")
        print("=" * 80)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
