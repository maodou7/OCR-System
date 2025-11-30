"""
最终验证脚本 - 运行所有测试套件
Task 12: 最终验证和清理
"""

import sys
import os
import subprocess
import time

def run_command(cmd, description):
    """运行命令并返回结果"""
    print(f"\n{'='*80}")
    print(f"{description}")
    print('='*80)
    print(f"命令: {cmd}")
    print()
    
    start_time = time.time()
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    elapsed = time.time() - start_time
    
    # Print output, handling encoding issues
    try:
        print(result.stdout)
    except UnicodeEncodeError:
        print(result.stdout.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))
    
    if result.stderr:
        try:
            print("STDERR:", result.stderr)
        except UnicodeEncodeError:
            print("STDERR:", result.stderr.encode('utf-8', errors='replace').decode('utf-8', errors='replace'))
    
    print(f"\n耗时: {elapsed:.2f}秒")
    print(f"返回码: {result.returncode}")
    
    return result.returncode == 0

def main():
    """运行所有测试"""
    print("="*80)
    print("最终验证 - 缓存引擎鲁棒性增强")
    print("="*80)
    
    results = {}
    
    # 1. 运行单元测试
    print("\n\n" + "="*80)
    print("第 1 步: 运行单元测试")
    print("="*80)
    
    results['unit_tests'] = run_command(
        'python -m unittest discover -s . -p "test_cache_engine_unit_tests.py" -v',
        "单元测试: OCRCacheManager 和 CacheManagerWrapper"
    )
    
    # 2. 运行集成测试
    print("\n\n" + "="*80)
    print("第 2 步: 运行集成测试")
    print("="*80)
    
    results['integration_tests'] = run_command(
        'python -m unittest discover -s . -p "test_cache_robustness_integration.py" -v',
        "集成测试: 应用启动流程和OCR工作流"
    )
    
    # 3. 运行诊断和日志测试
    print("\n\n" + "="*80)
    print("第 3 步: 运行诊断和日志测试")
    print("="*80)
    
    results['diagnostic_tests'] = run_command(
        'python -m unittest discover -s . -p "test_diagnostic_and_logging_system.py" -v',
        "诊断测试: 错误信息和日志系统"
    )
    
    # 4. 运行数据库恢复测试
    print("\n\n" + "="*80)
    print("第 4 步: 运行数据库恢复测试")
    print("="*80)
    
    results['database_tests'] = run_command(
        'python test_cache_manager_robustness.py',
        "数据库测试: 自动恢复机制"
    )
    
    # 5. 运行性能测试
    print("\n\n" + "="*80)
    print("第 5 步: 运行性能测试")
    print("="*80)
    
    results['performance_tests'] = run_command(
        'python test_cache_engine_performance.py',
        "性能测试: 缓存引擎性能"
    )
    
    # 打印总结
    print("\n\n" + "="*80)
    print("测试总结")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "通过" if passed else "失败"
        symbol = "✓" if passed else "✗"
        print(f"{symbol} {test_name}: {status}")
    
    passed_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n总计: {passed_count}/{total_count} 测试套件通过")
    
    if passed_count == total_count:
        print("\n" + "="*80)
        print("✓ 所有测试通过! 缓存引擎鲁棒性增强已完成")
        print("="*80)
        return 0
    else:
        print(f"\n✗ {total_count - passed_count} 个测试套件失败")
        return 1

if __name__ == "__main__":
    sys.exit(main())
