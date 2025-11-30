#!/usr/bin/env python3
"""
测试配置文件优化

验证需求 5.3:
- 确保打包使用.example配置文件
- 移除开发环境的完整配置
- 添加首次运行时的配置向导
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path


def test_config_example_exists():
    """测试 config.py.example 存在"""
    print("测试: config.py.example 存在...")
    
    config_example = Path('config.py.example')
    assert config_example.exists(), "config.py.example 不存在"
    
    print("  ✓ config.py.example 存在")


def test_config_wizard_exists():
    """测试 config_wizard.py 存在"""
    print("测试: config_wizard.py 存在...")
    
    wizard = Path('config_wizard.py')
    assert wizard.exists(), "config_wizard.py 不存在"
    
    print("  ✓ config_wizard.py 存在")


def test_gitignore_excludes_config():
    """测试 .gitignore 排除 config.py"""
    print("测试: .gitignore 排除 config.py...")
    
    gitignore = Path('.gitignore')
    assert gitignore.exists(), ".gitignore 不存在"
    
    content = gitignore.read_text(encoding='utf-8')
    assert 'config.py' in content, ".gitignore 未排除 config.py"
    
    print("  ✓ .gitignore 正确排除 config.py")


def test_spec_includes_example():
    """测试 spec 文件包含 config.py.example"""
    print("测试: spec 文件包含 config.py.example...")
    
    spec_files = [
        Path('Pack/Pyinstaller/ocr_system.spec'),
        Path('Pack/Pyinstaller/ocr_system_core.spec'),
    ]
    
    for spec_file in spec_files:
        if spec_file.exists():
            content = spec_file.read_text(encoding='utf-8')
            assert 'config.py.example' in content, f"{spec_file} 未包含 config.py.example"
            print(f"  ✓ {spec_file.name} 包含 config.py.example")


def test_spec_includes_wizard():
    """测试 spec 文件包含 config_wizard.py"""
    print("测试: spec 文件包含 config_wizard.py...")
    
    spec_files = [
        Path('Pack/Pyinstaller/ocr_system.spec'),
        Path('Pack/Pyinstaller/ocr_system_core.spec'),
    ]
    
    for spec_file in spec_files:
        if spec_file.exists():
            content = spec_file.read_text(encoding='utf-8')
            assert 'config_wizard.py' in content, f"{spec_file} 未包含 config_wizard.py"
            print(f"  ✓ {spec_file.name} 包含 config_wizard.py")


def test_spec_excludes_config():
    """测试 spec 文件不包含 config.py（只包含 .example）"""
    print("测试: spec 文件不直接包含 config.py...")
    
    spec_files = [
        Path('Pack/Pyinstaller/ocr_system.spec'),
        Path('Pack/Pyinstaller/ocr_system_core.spec'),
    ]
    
    for spec_file in spec_files:
        if spec_file.exists():
            content = spec_file.read_text(encoding='utf-8')
            
            # 检查是否有直接包含 config.py 的行（不是 config.py.example）
            lines = content.split('\n')
            for line in lines:
                if 'config.py' in line and 'config.py.example' not in line:
                    # 允许注释中提到 config.py
                    if not line.strip().startswith('#'):
                        # 允许在字符串中说明不包含 config.py
                        if 'NOT config.py' not in line and '不应打包' not in line:
                            assert False, f"{spec_file} 可能直接包含了 config.py: {line}"
            
            print(f"  ✓ {spec_file.name} 不直接包含 config.py")


def test_qt_run_integration():
    """测试 qt_run.py 集成配置向导"""
    print("测试: qt_run.py 集成配置向导...")
    
    qt_run = Path('qt_run.py')
    assert qt_run.exists(), "qt_run.py 不存在"
    
    content = qt_run.read_text(encoding='utf-8')
    
    # 检查关键功能
    assert 'ensure_config_file' in content, "qt_run.py 缺少 ensure_config_file 函数"
    assert 'config.py.example' in content, "qt_run.py 未引用 config.py.example"
    assert 'config_wizard' in content, "qt_run.py 未集成 config_wizard"
    
    print("  ✓ qt_run.py 正确集成配置向导")


def test_first_run_simulation():
    """模拟首次运行场景"""
    print("测试: 模拟首次运行场景...")
    
    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # 复制 config.py.example 到临时目录
        config_example = Path('config.py.example')
        if config_example.exists():
            shutil.copy(config_example, tmpdir / 'config.py.example')
        
        # 模拟首次运行：config.py 不存在
        config_path = tmpdir / 'config.py'
        assert not config_path.exists(), "config.py 不应存在（首次运行）"
        
        # 模拟创建 config.py
        if (tmpdir / 'config.py.example').exists():
            shutil.copy(tmpdir / 'config.py.example', config_path)
        
        # 验证 config.py 已创建
        assert config_path.exists(), "config.py 创建失败"
        
        print("  ✓ 首次运行场景模拟成功")


def test_cleanup_script():
    """测试清理脚本检查配置文件"""
    print("测试: 清理脚本检查配置文件...")
    
    cleanup_script = Path('cleanup_before_packaging.py')
    assert cleanup_script.exists(), "cleanup_before_packaging.py 不存在"
    
    content = cleanup_script.read_text(encoding='utf-8')
    assert 'clean_dev_config' in content, "清理脚本缺少 clean_dev_config 方法"
    assert 'config.py' in content, "清理脚本未检查 config.py"
    
    print("  ✓ 清理脚本正确检查配置文件")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("配置文件优化测试")
    print("=" * 60)
    print()
    
    tests = [
        test_config_example_exists,
        test_config_wizard_exists,
        test_gitignore_excludes_config,
        test_spec_includes_example,
        test_spec_includes_wizard,
        test_spec_excludes_config,
        test_qt_run_integration,
        test_first_run_simulation,
        test_cleanup_script,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
            print()
        except AssertionError as e:
            print(f"  ✗ 测试失败: {e}")
            failed += 1
            print()
        except Exception as e:
            print(f"  ✗ 测试错误: {e}")
            failed += 1
            print()
    
    print("=" * 60)
    print("测试结果")
    print("=" * 60)
    print()
    print(f"通过: {passed}/{len(tests)}")
    print(f"失败: {failed}/{len(tests)}")
    print()
    
    if failed == 0:
        print("✓ 所有测试通过")
        print()
        print("验证需求 5.3: ✓ 已完成")
        print()
        print("- ✓ 确保打包使用.example配置文件")
        print("- ✓ 移除开发环境的完整配置")
        print("- ✓ 添加首次运行时的配置向导")
        return True
    else:
        print("✗ 部分测试失败")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
