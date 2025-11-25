"""
RapidOCR引擎 - 快速轻量级OCR
基于ONNX Runtime，无需GPU，快速启动
"""

import os
import sys
from typing import List, Dict, Optional, Tuple
from PIL import Image
from config import Config, OCRRect

# 检查RapidOCR依赖
try:
    from rapidocr_onnxruntime import RapidOCR
    import numpy as np
    RAPID_AVAILABLE = True
except ImportError:
    RAPID_AVAILABLE = False
    print("警告: RapidOCR未安装")
    print("请运行: pip install rapidocr-onnxruntime")


class RapidOCREngine:
    """
    RapidOCR识别引擎
    快速轻量级OCR方案，适合对速度要求高的场景
    """
    
    def __init__(self):
        """
        初始化RapidOCR引擎
        """
        self.is_initialized = False
        self.ocr = None
        
        if not RAPID_AVAILABLE:
            print("❌ RapidOCR不可用")
            return
        
        try:
            # 初始化RapidOCR（自动使用CPU模式）
            # 优化参数配置：
            # det_limit_side_len: 限制图像长边，默认960，减小可提高速度
            # det_thresh: 检测阈值，默认0.3，适当降低可提高召回率
            # det_box_thresh: 文本框阈值，默认0.5
            self.ocr = RapidOCR(
                det_limit_side_len=960,  # 保持默认或根据需要调整
                det_thresh=0.3,
                det_box_thresh=0.5,
                det_unclip_ratio=1.6
            )
            
            self.is_initialized = True
            print(f"✓ RapidOCR引擎初始化成功")
            print(f"  - 运行模式: CPU (ONNX Runtime)")
            print(f"  - 特性: 轻量级、快速启动、无需GPU")
            print(f"  - 优化: 已应用参数调优")
            
        except Exception as e:
            print(f"❌ RapidOCR引擎初始化失败: {e}")
            self.is_initialized = False
    
    def is_ready(self) -> bool:
        """检查引擎是否就绪"""
        return self.is_initialized and self.ocr is not None
    
    def _preprocess_image(self, image) -> np.ndarray:
        """
        预处理图片
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
            raise RuntimeError("RapidOCR引擎未就绪")
        
        try:
            # 处理输入
            if isinstance(image, str):
                # 文件路径
                img_array = np.array(Image.open(image))
            else:
                img_array = self._preprocess_image(image)
            
            # 执行OCR识别
            # RapidOCR返回格式: (result, elapse)
            # result: [[box, text, confidence], ...]
            result, elapse = self.ocr(img_array)
            
            # 解析结果
            if result:
                return self._parse_result(result)
            else:
                return {
                    'success': True,
                    'content': '',
                    'items': [],
                    'raw_data': result
                }
        
        except Exception as e:
            print(f"❌ RapidOCR识别失败: {e}")
            return None
    
    def _parse_result(self, ocr_result: List) -> Dict:
        """
        解析OCR结果
        :param ocr_result: RapidOCR返回的结果
        :return: 标准化的识别结果
        """
        items = []
        all_text = []
        
        for line in ocr_result:
            if not line or len(line) < 3:
                continue
            
            # RapidOCR返回格式: [box, text, confidence]
            box = line[0]  # 坐标框 [[x1,y1], [x2,y2], [x3,y3], [x4,y4]]
            text = line[1]  # 文本
            confidence = line[2]  # 置信度
            
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
            raise RuntimeError("RapidOCR引擎未就绪")
        
        try:
            # 获取坐标
            if hasattr(rect, 'get_coords'):
                coords = rect.get_coords()
            else:
                coords = rect
            
            # 裁剪区域
            if isinstance(image, Image.Image):
                # 增加padding以提高边缘文字识别率
                padding = 10
                width, height = image.size
                x1, y1, x2, y2 = coords
                
                # 确保裁剪区域不超出图片范围
                x1 = max(0, x1 - padding)
                y1 = max(0, y1 - padding)
                x2 = min(width, x2 + padding)
                y2 = min(height, y2 + padding)
                
                cropped = image.crop((x1, y1, x2, y2))
            else:
                # numpy数组
                x1, y1, x2, y2 = coords
                # 增加padding
                padding = 10
                h, w = image.shape[:2]
                
                x1 = max(0, x1 - padding)
                y1 = max(0, y1 - padding)
                x2 = min(w, x2 + padding)
                y2 = min(h, y2 + padding)
                
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
            raise RuntimeError("RapidOCR引擎未就绪")
        
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
            raise RuntimeError("RapidOCR引擎未就绪")
        
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
                print("✓ RapidOCR引擎测试成功")
                if result.get('items'):
                    print(f"  识别到 {len(result['items'])} 个文本块")
                return True
            else:
                print("✗ RapidOCR引擎测试失败（无结果）")
                return False
        
        except Exception as e:
            print(f"✗ RapidOCR引擎测试失败: {e}")
            return False
    
    def get_config_info(self) -> Dict:
        """获取当前配置信息"""
        return {
            'engine': 'RapidOCR',
            'version': 'onnxruntime',
            'use_gpu': False,
            'runtime': 'ONNX Runtime',
            'is_ready': self.is_ready(),
            'features': [
                '轻量级部署',
                '快速启动',
                '无需GPU',
                'ONNX加速'
            ]
        }


# 便捷函数
def create_rapid_ocr_engine():
    """
    创建RapidOCR引擎实例
    :return: RapidOCREngine实例
    """
    return RapidOCREngine()


if __name__ == "__main__":
    """测试代码"""
    print("=" * 60)
    print("RapidOCR引擎测试")
    print("=" * 60)
    
    # 创建引擎实例
    print("\n正在初始化引擎...")
    engine = RapidOCREngine()
    
    if engine.is_ready():
        print("\n引擎初始化成功！")
        
        # 显示配置信息
        config = engine.get_config_info()
        print("\n当前配置:")
        print(f"  引擎: {config['engine']}")
        print(f"  版本: {config['version']}")
        print(f"  运行时: {config['runtime']}")
        
        print("\n特性:")
        for feature in config['features']:
            print(f"  ✓ {feature}")
        
        # 测试连接
        print("\n测试引擎...")
        engine.test_connection()
    else:
        print("\n引擎初始化失败")
        print("\n请确保已安装RapidOCR:")
        print("  pip install rapidocr-onnxruntime")
