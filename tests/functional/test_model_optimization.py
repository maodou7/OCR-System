# -*- coding: utf-8 -*-
"""
模型优化属性测试

**Feature: ocr-system-optimization, Property 6: 模型文件最小化**

测试models目录不包含非中英文模型，确保非必需的语言模型已被移除。

验证需求: 2.1, 2.2
"""

import os
import sys
import unittest
from pathlib import Path


class TestModelMinimizationProperty(unittest.TestCase):
    """
    属性6: 模型文件最小化
    
    对于任何配置为仅支持中英文的OCR引擎，
    models目录下不应包含日文（japan）、韩文（korean）、
    俄文（cyrillic）、繁体中文（cht）的模型文件。
    
    **验证需求: 2.1, 2.2**
    """
    
    def setUp(self):
        """设置测试环境"""
        self.project_root = Path(__file__).parent
        self.models_dir = self.project_root / 'models'
        
        # 定义非中英文语言模型的标识符
        self.excluded_language_markers = [
            'japan',      # 日文
            'japanese',   # 日文
            'jpn',        # 日文
            'korean',     # 韩文
            'kor',        # 韩文
            'cyrillic',   # 俄文
            'russian',    # 俄文
            'rus',        # 俄文
            'cht',        # 繁体中文
            'chinese_cht',# 繁体中文
            'taiwan',     # 繁体中文（台湾）
            'arabic',     # 阿拉伯文
            'devanagari', # 梵文
            'tamil',      # 泰米尔文
            'telugu',     # 泰卢固文
            'kannada',    # 卡纳达文
        ]
        
        # 允许的语言标识符（中英文）
        self.allowed_language_markers = [
            'ch',         # 中文
            'chinese',    # 中文
            'chs',        # 简体中文
            'en',         # 英文
            'english',    # 英文
        ]
    
    def test_models_directory_exists(self):
        """测试models目录存在"""
        self.assertTrue(
            self.models_dir.exists(),
            f"models目录应该存在: {self.models_dir}"
        )
        self.assertTrue(
            self.models_dir.is_dir(),
            f"models路径应该是目录: {self.models_dir}"
        )
    
    def test_no_excluded_language_models_in_paddle(self):
        """
        测试PaddleOCR模型目录不包含非中英文模型
        
        验证：PaddleOCR-json模型目录中不应包含日韩俄等语言模型
        """
        paddle_models_dir = self.models_dir / 'PaddleOCR-json' / 'PaddleOCR-json_v1.4.1' / 'models'
        
        if not paddle_models_dir.exists():
            self.skipTest(f"PaddleOCR模型目录不存在: {paddle_models_dir}")
        
        # 收集所有文件和目录
        all_items = []
        for root, dirs, files in os.walk(paddle_models_dir):
            for d in dirs:
                all_items.append(os.path.join(root, d))
            for f in files:
                all_items.append(os.path.join(root, f))
        
        # 检查是否包含非中英文语言标识符
        excluded_items = []
        for item in all_items:
            item_lower = item.lower()
            for marker in self.excluded_language_markers:
                if marker in item_lower:
                    # 确保不是误报（例如包含'en'的'japanese'）
                    # 检查是否是独立的词或下划线分隔
                    if self._is_language_marker_present(item_lower, marker):
                        excluded_items.append((item, marker))
                        break
        
        # 断言不应包含非中英文模型
        self.assertEqual(
            len(excluded_items), 0,
            f"PaddleOCR模型目录包含非中英文模型:\n" +
            "\n".join([f"  - {item} (标识符: {marker})" for item, marker in excluded_items])
        )
    
    def test_no_excluded_language_models_in_rapid(self):
        """
        测试RapidOCR模型目录不包含非中英文模型
        
        验证：RapidOCR-json模型目录中不应包含日韩俄等语言模型
        """
        rapid_models_dir = self.models_dir / 'RapidOCR-json' / 'RapidOCR-json_v0.2.0' / 'models'
        
        if not rapid_models_dir.exists():
            self.skipTest(f"RapidOCR模型目录不存在: {rapid_models_dir}")
        
        # 收集所有文件和目录
        all_items = []
        for root, dirs, files in os.walk(rapid_models_dir):
            for d in dirs:
                all_items.append(os.path.join(root, d))
            for f in files:
                all_items.append(os.path.join(root, f))
        
        # 检查是否包含非中英文语言标识符
        excluded_items = []
        for item in all_items:
            item_lower = item.lower()
            for marker in self.excluded_language_markers:
                if marker in item_lower:
                    if self._is_language_marker_present(item_lower, marker):
                        excluded_items.append((item, marker))
                        break
        
        # 断言不应包含非中英文模型
        self.assertEqual(
            len(excluded_items), 0,
            f"RapidOCR模型目录包含非中英文模型:\n" +
            "\n".join([f"  - {item} (标识符: {marker})" for item, marker in excluded_items])
        )
    
    def test_only_chinese_english_models_present(self):
        """
        测试只包含中英文模型
        
        验证：模型目录应该只包含中文和英文相关的模型文件
        """
        # 检查PaddleOCR
        paddle_models_dir = self.models_dir / 'PaddleOCR-json' / 'PaddleOCR-json_v1.4.1' / 'models'
        if paddle_models_dir.exists():
            model_dirs = [d for d in paddle_models_dir.iterdir() if d.is_dir()]
            
            # 应该只有中英文模型目录
            expected_patterns = ['ch_', 'en_', 'chinese', 'english']
            
            for model_dir in model_dirs:
                dir_name_lower = model_dir.name.lower()
                has_valid_marker = any(
                    pattern in dir_name_lower for pattern in expected_patterns
                )
                
                self.assertTrue(
                    has_valid_marker,
                    f"PaddleOCR模型目录包含非预期的模型: {model_dir.name}"
                )
        
        # 检查RapidOCR
        rapid_models_dir = self.models_dir / 'RapidOCR-json' / 'RapidOCR-json_v0.2.0' / 'models'
        if rapid_models_dir.exists():
            model_files = [f for f in rapid_models_dir.iterdir() if f.is_file() and f.suffix in ['.onnx', '.pdmodel']]
            
            # 应该只有中英文模型文件
            expected_patterns = ['ch_', 'en_', 'rec_ch', 'rec_en']
            
            for model_file in model_files:
                file_name_lower = model_file.name.lower()
                
                # 跳过配置文件和字典文件
                if any(skip in file_name_lower for skip in ['config', 'dict', 'keys']):
                    continue
                
                has_valid_marker = any(
                    pattern in file_name_lower for pattern in expected_patterns
                )
                
                self.assertTrue(
                    has_valid_marker,
                    f"RapidOCR模型目录包含非预期的模型: {model_file.name}"
                )
    
    def test_model_file_count_reasonable(self):
        """
        测试模型文件数量合理
        
        验证：移除非中英文模型后，模型文件数量应该显著减少
        """
        # PaddleOCR应该只有4个模型目录（检测、识别中文、识别英文、分类）
        paddle_models_dir = self.models_dir / 'PaddleOCR-json' / 'PaddleOCR-json_v1.4.1' / 'models'
        if paddle_models_dir.exists():
            model_dirs = [d for d in paddle_models_dir.iterdir() if d.is_dir()]
            
            # 应该不超过5个模型目录（留一些余地）
            self.assertLessEqual(
                len(model_dirs), 5,
                f"PaddleOCR模型目录数量过多: {len(model_dirs)}，可能包含非中英文模型"
            )
            
            # 至少应该有2个模型目录（检测和识别）
            self.assertGreaterEqual(
                len(model_dirs), 2,
                f"PaddleOCR模型目录数量过少: {len(model_dirs)}，可能缺少必要模型"
            )
        
        # RapidOCR应该只有中英文相关的onnx文件
        rapid_models_dir = self.models_dir / 'RapidOCR-json' / 'RapidOCR-json_v0.2.0' / 'models'
        if rapid_models_dir.exists():
            onnx_files = [f for f in rapid_models_dir.iterdir() if f.suffix == '.onnx']
            
            # 应该不超过8个onnx文件（留一些余地）
            self.assertLessEqual(
                len(onnx_files), 8,
                f"RapidOCR onnx文件数量过多: {len(onnx_files)}，可能包含非中英文模型"
            )
            
            # 至少应该有2个onnx文件（检测和识别）
            self.assertGreaterEqual(
                len(onnx_files), 2,
                f"RapidOCR onnx文件数量过少: {len(onnx_files)}，可能缺少必要模型"
            )
    
    def test_config_files_only_reference_chinese_english(self):
        """
        测试配置文件只引用中英文模型
        
        验证：配置文件中不应包含非中英文语言的引用
        """
        # 检查PaddleOCR配置文件
        paddle_models_dir = self.models_dir / 'PaddleOCR-json' / 'PaddleOCR-json_v1.4.1' / 'models'
        if paddle_models_dir.exists():
            config_files = list(paddle_models_dir.glob('config*.txt'))
            
            for config_file in config_files:
                with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                
                # 检查是否包含非中英文语言标识符
                excluded_found = []
                for marker in self.excluded_language_markers:
                    if self._is_language_marker_present(content, marker):
                        excluded_found.append(marker)
                
                self.assertEqual(
                    len(excluded_found), 0,
                    f"配置文件 {config_file.name} 包含非中英文语言引用: {', '.join(excluded_found)}"
                )
        
        # 检查RapidOCR配置文件
        rapid_models_dir = self.models_dir / 'RapidOCR-json' / 'RapidOCR-json_v0.2.0' / 'models'
        if rapid_models_dir.exists():
            config_files = list(rapid_models_dir.glob('config*.txt'))
            
            for config_file in config_files:
                with open(config_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read().lower()
                
                # 检查是否包含非中英文语言标识符
                excluded_found = []
                for marker in self.excluded_language_markers:
                    if self._is_language_marker_present(content, marker):
                        excluded_found.append(marker)
                
                self.assertEqual(
                    len(excluded_found), 0,
                    f"配置文件 {config_file.name} 包含非中英文语言引用: {', '.join(excluded_found)}"
                )
    
    def _is_language_marker_present(self, text: str, marker: str) -> bool:
        """
        检查语言标识符是否真正存在（避免误报）
        
        Args:
            text: 要检查的文本（小写）
            marker: 语言标识符（小写）
        
        Returns:
            bool: 如果标识符真正存在返回True
        """
        # 简单检查：标识符在文本中
        if marker not in text:
            return False
        
        # 检查是否是独立的词（前后是非字母字符）
        import re
        pattern = r'(?:^|[^a-z])' + re.escape(marker) + r'(?:[^a-z]|$)'
        return bool(re.search(pattern, text))


class TestModelOptimizationIntegration(unittest.TestCase):
    """模型优化集成测试"""
    
    def setUp(self):
        """设置测试环境"""
        self.project_root = Path(__file__).parent
        self.models_dir = self.project_root / 'models'
    
    def test_paddle_models_structure(self):
        """测试PaddleOCR模型结构正确"""
        paddle_models_dir = self.models_dir / 'PaddleOCR-json' / 'PaddleOCR-json_v1.4.1' / 'models'
        
        if not paddle_models_dir.exists():
            self.skipTest(f"PaddleOCR模型目录不存在")
        
        # 检查必需的模型目录
        expected_dirs = [
            'ch_PP-OCRv3_det_infer',      # 中文检测
            'ch_PP-OCRv3_rec_infer',      # 中文识别
            'en_PP-OCRv3_rec_infer',      # 英文识别
        ]
        
        for expected_dir in expected_dirs:
            dir_path = paddle_models_dir / expected_dir
            self.assertTrue(
                dir_path.exists(),
                f"PaddleOCR缺少必需的模型目录: {expected_dir}"
            )
    
    def test_rapid_models_structure(self):
        """测试RapidOCR模型结构正确"""
        rapid_models_dir = self.models_dir / 'RapidOCR-json' / 'RapidOCR-json_v0.2.0' / 'models'
        
        if not rapid_models_dir.exists():
            self.skipTest(f"RapidOCR模型目录不存在")
        
        # 检查必需的模型文件
        expected_files = [
            'ch_PP-OCRv3_det_infer.onnx',     # 中文检测
            'ch_PP-OCRv3_rec_infer.onnx',     # 中文识别
            'rec_en_PP-OCRv3_infer.onnx',     # 英文识别
        ]
        
        for expected_file in expected_files:
            file_path = rapid_models_dir / expected_file
            self.assertTrue(
                file_path.exists(),
                f"RapidOCR缺少必需的模型文件: {expected_file}"
            )
    
    def test_dict_files_only_chinese_english(self):
        """测试字典文件只包含中英文"""
        # 检查PaddleOCR字典
        paddle_models_dir = self.models_dir / 'PaddleOCR-json' / 'PaddleOCR-json_v1.4.1' / 'models'
        if paddle_models_dir.exists():
            dict_files = list(paddle_models_dir.glob('dict_*.txt'))
            
            # 应该只有中英文字典
            expected_dicts = {'dict_chinese.txt', 'dict_en.txt'}
            actual_dicts = {f.name for f in dict_files}
            
            # 不应该有其他语言的字典
            unexpected_dicts = actual_dicts - expected_dicts
            self.assertEqual(
                len(unexpected_dicts), 0,
                f"PaddleOCR包含非预期的字典文件: {unexpected_dicts}"
            )
        
        # 检查RapidOCR字典
        rapid_models_dir = self.models_dir / 'RapidOCR-json' / 'RapidOCR-json_v0.2.0' / 'models'
        if rapid_models_dir.exists():
            dict_files = list(rapid_models_dir.glob('dict_*.txt'))
            
            # 应该只有中英文字典
            expected_dicts = {'dict_chinese.txt', 'dict_en.txt'}
            actual_dicts = {f.name for f in dict_files}
            
            # 不应该有其他语言的字典
            unexpected_dicts = actual_dicts - expected_dicts
            self.assertEqual(
                len(unexpected_dicts), 0,
                f"RapidOCR包含非预期的字典文件: {unexpected_dicts}"
            )


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试
    suite.addTests(loader.loadTestsFromTestCase(TestModelMinimizationProperty))
    suite.addTests(loader.loadTestsFromTestCase(TestModelOptimizationIntegration))
    
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
    
    # 打印详细的失败信息
    if result.failures:
        print("\n" + "=" * 70)
        print("失败详情")
        print("=" * 70)
        for test, traceback in result.failures:
            print(f"\n{test}:")
            print(traceback)
    
    if result.errors:
        print("\n" + "=" * 70)
        print("错误详情")
        print("=" * 70)
        for test, traceback in result.errors:
            print(f"\n{test}:")
            print(traceback)
    
    print("=" * 70)
    
    # 返回结果
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
