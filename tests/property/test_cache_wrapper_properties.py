"""
缓存包装层属性测试
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

from cache_manager_wrapper import CacheManagerWrapper, CacheStatus
from config import OCRRect


# ============================================================================
# 测试策略（生成器）
# ============================================================================

@st.composite
def invalid_db_paths(draw):
    """生成各种无效的数据库路径"""
    choice = draw(st.integers(min_value=0, max_value=4))
    
    if choice == 0:
        # 不存在的目录
        return "/nonexistent/path/to/db.db"
    elif choice == 1:
        # 只读目录（如果可能）
        return "/root/cache.db"
    elif choice == 2:
        # 包含特殊字符的路径
        return draw(st.text(min_size=1, max_size=50))
    elif choice == 3:
        # 空字符串
        return ""
    else:
        # None
        return None


@st.composite
def ocr_rect_list(draw):
    """生成OCR矩形列表"""
    count = draw(st.integers(min_value=0, max_value=20))
    rects = []
    for _ in range(count):
        x1 = draw(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False))
        y1 = draw(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False))
        x2 = draw(st.floats(min_value=x1, max_value=1000, allow_nan=False, allow_infinity=False))
        y2 = draw(st.floats(min_value=y1, max_value=1000, allow_nan=False, allow_infinity=False))
        text = draw(st.text(min_size=0, max_size=100))
        
        rect = OCRRect(x1, y1, x2, y2)
        rect.text = text
        rects.append(rect)
    
    return rects


@st.composite
def file_paths(draw):
    """生成文件路径"""
    # 生成合理的文件路径
    filename = draw(st.text(min_size=1, max_size=50, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='._-'
    )))
    extension = draw(st.sampled_from(['.png', '.jpg', '.jpeg', '.bmp', '.tiff']))
    return filename + extension


# ============================================================================
# 属性 1: 初始化失败不导致应用崩溃
# **Feature: cache-engine-robustness, Property 1: 初始化失败不导致应用崩溃**
# **Validates: Requirements 1.1**
# ============================================================================

@given(db_path=st.one_of(st.none(), st.text(min_size=0, max_size=200)))
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_1_init_failure_does_not_crash(db_path):
    """
    属性 1: 初始化失败不导致应用崩溃
    
    对于任何导致OCRCacheManager初始化失败的条件（无效路径、损坏的库、NULL指针等），
    应用程序应该捕获异常并继续启动，而不是崩溃或终止。
    """
    # 这个测试验证：无论传入什么路径，CacheManagerWrapper都不应该抛出异常
    try:
        wrapper = CacheManagerWrapper(db_path)
        
        # 验证包装器被创建（即使后端失败）
        assert wrapper is not None
        
        # 验证包装器有状态信息
        status = wrapper.get_status()
        assert isinstance(status, CacheStatus)
        
        # 验证包装器可以报告其状态
        message = wrapper.get_status_message()
        assert isinstance(message, str)
        
        # 验证健康检查不会崩溃
        health = wrapper.health_check()
        assert isinstance(health, dict)
        
    except Exception as e:
        # 如果抛出任何异常，测试失败
        raise AssertionError(f"初始化失败导致异常，违反属性1: {e}")


# ============================================================================
# 属性 2: 引擎不可用时自动降级
# **Feature: cache-engine-robustness, Property 2: 引擎不可用时自动降级**
# **Validates: Requirements 1.2, 1.3**
# ============================================================================

@given(
    file_path=file_paths(),
    rects=ocr_rect_list(),
    status_text=st.text(min_size=0, max_size=50)
)
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_2_auto_degradation_save_result(file_path, rects, status_text):
    """
    属性 2: 引擎不可用时自动降级 - save_result
    
    对于任何缓存操作（save_result），当C++引擎不可用时，
    系统应该使用内存缓存或安全地跳过操作，而不是抛出异常。
    """
    # 创建一个肯定会失败的包装器（使用无效路径）
    wrapper = CacheManagerWrapper("/invalid/path/that/does/not/exist.db")
    
    try:
        # 调用save_result不应该抛出异常
        result = wrapper.save_result(file_path, rects, status_text)
        
        # 应该返回布尔值
        assert isinstance(result, bool)
        
        # 即使C++引擎失败，内存缓存应该成功
        # （除非发生了非常严重的错误）
        
    except Exception as e:
        raise AssertionError(f"save_result在引擎不可用时抛出异常，违反属性2: {e}")


@given(
    files=st.lists(file_paths(), min_size=0, max_size=20),
    cur_index=st.integers(min_value=0, max_value=100)
)
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_2_auto_degradation_save_session(files, cur_index):
    """
    属性 2: 引擎不可用时自动降级 - save_session
    
    对于任何缓存操作（save_session），当C++引擎不可用时，
    系统应该使用内存缓存或安全地跳过操作，而不是抛出异常。
    """
    wrapper = CacheManagerWrapper("/invalid/path/that/does/not/exist.db")
    
    try:
        result = wrapper.save_session(files, cur_index)
        assert isinstance(result, bool)
    except Exception as e:
        raise AssertionError(f"save_session在引擎不可用时抛出异常，违反属性2: {e}")


@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.none())
def test_property_2_auto_degradation_load_all(dummy):
    """
    属性 2: 引擎不可用时自动降级 - load_all_results
    
    对于任何缓存操作（load_all_results），当C++引擎不可用时，
    系统应该使用内存缓存或安全地跳过操作，而不是抛出异常。
    """
    wrapper = CacheManagerWrapper("/invalid/path/that/does/not/exist.db")
    
    try:
        results = wrapper.load_all_results()
        assert isinstance(results, dict)
    except Exception as e:
        raise AssertionError(f"load_all_results在引擎不可用时抛出异常，违反属性2: {e}")


@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.none())
def test_property_2_auto_degradation_load_session(dummy):
    """
    属性 2: 引擎不可用时自动降级 - load_session
    
    对于任何缓存操作（load_session），当C++引擎不可用时，
    系统应该使用内存缓存或安全地跳过操作，而不是抛出异常。
    """
    wrapper = CacheManagerWrapper("/invalid/path/that/does/not/exist.db")
    
    try:
        session = wrapper.load_session()
        # 应该返回None或dict
        assert session is None or isinstance(session, dict)
    except Exception as e:
        raise AssertionError(f"load_session在引擎不可用时抛出异常，违反属性2: {e}")


@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.none())
def test_property_2_auto_degradation_has_cache(dummy):
    """
    属性 2: 引擎不可用时自动降级 - has_cache
    """
    wrapper = CacheManagerWrapper("/invalid/path/that/does/not/exist.db")
    
    try:
        result = wrapper.has_cache()
        assert isinstance(result, bool)
    except Exception as e:
        raise AssertionError(f"has_cache在引擎不可用时抛出异常，违反属性2: {e}")


@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
@given(st.none())
def test_property_2_auto_degradation_clear_cache(dummy):
    """
    属性 2: 引擎不可用时自动降级 - clear_cache
    """
    wrapper = CacheManagerWrapper("/invalid/path/that/does/not/exist.db")
    
    try:
        wrapper.clear_cache()
        # clear_cache不返回值，只要不抛出异常就通过
    except Exception as e:
        raise AssertionError(f"clear_cache在引擎不可用时抛出异常，违反属性2: {e}")


# ============================================================================
# 属性 9: 核心功能独立性
# **Feature: cache-engine-robustness, Property 9: 核心功能独立性**
# **Validates: Requirements 5.1, 5.2, 5.3**
# ============================================================================

@given(
    file_path=file_paths(),
    rects=ocr_rect_list(),
    status_text=st.text(min_size=0, max_size=50)
)
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_9_core_functionality_independence(file_path, rects, status_text):
    """
    属性 9: 核心功能独立性
    
    对于任何OCR核心操作，当缓存管理器为None或不可用时，
    这些操作应该正常工作并返回正确结果。
    
    这个测试验证：即使缓存不可用，我们仍然可以处理OCR数据。
    """
    # 创建一个缓存不可用的包装器
    wrapper = CacheManagerWrapper("/invalid/path/that/does/not/exist.db")
    
    # 验证缓存操作不会阻止我们处理数据
    try:
        # 保存结果（应该使用内存缓存）
        wrapper.save_result(file_path, rects, status_text)
        
        # 加载结果（应该从内存缓存返回）
        results = wrapper.load_all_results()
        
        # 验证数据被保存到内存缓存
        if file_path in results:
            loaded_rects = results[file_path]["rects"]
            loaded_status = results[file_path]["status"]
            
            # 验证数据完整性
            assert len(loaded_rects) == len(rects)
            assert loaded_status == status_text
            
            # 验证每个矩形的数据
            for i, (original, loaded) in enumerate(zip(rects, loaded_rects)):
                assert abs(original.x1 - loaded.x1) < 0.001
                assert abs(original.y1 - loaded.y1) < 0.001
                assert abs(original.x2 - loaded.x2) < 0.001
                assert abs(original.y2 - loaded.y2) < 0.001
                assert original.text == loaded.text
        
    except Exception as e:
        raise AssertionError(f"核心功能在缓存不可用时失败，违反属性9: {e}")


# ============================================================================
# 属性 10: 缓存失败隔离性
# **Feature: cache-engine-robustness, Property 10: 缓存失败隔离性**
# **Validates: Requirements 5.4, 5.5**
# ============================================================================

@given(
    file_path1=file_paths(),
    file_path2=file_paths(),
    rects1=ocr_rect_list(),
    rects2=ocr_rect_list()
)
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_10_cache_failure_isolation(file_path1, file_path2, rects1, rects2):
    """
    属性 10: 缓存失败隔离性
    
    对于任何缓存操作失败（保存、加载、清除等），
    失败应该被隔离，不影响其他系统功能的正常运行。
    """
    wrapper = CacheManagerWrapper("/invalid/path/that/does/not/exist.db")
    
    try:
        # 第一次保存
        result1 = wrapper.save_result(file_path1, rects1, "状态1")
        
        # 即使第一次可能失败，第二次也应该能继续
        result2 = wrapper.save_result(file_path2, rects2, "状态2")
        
        # 加载操作应该独立工作
        all_results = wrapper.load_all_results()
        
        # 清除操作应该独立工作
        wrapper.clear_cache()
        
        # 清除后再次保存应该工作
        result3 = wrapper.save_result(file_path1, rects1, "状态3")
        
        # 所有操作都应该返回适当的类型，不抛出异常
        assert isinstance(result1, bool)
        assert isinstance(result2, bool)
        assert isinstance(all_results, dict)
        assert isinstance(result3, bool)
        
    except Exception as e:
        raise AssertionError(f"缓存操作失败影响了其他操作，违反属性10: {e}")


# ============================================================================
# 运行测试
# ============================================================================

if __name__ == "__main__":
    import unittest
    unittest.main()
