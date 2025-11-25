"""
统一的OCR引擎管理系统
支持无缝切换：PaddleOCR（优化版）、阿里云OCR、RapidOCR

使用方式：
    manager = OCREngineManager()
    manager.set_engine('paddle')  # 或 'aliyun', 'rapid'
    result = manager.recognize_image(image)
"""

import os
from typing import Optional, List, Dict, Tuple
from enum import Enum
from PIL import Image
# 延迟导入重型库，减小打包体积
# import numpy as np  # 改为按需导入（在具体引擎中使用时才导入）

# 延迟导入各引擎（提高启动速度）
# from ocr_engine_aliyun_new import AliyunOCRNewEngine  # 改为按需导入
from config import Config, OCRRect


class EngineType(Enum):
    """支持的引擎类型"""
    ALIYUN = "aliyun"      # 阿里云OCR
    PADDLE = "paddle"      # PaddleOCR
    RAPID = "rapid"        # RapidOCR
    DEEPSEEK = "deepseek"  # DeepSeek OCR


class EngineInfo:
    """引擎信息类"""
    
    def __init__(self, name: str, description: str, speed: str, accuracy: str, available: bool):
        self.name = name
        self.description = description
        self.speed = speed  # 快/中/慢
        self.accuracy = accuracy  # 高/中/低
        self.available = available


