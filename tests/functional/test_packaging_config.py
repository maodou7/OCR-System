# -*- coding: utf-8 -*-
"""
打包配置属性测试

**Feature: ocr-system-optimization, Property 5: 打包排除完整性**

对于任何打包后的dist目录，不应包含测试文件（test_*.py）、文档文件（*.md, *.txt除外必需文件）、
示例文件（examples/）、缓存文件（__pycache__, *.pyc, *.db）。

验证需求: 4.1, 5.4, 5.5
"""

import os
import sys
import unittest
from pathlib import Path
import fnmatch


class TestPackagingExclusionProperty(unittest.TestCase):
    """
    属性5: 打包排除完整性
    
    对于任何打包后的dist目录，不应包含测试文件（test_*.py）、
    文档文件（*.md, *.txt除外必需文件）、示例文件（examples/）、
    缓存文件（__pycache__, *.pyc, *.db）。
    """
    
    def setUp(self):
        """设置测试环境"""
        # 默认的dist目录路径
        self.dist_paths = [
            'Pack/Pyinstaller/dist/OCR-System',
            'dist/OCR-System',  # 备用路径
        ]
        
        # 找到存在的dist目录
        self.dist_path = None
        for path in self.dist_paths:
            if os.path.exists(path):
                self.dist_path = path
                break
        
        # 如果没有找到dist目录，跳过测试
        if not self.dist_path:
            self.skipTest("未找到打包后的dist目录，请先执行打包")
    
    def get_all_files(self, directory):
        """获取目录下的所有文件"""
        files = []
        for root, dirs, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                rel_path = os.path.relpath(file_path, directory)
                files.append({
                    'name': filename,
                    'path': file_path,
                    'rel_path': rel_path,
                    'dir': os.path.dirname(rel_path)
                })
        return files
    
    def test_no_test_files(self):
        """
        测试不包含测试文件
        
        验证：dist目录不应包含test_*.py文件
        """
        files = self.get_all_files(self.dist_path)
        
        test_files = []
        test_patterns = ['test_*.py', '*_test.py', 'test*.py']
        
        for file_info in files:
            for pattern in test_patterns:
                if fnmatch.fnmatch(file_info['name'].lower(), pattern):
                    test_files.append(file_info)
                    break
        
        self.assertEqual(len(test_files), 0,
                        f"发现测试文件: {[f['rel_path'] for f in test_files]}")
    
    def test_no_cache_files(self):
        """
        测试不包含缓存文件
        
        验证：dist目录不应包含__pycache__目录和.pyc文件
        """
        files = self.get_all_files(self.dist_path)
        
        cache_files = []
        cache_patterns = ['*.pyc', '*.pyo']
        
        for file_info in files:
            # 检查文件名
            for pattern in cache_patterns:
                if fnmatch.fnmatch(file_info['name'], pattern):
                    cache_files.append(file_info)
                    break
            
            # 检查目录路径中是否包含__pycache__
            if '__pycache__' in file_info['rel_path']:
                cache_files.append(file_info)
        
        self.assertEqual(len(cache_files), 0,
                        f"发现缓存文件: {[f['rel_path'] for f in cache_files]}")

    def test_no_development_files(self):
        """
        测试不包含开发文件
        
        验证：dist目录不应包含开发相关文件
        """
        files = self.get_all_files(self.dist_path)
        
        dev_files = []
        dev_patterns = [
            '*.spec',           # PyInstaller spec文件
            'build.py',         # 构建脚本
            'setup.py',         # 安装脚本
            'requirements*.txt', # 依赖文件（除非必需）
            '.git*',            # Git文件
            '.vscode',          # VS Code配置
            '.idea',            # PyCharm配置
            '*.log',            # 日志文件
            'debug*',           # 调试文件
        ]
        
        for file_info in files:
            for pattern in dev_patterns:
                if fnmatch.fnmatch(file_info['name'], pattern):
                    dev_files.append(file_info)
                    break
        
        # 过滤掉可能需要的文件
        allowed_files = ['requirements.txt']  # 如果程序需要检查依赖
        dev_files = [f for f in dev_files if f['name'] not in allowed_files]
        
        self.assertEqual(len(dev_files), 0,
                        f"发现开发文件: {[f['rel_path'] for f in dev_files]}")
    
    def test_no_documentation_files(self):
        """
        测试不包含非必需的文档文件
        
        验证：dist目录不应包含大部分文档文件（保留必需的README等）
        """
        files = self.get_all_files(self.dist_path)
        
        doc_files = []
        doc_patterns = [
            '*.md',
            '*.rst',
            '*.txt',
            'CHANGELOG*',
            'HISTORY*',
            'AUTHORS*',
            'CONTRIBUTORS*',
            'LICENSE*',
            'COPYING*',
        ]
        
        for file_info in files:
            for pattern in doc_patterns:
                if fnmatch.fnmatch(file_info['name'], pattern):
                    doc_files.append(file_info)
                    break
        
        # 过滤掉必需的文档文件
        allowed_docs = [
            'README.md', 'readme.txt', 'README.txt',
            'config.py.example',  # 配置示例
            'LICENSE', 'LICENSE.txt',  # 许可证（如果需要）
        ]
        
        unnecessary_docs = []
        for f in doc_files:
            if f['name'] not in allowed_docs:
                unnecessary_docs.append(f)
        
        # 允许少量必需的文档文件
        self.assertLessEqual(len(unnecessary_docs), 2,
                           f"发现过多非必需文档文件: {[f['rel_path'] for f in unnecessary_docs]}")
    
    def test_no_example_directories(self):
        """
        测试不包含示例目录
        
        验证：dist目录不应包含examples、samples、demo等目录
        """
        example_dirs = []
        example_dir_names = ['examples', 'example', 'samples', 'sample', 
                           'demo', 'demos', 'tutorial', 'tutorials']
        
        for root, dirs, files in os.walk(self.dist_path):
            for dir_name in dirs:
                if dir_name.lower() in example_dir_names:
                    rel_path = os.path.relpath(os.path.join(root, dir_name), self.dist_path)
                    example_dirs.append(rel_path)
        
        self.assertEqual(len(example_dirs), 0,
                        f"发现示例目录: {example_dirs}")
    
    def test_no_database_files(self):
        """
        测试不包含开发时的数据库文件
        
        验证：dist目录不应包含开发时的.db文件
        """
        files = self.get_all_files(self.dist_path)
        
        db_files = []
        db_patterns = ['*.db', '*.sqlite', '*.sqlite3']
        
        for file_info in files:
            for pattern in db_patterns:
                if fnmatch.fnmatch(file_info['name'], pattern):
                    # 检查是否是开发时的缓存文件
                    if any(keyword in file_info['name'].lower() 
                          for keyword in ['cache', 'temp', 'test', 'debug']):
                        db_files.append(file_info)
        
        self.assertEqual(len(db_files), 0,
                        f"发现开发时的数据库文件: {[f['rel_path'] for f in db_files]}")
    
    def test_no_temporary_files(self):
        """
        测试不包含临时文件
        
        验证：dist目录不应包含临时文件和构建产物
        """
        files = self.get_all_files(self.dist_path)
        
        temp_files = []
        temp_patterns = [
            '*.tmp', '*.temp', '*~', '*.bak', '*.orig',
            '*.swp', '*.swo',  # Vim临时文件
            '.DS_Store',       # macOS文件
            'Thumbs.db',       # Windows缩略图
            '*.pid',           # 进程ID文件
            '*.lock',          # 锁文件
        ]
        
        for file_info in files:
            for pattern in temp_patterns:
                if fnmatch.fnmatch(file_info['name'], pattern):
                    temp_files.append(file_info)
                    break
        
        self.assertEqual(len(temp_files), 0,
                        f"发现临时文件: {[f['rel_path'] for f in temp_files]}")


