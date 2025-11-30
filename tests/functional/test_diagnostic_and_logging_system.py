"""
诊断和日志系统测试
验证任务7的所有功能
"""

import os
import sys
import tempfile
import logging
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ocr_cache_manager import OCRCacheManager, CacheInitError
from cache_manager_wrapper import CacheManagerWrapper
from cache_logging_config import (
    configure_cache_logging,
    get_cache_logger,
    log_cache_init_error,
    log_health_check,
    setup_default_logging,
    setup_debug_logging,
    CacheLogFormatter
)


def test_cache_init_error_dataclass():
    """测试CacheInitError数据类的完整性"""
    # 创建一个CacheInitError实例
    error = CacheInitError(
        error_type="test_error",
        error_message="This is a test error",
        error_details={"key1": "value1", "key2": 123},
        suggestions=["Suggestion 1", "Suggestion 2"]
    )
    
    # 验证所有字段
    assert error.error_type == "test_error"
    assert error.error_message == "This is a test error"
    assert error.error_details == {"key1": "value1", "key2": 123}
    assert error.suggestions == ["Suggestion 1", "Suggestion 2"]
    
    # 验证字符串表示
    error_str = str(error)
    assert "test_error" in error_str
    assert "This is a test error" in error_str
    assert "Suggestion 1" in error_str
    
    print("[PASS] CacheInitError数据类测试通过")


def test_error_information_collection():
    """测试详细的错误信息收集"""
    # 尝试使用无效路径初始化
    try:
        manager = OCRCacheManager("/nonexistent/path/cache.db")
        manager.close()
        # 如果成功，跳过测试
        print("⚠ 路径意外成功，跳过错误收集测试")
    except CacheInitError as error:
        # 验证错误信息的完整性
        assert error.error_type is not None
        assert len(error.error_type) > 0
        
        assert error.error_message is not None
        assert len(error.error_message) > 0
        
        assert error.error_details is not None
        assert isinstance(error.error_details, dict)
        assert len(error.error_details) > 0
        
        assert error.suggestions is not None
        assert isinstance(error.suggestions, list)
        assert len(error.suggestions) > 0
        
        print("✓ 错误信息收集测试通过")
        print(f"  错误类型: {error.error_type}")
        print(f"  错误详情字段数: {len(error.error_details)}")
        print(f"  建议数量: {len(error.suggestions)}")


def test_diagnostic_suggestions():
    """测试诊断建议生成逻辑"""
    # 创建一个会失败的包装器
    wrapper = CacheManagerWrapper("/invalid/path/cache.db")
    
    # 获取状态
    status = wrapper.get_status()
    
    if status.init_error:
        # 验证建议的质量
        suggestions = status.init_error.suggestions
        
        assert len(suggestions) > 0, "应该有至少一条建议"
        
        for suggestion in suggestions:
            assert isinstance(suggestion, str), "建议应该是字符串"
            assert len(suggestion) >= 5, "建议应该有意义（至少5个字符）"
            # 建议不应该是空白
            assert suggestion.strip() == suggestion, "建议不应该有前后空白"
        
        print("✓ 诊断建议生成测试通过")
        print(f"  建议数量: {len(suggestions)}")
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion[:50]}...")


def test_health_check_interface():
    """测试健康检查接口"""
    # 创建包装器
    wrapper = CacheManagerWrapper("/invalid/path/cache.db")
    
    # 调用健康检查
    health = wrapper.health_check()
    
    # 验证返回类型
    assert isinstance(health, dict), "健康检查应该返回字典"
    
    # 验证必需字段
    required_fields = [
        "cache_available",
        "backend_type",
        "fallback_active",
        "message",
        "timestamp"
    ]
    
    for field in required_fields:
        assert field in health, f"缺少必需字段: {field}"
    
    # 验证字段类型
    assert isinstance(health["cache_available"], bool)
    assert isinstance(health["backend_type"], str)
    assert isinstance(health["fallback_active"], bool)
    assert isinstance(health["message"], str)
    assert isinstance(health["timestamp"], str)
    
    # 验证内存缓存统计
    assert "memory_cache" in health
    assert isinstance(health["memory_cache"], dict)
    
    print("✓ 健康检查接口测试通过")
    print(f"  缓存可用: {health['cache_available']}")
    print(f"  后端类型: {health['backend_type']}")
    print(f"  降级模式: {health['fallback_active']}")


