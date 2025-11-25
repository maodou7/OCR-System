"""
阿里云OCR识别引擎 - 新版SDK实现
使用阿里云OCR API 2021-07-07版本
支持统一的文字识别接口 RecognizeAllText
"""

import os
import sys
import base64
from io import BytesIO
from PIL import Image
# 延迟导入numpy，减小打包体积
# import numpy as np  # 改为按需导入
from typing import List, Dict, Optional
from config import Config

# 检查新版SDK依赖
try:
    from alibabacloud_ocr_api20210707.client import Client as OcrClient
    from alibabacloud_tea_openapi import models as open_api_models
    from alibabacloud_ocr_api20210707 import models as ocr_models
    from alibabacloud_tea_util import models as util_models
    from alibabacloud_tea_util.client import Client as UtilClient
    ALIYUN_NEW_SDK_AVAILABLE = True
except ImportError:
    ALIYUN_NEW_SDK_AVAILABLE = False
    print("警告: 阿里云新版SDK未安装")
    print("请运行: pip install alibabacloud-ocr-api20210707 alibabacloud-tea-openapi alibabacloud-tea-util")


class AliyunOCRNewEngine:
    """阿里云OCR识别引擎 - 新版API"""
    
    # 支持的识别类型映射（基于阿里云官方API文档）
    RECOGNITION_TYPES = {
        'general': 'Advanced',         # 通用文字识别（高精版）
        'accurate': 'Advanced',        # 高精度文字识别（同Advanced）
        'table': 'Table',              # 表格识别
        'multilang': 'MultiLang',      # 多语言识别
        'receipt': 'BankReceipt',      # 银行回单识别
        'id_card': 'IdCard',           # 身份证识别
        'passport': 'Passport',        # 护照识别
        'driving_license': 'DriverLicense',      # 驾驶证
        'vehicle_license': 'VehicleLicense',     # 行驶证
        'business_license': 'BusinessLicense',   # 营业执照
        'bank_card': 'BankCard',       # 银行卡
        'invoice': 'VATInvoice',       # 增值税发票
        'train_ticket': 'TrainTicket', # 火车票
        'taxi_receipt': 'TaxiReceipt', # 出租车发票
        'quota_invoice': 'QuotaInvoice',         # 定额发票
        'air_itinerary': 'AirItinerary',         # 航空行程单
        'hotel_consume': 'HotelConsume',         # 酒店账单
        'medical_record': 'MedicalRecordOCR',    # 病历识别
    }
    
    def __init__(self, access_key_id=None, access_key_secret=None, endpoint=None):
        """
        初始化阿里云OCR引擎
        :param access_key_id: AccessKey ID（可选，默认从config.py读取）
        :param access_key_secret: AccessKey Secret（可选，默认从config.py读取）
        :param endpoint: API端点（默认：ocr-api.cn-hangzhou.aliyuncs.com）
        """
        self.is_initialized = False
        self.client = None
        
        # 获取凭证（优先级：参数 > config.py配置 > 环境变量）
        self.access_key_id = (
            access_key_id or 
            getattr(Config, 'ALIYUN_ACCESS_KEY_ID', None) or 
            os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_ID') or
            os.environ.get('ALIYUN_ACCESS_KEY_ID')
        )
        
        self.access_key_secret = (
            access_key_secret or 
            getattr(Config, 'ALIYUN_ACCESS_KEY_SECRET', None) or 
            os.environ.get('ALIBABA_CLOUD_ACCESS_KEY_SECRET') or
            os.environ.get('ALIYUN_ACCESS_KEY_SECRET')
        )
        
        self.endpoint = endpoint or 'ocr-api.cn-hangzhou.aliyuncs.com'
        
        # 检查SDK和凭证
        if not ALIYUN_NEW_SDK_AVAILABLE:
            print("错误: 阿里云新版SDK未安装")
            return
        
        if not self.access_key_id or not self.access_key_secret:
            print("❌ 错误: 缺少阿里云凭证")
            print("\n请在 config.py 中设置:")
            print("  ALIYUN_ACCESS_KEY_ID = 'your_key_id'")
            print("  ALIYUN_ACCESS_KEY_SECRET = 'your_key_secret'")
            print("\n或设置环境变量:")
            print("  ALIBABA_CLOUD_ACCESS_KEY_ID")
            print("  ALIBABA_CLOUD_ACCESS_KEY_SECRET")
            return
        
        # 初始化客户端
        try:
            self.client = self._create_client()
            self.is_initialized = True
            print("✓ 阿里云OCR引擎初始化成功（新版API）")
            
            # 显示配置来源
            if access_key_id:
                print(f"  - 配置来源: 参数传入")
            elif getattr(Config, 'ALIYUN_ACCESS_KEY_ID', None):
                print(f"  - 配置来源: config.py")
            else:
                print(f"  - 配置来源: 环境变量")
            
            print(f"  - API端点: {self.endpoint}")
            print(f"  - AccessKey: {self.access_key_id[:10]}***")
        except Exception as e:
            print(f"阿里云OCR引擎初始化失败: {e}")
            self.is_initialized = False
    
    def _create_client(self) -> OcrClient:
        """创建阿里云OCR客户端"""
        config = open_api_models.Config(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret
        )
        config.endpoint = self.endpoint
        return OcrClient(config)
    
    def is_ready(self) -> bool:
        """检查引擎是否就绪"""
        return self.is_initialized and self.client is not None
    
    def _image_to_url(self, image) -> str:
        """
        将图片转换为URL或Base64
        :param image: PIL Image、numpy数组、文件路径或URL
        :return: 图片URL（http/https）或None（使用body传输）
        """
        if isinstance(image, str):
            # 如果是HTTP/HTTPS URL，直接返回
            if image.startswith('http://') or image.startswith('https://'):
                return image
        
        # 其他情况返回None，使用body传输
        return None
    
    def _image_to_body(self, image) -> bytes:
        """
        将图片转换为二进制数据
        :param image: PIL Image、numpy数组或文件路径
        :return: 图片二进制数据
        """
        if isinstance(image, str):
            # 文件路径
            if not image.startswith('http'):
                with open(image, 'rb') as f:
                    return f.read()
        elif isinstance(image, Image.Image):
            # PIL Image
            buffer = BytesIO()
            image.save(buffer, format='PNG')
            return buffer.getvalue()
        else:
            # 尝试处理numpy数组（按需导入）
            try:
                import numpy as np
                if isinstance(image, np.ndarray):
                    # numpy数组
                    img = Image.fromarray(image.astype('uint8'))
                    buffer = BytesIO()
                    img.save(buffer, format='PNG')
                    return buffer.getvalue()
            except ImportError:
                pass
        
        raise ValueError("不支持的图片格式")
    
    def recognize_image(self, image, recognition_type='general', **kwargs) -> Optional[Dict]:
        """
        识别整张图片
        :param image: PIL Image、numpy数组、文件路径或URL
        :param recognition_type: 识别类型（general, id_card, receipt等）
        :param kwargs: 额外参数
        :return: 识别结果字典
        """
        if not self.is_ready():
            raise RuntimeError("阿里云OCR引擎未就绪")
        
        try:
            # 获取识别类型
            ocr_type = self.RECOGNITION_TYPES.get(recognition_type, 'GeneralText')
            
            # 准备请求
            request = ocr_models.RecognizeAllTextRequest()
            request.type = ocr_type
            
            # 设置图片（优先使用URL）
            url = self._image_to_url(image)
            if url:
                request.url = url
            else:
                request.body = self._image_to_body(image)
            
            # 额外参数
            if 'output_figure' in kwargs:
                request.output_figure = kwargs['output_figure']
            if 'output_table' in kwargs:
                request.output_table = kwargs['output_table']
            
            # 调用API
            runtime = util_models.RuntimeOptions()
            response = self.client.recognize_all_text_with_options(request, runtime)
            
            # 解析结果
            if response and response.body and response.body.data:
                return self._parse_response(response.body.data)
            else:
                return None
        
        except Exception as error:
            print(f"阿里云OCR识别失败: {error}")
            if hasattr(error, 'message'):
                print(f"错误消息: {error.message}")
            if hasattr(error, 'data') and error.data:
                print(f"诊断建议: {error.data.get('Recommend', 'N/A')}")
            return None
    
    def _parse_response(self, data) -> Dict:
        """
        解析API响应数据
        :param data: API返回的data字段
        :return: 标准化的识别结果
        """
        result = {
            'success': True,
            'content': '',
            'items': [],
            'raw_data': data
        }
        
        # 提取文本内容
        if hasattr(data, 'content'):
            result['content'] = data.content
        
        # 提取详细项
        if hasattr(data, 'prism_words_info'):
            words_info = data.prism_words_info
            if words_info:
                for word in words_info:
                    item = {
                        'text': getattr(word, 'word', ''),
                        'confidence': getattr(word, 'prob', 0.0),
                        'position': None
                    }
                    
                    # 提取位置信息
                    if hasattr(word, 'pos'):
                        pos = word.pos
                        if pos:
                            item['position'] = {
                                'x': getattr(pos, 'x', 0),
                                'y': getattr(pos, 'y', 0),
                                'w': getattr(pos, 'w', 0),
                                'h': getattr(pos, 'h', 0)
                            }
                    
                    result['items'].append(item)
        
        # 如果没有详细项，尝试从content提取
        if not result['items'] and result['content']:
            result['items'] = [{'text': result['content'], 'confidence': 1.0}]
        
        return result
    
    def recognize_region(self, image, rect, recognition_type='general') -> str:
        """
        识别图片中的指定区域
        :param image: PIL Image对象
        :param rect: OCRRect对象或坐标元组 (x1, y1, x2, y2)
        :param recognition_type: 识别类型
        :return: 识别的文本字符串
        """
        if not self.is_ready():
            raise RuntimeError("阿里云OCR引擎未就绪")
        
        # 获取坐标
        if hasattr(rect, 'get_coords'):
            coords = rect.get_coords()
        else:
            coords = rect
        
        # 裁剪区域
        cropped = image.crop(coords)
        
        # 识别裁剪后的图片
        result = self.recognize_image(cropped, recognition_type)
        
        if result and result.get('content'):
            return result['content']
        elif result and result.get('items'):
            # 拼接所有文本
            return ' '.join([item['text'] for item in result['items']])
        else:
            return ""
    
    def recognize_regions(self, image, rects, recognition_type='general') -> Dict:
        """
        批量识别多个区域
        :param image: PIL Image对象
        :param rects: OCRRect对象列表
        :param recognition_type: 识别类型
        :return: 识别结果字典 {rect: text}
        """
        if not self.is_ready():
            raise RuntimeError("阿里云OCR引擎未就绪")
        
        results = {}
        
        for rect in rects:
            text = self.recognize_region(image, rect, recognition_type)
            results[rect] = text
            
            # 更新rect的text属性
            if hasattr(rect, 'text'):
                rect.text = text
        
        return results
    
    def get_supported_types(self) -> Dict[str, str]:
        """获取支持的识别类型"""
        return {
            key: f"{value} ({key})" 
            for key, value in self.RECOGNITION_TYPES.items()
        }
    
    def test_connection(self) -> bool:
        """
        测试连接是否正常
        :return: 是否连接成功
        """
        if not self.is_ready():
            return False
        
        try:
            # 使用一个小的测试图片
            from PIL import Image, ImageDraw, ImageFont
            
            # 创建一个简单的测试图片
            test_img = Image.new('RGB', (200, 100), color='white')
            draw = ImageDraw.Draw(test_img)
            draw.text((10, 40), "测试Test", fill='black')
            
            # 尝试识别
            result = self.recognize_image(test_img, 'general')
            
            if result:
                print("✓ 阿里云OCR连接测试成功")
                return True
            else:
                print("✗ 阿里云OCR连接测试失败（无返回结果）")
                return False
        
        except Exception as e:
            print(f"✗ 阿里云OCR连接测试失败: {e}")
            return False


# 便捷函数
def create_aliyun_ocr_engine(access_key_id=None, access_key_secret=None):
    """
    创建阿里云OCR引擎实例
    :param access_key_id: AccessKey ID（可选，默认从配置读取）
    :param access_key_secret: AccessKey Secret（可选，默认从配置读取）
    :return: AliyunOCRNewEngine实例
    """
    return AliyunOCRNewEngine(access_key_id, access_key_secret)


if __name__ == "__main__":
    """测试代码"""
    print("="*60)
    print("阿里云OCR引擎测试（新版API）")
    print("="*60)
    
    # 创建引擎实例
    engine = AliyunOCRNewEngine()
    
    if engine.is_ready():
        print("\n引擎初始化成功！")
        
        # 显示支持的类型
        print("\n支持的识别类型：")
        for key, desc in engine.get_supported_types().items():
            print(f"  - {desc}")
        
        # 测试连接
        print("\n测试连接...")
        engine.test_connection()
    else:
        print("\n引擎初始化失败，请检查配置")
        print("\n请确保在 config.py 中设置了正确的凭证：")
        print("  ALIYUN_ACCESS_KEY_ID = 'your_key_id'")
        print("  ALIYUN_ACCESS_KEY_SECRET = 'your_key_secret'")
