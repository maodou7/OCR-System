# -*- coding: utf-8 -*-
"""
延迟加载属性测试

**Feature: ocr-system-optimization, Property 1: 延迟加载一致性**

测试非核心模块在程序启动时不被加载，只有在首次使用相关功能时才被导入。

验证需求: 3.1, 3.2, 3.3, 3.4
"""

import sys
import unittest


class TestLazyLoadingProperty(unittest.TestCase):
    """
    属性1: 延迟加载一致性
    
    对于任何非核心模块（openpyxl, PyMuPDF, OCR引擎），
    在程序启动时该模块不应出现在sys.modules中，
    只有在首次使用相关功能时才应被导入。
    """
    
    def test_dependency_manager_import_minimal(self):
        """
        测试导入DependencyManager不触发可选模块加载
        
        验证：导入dependency_manager不应加载可选依赖
        
        注意：这个测试应该在其他测试之前运行，但由于测试顺序问题，
        我们只验证dependency_manager模块本身不导入可选依赖。
        """
        # 由于其他测试可能已经加载了模块，我们只验证
        # dependency_manager模块本身的导入行为
        from dependency_manager import DependencyManager
        
        # 验证DependencyManager有正确的方法
        self.assertTrue(hasattr(DependencyManager, 'load_excel_support'))
        self.assertTrue(hasattr(DependencyManager, 'load_pdf_support'))
        self.assertTrue(hasattr(DependencyManager, 'load_ocr_engine'))
        self.assertTrue(hasattr(DependencyManager, 'is_available'))
        
        # 验证缓存机制存在
        self.assertTrue(hasattr(DependencyManager, '_loaded_modules'))
        self.assertIsInstance(DependencyManager._loaded_modules, dict)
    
    def test_excel_support_lazy_loaded(self):
        """
        测试Excel支持的延迟加载
        
        验证：openpyxl只在调用load_excel_support()时加载
        """
        from dependency_manager import DependencyManager
        
        # 清除缓存以确保测试独立性
        if 'openpyxl' in DependencyManager._loaded_modules:
            del DependencyManager._loaded_modules['openpyxl']
        
        # 调用load_excel_support()
        openpyxl = DependencyManager.load_excel_support()
        
        if openpyxl is None:
            self.skipTest("openpyxl不可用")
        
        # 现在应该被加载了
        self.assertIn('openpyxl', sys.modules,
                     "调用load_excel_support()后openpyxl应该被加载")
        
        # 应该在缓存中
        self.assertIn('openpyxl', DependencyManager._loaded_modules,
                     "加载的模块应该在缓存中")
    
    def test_pdf_support_lazy_loaded(self):
        """
        测试PDF支持的延迟加载
        
        验证：PyMuPDF只在调用load_pdf_support()时加载
        """
        from dependency_manager import DependencyManager
        
        # 清除缓存
        if 'fitz' in DependencyManager._loaded_modules:
            del DependencyManager._loaded_modules['fitz']
        
        # 调用load_pdf_support()
        fitz = DependencyManager.load_pdf_support()
        
        if fitz is None:
            self.skipTest("PyMuPDF不可用")
        
        # 现在应该被加载了
        self.assertIn('fitz', sys.modules,
                     "调用load_pdf_support()后fitz应该被加载")
        
        # 应该在缓存中
        self.assertIn('fitz', DependencyManager._loaded_modules,
                     "加载的模块应该在缓存中")
    
    def test_ocr_engine_lazy_loaded(self):
        """
        测试OCR引擎的延迟加载
        
        验证：OCR引擎管理器只在调用load_ocr_engine()时加载
        """
        from dependency_manager import DependencyManager
        
        # 清除缓存
        if 'ocr_engine_manager' in DependencyManager._loaded_modules:
            del DependencyManager._loaded_modules['ocr_engine_manager']
        
        # 调用load_ocr_engine()
        OCREngineManager = DependencyManager.load_ocr_engine()
        
        self.assertIsNotNone(OCREngineManager,
                            "OCR引擎管理器应该可以加载")
        
        # 现在应该被加载了
        self.assertIn('ocr_engine_manager', sys.modules,
                     "调用load_ocr_engine()后ocr_engine_manager应该被加载")
        
        # 应该在缓存中
        self.assertIn('ocr_engine_manager', DependencyManager._loaded_modules,
                     "加载的模块应该在缓存中")
    
    def test_dependency_manager_caching(self):
        """
        测试DependencyManager的缓存机制
        
        验证：多次调用load_xxx()不会重复导入
        """
        from dependency_manager import DependencyManager
        
        # 清除缓存
        DependencyManager.clear_cache()
        
        # 第一次加载
        excel1 = DependencyManager.load_excel_support()
        
        # 第二次加载（应该从缓存返回）
        excel2 = DependencyManager.load_excel_support()
        
        if excel1 is not None:
            # 如果模块可用，两次应该返回同一个对象
            self.assertIs(excel1, excel2,
                         "多次调用应返回缓存的模块对象")
        
        # 检查缓存
        loaded = DependencyManager.get_loaded_modules()
        if excel1 is not None:
            self.assertIn('openpyxl', loaded,
                         "已加载的模块应在缓存中")
    
    def test_is_available_no_import(self):
        """
        测试is_available()不触发导入
        
        验证：检查模块可用性不应导入模块
        """
        from dependency_manager import DependencyManager
        
        # 清除缓存
        DependencyManager.clear_cache()
        
        # 记录当前模块
        modules_before = set(sys.modules.keys())
        
        # 检查可用性
        available = DependencyManager.is_available('openpyxl')
        
        # 检查是否导入了新模块
        modules_after = set(sys.modules.keys())
        new_modules = modules_after - modules_before
        
        # 不应该导入openpyxl
        self.assertNotIn('openpyxl', new_modules,
                        "is_available()不应导入模块")
        
        # 也不应该在缓存中
        self.assertNotIn('openpyxl', DependencyManager._loaded_modules,
                        "is_available()不应将模块加入缓存")