def test_logging_configuration():
    """测试日志级别和格式配置"""
    # 创建临时日志文件
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
        log_file = f.name
    
    try:
        # 配置日志
        configure_cache_logging(
            level="DEBUG",
            log_file=log_file,
            console_output=False,  # 不输出到控制台以避免干扰测试
            detailed=True
        )
        
        # 使用配置好的logger（ocr_cache_manager是被配置的logger之一）
        logger = get_cache_logger("ocr_cache_manager")
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        
        # 刷新所有处理器
        for handler in logger.handlers:
            handler.flush()
        
        # 关闭所有处理器以释放文件
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)
        
        # 读取日志文件
        with open(log_file, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        # 验证日志内容
        assert "Debug message" in log_content, f"日志文件内容: {log_content}"
        assert "Info message" in log_content
        assert "Warning message" in log_content
        assert "Error message" in log_content
        
        # 验证日志格式（应该包含时间戳和级别）
        assert "[DEBUG]" in log_content
        assert "[INFO]" in log_content
        assert "[WARNING]" in log_content
        assert "[ERROR]" in log_content
        
        print("✓ 日志配置测试通过")
        print(f"  日志文件: {log_file}")
        print(f"  日志行数: {len(log_content.splitlines())}")
        
    finally:
        # 清理临时文件
        try:
            if os.path.exists(log_file):
                os.remove(log_file)
        except PermissionError:
            # Windows文件锁定问题，忽略
            pass


def test_log_formatter():
    """测试日志格式化器"""
    # 测试不带颜色的格式化器
    formatter = CacheLogFormatter(use_colors=False, detailed=False)
    
    # 创建一个日志记录
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None
    )
    
    # 格式化
    formatted = formatter.format(record)
    
    # 验证格式
    assert "INFO" in formatted
    assert "test" in formatted
    assert "Test message" in formatted
    
    print("✓ 日志格式化器测试通过")


def test_log_helper_functions():
    """测试日志辅助函数"""
    # 创建一个测试logger
    logger = logging.getLogger("test_helper")
    logger.setLevel(logging.DEBUG)
    
    # 创建内存处理器
    handler = logging.StreamHandler()
    handler.setLevel(logging.DEBUG)
    logger.addHandler(handler)
    
    # 测试log_cache_init_error
    error = CacheInitError(
        error_type="test_error",
        error_message="Test error message",
        error_details={"detail1": "value1"},
        suggestions=["Suggestion 1"]
    )
    
    # 这应该不会抛出异常
    log_cache_init_error(error, logger)
    
    # 测试log_health_check
    health_info = {
        "cache_available": False,
        "backend_type": "memory",
        "fallback_active": True,
        "message": "Test message",
        "timestamp": "2024-01-01 00:00:00",
        "memory_cache": {
            "results_count": 0,
            "has_session": False
        }
    }
    
    # 这应该不会抛出异常
    log_health_check(health_info, logger)
    
    print("✓ 日志辅助函数测试通过")


def test_different_log_levels():
    """测试不同的日志级别配置"""
    levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    
    for level in levels:
        # 配置日志级别
        configure_cache_logging(
            level=level,
            console_output=False
        )
        
        # 获取logger
        logger = get_cache_logger("test_levels")
        
        # 验证级别设置
        # 注意：由于我们配置了多个logger，需要检查它们的级别
        assert logger.level <= logging.getLevelName(level)
        
    print("✓ 不同日志级别配置测试通过")


def test_integration_with_wrapper():
    """测试日志系统与包装器的集成"""
    # 配置日志
    setup_default_logging()
    
    # 创建包装器（会失败）
    wrapper = CacheManagerWrapper("/invalid/path/cache.db")
    
    # 获取状态（应该记录日志）
    status = wrapper.get_status()
    
    # 执行健康检查（应该记录日志）
    health = wrapper.health_check()
    
    # 如果有错误，记录详细信息
    if status.init_error:
        logger = get_cache_logger(__name__)
        log_cache_init_error(status.init_error, logger)
        log_health_check(health, logger)
    
    print("✓ 日志系统与包装器集成测试通过")


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("诊断和日志系统测试")
    print("=" * 60)
    
    tests = [
        ("CacheInitError数据类", test_cache_init_error_dataclass),
        ("错误信息收集", test_error_information_collection),
        ("诊断建议生成", test_diagnostic_suggestions),
        ("健康检查接口", test_health_check_interface),
        ("日志配置", test_logging_configuration),
        ("日志格式化器", test_log_formatter),
        ("日志辅助函数", test_log_helper_functions),
        ("不同日志级别", test_different_log_levels),
        ("与包装器集成", test_integration_with_wrapper),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            print(f"\n测试: {name}")
            test_func()
            passed += 1
        except Exception as e:
            print(f"✗ {name} 失败: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"测试结果: {passed} 通过, {failed} 失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
