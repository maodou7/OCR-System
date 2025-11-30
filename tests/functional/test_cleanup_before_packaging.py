#!/usr/bin/env python3
"""
测试打包前清理脚本

验证需求: 5.4, 5.5
"""

import os
import shutil
import tempfile
from pathlib import Path
import sys

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from cleanup_before_packaging import PackagingCleaner


def test_clean_pycache():
    """测试清理 __pycache__ 目录"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建测试目录结构
        pycache_dir = Path(tmpdir) / 'test_module' / '__pycache__'
        pycache_dir.mkdir(parents=True)
        
        # 创建测试文件
        test_file = pycache_dir / 'test.pyc'
        test_file.write_text('test')
        
        # 执行清理
        cleaner = PackagingCleaner(tmpdir)
        cleaner.clean_pycache()
        
        # 验证
        assert not pycache_dir.exists(), "__pycache__ 目录应该被删除"
        print("✓ test_clean_pycache 通过")


def test_clean_pyc_files():
    """测试清理 .pyc 文件"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建测试文件
        pyc_file = Path(tmpdir) / 'test.pyc'
        pyc_file.write_text('test')
        
        # 执行清理
        cleaner = PackagingCleaner(tmpdir)
        cleaner.clean_pyc_files()
        
        # 验证
        assert not pyc_file.exists(), ".pyc 文件应该被删除"
        print("✓ test_clean_pyc_files 通过")


def test_clean_cache_db():
    """测试清理缓存数据库"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建测试缓存目录
        cache_dir = Path(tmpdir) / '.ocr_cache'
        cache_dir.mkdir()
        db_file = cache_dir / 'cache.db'
        db_file.write_text('test')
        
        # 创建测试 .db 文件
        test_db = Path(tmpdir) / 'test.db'
        test_db.write_text('test')
        
        # 执行清理
        cleaner = PackagingCleaner(tmpdir)
        cleaner.clean_cache_db()
        
        # 验证
        assert not cache_dir.exists(), "缓存目录应该被删除"
        assert not test_db.exists(), ".db 文件应该被删除"
        print("✓ test_clean_cache_db 通过")


def test_clean_build_artifacts():
    """测试清理构建产物"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建测试构建目录
        build_dir = Path(tmpdir) / 'build'
        build_dir.mkdir()
        (build_dir / 'test.txt').write_text('test')
        
        dist_dir = Path(tmpdir) / 'dist'
        dist_dir.mkdir()
        (dist_dir / 'test.txt').write_text('test')
        
        # 执行清理
        cleaner = PackagingCleaner(tmpdir)
        cleaner.clean_build_artifacts()
        
        # 验证
        assert not build_dir.exists(), "build 目录应该被删除"
        assert not dist_dir.exists(), "dist 目录应该被删除"
        print("✓ test_clean_build_artifacts 通过")


def test_clean_temp_files():
    """测试清理临时文件"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建测试临时文件
        tmp_file = Path(tmpdir) / 'test.tmp'
        tmp_file.write_text('test')
        
        log_file = Path(tmpdir) / 'test.log'
        log_file.write_text('test')
        
        bak_file = Path(tmpdir) / 'test.bak'
        bak_file.write_text('test')
        
        # 执行清理
        cleaner = PackagingCleaner(tmpdir)
        cleaner.clean_temp_files()
        
        # 验证
        assert not tmp_file.exists(), ".tmp 文件应该被删除"
        assert not log_file.exists(), ".log 文件应该被删除"
        assert not bak_file.exists(), ".bak 文件应该被删除"
        print("✓ test_clean_temp_files 通过")


def test_generate_report():
    """测试生成清理报告"""
    with tempfile.TemporaryDirectory() as tmpdir:
        cleaner = PackagingCleaner(tmpdir)
        
        # 添加一些清理项
        cleaner.cleaned_items = ['test1', 'test2']
        cleaner.total_size_freed = 1024 * 1024  # 1 MB
        
        # 生成报告
        report = cleaner.generate_report()
        
        # 验证
        assert '# 打包前清理报告' in report, "报告应包含标题"
        assert '清理项目数' in report, "报告应包含清理项目数"
        assert '释放空间' in report, "报告应包含释放空间"
        assert '需求 5.4, 5.5' in report, "报告应引用需求"
        print("✓ test_generate_report 通过")


def test_full_cleanup():
    """测试完整清理流程"""
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建各种测试文件
        test_dir = Path(tmpdir)
        
        # __pycache__
        pycache = test_dir / '__pycache__'
        pycache.mkdir()
        (pycache / 'test.pyc').write_text('test')
        
        # .pyc 文件
        (test_dir / 'module.pyc').write_text('test')
        
        # 缓存数据库
        (test_dir / 'cache.db').write_text('test')
        
        # 构建产物
        build = test_dir / 'build'
        build.mkdir()
        (build / 'output.txt').write_text('test')
        
        # 临时文件
        (test_dir / 'temp.tmp').write_text('test')
        
        # 执行完整清理
        cleaner = PackagingCleaner(tmpdir)
        cleaner.clean_pycache()
        cleaner.clean_pyc_files()
        cleaner.clean_cache_db()
        cleaner.clean_build_artifacts()
        cleaner.clean_temp_files()
        
        # 验证所有文件都被清理
        assert not pycache.exists(), "__pycache__ 应被删除"
        assert not (test_dir / 'module.pyc').exists(), ".pyc 文件应被删除"
        assert not (test_dir / 'cache.db').exists(), ".db 文件应被删除"
        assert not build.exists(), "build 目录应被删除"
        assert not (test_dir / 'temp.tmp').exists(), ".tmp 文件应被删除"
        
        # 验证清理统计
        assert len(cleaner.cleaned_items) > 0, "应该有清理项"
        assert cleaner.total_size_freed > 0, "应该释放了空间"
        
        print("✓ test_full_cleanup 通过")


def main():
    """运行所有测试"""
    print("=" * 60)
    print("测试打包前清理脚本")
    print("=" * 60)
    print()
    
    tests = [
        test_clean_pycache,
        test_clean_pyc_files,
        test_clean_cache_db,
        test_clean_build_artifacts,
        test_clean_temp_files,
        test_generate_report,
        test_full_cleanup,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} 失败: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} 错误: {e}")
            failed += 1
    
    print()
    print("=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    if failed == 0:
        print()
        print("✓ 所有测试通过!")
        print()
        print("验证需求:")
        print("  - 需求 5.4: ✓ 清理缓存和临时文件")
        print("  - 需求 5.5: ✓ 清理构建产物")
        return 0
    else:
        return 1


if __name__ == '__main__':
    sys.exit(main())
