"""
配置管理模块

引擎启用控制：
所有OCR引擎都可以通过 ENABLED 开关控制是否启用。

1. 本地OCR引擎（推荐，开箱即用）：
   - paddle: PaddleOCR（极高精度，自动检测硬件）
   - rapid: RapidOCR（高速度，轻量级）
   
   控制开关（默认都启用）：
     PADDLE_ENABLED = True   # 是否启用PaddleOCR
     RAPID_ENABLED = True    # 是否启用RapidOCR
   
   如需禁用某个本地引擎（如仅使用PaddleOCR）：
     PADDLE_ENABLED = True   # 启用
     RAPID_ENABLED = False   # 禁用

2. 在线OCR服务（可选，需配置密钥）：
   - aliyun: 阿里云OCR（支持多种证件识别）
   - deepseek: DeepSeek OCR（AI大模型驱动）
   
   配置步骤：
   
   步骤1：配置API密钥（推荐按优先级顺序）
     方式1（推荐）：设置环境变量
       export ALIYUN_ACCESS_KEY_ID="your_key"
       export ALIYUN_ACCESS_KEY_SECRET="your_secret"
       export DEEPSEEK_API_KEY="your_key"
     
     方式2：在config.py中直接填写（不推荐，请勿上传到Git仓库）
       ALIYUN_ACCESS_KEY_ID = 'your_key'
       ALIYUN_ACCESS_KEY_SECRET = 'your_secret'
       DEEPSEEK_API_KEY = 'your_key'
   
   步骤2：启用对应引擎
     ALIYUN_ENABLED = True   # 启用阿里云OCR
     DEEPSEEK_ENABLED = True  # 启用DeepSeek OCR
"""

import os
import sys
from pathlib import Path
from lightweight_config import LightweightConfig


def get_resource_path(relative_path):
    """
    获取资源文件的绝对路径（支持PyInstaller打包）
    
    PyInstaller打包后，资源文件会被解压到临时目录sys._MEIPASS中。
    此函数会自动处理打包和开发环境的路径差异。
    
    :param relative_path: 相对于项目根目录的路径
    :return: 资源文件的绝对路径
    """
    try:
        # PyInstaller创建临时文件夹，路径存储在sys._MEIPASS中
        base_path = sys._MEIPASS
    except AttributeError:
        # 开发环境：使用脚本所在目录
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)


def is_frozen():
    """
    检测是否运行在PyInstaller打包环境中
    
    :return: True表示已打包，False表示开发环境
    """
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def get_executable_dir():
    """
    获取可执行文件所在目录
    
    用于存放外部配置文件、缓存数据等用户可修改的文件。
    - 打包环境：返回.exe文件所在目录
    - 开发环境：返回脚本所在目录
    
    :return: 可执行文件目录的绝对路径
    """
    if is_frozen():
        # 打包环境：sys.executable是.exe文件路径
        return os.path.dirname(os.path.abspath(sys.executable))
    else:
        # 开发环境：使用脚本所在目录
        return os.path.dirname(os.path.abspath(__file__))