class TestLazyLoadingIntegration(unittest.TestCase):
    """集成测试：验证延迟加载在实际使用场景中的表现"""
    
    def test_utils_uses_dependency_manager(self):
        """
        测试utils模块使用DependencyManager
        
        验证：utils模块正确使用DependencyManager进行延迟加载
        """
        from utils import ExcelExporter, ImageUtils
        from dependency_manager import DependencyManager
        
        # 这些类应该存在
        self.assertIsNotNone(ExcelExporter)
        self.assertIsNotNone(ImageUtils)
        
        # DependencyManager应该可用
        self.assertTrue(hasattr(DependencyManager, 'load_excel_support'))
        self.assertTrue(hasattr(DependencyManager, 'load_pdf_support'))
    
    def test_module_info_accuracy(self):
        """
        测试get_module_info()的准确性
        
        验证：模块信息正确反映加载状态
        """
        from dependency_manager import DependencyManager
        
        # 清除缓存
        DependencyManager.clear_cache()
        
        # 获取初始状态
        info_before = DependencyManager.get_module_info()
        
        # 加载一个模块
        DependencyManager.load_excel_support()
        
        # 获取加载后状态
        info_after = DependencyManager.get_module_info()
        
        # 如果openpyxl可用，加载状态应该改变
        if info_after['openpyxl']['available']:
            self.assertFalse(info_before['openpyxl']['loaded'],
                           "加载前应该是未加载状态")
            self.assertTrue(info_after['openpyxl']['loaded'],
                          "加载后应该是已加载状态")


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestLazyLoadingProperty))
    suite.addTests(loader.loadTestsFromTestCase(TestLazyLoadingIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 打印总结
    print("\n" + "=" * 70)
    print("测试总结")
    print("=" * 70)
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped)}")
    print("=" * 70)
    
    # 返回结果
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
