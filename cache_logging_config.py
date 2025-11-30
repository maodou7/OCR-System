"""
缓存系统日志配置模块
提供统一的日志配置和格式化
"""

import logging
import sys
from datetime import datetime
from pathlib import Path


# 日志级别映射
LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL
}


class CacheLogFormatter(logging.Formatter):
    """
    缓存系统专用日志格式化器
    提供彩色输出和详细的上下文信息
    """
    
    # ANSI颜色代码（用于终端输出）
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m'        # 重置
    }
    
    def __init__(self, use_colors=True, detailed=False):
        """
        初始化格式化器
        :param use_colors: 是否使用颜色（终端输出时）
        :param detailed: 是否显示详细信息（文件名、行号等）
        """
        self.use_colors = use_colors and sys.stderr.isatty()
        self.detailed = detailed
        
        if detailed:
            fmt = '%(asctime)s [%(levelname)s] %(name)s:%(funcName)s:%(lineno)d - %(message)s'
        else:
            fmt = '%(asctime)s [%(levelname)s] %(name)s - %(message)s'
        
        super().__init__(fmt, datefmt='%Y-%m-%d %H:%M:%S')
    
    def format(self, record):
        """格式化日志记录"""
        # 保存原始级别名称
        levelname = record.levelname
        
        # 如果使用颜色，添加颜色代码
        if self.use_colors:
            color = self.COLORS.get(levelname, self.COLORS['RESET'])
            record.levelname = f"{color}{levelname}{self.COLORS['RESET']}"
        
        # 格式化消息
        result = super().format(record)
        
        # 恢复原始级别名称
        record.levelname = levelname
        
        return result


def configure_cache_logging(
    level="INFO",
    log_file=None,
    console_output=True,
    detailed=False,
    use_colors=True
):
    """
    配置缓存系统的日志
    
    :param level: 日志级别 ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
    :param log_file: 日志文件路径（可选）
    :param console_output: 是否输出到控制台
    :param detailed: 是否显示详细信息（文件名、行号等）
    :param use_colors: 是否使用颜色（仅控制台）
    """
    # 获取日志级别
    log_level = LOG_LEVELS.get(level.upper(), logging.INFO)
    
    # 获取缓存相关的logger
    cache_loggers = [
        logging.getLogger("ocr_cache_manager"),
        logging.getLogger("cache_manager_wrapper"),
        logging.getLogger("__main__")  # 主程序
    ]
    
    # 配置每个logger
    for logger in cache_loggers:
        logger.setLevel(log_level)
        logger.handlers.clear()  # 清除现有处理器
        
        # 添加控制台处理器
        if console_output:
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setLevel(log_level)
            console_formatter = CacheLogFormatter(
                use_colors=use_colors,
                detailed=detailed
            )
            console_handler.setFormatter(console_formatter)
            logger.addHandler(console_handler)
        
        # 添加文件处理器
        if log_file:
            # 确保日志目录存在
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(
                log_file,
                encoding='utf-8',
                mode='a'  # 追加模式
            )
            file_handler.setLevel(log_level)
            file_formatter = CacheLogFormatter(
                use_colors=False,  # 文件不使用颜色
                detailed=True      # 文件使用详细格式
            )
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)
        
        # 防止日志传播到根logger
        logger.propagate = False
    
    # 记录配置信息
    logger = logging.getLogger("cache_logging_config")
    logger.setLevel(log_level)
    logger.info(f"缓存日志系统已配置: 级别={level}, 文件={log_file}, 控制台={console_output}")


def get_cache_logger(name):
    """
    获取缓存系统的logger
    
    :param name: logger名称（通常使用__name__）
    :return: logger对象
    """
    return logging.getLogger(name)


def log_cache_init_error(error, logger=None):
    """
    记录缓存初始化错误的辅助函数
    
    :param error: CacheInitError对象
    :param logger: logger对象（可选）
    """
    if logger is None:
        logger = logging.getLogger("ocr_cache_manager")
    
    logger.error("=" * 60)
    logger.error("缓存引擎初始化失败")
    logger.error(f"错误类型: {error.error_type}")
    logger.error(f"错误消息: {error.error_message}")
    
    if error.error_details:
        logger.error("详细信息:")
        for key, value in error.error_details.items():
            logger.error(f"  {key}: {value}")
    
    if error.suggestions:
        logger.error("可能的解决方案:")
        for i, suggestion in enumerate(error.suggestions, 1):
            logger.error(f"  {i}. {suggestion}")
    
    logger.error("=" * 60)


def log_health_check(health_info, logger=None):
    """
    记录健康检查信息的辅助函数
    
    :param health_info: 健康检查字典
    :param logger: logger对象（可选）
    """
    if logger is None:
        logger = logging.getLogger("cache_manager_wrapper")
    
    logger.info("=" * 60)
    logger.info("缓存系统健康检查")
    logger.info(f"缓存可用: {health_info.get('cache_available', 'Unknown')}")
    logger.info(f"后端类型: {health_info.get('backend_type', 'Unknown')}")
    logger.info(f"降级模式: {health_info.get('fallback_active', 'Unknown')}")
    logger.info(f"状态消息: {health_info.get('message', 'Unknown')}")
    logger.info(f"时间戳: {health_info.get('timestamp', 'Unknown')}")
    
    if 'init_error' in health_info:
        logger.warning("初始化错误:")
        error_info = health_info['init_error']
        logger.warning(f"  类型: {error_info.get('type', 'Unknown')}")
        logger.warning(f"  消息: {error_info.get('message', 'Unknown')}")
        if 'suggestions' in error_info:
            logger.warning("  建议:")
            for suggestion in error_info['suggestions']:
                logger.warning(f"    - {suggestion}")
    
    if 'memory_cache' in health_info:
        memory_cache = health_info['memory_cache']
        logger.info(f"内存缓存: {memory_cache.get('results_count', 0)} 个结果, "
                   f"会话: {'是' if memory_cache.get('has_session') else '否'}")
    
    logger.info("=" * 60)


# 默认配置（可以在应用启动时调用）
def setup_default_logging():
    """
    设置默认的日志配置
    适用于大多数场景
    """
    configure_cache_logging(
        level="INFO",
        console_output=True,
        detailed=False,
        use_colors=True
    )


# 调试模式配置
def setup_debug_logging(log_file="cache_debug.log"):
    """
    设置调试模式的日志配置
    输出详细信息到控制台和文件
    """
    configure_cache_logging(
        level="DEBUG",
        log_file=log_file,
        console_output=True,
        detailed=True,
        use_colors=True
    )


# 生产模式配置
def setup_production_logging(log_file="cache.log"):
    """
    设置生产模式的日志配置
    只记录警告和错误到文件
    """
    configure_cache_logging(
        level="WARNING",
        log_file=log_file,
        console_output=False,
        detailed=True,
        use_colors=False
    )


if __name__ == "__main__":
    # 测试日志配置
    setup_debug_logging()
    
    logger = get_cache_logger(__name__)
    logger.debug("这是一条调试消息")
    logger.info("这是一条信息消息")
    logger.warning("这是一条警告消息")
    logger.error("这是一条错误消息")
    logger.critical("这是一条严重错误消息")
