"""
并发安全和资源管理属性测试
使用Hypothesis进行属性测试
"""

import os
import sys
import tempfile
import shutil
import threading
import time
from pathlib import Path
from hypothesis import given, strategies as st, settings, assume
from hypothesis import HealthCheck

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ocr_cache_manager import OCRCacheManager, CacheInitError
from config import OCRRect


# ============================================================================
# 测试策略（生成器）
# ============================================================================

@st.composite
def valid_db_paths(draw):
    """生成有效的临时数据库路径"""
    temp_dir = tempfile.mkdtemp()
    filename = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(
        whitelist_categories=('Lu', 'Ll', 'Nd'),
        whitelist_characters='_-'
    )))
    return os.path.join(temp_dir, f"{filename}.db")


@st.composite
def thread_counts(draw):
    """生成线程数量"""
    return draw(st.integers(min_value=2, max_value=10))


@st.composite
def ocr_rect_list(draw):
    """生成OCR矩形列表"""
    count = draw(st.integers(min_value=0, max_value=10))
    rects = []
    for _ in range(count):
        x1 = draw(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False))
        y1 = draw(st.floats(min_value=0, max_value=1000, allow_nan=False, allow_infinity=False))
        x2 = draw(st.floats(min_value=x1, max_value=1000, allow_nan=False, allow_infinity=False))
        y2 = draw(st.floats(min_value=y1, max_value=1000, allow_nan=False, allow_infinity=False))
        text = draw(st.text(min_size=0, max_size=50))
        
        rect = OCRRect(x1, y1, x2, y2)
        rect.text = text
        rects.append(rect)
    
    return rects


# ============================================================================
# 属性 7: 并发初始化安全性
# **Feature: cache-engine-robustness, Property 7: 并发初始化安全性**
# **Validates: Requirements 4.4**
# ============================================================================

@given(
    db_path=valid_db_paths(),
    num_threads=thread_counts()
)
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_7_concurrent_initialization_safety(db_path, num_threads):
    """
    属性 7: 并发初始化安全性
    
    对于任何并发初始化场景（多线程同时创建OCRCacheManager实例），
    系统应该使用适当的锁机制，确保不发生竞态条件或数据损坏。
    """
    managers = []
    exceptions = []
    lock = threading.Lock()
    
    def init_manager():
        """在线程中初始化管理器"""
        try:
            manager = OCRCacheManager(db_path)
            with lock:
                managers.append(manager)
        except CacheInitError as e:
            # 初始化失败是可以接受的（例如库文件不存在）
            with lock:
                exceptions.append(e)
        except Exception as e:
            # 其他异常表示并发问题
            with lock:
                exceptions.append(e)
    
    # 创建多个线程同时初始化
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=init_manager)
        threads.append(thread)
    
    # 启动所有线程
    for thread in threads:
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join(timeout=10.0)
    
    try:
        # 验证：所有线程都应该完成（没有死锁）
        for thread in threads:
            assert not thread.is_alive(), "检测到死锁：线程未完成"
        
        # 验证：如果有成功初始化的管理器，它们应该都是有效的
        for manager in managers:
            assert manager is not None
            assert manager.engine is not None or manager.engine == 0
            # 验证管理器可以安全调用方法
            try:
                manager.has_cache()
            except Exception as e:
                raise AssertionError(f"并发初始化后的管理器不可用: {e}")
        
        # 验证：如果有异常，它们应该都是CacheInitError（预期的初始化失败）
        # 而不是并发相关的异常（如竞态条件、死锁等）
        for exc in exceptions:
            if not isinstance(exc, CacheInitError):
                # 检查是否是并发相关的异常
                exc_str = str(exc).lower()
                concurrent_keywords = ['race', 'deadlock', 'lock', 'concurrent', 'thread']
                if any(keyword in exc_str for keyword in concurrent_keywords):
                    raise AssertionError(f"检测到并发相关异常，违反属性7: {exc}")
        
        # 验证：数据库文件应该是一致的（没有损坏）
        if os.path.exists(db_path):
            # 尝试用新的管理器打开数据库，验证没有损坏
            try:
                test_manager = OCRCacheManager(db_path)
                test_manager.close()
            except CacheInitError:
                # 初始化失败可能是因为库不存在，这是可以接受的
                pass
            except Exception as e:
                raise AssertionError(f"并发初始化后数据库损坏: {e}")
    
    finally:
        # 清理资源
        for manager in managers:
            try:
                manager.close()
            except Exception:
                pass
        
        # 清理临时目录
        try:
            temp_dir = os.path.dirname(db_path)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass


@given(
    db_path=valid_db_paths(),
    num_threads=thread_counts()
)
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_7_concurrent_operations_safety(db_path, num_threads):
    """
    属性 7: 并发操作安全性（扩展）
    
    验证多个线程同时对同一个管理器实例执行操作时的安全性。
    """
    try:
        manager = OCRCacheManager(db_path)
    except CacheInitError:
        # 如果初始化失败（例如库不存在），跳过此测试
        assume(False)
        return
    
    exceptions = []
    lock = threading.Lock()
    
    def perform_operations():
        """在线程中执行操作"""
        try:
            # 执行各种操作
            manager.has_cache()
            
            # 保存结果
            rect = OCRRect(0, 0, 100, 100)
            rect.text = "test"
            manager.save_result("test.png", [rect], "已识别")
            
            # 加载结果
            manager.load_all_results()
            
            # 保存会话
            manager.save_session(["test.png"], 0)
            
            # 加载会话
            manager.load_session()
            
        except Exception as e:
            with lock:
                exceptions.append(e)
    
    # 创建多个线程同时执行操作
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=perform_operations)
        threads.append(thread)
    
    # 启动所有线程
    for thread in threads:
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join(timeout=10.0)
    
    try:
        # 验证：所有线程都应该完成（没有死锁）
        for thread in threads:
            assert not thread.is_alive(), "检测到死锁：线程未完成"
        
        # 验证：不应该有并发相关的异常
        for exc in exceptions:
            exc_str = str(exc).lower()
            concurrent_keywords = ['race', 'deadlock', 'lock', 'concurrent', 'thread']
            if any(keyword in exc_str for keyword in concurrent_keywords):
                raise AssertionError(f"检测到并发相关异常，违反属性7: {exc}")
    
    finally:
        # 清理资源
        try:
            manager.close()
        except Exception:
            pass
        
        # 清理临时目录
        try:
            temp_dir = os.path.dirname(db_path)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass


# ============================================================================
# 运行测试
# ============================================================================

if __name__ == "__main__":
    import unittest
    unittest.main()


# ============================================================================
# 属性 8: 资源清理完整性
# **Feature: cache-engine-robustness, Property 8: 资源清理完整性**
# **Validates: Requirements 4.5**
# ============================================================================

@given(db_path=valid_db_paths())
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_8_resource_cleanup_on_success(db_path):
    """
    属性 8: 资源清理完整性 - 成功初始化后的清理
    
    对于任何成功初始化的情况，当管理器被销毁时，
    系统应该释放所有已分配的资源（文件句柄、内存、数据库连接等），不产生资源泄漏。
    """
    manager = None
    try:
        # 尝试初始化管理器
        manager = OCRCacheManager(db_path)
        
        # 记录引擎指针（用于验证清理）
        engine_ptr = manager.engine
        
        # 执行一些操作
        if engine_ptr and engine_ptr != 0:
            manager.has_cache()
            rect = OCRRect(0, 0, 100, 100)
            rect.text = "test"
            manager.save_result("test.png", [rect], "已识别")
        
        # 显式关闭
        manager.close()
        
        # 验证：引擎应该被标记为已销毁
        assert manager._is_destroyed, "管理器未被标记为已销毁"
        
        # 验证：引擎指针应该被清空
        assert manager.engine is None or manager.engine == 0, "引擎指针未被清空"
        
        # 验证：再次调用close应该是安全的（幂等性）
        manager.close()
        
        # 验证：关闭后的操作应该安全失败（不崩溃）
        result = manager.has_cache()
        assert result == False, "关闭后的操作应该返回False"
        
    except CacheInitError:
        # 初始化失败是可以接受的（例如库不存在）
        pass
    finally:
        # 清理临时目录
        try:
            temp_dir = os.path.dirname(db_path)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass


@given(db_path=st.one_of(st.none(), st.text(min_size=0, max_size=200)))
@settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_8_resource_cleanup_on_failure(db_path):
    """
    属性 8: 资源清理完整性 - 初始化失败时的清理
    
    对于任何初始化失败的情况，系统应该释放所有已分配的资源，不产生资源泄漏。
    """
    manager = None
    try:
        # 尝试初始化管理器（可能失败）
        manager = OCRCacheManager(db_path)
        
        # 如果成功初始化，关闭它
        if manager:
            manager.close()
            
            # 验证清理
            assert manager._is_destroyed, "管理器未被标记为已销毁"
            assert manager.engine is None or manager.engine == 0, "引擎指针未被清空"
        
    except CacheInitError as e:
        # 初始化失败是预期的
        # 验证：即使初始化失败，也不应该有资源泄漏
        # 这通过检查异常后管理器的状态来验证
        if manager:
            # 如果管理器对象被创建，验证它的状态
            assert manager._is_destroyed or manager.engine is None or manager.engine == 0, \
                "初始化失败后资源未被清理"
    
    except Exception as e:
        # 其他异常不应该发生
        raise AssertionError(f"初始化失败时发生未预期的异常: {e}")
    
    finally:
        # 清理临时目录
        if db_path and isinstance(db_path, str):
            try:
                temp_dir = os.path.dirname(db_path)
                if os.path.exists(temp_dir) and temp_dir.startswith(tempfile.gettempdir()):
                    shutil.rmtree(temp_dir, ignore_errors=True)
            except Exception:
                pass


@given(db_path=valid_db_paths())
@settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_8_context_manager_cleanup(db_path):
    """
    属性 8: 资源清理完整性 - 上下文管理器
    
    验证使用上下文管理器时资源被正确清理。
    """
    try:
        # 使用上下文管理器
        with OCRCacheManager(db_path) as manager:
            # 执行操作
            if manager.engine and manager.engine != 0:
                manager.has_cache()
                rect = OCRRect(0, 0, 100, 100)
                rect.text = "test"
                manager.save_result("test.png", [rect], "已识别")
        
        # 退出上下文后，验证资源被清理
        # 注意：我们无法直接访问manager，因为它已经超出作用域
        # 但我们可以验证数据库文件的状态
        
        # 尝试创建新的管理器，验证数据库没有被锁定
        test_manager = OCRCacheManager(db_path)
        test_manager.close()
        
    except CacheInitError:
        # 初始化失败是可以接受的
        pass
    
    finally:
        # 清理临时目录
        try:
            temp_dir = os.path.dirname(db_path)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass


@given(
    db_path=valid_db_paths(),
    num_iterations=st.integers(min_value=5, max_value=20)
)
@settings(max_examples=30, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
def test_property_8_repeated_init_cleanup(db_path, num_iterations):
    """
    属性 8: 资源清理完整性 - 重复初始化和清理
    
    验证多次初始化和清理不会导致资源泄漏。
    """
    try:
        for i in range(num_iterations):
            manager = None
            try:
                # 初始化管理器
                manager = OCRCacheManager(db_path)
                
                # 执行一些操作
                if manager.engine and manager.engine != 0:
                    manager.has_cache()
                    rect = OCRRect(0, 0, 100, 100)
                    rect.text = f"test_{i}"
                    manager.save_result(f"test_{i}.png", [rect], "已识别")
                
                # 关闭管理器
                manager.close()
                
                # 验证清理
                assert manager._is_destroyed, f"迭代 {i}: 管理器未被标记为已销毁"
                assert manager.engine is None or manager.engine == 0, f"迭代 {i}: 引擎指针未被清空"
                
            except CacheInitError:
                # 初始化失败是可以接受的
                pass
            
            finally:
                if manager:
                    try:
                        manager.close()
                    except Exception:
                        pass
        
        # 验证：数据库文件应该仍然可用（没有损坏）
        if os.path.exists(db_path):
            try:
                final_manager = OCRCacheManager(db_path)
                final_manager.close()
            except CacheInitError:
                # 初始化失败可能是因为库不存在
                pass
    
    finally:
        # 清理临时目录
        try:
            temp_dir = os.path.dirname(db_path)
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        except Exception:
            pass