class OCREngineManager:
    """
    OCR引擎管理器
    统一接口，支持多个OCR引擎的切换
    """
    
    # 引擎信息表
    ENGINE_INFO = {
        EngineType.ALIYUN: EngineInfo(
            "Alibaba OCR",
            "阿里云在线OCR服务，支持多种特殊证件识别",
            "中",
            "高",
            True
        ),
        EngineType.PADDLE: EngineInfo(
            "PaddleOCR (优化版)",
            "百度飞桨OCR框架-高性能优化版，适合复杂场景（文字/数字/符号/时间）",
            "快",
            "极高",
            False  # 根据实际安装情况
        ),
        EngineType.RAPID: EngineInfo(
            "RapidOCR",
            "快速轻量级OCR引擎",
            "快",
            "中",
            False  # 根据实际安装情况
        ),
        EngineType.DEEPSEEK: EngineInfo(
            "DeepSeek OCR",
            "硅基流动DeepSeek-OCR服务（当前限免测试）",
            "快",
            "待测试",
            False  # 根据实际安装情况
        ),
    }
    
    def __init__(self, engine_type: str = None):
        """
        初始化引擎管理器
        :param engine_type: 初始引擎类型 ('aliyun', 'paddle', 'rapid')
        """
        self.current_engine = None
        self.current_engine_type = None
        self._engine_instances = {}  # 缓存引擎实例
        
        # 检查各引擎的可用性
        self._check_engine_availability()
        
        # 确定初始引擎
        # 如果未指定，则使用配置中的默认引擎，或者按优先级选择
        if not engine_type:
            # 优先使用配置的默认引擎
            default_engine = getattr(Config, 'OCR_ENGINE', 'aliyun')
            if self.is_engine_available(default_engine):
                engine_type = default_engine
            else:
                # 如果默认引擎不可用，按优先级选择：aliyun > paddle > rapid
                for et in ['aliyun', 'paddle', 'rapid']:
                    if self.is_engine_available(et):
                        engine_type = et
                        break
        
        # 1. 优先初始化当前选定的引擎（确保用户能尽快使用）
        if engine_type and self.is_engine_available(engine_type):
            print(f"正在初始化默认引擎: {engine_type}...")
            self.set_engine(engine_type)
            
    def init_background_engines(self):
        """
        后台静默初始化其他引擎（按顺序：Aliyun -> Paddle -> Rapid -> DeepSeek）
        注意：set_engine已经初始化了当前引擎，这里只需要初始化剩下的
        """
        init_order = [EngineType.ALIYUN, EngineType.PADDLE, EngineType.RAPID, EngineType.DEEPSEEK]
        
        for et in init_order:
            # 跳过已经初始化的当前引擎
            if self.current_engine_type == et:
                continue
                
            # 检查可用性
            if not self.ENGINE_INFO[et].available:
                continue
                
            # 检查是否已初始化
            if et in self._engine_instances:
                continue
                
            try:
                print(f"正在后台初始化引擎: {et.value}...")
                instance = self._create_engine(et)
                if instance:
                    self._engine_instances[et] = instance
                    print(f"✓ {self.ENGINE_INFO[et].name} 初始化完成")
            except Exception as e:
                print(f"❌ {self.ENGINE_INFO[et].name} 初始化失败: {e}")
    
    @staticmethod
    def _check_engine_availability():
        """检查各引擎的可用性"""
        # 检查阿里云OCR（检查SDK和密钥配置）
        try:
            from alibabacloud_ocr_api20210707.client import Client as OcrClient
            # 检查config.py中是否配置了密钥
            if hasattr(Config, 'ALIYUN_ACCESS_KEY_ID') and Config.ALIYUN_ACCESS_KEY_ID:
                OCREngineManager.ENGINE_INFO[EngineType.ALIYUN].available = True
        except ImportError:
            pass
        
        # 检查PaddleOCR（使用优化版引擎）
        try:
            from paddleocr import PaddleOCR
            import numpy as np
            OCREngineManager.ENGINE_INFO[EngineType.PADDLE].available = True
        except ImportError:
            pass
        
        # 检查RapidOCR
        try:
            from rapidocr_onnxruntime import RapidOCR
            OCREngineManager.ENGINE_INFO[EngineType.RAPID].available = True
        except ImportError:
            pass
        
        # 检查DeepSeek OCR（检查SDK和API Key配置）
        try:
            from openai import OpenAI
            # 检查config.py中是否配置了API Key
            if hasattr(Config, 'DEEPSEEK_API_KEY') and Config.DEEPSEEK_API_KEY:
                OCREngineManager.ENGINE_INFO[EngineType.DEEPSEEK].available = True
        except ImportError:
            pass
    
    def is_engine_available(self, engine_type: str) -> bool:
        """
        检查引擎是否可用
        :param engine_type: 引擎类型
        :return: 是否可用
        """
        try:
            engine = EngineType(engine_type)
            return self.ENGINE_INFO[engine].available
        except (ValueError, KeyError):
            return False
    
    def get_available_engines(self) -> List[Tuple[str, str, str, str]]:
        """
        获取所有可用引擎列表
        :return: [(名称, 描述, 速度, 精度), ...]
        """
        available = []
        for engine_type, info in self.ENGINE_INFO.items():
            if info.available:
                available.append((
                    engine_type.value,
                    info.name,
                    info.description,
                    f"速度:{info.speed} 精度:{info.accuracy}"
                ))
        return available
    
    def set_engine(self, engine_type: str) -> bool:
        """
        切换OCR引擎
        :param engine_type: 引擎类型 ('aliyun', 'paddle', 'rapid')
        :return: 是否切换成功
        """
        try:
            engine = EngineType(engine_type)
        except ValueError:
            print(f"❌ 不支持的引擎类型: {engine_type}")
            return False
        
        # 检查引擎是否可用
        if not self.is_engine_available(engine_type):
            print(f"❌ 引擎 {engine.value} 不可用")
            return False
        
        # 从缓存中获取或创建引擎实例
        if engine not in self._engine_instances:
            try:
                instance = self._create_engine(engine)
                if not instance:
                    return False
                self._engine_instances[engine] = instance
            except Exception as e:
                print(f"❌ 初始化引擎失败: {e}")
                return False
        
        self.current_engine = self._engine_instances[engine]
        self.current_engine_type = engine
        
        info = self.ENGINE_INFO[engine]
        print(f"✓ 已切换到 {info.name}")
        print(f"  - 描述: {info.description}")
        print(f"  - 速度: {info.speed} | 精度: {info.accuracy}")
        
        return True
    
    @staticmethod
    def _create_engine(engine_type: EngineType):
        """
        创建引擎实例（延迟导入，提高性能）
        :param engine_type: 引擎类型
        :return: 引擎实例
        """
        if engine_type == EngineType.ALIYUN:
            # 延迟导入阿里云OCR引擎
            from ocr_engine_aliyun_new import AliyunOCRNewEngine
            return AliyunOCRNewEngine()
        
        elif engine_type == EngineType.PADDLE:
            from ocr_engine_paddle import PaddleOCREngine
            # 从配置读取GPU设置（None表示自动检测）
            use_gpu_config = getattr(Config, 'OCR_USE_GPU', None)
            # 如果配置为True则强制使用GPU，False则强制CPU，None则自动检测
            use_gpu = use_gpu_config if isinstance(use_gpu_config, bool) else None
            lang = getattr(Config, 'OCR_LANG', 'ch')
            return PaddleOCREngine(use_gpu=use_gpu, lang=lang)
        
        elif engine_type == EngineType.RAPID:
            from ocr_engine_rapid import RapidOCREngine
            return RapidOCREngine()
        
        elif engine_type == EngineType.DEEPSEEK:
            from ocr_engine_deepseek import DeepSeekOCREngine
            return DeepSeekOCREngine()
        
        return None
    
    def is_ready(self) -> bool:
        """
        检查当前引擎是否就绪
        :return: 是否就绪
        """
        if not self.current_engine:
            return False
        return self.current_engine.is_ready()
    
    def recognize_image(self, image, **kwargs):
        """
        识别整张图片
        :param image: PIL Image或numpy数组
        :param kwargs: 引擎特定参数
        :return: 识别结果（格式统一化）
        """
        if not self.is_ready():
            print("❌ 当前引擎未就绪")
            return None
        
        try:
            result = self.current_engine.recognize_image(image, **kwargs)
            return self._normalize_result(result)
        except Exception as e:
            print(f"❌ 识别失败: {e}")
            return None
    
    def recognize_region(self, image, rect, **kwargs) -> str:
        """
        识别指定区域
        :param image: PIL Image
        :param rect: 坐标元组或OCRRect对象
        :param kwargs: 引擎特定参数
        :return: 识别文本
        """
        if not self.is_ready():
            print("❌ 当前引擎未就绪")
            return ""
        
        try:
            return self.current_engine.recognize_region(image, rect, **kwargs)
        except Exception as e:
            print(f"❌ 区域识别失败: {e}")
            return ""
    
    def recognize_regions(self, image, rects: List[OCRRect], **kwargs) -> Dict[OCRRect, str]:
        """
        批量识别多个区域
        :param image: PIL Image
        :param rects: OCRRect对象列表
        :param kwargs: 引擎特定参数
        :return: {rect: text} 字典
        """
        if not self.is_ready():
            print("❌ 当前引擎未就绪")
            return {}
        
        try:
            return self.current_engine.recognize_regions(image, rects, **kwargs)
        except Exception as e:
            print(f"❌ 批量识别失败: {e}")
            return {}
    
    def batch_recognize(self, image_rect_pairs: List[Tuple], **kwargs):
        """
        批量处理多个图片
        :param image_rect_pairs: [(image, [rects]), ...] 列表
        :param kwargs: 引擎特定参数
        :return: 识别结果列表
        """
        if not self.is_ready():
            print("❌ 当前引擎未就绪")
            return []
        
        try:
            return self.current_engine.batch_recognize(image_rect_pairs, **kwargs)
        except Exception as e:
            print(f"❌ 批量处理失败: {e}")
            return []
    
    @staticmethod
    def _normalize_result(result):
        """
        统一化识别结果格式
        注：各引擎返回格式差异大，此处保持原格式，由调用者处理
        :param result: 原始识别结果
        :return: 统一化结果
        """
        # 保持原格式，供上层处理
        return result
    
    def get_current_engine_info(self) -> Optional[Dict]:
        """
        获取当前引擎信息
        :return: 引擎信息字典
        """
        if not self.current_engine_type:
            return None
        
        info = self.ENGINE_INFO[self.current_engine_type]
        return {
            'type': self.current_engine_type.value,
            'name': info.name,
            'description': info.description,
            'speed': info.speed,
            'accuracy': info.accuracy,
            'available': info.available,
            'is_ready': self.is_ready()
        }
    
    def print_engine_status(self):
        """打印所有引擎状态"""
        print("\n" + "="*60)
        print("OCR 引擎状态")
        print("="*60)
        
        for engine_type, info in self.ENGINE_INFO.items():
            status = "✓ 可用" if info.available else "✗ 不可用"
            current = " (当前)" if self.current_engine_type == engine_type else ""
            
            print(f"\n{info.name}{current}")
            print(f"  状态: {status}")
            print(f"  描述: {info.description}")
            print(f"  速度: {info.speed} | 精度: {info.accuracy}")
        
        if self.current_engine_type:
            print(f"\n当前引擎: {self.ENGINE_INFO[self.current_engine_type].name}")
            print(f"引擎就绪: {'✓ 是' if self.is_ready() else '✗ 否'}")
        
        print("="*60)
    
    def print_available_engines(self):
        """打印所有可用引擎"""
        available = self.get_available_engines()
        
        if not available:
            print("❌ 没有可用的OCR引擎")
            return
        
        print("\n可用的OCR引擎:")
        print("-" * 60)
        
        for i, (engine_type, name, description, specs) in enumerate(available, 1):
            current = " ◄ 当前" if engine_type == self.current_engine_type.value else ""
            print(f"{i}. {name}{current}")
            print(f"   类型: {engine_type}")
            print(f"   描述: {description}")
            print(f"   规格: {specs}")
            print()


class EngineContext:
    """
    引擎上下文管理器
    用于临时切换引擎
    
    使用方式:
        with EngineContext(manager, 'paddle'):
            result = manager.recognize_image(image)
        # 自动恢复之前的引擎
    """
    
    def __init__(self, manager: OCREngineManager, engine_type: str):
        self.manager = manager
        self.engine_type = engine_type
        self.previous_engine = None
    
    def __enter__(self):
        self.previous_engine = self.manager.current_engine_type
        self.manager.set_engine(self.engine_type)
        return self.manager
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.previous_engine:
            self.manager.set_engine(self.previous_engine.value)


# 创建全局管理器实例
_global_manager = None

def get_ocr_manager() -> OCREngineManager:
    """获取全局OCR引擎管理器"""
    global _global_manager
    if _global_manager is None:
        _global_manager = OCREngineManager()
    return _global_manager

def set_ocr_engine(engine_type: str) -> bool:
    """全局设置OCR引擎"""
    return get_ocr_manager().set_engine(engine_type)

def get_available_engines() -> List[Tuple[str, str, str, str]]:
    """获取所有可用引擎"""
    return get_ocr_manager().get_available_engines()
