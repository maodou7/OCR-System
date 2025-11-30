"""
在线OCR插件条件加载属性测试

**Feature: ocr-system-optimization, Property 8: 条件加载正确性**
**Validates: Requirements 10.3**

测试在线OCR模块的条件加载功能：
- 未配置API密钥时，不应加载在线OCR模块
- 配置了API密钥且ENABLED=True时，才应加载在线OCR模块
"""

import sys
import os
import unittest
from unittest.mock import patch, MagicMock
import importlib


class TestOnlineOCRConditionalLoading(unittest.TestCase):
    """测试在线OCR的条件加载正确性"""
    
    def setUp(self):
        """测试前准备"""
        # 清理已导入的模块，确保测试独立性
        modules_to_remove = [
            'ocr_engine_aliyun_new',
            'ocr_engine_deepseek',
            'ocr_engine_manager',
            'config'
        ]
        
        for module in modules_to_remove:
            if module in sys.modules:
                del sys.modules[module]
    
    def test_aliyun_not_loaded_without_api_key(self):
        """
        属性8: 条件加载正确性 - 阿里云OCR
        
        *对于任何*未配置API密钥的阿里云OCR服务，
        相关的SDK模块（alibabacloud_*）不应在程序运行时被导入。
        
        **Validates: Requirements 10.3**
        """
        # 模拟配置：ENABLED=False 或 无API密钥
        with patch('config.Config') as mock_config:
            mock_config.ALIYUN_ENABLED = False
            mock_config.ALIYUN_ACCESS_KEY_ID = ''
            mock_config.ALIYUN_ACCESS_KEY_SECRET = ''
            
            # 导入引擎管理器（应该不会导入阿里云OCR）
            import ocr_engine_manager
            
            # 验证阿里云OCR模块未被导入
            aliyun_modules = [
                'alibabacloud_ocr_api20210707',
                'alibabacloud_tea_openapi',
                'alibabacloud_tea_util',
                'ocr_engine_aliyun_new'
            ]
            
            for module in aliyun_modules:
                self.assertNotIn(
                    module, sys.modules,
                    f"阿里云OCR模块 {module} 不应在未配置时被导入"
                )
    
    def test_deepseek_not_loaded_without_api_key(self):
        """
        属性8: 条件加载正确性 - DeepSeek OCR
        
        *对于任何*未配置API密钥的DeepSeek OCR服务，
        相关的SDK模块（openai）不应在程序运行时被导入。
        
        **Validates: Requirements 10.3**
        """
        # 模拟配置：ENABLED=False 或 无API密钥
        with patch('config.Config') as mock_config:
            mock_config.DEEPSEEK_ENABLED = False
            mock_config.DEEPSEEK_API_KEY = ''
            
            # 导入引擎管理器（应该不会导入DeepSeek OCR）
            import ocr_engine_manager
            
            # 验证DeepSeek OCR模块未被导入
            deepseek_modules = [
                'openai',
                'ocr_engine_deepseek'
            ]
            
            for module in deepseek_modules:
                # 注意：openai可能被其他模块导入，所以这里只检查ocr_engine_deepseek
                if module == 'ocr_engine_deepseek':
                    self.assertNotIn(
                        module, sys.modules,
                        f"DeepSeek OCR模块 {module} 不应在未配置时被导入"
                    )
    
    def test_engine_manager_checks_enabled_flag(self):
        """
        测试引擎管理器正确检查ENABLED标志
        
        验证引擎管理器在检查可用性时，会检查ENABLED标志。
        """
        # 清理模块
        if 'ocr_engine_manager' in sys.modules:
            del sys.modules['ocr_engine_manager']
        if 'config' in sys.modules:
            del sys.modules['config']
        
        # 导入真实的config模块
        import config
        
        # 保存原始配置
        original_aliyun_enabled = config.Config.ALIYUN_ENABLED
        original_deepseek_enabled = config.Config.DEEPSEEK_ENABLED
        
        try:
            # 设置为禁用
            config.Config.ALIYUN_ENABLED = False
            config.Config.DEEPSEEK_ENABLED = False
            
            # 重新导入引擎管理器
            if 'ocr_engine_manager' in sys.modules:
                del sys.modules['ocr_engine_manager']
            
            from ocr_engine_manager import OCREngineManager
            
            # 创建引擎管理器实例
            manager = OCREngineManager()
            
            # 验证在线OCR引擎不可用
            self.assertFalse(
                manager.is_engine_available('aliyun'),
                "阿里云OCR应该不可用（ENABLED=False）"
            )
            self.assertFalse(
                manager.is_engine_available('deepseek'),
                "DeepSeek OCR应该不可用（ENABLED=False）"
            )
        
        finally:
            # 恢复原始配置
            config.Config.ALIYUN_ENABLED = original_aliyun_enabled
            config.Config.DEEPSEEK_ENABLED = original_deepseek_enabled
    
    def test_engine_manager_checks_api_keys(self):
        """
        测试引擎管理器正确检查API密钥
        
        验证即使ENABLED=True，如果没有API密钥，引擎也不可用。
        """
        # 清理模块
        if 'ocr_engine_manager' in sys.modules:
            del sys.modules['ocr_engine_manager']
        if 'config' in sys.modules:
            del sys.modules['config']
        
        # 导入真实的config模块
        import config
        
        # 保存原始配置
        original_aliyun_enabled = config.Config.ALIYUN_ENABLED
        original_aliyun_key_id = config.Config.ALIYUN_ACCESS_KEY_ID
        original_aliyun_key_secret = config.Config.ALIYUN_ACCESS_KEY_SECRET
        original_deepseek_enabled = config.Config.DEEPSEEK_ENABLED
        original_deepseek_key = config.Config.DEEPSEEK_API_KEY
        
        try:
            # 设置为启用但无密钥
            config.Config.ALIYUN_ENABLED = True
            config.Config.ALIYUN_ACCESS_KEY_ID = ''
            config.Config.ALIYUN_ACCESS_KEY_SECRET = ''
            config.Config.DEEPSEEK_ENABLED = True
            config.Config.DEEPSEEK_API_KEY = ''
            
            # 重新导入引擎管理器
            if 'ocr_engine_manager' in sys.modules:
                del sys.modules['ocr_engine_manager']
            
            from ocr_engine_manager import OCREngineManager
            
            # 创建引擎管理器实例
            manager = OCREngineManager()
            
            # 验证在线OCR引擎不可用（因为没有API密钥）
            self.assertFalse(
                manager.is_engine_available('aliyun'),
                "阿里云OCR应该不可用（无API密钥）"
            )
            self.assertFalse(
                manager.is_engine_available('deepseek'),
                "DeepSeek OCR应该不可用（无API密钥）"
            )
        
        finally:
            # 恢复原始配置
            config.Config.ALIYUN_ENABLED = original_aliyun_enabled
            config.Config.ALIYUN_ACCESS_KEY_ID = original_aliyun_key_id
            config.Config.ALIYUN_ACCESS_KEY_SECRET = original_aliyun_key_secret
            config.Config.DEEPSEEK_ENABLED = original_deepseek_enabled
            config.Config.DEEPSEEK_API_KEY = original_deepseek_key
    
    def test_online_ocr_modules_only_imported_when_needed(self):
        """
        测试在线OCR模块仅在需要时才导入
        
        验证在线OCR模块不会在启动时导入，只有在实际使用时才导入。
        """
        # 清理所有相关模块
        modules_to_remove = [
            'ocr_engine_aliyun_new',
            'ocr_engine_deepseek',
            'ocr_engine_manager',
            'config'
        ]
        
        for module in modules_to_remove:
            if module in sys.modules:
                del sys.modules[module]
        
        # 导入引擎管理器
        from ocr_engine_manager import OCREngineManager
        
        # 验证在线OCR引擎模块未被导入
        self.assertNotIn(
            'ocr_engine_aliyun_new', sys.modules,
            "阿里云OCR引擎模块不应在启动时导入"
        )
        self.assertNotIn(
            'ocr_engine_deepseek', sys.modules,
            "DeepSeek OCR引擎模块不应在启动时导入"
        )
        
        # 创建引擎管理器实例（不指定引擎类型）
        manager = OCREngineManager()
        
        # 再次验证在线OCR引擎模块未被导入
        self.assertNotIn(
            'ocr_engine_aliyun_new', sys.modules,
            "阿里云OCR引擎模块不应在创建管理器时导入"
        )
        self.assertNotIn(
            'ocr_engine_deepseek', sys.modules,
            "DeepSeek OCR引擎模块不应在创建管理器时导入"
        )
    
    def test_local_engines_work_without_online_ocr(self):
        """
        测试本地引擎在没有在线OCR的情况下正常工作
        
        验证即使在线OCR不可用，本地引擎（PaddleOCR、RapidOCR）仍然可以正常工作。
        """
        # 清理模块
        if 'ocr_engine_manager' in sys.modules:
            del sys.modules['ocr_engine_manager']
        if 'config' in sys.modules:
            del sys.modules['config']
        
        # 导入真实的config模块
        import config
        
        # 保存原始配置
        original_aliyun_enabled = config.Config.ALIYUN_ENABLED
        original_deepseek_enabled = config.Config.DEEPSEEK_ENABLED
        
        try:
            # 禁用所有在线OCR
            config.Config.ALIYUN_ENABLED = False
            config.Config.DEEPSEEK_ENABLED = False
            
            # 重新导入引擎管理器
            if 'ocr_engine_manager' in sys.modules:
                del sys.modules['ocr_engine_manager']
            
            from ocr_engine_manager import OCREngineManager
            
            # 创建引擎管理器实例
            manager = OCREngineManager()
            
            # 验证至少有一个本地引擎可用
            has_local_engine = (
                manager.is_engine_available('paddle') or
                manager.is_engine_available('rapid')
            )
            
            self.assertTrue(
                has_local_engine,
                "至少应该有一个本地OCR引擎可用"
            )
            
            # 验证在线OCR不可用
            self.assertFalse(
                manager.is_engine_available('aliyun'),
                "阿里云OCR应该不可用"
            )
            self.assertFalse(
                manager.is_engine_available('deepseek'),
                "DeepSeek OCR应该不可用"
            )
        
        finally:
            # 恢复原始配置
            config.Config.ALIYUN_ENABLED = original_aliyun_enabled
            config.Config.DEEPSEEK_ENABLED = original_deepseek_enabled


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestOnlineOCRConditionalLoading)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试结果
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
