"""
轻量级配置管理模块

避免使用json模块，使用简单的INI格式解析器，实现配置缓存和验证。
这个模块的目标是减少启动时的配置加载开销。
"""

import os
import sys
from typing import Dict, Any, Optional, List


class LightweightConfig:
    """
    轻量级配置管理器
    
    使用简单的INI格式替代JSON，避免导入json模块。
    实现配置缓存机制，减少重复解析开销。
    """
    
    # 配置缓存
    _config_cache: Optional[Dict[str, Any]] = None
    _config_file_mtime: Optional[float] = None
    
    # 默认配置
    DEFAULT_CONFIG = {
        # 应用信息
        'APP_NAME': 'OCR系统',
        'APP_VERSION': '1.4.1',
        
        # 窗口配置
        'WINDOW_WIDTH': '1400',
        'WINDOW_HEIGHT': '800',
        
        # OCR配置
        'OCR_ENGINE': 'rapid',
        'OCR_USE_GPU': 'auto',
        'OCR_USE_ANGLE_CLS': 'True',
        'OCR_LANG': 'ch',
        'OCR_SHOW_LOG': 'False',
        
        # 引擎启用配置
        'PADDLE_ENABLED': 'True',
        'RAPID_ENABLED': 'True',
        'ALIYUN_ENABLED': 'False',
        'DEEPSEEK_ENABLED': 'False',
        
        # 阿里云配置
        'ALIYUN_ACCESS_KEY_ID': '',
        'ALIYUN_ACCESS_KEY_SECRET': '',
        'ALIYUN_REGION': 'cn-hangzhou',
        'ALIYUN_RECOGNITION_TYPE': 'general',
        
        # DeepSeek配置
        'DEEPSEEK_API_KEY': '',
        'DEEPSEEK_BASE_URL': 'https://api.siliconflow.cn/v1',
        'DEEPSEEK_MODEL': 'deepseek-ai/DeepSeek-OCR',
        'DEEPSEEK_OCR_PROMPT': '<image>\nFree OCR.',
        
        # PaddleOCR参数
        'OCR_DET_DB_THRESH': '0.2',
        'OCR_DET_DB_BOX_THRESH': '0.4',
        'OCR_DET_DB_UNCLIP_RATIO': '2.0',
        'OCR_REC_BATCH_NUM': '6',
        'OCR_USE_SERVER_MODEL': 'True',
        
        # 显示配置
        'MAX_DISPLAY_SCALE': '1.0',
        'MIN_RECT_SIZE': '10',
        
        # PDF配置
        'PDF_ZOOM_FACTOR': '2',
        
        # Excel配置
        'EXCEL_HEADER_FONT_SIZE': '11',
        'EXCEL_MAX_COLUMN_WIDTH': '50',
        
        # 颜色配置
        'COLOR_PRIMARY': '#4CAF50',
        'COLOR_SECONDARY': '#2196F3',
        'COLOR_BACKGROUND': '#f8f9fa',
        'COLOR_TOOLBAR': '#f0f0f0',
        'COLOR_RECT_NORMAL': 'red',
        'COLOR_RECT_DRAWING': 'blue',
    }
    
    # 配置验证规则
    VALIDATION_RULES = {
        'WINDOW_WIDTH': ('int', 800, 3840),
        'WINDOW_HEIGHT': ('int', 600, 2160),
        'OCR_ENGINE': ('choice', ['paddle', 'rapid', 'aliyun', 'deepseek']),
        'OCR_USE_GPU': ('choice', ['auto', 'True', 'False']),
        'OCR_USE_ANGLE_CLS': ('bool', None, None),
        'OCR_SHOW_LOG': ('bool', None, None),
        'PADDLE_ENABLED': ('bool', None, None),
        'RAPID_ENABLED': ('bool', None, None),
        'ALIYUN_ENABLED': ('bool', None, None),
        'DEEPSEEK_ENABLED': ('bool', None, None),
        'OCR_DET_DB_THRESH': ('float', 0.0, 1.0),
        'OCR_DET_DB_BOX_THRESH': ('float', 0.0, 1.0),
        'OCR_DET_DB_UNCLIP_RATIO': ('float', 1.0, 5.0),
        'OCR_REC_BATCH_NUM': ('int', 1, 32),
        'OCR_USE_SERVER_MODEL': ('bool', None, None),
        'MAX_DISPLAY_SCALE': ('float', 0.1, 5.0),
        'MIN_RECT_SIZE': ('int', 1, 100),
        'PDF_ZOOM_FACTOR': ('int', 1, 10),
        'EXCEL_HEADER_FONT_SIZE': ('int', 8, 20),
        'EXCEL_MAX_COLUMN_WIDTH': ('int', 10, 200),
    }
    
    @classmethod
    def get_config_dir(cls) -> str:
        """获取配置目录路径（便携式）"""
        # 首选：可执行文件目录（便携式，支持PyInstaller打包）
        exe_dir = cls._get_executable_dir()
        local_config_dir = os.path.join(exe_dir, ".ocr_system_config")
        
        # 如果本地配置目录存在或可创建，使用它
        if os.path.exists(local_config_dir) or os.access(exe_dir, os.W_OK):
            return local_config_dir
        
        # 回退：用户主目录
        return os.path.join(os.path.expanduser("~"), ".ocr_system")
    
    @classmethod
    def get_config_file(cls) -> str:
        """获取配置文件路径"""
        return os.path.join(cls.get_config_dir(), "config.ini")
    
    @classmethod
    def _get_executable_dir(cls) -> str:
        """获取可执行文件所在目录"""
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            # 打包环境：sys.executable是.exe文件路径
            return os.path.dirname(os.path.abspath(sys.executable))
        else:
            # 开发环境：使用脚本所在目录
            return os.path.dirname(os.path.abspath(__file__))
    
    @classmethod
    def load(cls, force_reload: bool = False) -> Dict[str, Any]:
        """
        加载配置（使用缓存）
        
        :param force_reload: 是否强制重新加载，忽略缓存
        :return: 配置字典
        """
        config_file = cls.get_config_file()
        
        # 检查文件是否存在
        if not os.path.exists(config_file):
            # 文件不存在，使用默认配置
            if cls._config_cache is None or force_reload:
                cls._config_cache = cls.DEFAULT_CONFIG.copy()
                cls._config_file_mtime = None
            return cls._config_cache
        
        # 获取文件修改时间
        try:
            current_mtime = os.path.getmtime(config_file)
        except OSError:
            # 无法获取修改时间，使用缓存或默认配置
            if cls._config_cache is not None and not force_reload:
                return cls._config_cache
            cls._config_cache = cls.DEFAULT_CONFIG.copy()
            return cls._config_cache
        
        # 检查缓存是否有效
        if (not force_reload and 
            cls._config_cache is not None and 
            cls._config_file_mtime is not None and 
            cls._config_file_mtime == current_mtime):
            return cls._config_cache
        
        # 解析配置文件
        config = cls._parse_config_file(config_file)
        
        # 更新缓存
        cls._config_cache = config
        cls._config_file_mtime = current_mtime
        
        return config
    
    @classmethod
    def _parse_config_file(cls, config_file: str) -> Dict[str, Any]:
        """
        解析INI格式配置文件
        
        :param config_file: 配置文件路径
        :return: 配置字典
        """
        config = cls.DEFAULT_CONFIG.copy()
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # 跳过空行和注释
                    if not line or line.startswith('#') or line.startswith(';'):
                        continue
                    
                    # 跳过section标记（[section]）
                    if line.startswith('[') and line.endswith(']'):
                        continue
                    
                    # 解析键值对
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # 移除值两端的引号
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        # 存储配置
                        config[key] = value
        
        except Exception as e:
            print(f"解析配置文件失败: {e}")
            # 解析失败，返回默认配置
            return cls.DEFAULT_CONFIG.copy()
        
        return config
    
    @classmethod
    def save(cls, config: Dict[str, Any]) -> bool:
        """
        保存配置到文件
        
        :param config: 配置字典
        :return: 是否保存成功
        """
        try:
            # 确保配置目录存在
            config_dir = cls.get_config_dir()
            os.makedirs(config_dir, exist_ok=True)
            
            # 获取配置文件路径
            config_file = cls.get_config_file()
            
            # 写入配置文件
            with open(config_file, 'w', encoding='utf-8') as f:
                f.write("# OCR系统配置文件\n")
                f.write("# 此文件使用INI格式\n\n")
                
                # 写入配置项
                for key, value in sorted(config.items()):
                    # 如果值包含特殊字符，使用引号包裹
                    if isinstance(value, str) and (' ' in value or '#' in value):
                        f.write(f'{key} = "{value}"\n')
                    else:
                        f.write(f'{key} = {value}\n')
            
            # 更新缓存
            cls._config_cache = config.copy()
            cls._config_file_mtime = os.path.getmtime(config_file)
            
            return True
        
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    @classmethod
    def validate(cls, config: Dict[str, Any]) -> tuple[bool, List[str]]:
        """
        验证配置
        
        :param config: 配置字典
        :return: (是否有效, 错误消息列表)
        """
        errors = []
        
        for key, value in config.items():
            # 跳过没有验证规则的配置项
            if key not in cls.VALIDATION_RULES:
                continue
            
            rule = cls.VALIDATION_RULES[key]
            rule_type = rule[0]
            
            try:
                if rule_type == 'int':
                    # 整数验证
                    int_value = int(value)
                    min_val, max_val = rule[1], rule[2]
                    if min_val is not None and int_value < min_val:
                        errors.append(f"{key}: 值 {int_value} 小于最小值 {min_val}")
                    if max_val is not None and int_value > max_val:
                        errors.append(f"{key}: 值 {int_value} 大于最大值 {max_val}")
                
                elif rule_type == 'float':
                    # 浮点数验证
                    float_value = float(value)
                    min_val, max_val = rule[1], rule[2]
                    if min_val is not None and float_value < min_val:
                        errors.append(f"{key}: 值 {float_value} 小于最小值 {min_val}")
                    if max_val is not None and float_value > max_val:
                        errors.append(f"{key}: 值 {float_value} 大于最大值 {max_val}")
                
                elif rule_type == 'bool':
                    # 布尔值验证
                    if value not in ['True', 'False', 'true', 'false', '1', '0']:
                        errors.append(f"{key}: 值 {value} 不是有效的布尔值")
                
                elif rule_type == 'choice':
                    # 选项验证
                    choices = rule[1]
                    if value not in choices:
                        errors.append(f"{key}: 值 {value} 不在允许的选项中 {choices}")
            
            except (ValueError, TypeError) as e:
                errors.append(f"{key}: 无法解析值 {value} ({e})")
        
        return len(errors) == 0, errors
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        获取配置项
        
        :param key: 配置键
        :param default: 默认值
        :return: 配置值
        """
        config = cls.load()
        return config.get(key, default)
    
    @classmethod
    def set(cls, key: str, value: Any) -> bool:
        """
        设置配置项
        
        :param key: 配置键
        :param value: 配置值
        :return: 是否设置成功
        """
        config = cls.load()
        config[key] = str(value)
        return cls.save(config)
    
    @classmethod
    def get_bool(cls, key: str, default: bool = False) -> bool:
        """
        获取布尔类型配置项
        
        :param key: 配置键
        :param default: 默认值
        :return: 布尔值
        """
        value = cls.get(key, str(default))
        return value in ['True', 'true', '1', 'yes', 'Yes']
    
    @classmethod
    def get_int(cls, key: str, default: int = 0) -> int:
        """
        获取整数类型配置项
        
        :param key: 配置键
        :param default: 默认值
        :return: 整数值
        """
        value = cls.get(key, str(default))
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    @classmethod
    def get_float(cls, key: str, default: float = 0.0) -> float:
        """
        获取浮点数类型配置项
        
        :param key: 配置键
        :param default: 默认值
        :return: 浮点数值
        """
        value = cls.get(key, str(default))
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    @classmethod
    def clear_cache(cls):
        """清除配置缓存"""
        cls._config_cache = None
        cls._config_file_mtime = None
    
    @classmethod
    def reset_to_default(cls) -> bool:
        """
        重置为默认配置
        
        :return: 是否重置成功
        """
        return cls.save(cls.DEFAULT_CONFIG.copy())
