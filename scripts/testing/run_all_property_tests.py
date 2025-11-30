"""
运行所有属性测试的脚本
"""

import sys

def run_test(test_name, test_func):
    """运行单个测试并报告结果"""
    print(f"\n{'='*80}")
    print(f"运行测试: {test_name}")
    print('='*80)
    try:
        test_func()
        print(f"✓ {test_name} 通过")
        return True
    except Exception as e:
        print(f"✗ {test_name} 失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """运行所有属性测试"""
    results = []
    
    # 测试 1: cache_wrapper_properties
    print("\n" + "="*80)
    print("测试套件 1: CacheManagerWrapper 属性测试")
    print("="*80)
    
    try:
        from test_cache_wrapper_properties import (
            test_property_1_init_failure_does_not_crash,
            test_property_2_auto_degradation_save_result,
            test_property_2_auto_degradation_save_session,
            test_property_2_auto_degradation_load_all,
            test_property_2_auto_degradation_load_session,
            test_property_2_auto_degradation_has_cache,
            test_property_2_auto_degradation_clear_cache,
            test_property_9_core_functionality_independence,
            test_property_10_cache_failure_isolation
        )
        
        results.append(run_test("属性1: 初始化失败不导致应用崩溃", test_property_1_init_failure_does_not_crash))
        results.append(run_test("属性2: 自动降级 - save_result", test_property_2_auto_degradation_save_result))
        results.append(run_test("属性2: 自动降级 - save_session", test_property_2_auto_degradation_save_session))
        results.append(run_test("属性2: 自动降级 - load_all", test_property_2_auto_degradation_load_all))
        results.append(run_test("属性2: 自动降级 - load_session", test_property_2_auto_degradation_load_session))
        results.append(run_test("属性2: 自动降级 - has_cache", test_property_2_auto_degradation_has_cache))
        results.append(run_test("属性2: 自动降级 - clear_cache", test_property_2_auto_degradation_clear_cache))
        results.append(run_test("属性9: 核心功能独立性", test_property_9_core_functionality_independence))
        results.append(run_test("属性10: 缓存失败隔离性", test_property_10_cache_failure_isolation))
    except Exception as e:
        print(f"✗ 无法加载 test_cache_wrapper_properties: {e}")
    
    # 测试 2: concurrent_safety_properties
    print("\n" + "="*80)
    print("测试套件 2: 并发安全属性测试")
    print("="*80)
    
    try:
        from test_concurrent_safety_properties import (
            test_property_7_concurrent_initialization_safety,
            test_property_7_concurrent_operations_safety,
            test_property_8_resource_cleanup_on_success,
            test_property_8_resource_cleanup_on_failure,
            test_property_8_context_manager_cleanup,
            test_property_8_repeated_init_cleanup
        )
        
        results.append(run_test("属性7: 并发初始化安全性", test_property_7_concurrent_initialization_safety))
        results.append(run_test("属性7: 并发操作安全性", test_property_7_concurrent_operations_safety))
        results.append(run_test("属性8: 资源清理 - 成功初始化", test_property_8_resource_cleanup_on_success))
        results.append(run_test("属性8: 资源清理 - 初始化失败", test_property_8_resource_cleanup_on_failure))
        results.append(run_test("属性8: 资源清理 - 上下文管理器", test_property_8_context_manager_cleanup))
        results.append(run_test("属性8: 资源清理 - 重复初始化", test_property_8_repeated_init_cleanup))
    except Exception as e:
        print(f"✗ 无法加载 test_concurrent_safety_properties: {e}")
    
    # 测试 3: error_information_completeness
    print("\n" + "="*80)
    print("测试套件 3: 错误信息完整性属性测试")
    print("="*80)
    
    try:
        from test_error_information_completeness import (
            test_property_3_error_information_completeness_via_wrapper,
            test_property_3_error_information_completeness_direct,
            test_property_3_health_check_completeness,
            test_property_3_error_message_format
        )
        
        results.append(run_test("属性3: 错误信息完整性 - Wrapper", test_property_3_error_information_completeness_via_wrapper))
        results.append(run_test("属性3: 错误信息完整性 - Direct", test_property_3_error_information_completeness_direct))
        results.append(run_test("属性3: 健康检查完整性", test_property_3_health_check_completeness))
        results.append(run_test("属性3: 错误消息格式", test_property_3_error_message_format))
    except Exception as e:
        print(f"✗ 无法加载 test_error_information_completeness: {e}")
    
    # 打印总结
    print("\n" + "="*80)
    print("测试总结")
    print("="*80)
    passed = sum(results)
    total = len(results)
    print(f"通过: {passed}/{total}")
    print(f"失败: {total - passed}/{total}")
    
    if passed == total:
        print("\n✓ 所有属性测试通过!")
        return 0
    else:
        print(f"\n✗ {total - passed} 个测试失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
