"""
DeepSeek OCR引擎 - 基于硅基流动平台
使用OpenAI兼容接口调用DeepSeek-OCR模型
"""

import os
import sys
import base64
from io import BytesIO
from typing import List, Dict, Optional, Tuple
from PIL import Image
from config import Config, OCRRect

# 检查OpenAI SDK依赖
try:
    from openai import OpenAI
    OPENAI_SDK_AVAILABLE = True
except ImportError:
    OPENAI_SDK_AVAILABLE = False
    print("警告: OpenAI SDK未安装")
    print("请运行: pip install openai>=1.0.0")


class DeepSeekOCREngine:
    """
    DeepSeek OCR识别引擎 - 硅基流动平台
    使用OpenAI兼容接口，支持高质量OCR识别
    """
    
    def __init__(self, api_key: str = None, base_url: str = None, model: str = None):
        """
        初始化DeepSeek OCR引擎
        :param api_key: API密钥（可选，默认从config.py读取）
        :param base_url: API端点（可选，默认从config.py读取）
        :param model: 模型名称（可选，默认从config.py读取）
        """
        self.is_initialized = False
        self.client = None
        
        # 检查SDK可用性
        if not OPENAI_SDK_AVAILABLE:
            print("❌ DeepSeek OCR引擎初始化失败: OpenAI SDK未安装")
            return
        
        # 从配置或参数获取设置
        self.api_key = api_key or getattr(Config, 'DEEPSEEK_API_KEY', '')
        self.base_url = base_url or getattr(Config, 'DEEPSEEK_BASE_URL', 'https://api.siliconflow.cn/v1')
        self.model = model or getattr(Config, 'DEEPSEEK_MODEL', 'deepseek-ai/DeepSeek-OCR')
        self.ocr_prompt = getattr(Config, 'DEEPSEEK_OCR_PROMPT', '<image>\n<|grounding|>OCR this image.')
        
        # 检查API Key
        if not self.api_key:
            print("⚠️ DeepSeek API Key未配置")
            print("提示: 请在config.py中设置DEEPSEEK_API_KEY或使用环境变量DEEPSEEK_API_KEY")
            return
        
        # 创建OpenAI客户端
        try:
            self.client = OpenAI(
                api_key=self.api_key,
                base_url=self.base_url
            )
            self.is_initialized = True
            print(f"✓ DeepSeek OCR引擎初始化成功")
            print(f"  - 模型: {self.model}")
            print(f"  - 端点: {self.base_url}")
        except Exception as e:
            print(f"❌ DeepSeek OCR引擎初始化失败: {e}")
    
    def is_ready(self) -> bool:
        """检查引擎是否就绪"""
        return self.is_initialized and self.client is not None
    
    def _clean_ocr_result(self, raw_text: str) -> str:
        """
        清理DeepSeek OCR返回的原始结果，提取纯文本
        :param raw_text: 原始OCR结果（可能包含<|ref|>、<|det|>等标记）
        :return: 清理后的纯文本
        """
        import re
        
        # 如果没有标记，直接返回
        if '<|ref|>' not in raw_text and '<|det|>' not in raw_text:
            return raw_text.strip()
        
        # 提取所有<|ref|>标签内的文本
        pattern = r'<\|ref\|>(.*?)<\/\|ref\|>'
        matches = re.findall(pattern, raw_text)
        
        if matches:
            # 将所有识别的文本用换行连接
            clean_text = '\n'.join(matches)
            return clean_text.strip()
        
        # 如果没有匹配到，尝试移除所有标记
        clean_text = re.sub(r'<\|[^|]+\|>', '', raw_text)
        clean_text = re.sub(r'\[\[.*?\]\]', '', clean_text)
        
        return clean_text.strip()
    
    def _image_to_base64(self, image) -> str:
        """
        将图片转换为Base64编码的Data URL
        :param image: PIL Image、文件路径或numpy数组
        :return: Base64 Data URL字符串
        """
        # 处理不同类型的输入
        if isinstance(image, str):
            # 文件路径
            image = Image.open(image)
        elif isinstance(image, bytes):
            # 字节数据
            image = Image.open(BytesIO(image))
        elif hasattr(image, 'shape'):  # numpy数组
            # 延迟导入numpy
            import numpy as np
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)
        
        # 确保是PIL Image
        if not isinstance(image, Image.Image):
            raise ValueError(f"不支持的图片类型: {type(image)}")
        
        # 转换为RGB模式
        if image.mode not in ('RGB', 'L'):
            image = image.convert('RGB')
        
        # 编码为JPEG格式的Base64
        buffer = BytesIO()
        image.save(buffer, format='JPEG', quality=95)
        img_bytes = buffer.getvalue()
        base64_str = base64.b64encode(img_bytes).decode('utf-8')
        
        # 返回Data URL
        return f"data:image/jpeg;base64,{base64_str}"
    
    def recognize_image(self, image, **kwargs) -> List[Dict]:
        """
        识别整张图片
        :param image: PIL Image、numpy数组或文件路径
        :param kwargs: 额外参数（prompt: 自定义OCR提示词）
        :return: 识别结果列表
        """
        if not self.is_ready():
            print("❌ DeepSeek OCR引擎未就绪")
            return []
        
        try:
            # 转换图片为Base64
            image_data_url = self._image_to_base64(image)
            
            # 获取OCR提示词
            prompt = kwargs.get('prompt', self.ocr_prompt)
            
            # 调用API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": image_data_url}
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                max_tokens=4096,
                temperature=0.1  # 降低温度以提高识别稳定性
            )
            
            # 解析响应
            if response.choices and len(response.choices) > 0:
                content = response.choices[0].message.content
                
                # 清理结果，提取纯文本
                clean_text = self._clean_ocr_result(content)
                
                # 返回标准化格式
                return [{
                    'text': clean_text,
                    'confidence': 0.95,  # DeepSeek不返回置信度，给一个默认值
                    'box': None  # 全图识别没有位置信息
                }]
            else:
                return []
                
        except Exception as e:
            print(f"❌ DeepSeek OCR识别失败: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def recognize_region(self, image, rect, **kwargs) -> str:
        """
        识别图片中的指定区域
        :param image: PIL Image对象
        :param rect: OCRRect对象或坐标元组 (x1, y1, x2, y2)
        :param kwargs: 额外参数
        :return: 识别的文本字符串
        """
        if not self.is_ready():
            print("❌ DeepSeek OCR引擎未就绪")
            return ""
        
        try:
            # 确保image是PIL Image
            if not isinstance(image, Image.Image):
                if isinstance(image, str):
                    image = Image.open(image)
                elif hasattr(image, 'shape'):  # numpy数组
                    import numpy as np
                    if isinstance(image, np.ndarray):
                        image = Image.fromarray(image)
            
            # 解析矩形坐标
            if isinstance(rect, OCRRect):
                x1, y1, x2, y2 = rect.x1, rect.y1, rect.x2, rect.y2
            elif isinstance(rect, (tuple, list)) and len(rect) == 4:
                x1, y1, x2, y2 = rect
            else:
                raise ValueError(f"不支持的矩形格式: {type(rect)}")
            
            # 裁剪图片区域
            cropped = image.crop((x1, y1, x2, y2))
            
            # 识别裁剪后的图片
            results = self.recognize_image(cropped, **kwargs)
            
            # 提取文本
            if results and len(results) > 0:
                return results[0].get('text', '').strip()
            return ""
            
        except Exception as e:
            print(f"❌ DeepSeek OCR区域识别失败: {e}")
            import traceback
            traceback.print_exc()
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
            print("❌ DeepSeek OCR引擎未就绪")
            return {}
        
        results = {}
        for rect in rects:
            text = self.recognize_region(image, rect, **kwargs)
            results[rect] = text
        
        return results
    
    def batch_recognize(self, image_rect_pairs: List[Tuple], **kwargs):
        """
        批量处理多个图片
        :param image_rect_pairs: [(image, [rects]), ...] 列表
        :param kwargs: 额外参数
        :return: 识别结果列表
        """
        if not self.is_ready():
            print("❌ DeepSeek OCR引擎未就绪")
            return []
        
        results = []
        for image, rects in image_rect_pairs:
            if rects:
                # 有区域，识别各区域
                region_results = self.recognize_regions(image, rects, **kwargs)
                results.append(region_results)
            else:
                # 无区域，识别整图
                img_result = self.recognize_image(image, **kwargs)
                results.append(img_result)
        
        return results
    
    def test_connection(self) -> bool:
        """
        测试API连接是否正常
        :return: 是否连接成功
        """
        if not self.is_ready():
            print("❌ 引擎未就绪，无法测试连接")
            return False
        
        print("\n正在测试DeepSeek OCR连接...")
        
        try:
            # 创建一个简单的测试图片（白底黑字）
            from PIL import ImageDraw, ImageFont
            
            test_img = Image.new('RGB', (200, 60), color='white')
            draw = ImageDraw.Draw(test_img)
            
            # 绘制测试文字
            try:
                # 尝试使用系统字体
                font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
            except:
                # 使用默认字体
                font = ImageFont.load_default()
            
            draw.text((10, 15), "Test OCR", fill='black', font=font)
            
            # 测试识别
            results = self.recognize_image(test_img)
            
            if results and len(results) > 0:
                print(f"✓ 连接测试成功")
                print(f"  识别结果: {results[0].get('text', '')}")
                return True
            else:
                print("⚠️ API调用成功但未返回结果")
                return False
                
        except Exception as e:
            print(f"❌ 连接测试失败: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_config_info(self) -> Dict:
        """获取当前配置信息"""
        return {
            'engine_name': 'DeepSeek OCR',
            'platform': 'SiliconFlow',
            'model': self.model,
            'base_url': self.base_url,
            'api_key_configured': bool(self.api_key),
            'is_ready': self.is_ready()
        }


# 便捷函数
def create_deepseek_ocr_engine(api_key: str = None) -> DeepSeekOCREngine:
    """
    创建DeepSeek OCR引擎实例
    :param api_key: API密钥（可选，默认从配置读取）
    :return: DeepSeekOCREngine实例
    """
    return DeepSeekOCREngine(api_key=api_key)


if __name__ == "__main__":
    """测试代码"""
    print("=" * 60)
    print("DeepSeek OCR引擎测试（硅基流动平台）")
    print("=" * 60)
    
    # 创建引擎实例
    engine = DeepSeekOCREngine()
    
    if engine.is_ready():
        print("\n引擎配置信息:")
        config = engine.get_config_info()
        for key, value in config.items():
            print(f"  {key}: {value}")
        
        # 测试连接
        print("\n" + "=" * 60)
        engine.test_connection()
    else:
        print("\n引擎初始化失败，请检查配置")
        print("\n请确保在 config.py 中设置了正确的配置：")
        print("  DEEPSEEK_API_KEY = 'your_api_key'")
        print("\n或使用环境变量：")
        print("  export DEEPSEEK_API_KEY='your_api_key'")