class TestUPXConfiguration(unittest.TestCase):
    """
    UPX压缩配置测试
    
    验证需求: 4.4
    """
    
    def test_upx_enabled_in_spec(self):
        """
        测试spec文件中启用了UPX压缩
        
        验证：spec文件应该包含upx=True配置
        """
        spec_path = 'Pack/Pyinstaller/ocr_system.spec'
        
        if not os.path.exists(spec_path):
            self.skipTest(f"未找到spec文件: {spec_path}")
        
        with open(spec_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查EXE中的upx配置
        self.assertIn('upx=True', content,
                     "spec文件中未启用UPX压缩")
        
        # 检查是否定义了upx_exclude_list
        self.assertIn('upx_exclude_list', content,
                     "spec文件中未定义upx_exclude_list")
    
    def test_upx_exclude_list_configured(self):
        """
        测试UPX排除列表已正确配置
        
        验证：spec文件应该包含合理的upx_exclude配置
        """
        spec_path = 'Pack/Pyinstaller/ocr_system.spec'
        
        if not os.path.exists(spec_path):
            self.skipTest(f"未找到spec文件: {spec_path}")
        
        with open(spec_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查关键的排除项
        critical_excludes = [
            'Qt6Core.dll',      # Qt核心库
            'python3.dll',      # Python运行时
            'vcruntime',        # VC运行时
        ]
        
        for exclude in critical_excludes:
            self.assertIn(exclude, content,
                         f"upx_exclude_list中缺少关键排除项: {exclude}")
    
    def test_upx_exclude_applied_to_collect(self):
        """
        测试COLLECT中应用了upx_exclude配置
        
        验证：COLLECT应该使用upx_exclude_list
        """
        spec_path = 'Pack/Pyinstaller/ocr_system.spec'
        
        if not os.path.exists(spec_path):
            self.skipTest(f"未找到spec文件: {spec_path}")
        
        with open(spec_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查COLLECT中使用了upx_exclude_list
        self.assertIn('upx_exclude=upx_exclude_list', content,
                     "COLLECT中未应用upx_exclude_list")


class TestPackagingSizeProperty(unittest.TestCase):
    """
    打包大小相关的属性测试
    """
    
    def setUp(self):
        """设置测试环境"""
        self.dist_paths = [
            'Pack/Pyinstaller/dist/OCR-System',
            'dist/OCR-System',
        ]
        
        self.dist_path = None
        for path in self.dist_paths:
            if os.path.exists(path):
                self.dist_path = path
                break
        
        if not self.dist_path:
            self.skipTest("未找到打包后的dist目录，请先执行打包")
    
    def get_directory_size(self, directory):
        """计算目录大小"""
        total_size = 0
        for root, dirs, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    total_size += os.path.getsize(file_path)
                except (OSError, IOError):
                    pass
        return total_size
    
    def test_package_size_reasonable(self):
        """
        测试打包大小在合理范围内
        
        验证：优化后的打包大小应该显著小于优化前
        """
        total_size = self.get_directory_size(self.dist_path)
        size_mb = total_size / (1024 * 1024)
        
        print(f"\n当前打包大小: {size_mb:.1f} MB")
        
        # 设置合理的大小上限（根据优化目标调整）
        # 优化前预计200MB，优化后目标50-100MB
        max_size_mb = 150  # 给一些缓冲空间
        
        self.assertLess(size_mb, max_size_mb,
                       f"打包大小 {size_mb:.1f}MB 超过预期上限 {max_size_mb}MB")
        
        # 如果大小非常小，可能是打包不完整
        min_size_mb = 20  # 最小合理大小
        self.assertGreater(size_mb, min_size_mb,
                          f"打包大小 {size_mb:.1f}MB 过小，可能打包不完整")
    
    def test_no_oversized_single_files(self):
        """
        测试没有过大的单个文件
        
        验证：单个文件不应超过合理大小限制
        """
        max_file_size_mb = 50  # 单个文件最大50MB
        max_file_size = max_file_size_mb * 1024 * 1024
        
        oversized_files = []
        
        for root, dirs, files in os.walk(self.dist_path):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                    if file_size > max_file_size:
                        rel_path = os.path.relpath(file_path, self.dist_path)
                        oversized_files.append({
                            'path': rel_path,
                            'size_mb': file_size / (1024 * 1024)
                        })
                except (OSError, IOError):
                    pass
        
        if oversized_files:
            file_list = [f"{f['path']} ({f['size_mb']:.1f}MB)" for f in oversized_files]
            self.fail(f"发现过大的文件: {file_list}")


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestPackagingExclusionProperty))
    suite.addTests(loader.loadTestsFromTestCase(TestUPXConfiguration))
    suite.addTests(loader.loadTestsFromTestCase(TestPackagingSizeProperty))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 打印总结
    print("\n" + "=" * 70)
    print("打包配置测试总结")
    print("=" * 70)
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped)}")
    
    if result.failures:
        print("\n失败的测试:")
        for test, traceback in result.failures:
            lines = traceback.split('\n')
            error_msg = [line for line in lines if 'AssertionError:' in line]
            if error_msg:
                print(f"- {test}: {error_msg[0].split('AssertionError: ')[-1]}")
            else:
                print(f"- {test}")
    
    if result.errors:
        print("\n错误的测试:")
        for test, traceback in result.errors:
            lines = traceback.split('\n')
            if len(lines) >= 2:
                print(f"- {test}: {lines[-2]}")
            else:
                print(f"- {test}")
    
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
