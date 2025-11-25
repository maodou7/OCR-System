"""
PaddleOCR引擎 - 高性能优化版
针对复杂场景（文字、数字、时间、特殊符号）优化
"""

import os
import sys
from typing import List, Dict, Optional, Tuple
from PIL import Image
from config import Config, OCRRect

# 检查PaddleOCR依赖
try:
    from paddleocr import PaddleOCR
    import numpy as np
    PADDLE_AVAILABLE = True
except ImportError:
    PADDLE_AVAILABLE = False
    print("警告: PaddleOCR未安装")
    print("请运行: pip install paddleocr paddlepaddle")


class PaddleOCREngine:
    """
    PaddleOCR识别引擎 - 高性能优化版
    针对复杂识别场景（文字、数字、时间、特殊符号）进行优化
    """
    
    def __init__(self, use_gpu=None, lang='ch'):
        """
        初始化PaddleOCR引擎（自动检测最优配置）
        :param use_gpu: 是否使用GPU加速（None=自动检测）
        :param lang: 语言模型 ('ch'=中英文, 'en'=英文, 'chinese_cht'=繁体中文)
        """
        self.is_initialized = False
        self.ocr = None
        self.lang = lang
        self.use_gpu = False
        self.detected_features = {}
        
        if not PADDLE_AVAILABLE:
            print("❌ PaddleOCR不可用")
            return
        
        try:
            # 自动检测GPU可用性
            if use_gpu is None:
                self.use_gpu = self._detect_gpu()
            else:
                self.use_gpu = use_gpu
            
            # 使用参数降级策略初始化PaddleOCR
            init_success = False
            for level in range(4):  # 尝试4个兼容级别（3.x -> 2.x完整 -> 2.x基础 -> 最小）
                try:
                    ocr_params = self._build_compatible_params(lang, self.use_gpu, level)
                    self.ocr = PaddleOCR(**ocr_params)
                    init_success = True
                    
                    # 记录成功的参数级别和版本
                    if level == 0:
                        self.detected_features = {'version': '3.x', 'doc_orientation': False, 'doc_unwarping': False}
                    elif level == 1:
                        self.detected_features = {'version': '2.x', 'use_angle_cls': True, 'use_space_char': True}
                    elif level == 2:
                        self.detected_features = {'version': '2.x', 'use_angle_cls': True, 'use_space_char': False}
                    else:
                        self.detected_features = {'version': 'minimal', 'use_angle_cls': False, 'use_space_char': False}
                    
                    break
                except Exception as e:
                    if level < 3:  # 还有降级选项
                        continue
                    else:  # 最后一次尝试也失败
                        raise e
            
            if init_success:
                self.is_initialized = True
                gpu_status = "GPU加速" if self.use_gpu else "CPU"
                version = self.detected_features.get('version', 'unknown')
                print(f"✓ PaddleOCR引擎初始化成功 ({gpu_status}模式)")
                print(f"  - API版本: {version}")
                print(f"  - 语言模型: {lang}")
                
                # 显示启用的优化特性
                enabled_features = []
                if version == '3.x':
                    enabled_features.append("最新API")
                else:
                    if self.detected_features.get('use_angle_cls'):
                        enabled_features.append("角度分类")
                    if self.detected_features.get('use_space_char'):
                        enabled_features.append("空格识别")
                
                if enabled_features:
                    print(f"  - 特性: {', '.join(enabled_features)}")
            
        except Exception as e:
            print(f"❌ PaddleOCR引擎初始化失败: {e}")
            self.is_initialized = False
    
    def _detect_gpu(self) -> bool:
        """
        自动检测GPU是否可用
        :return: True表示有可用GPU
        """
        try:
            import paddle
            # 检测是否有CUDA
            if paddle.is_compiled_with_cuda():
                # 尝试获取GPU数量
                gpu_count = paddle.device.get_device()
                if 'gpu' in str(gpu_count).lower():
                    self.detected_features['gpu'] = True
                    print("  ✓ 检测到GPU，启用GPU加速")
                    return True
        except:
            pass
        
        self.detected_features['gpu'] = False
        print("  ℹ 未检测到GPU，使用CPU模式")
        return False
    
    def _build_compatible_params(self, lang: str, use_gpu: bool, level: int = 0) -> dict:
        """
        构建兼容不同版本PaddleOCR的参数字典
        支持PaddleOCR 2.x和3.x版本
        :param lang: 语言模型
        :param use_gpu: 是否使用GPU
        :param level: 兼容级别 (0=PaddleOCR 3.x, 1=PaddleOCR 2.x完整, 2=PaddleOCR 2.x基础, 3=最小)
        :return: 参数字典
        """
        if level == 0:
            # PaddleOCR 3.x API（最新版本）
            params = {
                'lang': lang,
                'use_doc_orientation_classify': False,  # 文档方向分类
                'use_doc_unwarping': False,  # 文档反扭曲
                'use_textline_orientation': False,  # 文本行方向检测
            }
        elif level == 1:
            # PaddleOCR 2.x API - 完整参数
            params = {
                'lang': lang,
                'use_angle_cls': True,
                'use_space_char': True,
            }
        elif level == 2:
            # PaddleOCR 2.x API - 基础参数（移除use_space_char）
            params = {
                'lang': lang,
                'use_angle_cls': True,
            }
        else:
            # 最小参数集（仅lang）
            params = {
                'lang': lang,
            }
        
        # GPU参数（3.x版本不使用use_gpu参数）
        if use_gpu and level > 0:
            params['use_gpu'] = True
        
        return params
    
    def is_ready(self) -> bool:
        """检查引擎是否就绪"""
        return self.is_initialized and self.ocr is not None
    
    def _preprocess_image(self, image) -> np.ndarray:
        """
        预处理图片以提高识别准确率
        :param image: PIL Image或numpy数组
        :return: numpy数组
        """
        # 转换为numpy数组
        if isinstance(image, Image.Image):
            img_array = np.array(image)
        elif isinstance(image, np.ndarray):
            img_array = image.copy()
        else:
            raise ValueError("不支持的图片格式")
        
        # 确保是RGB格式
        if len(img_array.shape) == 2:  # 灰度图
            img_array = np.stack([img_array] * 3, axis=-1)
        elif img_array.shape[2] == 4:  # RGBA
            img_array = img_array[:, :, :3]
        
        return img_array
    
    def recognize_image(self, image, **kwargs) -> Optional[Dict]:
        """
        识别整张图片
        :param image: PIL Image、numpy数组或文件路径
        :param kwargs: 额外参数
        :return: 识别结果字典
        """
        if not self.is_ready():
            raise RuntimeError("PaddleOCR引擎未就绪")
        
        try:
            # 检测API版本
            api_version = self.detected_features.get('version', '2.x')
            
            # 处理输入
            if isinstance(image, str):
                # 文件路径
                img_input = image if api_version == '3.x' else np.array(Image.open(image))
            else:
                img_input = self._preprocess_image(image)
            
            # 执行OCR识别（根据版本使用不同API）
            if api_version == '3.x':
                # PaddleOCR 3.x API
                result = self.ocr.predict(input=img_input)
                # 3.x返回的是结果对象列表
                if result and len(result) > 0:
                    return self._parse_result_v3(result[0])
                else:
                    return {
                        'success': True,
                        'content': '',
                        'items': [],
                        'raw_data': result
                    }
            else:
                # PaddleOCR 2.x API
                result = self.ocr.ocr(img_input, cls=True)
                # 解析结果
                if result and result[0]:
                    return self._parse_result(result[0])
                else:
                    return {
                        'success': True,
                        'content': '',
                        'items': [],
                        'raw_data': result
                    }
        
        except Exception as e:
            print(f"❌ PaddleOCR识别失败: {e}")
            return None
    
    def _parse_result_v3(self, result_dict) -> Dict:
        """
        解析PaddleOCR 3.x结果字典
        :param result_dict: PaddleOCR 3.x返回的结果字典
        :return: 标准化的识别结果
        """
        items = []
        all_text = []
        
        try:
            # 3.x版本返回字典，包含dt_polys、rec_texts、rec_scores等键
            if isinstance(result_dict, dict):
                dt_polys = result_dict.get('dt_polys', [])  # 检测框
                rec_texts = result_dict.get('rec_texts', [])  # 识别文本
                rec_scores = result_dict.get('rec_scores', [1.0] * len(rec_texts))  # 置信度
                
                for i, (poly, text, score) in enumerate(zip(dt_polys, rec_texts, rec_scores)):
                    # 提取位置信息
                    x_coords = [point[0] for point in poly]
                    y_coords = [point[1] for point in poly]
                    
                    item = {
                        'text': text,
                        'confidence': float(score) if isinstance(score, (int, float)) else 1.0,
                        'position': {
                            'x': int(min(x_coords)),
                            'y': int(min(y_coords)),
                            'w': int(max(x_coords) - min(x_coords)),
                            'h': int(max(y_coords) - min(y_coords))
                        }
                    }
                    
                    items.append(item)
                    all_text.append(text)
            else:
                print(f"警告: 3.x结果不是字典类型: {type(result_dict)}")
        except Exception as e:
            print(f"解析3.x结果时出错: {e}")
        
        return {
            'success': True,
            'content': '\n'.join(all_text),
            'items': items,
            'raw_data': result_dict
        }
    
    def _parse_result(self, ocr_result: List) -> Dict:
        """
        解析OCR结果
        :param ocr_result: PaddleOCR返回的结果
        :return: 标准化的识别结果
        """
        items = []
        all_text = []
        
        for line in ocr_result:
            if not line:
                continue
            
            # PaddleOCR返回格式: [[box], (text, confidence)]
            box = line[0]  # 坐标框 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            text_info = line[1]  # (text, confidence)
            
            text = text_info[0]
            confidence = text_info[1]
            
            # 提取位置信息
            x_coords = [point[0] for point in box]
            y_coords = [point[1] for point in box]
            
            item = {
                'text': text,
                'confidence': float(confidence),
                'position': {
                    'x': int(min(x_coords)),
                    'y': int(min(y_coords)),
                    'w': int(max(x_coords) - min(x_coords)),
                    'h': int(max(y_coords) - min(y_coords))
                }
            }
            
            items.append(item)
            all_text.append(text)
        
        return {
            'success': True,
            'content': '\n'.join(all_text),
            'items': items,
            'raw_data': ocr_result
        }
    
    def recognize_region(self, image, rect, **kwargs) -> str:
        """
        识别图片中的指定区域
        :param image: PIL Image对象
        :param rect: OCRRect对象或坐标元组 (x1, y1, x2, y2)
        :param kwargs: 额外参数
        :return: 识别的文本字符串
        """
        if not self.is_ready():
            raise RuntimeError("PaddleOCR引擎未就绪")
        
        try:
            # 获取坐标
            if hasattr(rect, 'get_coords'):
                coords = rect.get_coords()
            else:
                coords = rect
            
            # 裁剪区域
            if isinstance(image, Image.Image):
                cropped = image.crop(coords)
            else:
                # numpy数组
                x1, y1, x2, y2 = coords
                cropped = image[y1:y2, x1:x2]
            
            # 识别裁剪后的图片
            result = self.recognize_image(cropped)
            
            if result and result.get('content'):
                return result['content'].strip()
            elif result and result.get('items'):
                # 拼接所有文本（保持换行）
                return '\n'.join([item['text'] for item in result['items']])
            else:
                return ""
        
        except Exception as e:
            print(f"❌ 区域识别失败: {e}")
            return ""
    
    def recognize_regions(self, image, rects: List[OCRRect], **kwargs) -> Dict[OCRRect, str]:
        """
        批量识别多个区域
        :param image: PIL Image对象
        :param rects: OCRRect对象列表
        :param kwargs: 额外参数
        :return: 识别结果字典 {rect: text}
        """
        if not self.is_ready():
            raise RuntimeError("PaddleOCR引擎未就绪")
        
        results = {}
        
        for rect in rects:
            text = self.recognize_region(image, rect, **kwargs)
            results[rect] = text
            
            # 更新rect的text属性
            if hasattr(rect, 'text'):
                rect.text = text
        
        return results
    
    def batch_recognize(self, image_rect_pairs: List[Tuple], **kwargs) -> List[Dict]:
        """
        批量处理多个图片
        :param image_rect_pairs: [(image, [rects]), ...] 列表
        :param kwargs: 额外参数
        :return: 识别结果列表
        """
        if not self.is_ready():
            raise RuntimeError("PaddleOCR引擎未就绪")
        
        all_results = []
        
        for image, rects in image_rect_pairs:
            if rects:
                # 有指定区域，识别区域
                region_results = self.recognize_regions(image, rects, **kwargs)
                all_results.append({
                    'type': 'regions',
                    'results': region_results
                })
            else:
                # 没有指定区域，识别整张图片
                image_result = self.recognize_image(image, **kwargs)
                all_results.append({
                    'type': 'full_image',
                    'result': image_result
                })
        
        return all_results
    
    def test_connection(self) -> bool:
        """
        测试引擎是否正常工作
        :return: 是否正常
        """
        if not self.is_ready():
            return False
        
        try:
            # 创建测试图片
            from PIL import ImageDraw, ImageFont
            
            test_img = Image.new('RGB', (300, 150), color='white')
            draw = ImageDraw.Draw(test_img)
            
            # 绘制多种类型的文本
            test_text = "测试Text123\n2024-01-01\n特殊符号@#$%"
            draw.text((10, 10), test_text, fill='black')
            
            # 测试识别
            result = self.recognize_image(test_img)
            
            if result and result.get('success'):
                print("✓ PaddleOCR引擎测试成功")
                if result.get('items'):
                    print(f"  识别到 {len(result['items'])} 个文本块")
                return True
            else:
                print("✗ PaddleOCR引擎测试失败（无结果）")
                return False
        
        except Exception as e:
            print(f"✗ PaddleOCR引擎测试失败: {e}")
            return False
    
    def get_config_info(self) -> Dict:
        """获取当前配置信息"""
        # 根据实际检测到的特性构建优化列表
        optimizations = []
        
        if self.detected_features.get('det_db_thresh'):
            optimizations.append('高精度检测（det_db_thresh=0.2）')
        if self.detected_features.get('det_db_box_thresh'):
            optimizations.append('高召回率（det_db_box_thresh=0.4）')
        if self.detected_features.get('det_db_unclip_ratio'):
            optimizations.append('文本框扩展（det_db_unclip_ratio=2.0）')
        if self.detected_features.get('drop_score'):
            optimizations.append('低置信度阈值（drop_score=0.3）')
        if self.detected_features.get('use_angle_cls'):
            optimizations.append('角度分类（处理旋转文字）')
        if self.detected_features.get('use_space_char'):
            optimizations.append('空格识别')
        if self.detected_features.get('gpu'):
            optimizations.append('GPU加速')
        
        return {
            'engine': 'PaddleOCR',
            'version': 'auto-optimized',
            'use_gpu': self.use_gpu,
            'lang': self.lang,
            'is_ready': self.is_ready(),
            'detected_features': self.detected_features,
            'optimizations': optimizations
        }


