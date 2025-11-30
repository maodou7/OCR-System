"""
错误信息完整性属性测试
使用Hypothesis进行属性测试
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from hypothesis import HealthCheck

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ocr_cache_manager import OCRCacheManager, CacheInitError
from cache_manager_wrapper import CacheManagerWrapper


# ============================================================================
# 测试策略（生成器）
# ============================================================================

@st.composite
def invalid_db_paths(draw):
    """生成各种会导致初始化失败的数据库路径"""
    choice = draw(st.integers(min_value=0, max_value=5))
    
    if choice == 0:
        # 不存在的目录
        return "/nonexistent/directory/that/does/not/exist/cache.db"
    elif choice == 1:
        # 只读目录（尝试）
        return "/root/cache.db"
    elif choice == 2:
        # 包含特殊字符的路径
        special_chars = draw(st.text(
            alphabet=st.characters(blacklist_characters='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/_.-'),
            min_size=1,
            max_size=20
        ))
        return f"/tmp/{special_chars}/cache.db"
    elif choice == 3:
        # 空字符串
        return ""
    elif choice == 4:
        # 非常长的路径
        long_path = "a" * 500
        return f"/tmp/{long_path}/cache.db"
    else:
        # 路径指向一个文件而不是目录的父目录
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        temp_file.close()
        return temp_file.name + "/cache.db"


# ============================================================================
# 属性 3: 错误信息完整性
# **Feature: cache-engine-robustness, Property 3: 错误信息完整性**
# **Validates: Requirements 1.4, 2.4, 2.5**
# ============================================================================

@given(db_path=invalid_db_paths())
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_3_error_information_completeness_via_wrapper(db_path):
    """
    属性 3: 错误信息完整性（通过Wrapper）
    
    对于任何初始化失败的场景，系统应该记录包含错误类型、具体步骤、
    路径信息和诊断建议的完整错误信息。
    
    这个测试通过CacheManagerWrapper验证错误信息的完整性。
    """
    # 创建包装器（应该捕获初始化错误）
    wrapper = CacheManagerWrapper(db_path)
    
    # 获取状态
    status = wrapper.get_status()
    
    # 如果C++引擎不可用（初始化失败），应该有错误信息
    if status.backend_type != "cpp_engine":
        # 应该有初始化错误
        assert status.init_error is not None, \
            f"初始化失败但没有错误信息，路径: {db_path}"
        
        error = status.init_error
        
        # 验证错误信息的完整性
        
        # 1. 必须有错误类型
        assert hasattr(error, 'error_type'), "缺少error_type字段"
        assert error.error_type is not None, "error_type为None"
        assert isinstance(error.error_type, str), "error_type不是字符串"
        assert len(error.error_type) > 0, "error_type为空字符串"
        
        # 2. 必须有错误消息
        assert hasattr(error, 'error_message'), "缺少error_message字段"
        assert error.error_message is not None, "error_message为None"
        assert isinstance(error.error_message, str), "error_message不是字符串"
        assert len(error.error_message) > 0, "error_message为空字符串"
        
        # 3. 必须有错误详情
        assert hasattr(error, 'error_details'), "缺少error_details字段"
        assert error.error_details is not None, "error_details为None"
        assert isinstance(error.error_details, dict), "error_details不是字典"
        
        # 4. 必须有诊断建议
        assert hasattr(error, 'suggestions'), "缺少suggestions字段"
        assert error.suggestions is not None, "suggestions为None"
        assert isinstance(error.suggestions, list), "suggestions不是列表"
        assert len(error.suggestions) > 0, "suggestions为空列表"
        
        # 5. 建议应该是有意义的字符串
        for suggestion in error.suggestions:
            assert isinstance(suggestion, str), f"建议不是字符串: {suggestion}"
            assert len(suggestion) > 0, "建议为空字符串"
        
        # 6. 错误详情应该包含有用的信息
        # 至少应该有一些键值对
        assert len(error.error_details) > 0, "error_details为空字典"
        
        # 7. 验证错误信息可以被转换为字符串（用于日志）
        error_str = str(error)
        assert isinstance(error_str, str), "错误对象无法转换为字符串"
        assert len(error_str) > 0, "错误字符串为空"
        
        # 8. 错误字符串应该包含关键信息
        assert error.error_type in error_str, "错误字符串不包含错误类型"
        assert error.error_message in error_str, "错误字符串不包含错误消息"


@given(db_path=invalid_db_paths())
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_3_error_information_completeness_direct(db_path):
    """
    属性 3: 错误信息完整性（直接测试OCRCacheManager）
    
    对于任何初始化失败的场景，OCRCacheManager应该抛出包含完整信息的CacheInitError。
    """
    # 尝试直接初始化OCRCacheManager
    try:
        manager = OCRCacheManager(db_path)
        # 如果成功初始化，清理资源
        manager.close()
        # 注意：某些路径可能意外成功（如空字符串使用默认路径）
        # 这不是错误，只是这个特定输入没有触发失败
    except CacheInitError as error:
        # 捕获到CacheInitError，验证其完整性
        
        # 1. 必须有错误类型
        assert hasattr(error, 'error_type'), "缺少error_type字段"
        assert error.error_type is not None, "error_type为None"
        assert isinstance(error.error_type, str), "error_type不是字符串"
        assert len(error.error_type) > 0, "error_type为空字符串"
        
        # 2. 必须有错误消息
        assert hasattr(error, 'error_message'), "缺少error_message字段"
        assert error.error_message is not None, "error_message为None"
        assert isinstance(error.error_message, str), "error_message不是字符串"
        assert len(error.error_message) > 0, "error_message为空字符串"
        
        # 3. 必须有错误详情
        assert hasattr(error, 'error_details'), "缺少error_details字段"
        assert error.error_details is not None, "error_details为None"
        assert isinstance(error.error_details, dict), "error_details不是字典"
        
        # 4. 必须有诊断建议
        assert hasattr(error, 'suggestions'), "缺少suggestions字段"
        assert error.suggestions is not None, "suggestions为None"
        assert isinstance(error.suggestions, list), "suggestions不是列表"
        assert len(error.suggestions) > 0, "suggestions为空列表，应该至少有一条建议"
        
        # 5. 建议应该是有意义的字符串
        for i, suggestion in enumerate(error.suggestions):
            assert isinstance(suggestion, str), f"建议{i}不是字符串: {suggestion}"
            assert len(suggestion) > 0, f"建议{i}为空字符串"
            # 建议应该是有意义的（至少5个字符）
            assert len(suggestion) >= 5, f"建议{i}太短，可能没有意义: {suggestion}"
        
        # 6. 错误详情应该包含有用的信息
        assert len(error.error_details) > 0, "error_details为空字典，应该包含诊断信息"
        
        # 7. 验证错误信息可以被转换为字符串（用于日志）
        error_str = str(error)
        assert isinstance(error_str, str), "错误对象无法转换为字符串"
        assert len(error_str) > 0, "错误字符串为空"
        
        # 8. 错误字符串应该包含关键信息
        assert error.error_type in error_str, "错误字符串不包含错误类型"
        assert error.error_message in error_str, "错误字符串不包含错误消息"
        
        # 9. 错误字符串应该包含建议
        assert "建议" in error_str or "解决方案" in error_str, \
            "错误字符串不包含建议或解决方案"
        
        # 10. 错误详情中的值应该是可序列化的（用于日志）
        for key, value in error.error_details.items():
            assert isinstance(key, str), f"错误详情的键不是字符串: {key}"
            # 值应该是基本类型或可转换为字符串
            try:
                str(value)
            except Exception as e:
                raise AssertionError(f"错误详情的值无法转换为字符串: {key}={value}, 错误: {e}")
    
    except Exception as e:
        # 如果抛出其他类型的异常，这违反了错误处理规范
        raise AssertionError(
            f"初始化失败应该抛出CacheInitError，但抛出了{type(e).__name__}: {e}"
        )


@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.none())
def test_property_3_health_check_completeness(dummy):
    """
    属性 3: 健康检查信息完整性
    
    验证健康检查接口返回完整的诊断信息。
    """
    # 创建一个会失败的包装器
    wrapper = CacheManagerWrapper("/invalid/path/to/database.db")
    
    # 获取健康检查信息
    health = wrapper.health_check()
    
    # 验证健康检查返回字典
    assert isinstance(health, dict), "health_check应该返回字典"
    
    # 验证必需的字段
    required_fields = [
        "cache_available",
        "backend_type",
        "fallback_active",
        "message",
        "timestamp"
    ]
    
    for field in required_fields:
        assert field in health, f"健康检查缺少必需字段: {field}"
    
    # 验证字段类型
    assert isinstance(health["cache_available"], bool), "cache_available应该是布尔值"
    assert isinstance(health["backend_type"], str), "backend_type应该是字符串"
    assert isinstance(health["fallback_active"], bool), "fallback_active应该是布尔值"
    assert isinstance(health["message"], str), "message应该是字符串"
    assert isinstance(health["timestamp"], str), "timestamp应该是字符串"
    
    # 验证消息不为空
    assert len(health["message"]) > 0, "健康检查消息为空"
    
    # 如果有初始化错误，应该包含错误信息
    if "init_error" in health:
        error_info = health["init_error"]
        assert isinstance(error_info, dict), "init_error应该是字典"
        
        # 验证错误信息的必需字段
        assert "type" in error_info, "错误信息缺少type字段"
        assert "message" in error_info, "错误信息缺少message字段"
        assert "suggestions" in error_info, "错误信息缺少suggestions字段"
        
        assert isinstance(error_info["type"], str), "错误类型应该是字符串"
        assert isinstance(error_info["message"], str), "错误消息应该是字符串"
        assert isinstance(error_info["suggestions"], list), "建议应该是列表"
        assert len(error_info["suggestions"]) > 0, "建议列表不应为空"
    
    # 验证内存缓存统计信息
    assert "memory_cache" in health, "健康检查缺少memory_cache字段"
    memory_cache = health["memory_cache"]
    assert isinstance(memory_cache, dict), "memory_cache应该是字典"
    assert "results_count" in memory_cache, "memory_cache缺少results_count字段"
    assert "has_session" in memory_cache, "memory_cache缺少has_session字段"


@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.none())
def test_property_3_error_message_format(dummy):
    """
    属性 3: 错误消息格式验证
    
    验证错误消息的格式符合规范，便于用户理解和调试。
    """
    # 创建一个会失败的包装器
    wrapper = CacheManagerWrapper("/nonexistent/path/cache.db")
    
    # 获取状态消息
    status_message = wrapper.get_status_message()
    
    # 验证消息是字符串
    assert isinstance(status_message, str), "状态消息应该是字符串"
    
    # 验证消息不为空
    assert len(status_message) > 0, "状态消息为空"
    
    # 验证消息包含有用信息
    # 应该提到缓存或引擎
    assert any(keyword in status_message for keyword in ["缓存", "引擎", "cache", "engine"]), \
        f"状态消息不包含关键词: {status_message}"
    
    # 获取完整状态
    status = wrapper.get_status()
    
    if status.init_error:
        # 验证错误对象的字符串表示
        error_str = str(status.init_error)
        
        # 应该是多行的（包含详细信息）
        lines = error_str.split('\n')
        assert len(lines) > 1, "错误消息应该是多行的，包含详细信息"
        
        # 应该包含关键部分
        assert "错误类型" in error_str or "error" in error_str.lower(), \
            "错误消息应该包含错误类型"
        assert "建议" in error_str or "suggestion" in error_str.lower(), \
            "错误消息应该包含建议"


# ============================================================================
# 运行测试
# ============================================================================

if __name__ == "__main__":
    import unittest
    unittest.main()