class Config:
    """系统配置类"""
    
    # 应用信息
    APP_NAME = "OCR系统"
    APP_VERSION = "1.4.1"
    
    # 窗口配置
    WINDOW_WIDTH = 1400
    WINDOW_HEIGHT = 800
    
    # 支持的文件格式
    SUPPORTED_IMAGE_FORMATS = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.tif']
    SUPPORTED_PDF_FORMAT = ['.pdf']
    
    @classmethod
    def get_all_supported_formats(cls):
        """获取所有支持的文件格式"""
        return cls.SUPPORTED_IMAGE_FORMATS + cls.SUPPORTED_PDF_FORMAT
    
    # 颜色配置
    COLOR_PRIMARY = "#4CAF50"
    COLOR_SECONDARY = "#2196F3"
    COLOR_BACKGROUND = "#f8f9fa"
    COLOR_TOOLBAR = "#f0f0f0"
    COLOR_RECT_NORMAL = "red"
    COLOR_RECT_DRAWING = "blue"
    
    # OCR配置
    OCR_ENGINE = 'rapid'  # 引擎选择：rapid=RapidOCR（本地运行，轻量级，默认）, paddle=PaddleOCR（本地运行，极高精度，可选下载）, aliyun=阿里云OCR（在线服务，需配置密钥）, deepseek=DeepSeek OCR（在线服务，需配置密钥）
    # 注意：rapid引擎为默认引擎，体积小启动快；paddle引擎精度更高但需单独下载
    OCR_USE_GPU = 'auto'  # GPU设置：'auto'=自动检测，True=强制GPU，False=强制CPU
    OCR_USE_ANGLE_CLS = True  # 是否使用角度分类（处理旋转文字）
    OCR_LANG = 'ch'  # 语言：ch=中英文, en=英文, chinese_cht=繁体中文
    OCR_SHOW_LOG = False  # 是否显示详细日志（建议关闭以提高性能）
    
    # 本地OCR引擎配置,True(启用),False(禁用)
    PADDLE_ENABLED = True   # 是否启用PaddleOCR（本地引擎，高精度，可选下载）
    RAPID_ENABLED = True    # 是否启用RapidOCR（本地引擎，轻量级，默认打包）
    
    # ==================== 在线OCR配置（可选插件） ====================
    # 注意：在线OCR为可选功能，需要配置API密钥才能使用
    # 如不需要在线OCR，保持ENABLED=False即可，不影响本地OCR功能
    
    # 阿里云OCR配置（可选插件）
    ALIYUN_ENABLED = False  # 是否启用阿里云OCR（配置密钥后改为True）
    ALIYUN_ACCESS_KEY_ID = os.getenv('ALIYUN_ACCESS_KEY_ID', '')  # 阿里云AccessKey ID（从环境变量读取，或在此直接填写）
    ALIYUN_ACCESS_KEY_SECRET = os.getenv('ALIYUN_ACCESS_KEY_SECRET', '')  # 阿里云AccessKey Secret（从环境变量读取，或在此直接填写）
    ALIYUN_REGION = 'cn-hangzhou'  # 阿里云区域（根据实际API端点配置）
    ALIYUN_RECOGNITION_TYPE = 'general'  # 识别类型：general=通用, receipt=票据, id_card=身份证等
    
    # DeepSeek OCR配置（可选插件，硅基流动平台）
    DEEPSEEK_ENABLED = False  # 是否启用DeepSeek OCR（配置密钥后改为True）
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')  # API密钥（从环境变量读取，或在此直接填写）
    DEEPSEEK_BASE_URL = 'https://api.siliconflow.cn/v1'  # 硅基流动API端点
    DEEPSEEK_MODEL = 'deepseek-ai/DeepSeek-OCR'  # DeepSeek OCR模型名称
    DEEPSEEK_OCR_PROMPT = '<image>\nFree OCR.'  # OCR识别提示词（Free OCR模式：无布局标记，纯文本输出）
    # ================================================================
    
    # PaddleOCR精度优化参数（已内置到优化版引擎中，这里仅作记录）
    # 注意：优化版PaddleOCR引擎已自动应用以下最优参数
    # 检测模型参数
    OCR_DET_DB_THRESH = 0.2  # 检测阈值（降低提高召回率）- 已应用
    OCR_DET_DB_BOX_THRESH = 0.4  # 文本框阈值（降低检测更多文本）- 已应用
    OCR_DET_DB_UNCLIP_RATIO = 2.0  # 文本框扩大比例（增加提高准确率）- 已应用
    
    # 识别模型参数
    OCR_REC_BATCH_NUM = 6  # 识别批次大小 - 已应用
    
    # 高精度模型（优化版引擎已自动使用最优模型）
    OCR_USE_SERVER_MODEL = True  # 使用server模型（精度更高）- 已应用
    
    # 图片显示配置
    MAX_DISPLAY_SCALE = 1.0  # 最大显示比例（不放大）
    MIN_RECT_SIZE = 10  # 最小识别区域尺寸（像素）
    
    # PDF转图片配置
    PDF_ZOOM_FACTOR = 2  # PDF转图片的缩放因子
    
    # 文件重命名配置
    RENAME_INVALID_CHARS = r'\/:*?"<>|'  # 文件名中的非法字符
    
    # Excel导出配置
    EXCEL_HEADER_FONT_SIZE = 11
    EXCEL_MAX_COLUMN_WIDTH = 50
    
    # 配置文件路径（便携式设计）
    # 优先使用项目本地目录，回退到用户主目录
    @classmethod
    def _get_config_dir(cls):
        """获取配置目录路径（便携式）"""
        # 首选：可执行文件目录（便携式，支持PyInstaller打包）
        exe_dir = get_executable_dir()
        local_config_dir = os.path.join(exe_dir, ".ocr_system_config")
        
        # 如果本地配置目录存在或可创建，使用它
        if os.path.exists(local_config_dir) or os.access(exe_dir, os.W_OK):
            return local_config_dir
        
        # 回退：用户主目录
        return os.path.join(os.path.expanduser("~"), ".ocr_system")
    
    @classmethod
    def _get_config_file(cls):
        """获取配置文件路径"""
        return os.path.join(cls._get_config_dir(), "config.json")
    
    @classmethod
    def load_user_config(cls):
        """
        加载用户配置（使用轻量级配置管理器）
        
        保持向后兼容：
        1. 优先尝试加载新的INI格式配置
        2. 如果存在旧的JSON格式配置，自动迁移
        """
        # 尝试加载INI格式配置
        ini_config = LightweightConfig.load()
        
        # 检查是否存在旧的JSON格式配置
        old_json_file = cls._get_config_file()
        if os.path.exists(old_json_file):
            try:
                # 延迟导入json模块（仅在需要迁移时）
                import json
                with open(old_json_file, 'r', encoding='utf-8') as f:
                    json_config = json.load(f)
                
                # 合并配置（JSON配置优先）
                merged_config = ini_config.copy()
                for key, value in json_config.items():
                    merged_config[key] = str(value)
                
                # 保存为INI格式
                LightweightConfig.save(merged_config)
                
                # 备份并删除旧的JSON文件
                backup_file = old_json_file + '.backup'
                try:
                    os.rename(old_json_file, backup_file)
                    print(f"已将旧配置文件迁移到: {backup_file}")
                except Exception as e:
                    print(f"备份旧配置文件失败: {e}")
                
                return merged_config
            
            except Exception as e:
                print(f"迁移旧配置文件失败: {e}")
        
        return ini_config
    
    @classmethod
    def save_user_config(cls, config_dict):
        """
        保存用户配置（使用轻量级配置管理器）
        
        :param config_dict: 配置字典
        :return: 是否保存成功
        """
        # 转换所有值为字符串
        str_config = {k: str(v) for k, v in config_dict.items()}
        return LightweightConfig.save(str_config)
    
    @classmethod
    def get_config_value(cls, key: str, default=None):
        """
        获取配置值（从轻量级配置管理器）
        
        :param key: 配置键
        :param default: 默认值
        :return: 配置值
        """
        return LightweightConfig.get(key, default)
    
    @classmethod
    def get_config_bool(cls, key: str, default: bool = False) -> bool:
        """
        获取布尔类型配置值
        
        :param key: 配置键
        :param default: 默认值
        :return: 布尔值
        """
        return LightweightConfig.get_bool(key, default)
    
    @classmethod
    def get_config_int(cls, key: str, default: int = 0) -> int:
        """
        获取整数类型配置值
        
        :param key: 配置键
        :param default: 默认值
        :return: 整数值
        """
        return LightweightConfig.get_int(key, default)
    
    @classmethod
    def get_config_float(cls, key: str, default: float = 0.0) -> float:
        """
        获取浮点数类型配置值
        
        :param key: 配置键
        :param default: 默认值
        :return: 浮点数值
        """
        return LightweightConfig.get_float(key, default)
    
    @classmethod
    def set_config_value(cls, key: str, value) -> bool:
        """
        设置配置值
        
        :param key: 配置键
        :param value: 配置值
        :return: 是否设置成功
        """
        return LightweightConfig.set(key, value)