# 便捷函数
def create_paddle_ocr_engine(use_gpu=None, lang='ch'):
    """
    创建PaddleOCR引擎实例（自动检测最优配置）
    :param use_gpu: 是否使用GPU（None=自动检测，True=强制GPU，False=强制CPU）
    :param lang: 语言模型
    :return: PaddleOCREngine实例
    """
    return PaddleOCREngine(use_gpu=use_gpu, lang=lang)


if __name__ == "__main__":
    """测试代码"""
    print("=" * 60)
    print("PaddleOCR引擎测试（自动优化版）")
    print("=" * 60)
    
    # 创建引擎实例（自动检测GPU）
    print("\n正在初始化引擎并自动检测硬件配置...")
    engine = PaddleOCREngine(use_gpu=None, lang='ch')
    
    if engine.is_ready():
        print("\n引擎初始化成功！")
        
        # 显示配置信息
        config = engine.get_config_info()
        print("\n当前配置:")
        print(f"  引擎: {config['engine']}")
        print(f"  版本: {config['version']}")
        print(f"  GPU: {config['use_gpu']}")
        print(f"  语言: {config['lang']}")
        
        print("\n优化特性:")
        for opt in config['optimizations']:
            print(f"  ✓ {opt}")
        
        # 测试连接
        print("\n测试引擎...")
        engine.test_connection()
    else:
        print("\n引擎初始化失败")
        print("\n请确保已安装PaddleOCR:")
        print("  pip install paddleocr paddlepaddle")