class OCRRect:
    """OCR识别区域类"""
    
    def __init__(self, x1, y1, x2, y2, name=""):
        """
        初始化识别区域
        :param x1: 左上角x坐标
        :param y1: 左上角y坐标
        :param x2: 右下角x坐标
        :param y2: 右下角y坐标
        :param name: 区域名称
        """
        self.x1 = min(x1, x2)
        self.y1 = min(y1, y2)
        self.x2 = max(x1, x2)
        self.y2 = max(y1, y2)
        self.name = name
        self.text = ""  # 识别结果文本
    
    def get_coords(self):
        """获取坐标元组"""
        return (self.x1, self.y1, self.x2, self.y2)
    
    def get_size(self):
        """获取区域尺寸"""
        return (self.x2 - self.x1, self.y2 - self.y1)
    
    def contains_point(self, x, y):
        """判断点是否在区域内"""
        return self.x1 <= x <= self.x2 and self.y1 <= y <= self.y2
    
    def is_valid(self, min_size=10):
        """判断区域是否有效"""
        width = self.x2 - self.x1
        height = self.y2 - self.y1
        return width >= min_size and height >= min_size
    
    def to_dict(self):
        """转换为字典"""
        return {
            'x1': self.x1,
            'y1': self.y1,
            'x2': self.x2,
            'y2': self.y2,
            'name': self.name,
            'text': self.text
        }
    
    @classmethod
    def from_dict(cls, data):
        """从字典创建实例"""
        rect = cls(data['x1'], data['y1'], data['x2'], data['y2'], data.get('name', ''))
        rect.text = data.get('text', '')
        return rect
