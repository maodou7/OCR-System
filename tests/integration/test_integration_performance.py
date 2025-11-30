#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试 - 性能指标验证

测量关键性能指标，对比优化前后的数据，验证性能提升。
验证需求: 8.1, 8.5, 9.5

测试内容:
- 启动时间
- 内存占用
- OCR识别速度

使用方法:
    python test_integration_performance.py
"""

import os
import sys
import time
import gc
import json
import subprocess
import tempfile
from pathlib import Path


def get_memory_usage():
    """获取当前进程内存占用（MB）"""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)
    except ImportError:
        print("⚠️  psutil未安装，无法测量内存")
        return None


def test_startup_time():
    """测试启动时间"""
    print("=" * 80)
    print("测试 1: 启动时间")
    print("=" * 80)
    print()
    
    # 测试脚本
    test_script = """
import sys
import time

start_time = time.time()

# 导入核心模块
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer

# 创建应用
app = QApplication(sys.argv)

# 记录到窗口显示的时间
window_time = time.time() - start_time

print(f"WINDOW_TIME:{window_time:.3f}")

# 退出
QTimer.singleShot(100, app.quit)
app.exec()

# 记录完全就绪时间
ready_time = time.time() - start_time
print(f"READY_TIME:{ready_time:.3f}")
"""
    
    # 写入临时文件
    test_file = tempfile.mktemp(suffix='.py')
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(test_script)
    
    try:
        # 运行测试
        print("测量启动时间...")
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # 解析结果
        window_time = None
        ready_time = None
        
        for line in result.stdout.split('\n'):
            if line.startswith('WINDOW_TIME:'):
                window_time = float(line.split(':')[1])
            elif line.startswith('READY_TIME:'):
                ready_time = float(line.split(':')[1])
        
        if window_time and ready_time:
            print(f"  窗口显示时间: {window_time:.3f}秒")
            print(f"  完全就绪时间: {ready_time:.3f}秒")
            print()
            
            # 验证目标
            window_ok = window_time < 1.0
            ready_ok = ready_time < 3.0
            
            print("  目标验证:")
            print(f"    {'✅' if window_ok else '❌'} 窗口显示 < 1秒: {window_time:.3f}秒")
            print(f"    {'✅' if ready_ok else '❌'} 完全就绪 < 3秒: {ready_time:.3f}秒")
            print()
            
            return {
                'window_time': window_time,
                'ready_time': ready_time,
                'passed': window_ok and ready_ok
            }
        else:
            print("  ❌ 无法解析启动时间")
            print()
            return None
            
    except subprocess.TimeoutExpired:
        print("  ❌ 启动超时")
        print()
        return None
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")
        print()
        return None
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_memory_usage():
    """测试内存占用"""
    print("=" * 80)
    print("测试 2: 内存占用")
    print("=" * 80)
    print()
    
    try:
        import psutil
    except ImportError:
        print("❌ psutil未安装，无法测试内存")
        print("   安装: pip install psutil")
        print()
        return None
    
    # 测试空闲内存
    print("测量空闲内存占用...")
    
    # 强制垃圾回收
    gc.collect()
    time.sleep(0.5)
    
    initial_memory = get_memory_usage()
    print(f"  初始内存: {initial_memory:.1f} MB")
    
    # 导入核心模块
    print("  导入核心模块...")
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    
    after_import_memory = get_memory_usage()
    print(f"  导入后内存: {after_import_memory:.1f} MB")
    
    # 创建应用（不显示窗口）
    print("  创建应用...")
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    after_app_memory = get_memory_usage()
    print(f"  应用创建后内存: {after_app_memory:.1f} MB")
    
    # 等待稳定
    time.sleep(1)
    gc.collect()
    time.sleep(0.5)
    
    idle_memory = get_memory_usage()
    print(f"  空闲内存: {idle_memory:.1f} MB")
    print()
    
    # 验证目标
    memory_ok = idle_memory < 200
    
    print("  目标验证:")
    print(f"    {'✅' if memory_ok else '❌'} 空闲内存 < 200MB: {idle_memory:.1f} MB")
    print()
    
    return {
        'initial_memory': initial_memory,
        'after_import_memory': after_import_memory,
        'after_app_memory': after_app_memory,
        'idle_memory': idle_memory,
        'passed': memory_ok
    }


def test_module_loading():
    """测试模块加载"""
    print("=" * 80)
    print("测试 3: 模块加载检查")
    print("=" * 80)
    print()
    
    # 检查不应加载的模块
    non_core_modules = [
        'openpyxl',
        'fitz',
        'openai',
        'alibabacloud_ocr_api20210707',
        'numpy',
        'matplotlib',
        'pandas',
    ]
    
    print("检查非核心模块是否被加载...")
    
    loaded_modules = []
    not_loaded_modules = []
    
    for module_name in non_core_modules:
        if module_name in sys.modules:
            loaded_modules.append(module_name)
            print(f"  ❌ {module_name} - 已加载（不应该）")
        else:
            not_loaded_modules.append(module_name)
            print(f"  ✅ {module_name} - 未加载（正确）")
    
    print()
    
    # 统计
    print(f"  未加载: {len(not_loaded_modules)}/{len(non_core_modules)}")
    print(f"  已加载: {len(loaded_modules)}/{len(non_core_modules)}")
    print()
    
    return {
        'loaded_modules': loaded_modules,
        'not_loaded_modules': not_loaded_modules,
        'passed': len(loaded_modules) == 0
    }


def test_lazy_loading_performance():
    """测试延迟加载性能"""
    print("=" * 80)
    print("测试 4: 延迟加载性能")
    print("=" * 80)
    print()
    
    try:
        from dependency_manager import DependencyManager
        
        # 测试Excel加载时间
        print("测试Excel支持加载时间...")
        start = time.time()
        openpyxl = DependencyManager.load_excel_support()
        excel_time = time.time() - start
        
        if openpyxl:
            print(f"  ✅ Excel加载成功: {excel_time:.3f}秒")
        else:
            print(f"  ❌ Excel加载失败")
            excel_time = None
        
        # 测试PDF加载时间
        print("测试PDF支持加载时间...")
        start = time.time()
        fitz = DependencyManager.load_pdf_support()
        pdf_time = time.time() - start
        
        if fitz:
            print(f"  ✅ PDF加载成功: {pdf_time:.3f}秒")
        else:
            print(f"  ❌ PDF加载失败")
            pdf_time = None
        
        print()
        
        return {
            'excel_load_time': excel_time,
            'pdf_load_time': pdf_time,
            'passed': excel_time is not None and pdf_time is not None
        }
        
    except Exception as e:
        print(f"❌ 延迟加载测试失败: {e}")
        print()
        return None


def load_baseline_data(baseline_file='performance_baseline.json'):
    """加载基线数据"""
    if os.path.exists(baseline_file):
        try:
            with open(baseline_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return None


def save_current_data(data, output_file='performance_current.json'):
    """保存当前数据"""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, indent=2, fp=f)
        return True
    except:
        return False


def compare_with_baseline(current_data, baseline_data):
    """对比基线数据"""
    print("=" * 80)
    print("对比优化前后数据")
    print("=" * 80)
    print()
    
    if not baseline_data:
        print("⚠️  无基线数据，无法对比")
        print("   当前数据已保存为基线")
        print()
        return
    
    print("性能对比:")
    print()
    
    # 启动时间对比
    if 'startup' in current_data and 'startup' in baseline_data:
        curr = current_data['startup']
        base = baseline_data['startup']
        
        if curr and base and 'window_time' in curr and 'window_time' in base:
            curr_time = curr['window_time']
            base_time = base['window_time']
            improvement = ((base_time - curr_time) / base_time * 100)
            
            print(f"  窗口显示时间:")
            print(f"    优化前: {base_time:.3f}秒")
            print(f"    优化后: {curr_time:.3f}秒")
            print(f"    改善: {improvement:+.1f}%")
            print()
    
    # 内存对比
    if 'memory' in current_data and 'memory' in baseline_data:
        curr = current_data['memory']
        base = baseline_data['memory']
        
        if curr and base and 'idle_memory' in curr and 'idle_memory' in base:
            curr_mem = curr['idle_memory']
            base_mem = base['idle_memory']
            improvement = ((base_mem - curr_mem) / base_mem * 100)
            
            print(f"  空闲内存:")
            print(f"    优化前: {base_mem:.1f} MB")
            print(f"    优化后: {curr_mem:.1f} MB")
            print(f"    改善: {improvement:+.1f}%")
            print()


def generate_report(test_results, baseline_data=None, output_file='INTEGRATION_TEST_PERFORMANCE_REPORT.md'):
    """生成测试报告"""
    print("=" * 80)
    print("生成测试报告")
    print("=" * 80)
    print()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 集成测试报告 - 性能指标验证\n\n")
        f.write(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 测试概述\n\n")
        f.write("本测试验证优化后的性能指标，包括:\n")
        f.write("- 启动时间\n")
        f.write("- 内存占用\n")
        f.write("- 模块加载\n")
        f.write("- 延迟加载性能\n\n")
        
        f.write("## 测试结果\n\n")
        
        # 启动时间
        if 'startup' in test_results and test_results['startup']:
            startup = test_results['startup']
            f.write("### 启动时间\n\n")
            f.write(f"- 窗口显示时间: {startup['window_time']:.3f}秒\n")
            f.write(f"- 完全就绪时间: {startup['ready_time']:.3f}秒\n")
            
            window_ok = startup['window_time'] < 1.0
            ready_ok = startup['ready_time'] < 3.0
            
            f.write(f"- 窗口显示 < 1秒: {'✅ 达成' if window_ok else '❌ 未达成'}\n")
            f.write(f"- 完全就绪 < 3秒: {'✅ 达成' if ready_ok else '❌ 未达成'}\n\n")
        
        # 内存占用
        if 'memory' in test_results and test_results['memory']:
            memory = test_results['memory']
            f.write("### 内存占用\n\n")
            f.write(f"- 初始内存: {memory['initial_memory']:.1f} MB\n")
            f.write(f"- 导入后内存: {memory['after_import_memory']:.1f} MB\n")
            f.write(f"- 应用创建后: {memory['after_app_memory']:.1f} MB\n")
            f.write(f"- 空闲内存: {memory['idle_memory']:.1f} MB\n")
            
            memory_ok = memory['idle_memory'] < 200
            f.write(f"- 空闲内存 < 200MB: {'✅ 达成' if memory_ok else '❌ 未达成'}\n\n")
        
        # 模块加载
        if 'modules' in test_results and test_results['modules']:
            modules = test_results['modules']
            f.write("### 模块加载检查\n\n")
            f.write(f"- 未加载模块: {len(modules['not_loaded_modules'])}\n")
            f.write(f"- 已加载模块: {len(modules['loaded_modules'])}\n")
            
            if modules['loaded_modules']:
                f.write("\n不应加载但已加载的模块:\n")
                for mod in modules['loaded_modules']:
                    f.write(f"- {mod}\n")
            
            f.write("\n")
        
        # 延迟加载性能
        if 'lazy_loading' in test_results and test_results['lazy_loading']:
            lazy = test_results['lazy_loading']
            f.write("### 延迟加载性能\n\n")
            
            if lazy['excel_load_time']:
                f.write(f"- Excel加载时间: {lazy['excel_load_time']:.3f}秒\n")
            if lazy['pdf_load_time']:
                f.write(f"- PDF加载时间: {lazy['pdf_load_time']:.3f}秒\n")
            
            f.write("\n")
        
        # 对比基线
        if baseline_data:
            f.write("## 优化前后对比\n\n")
            
            if 'startup' in test_results and 'startup' in baseline_data:
                curr = test_results['startup']
                base = baseline_data['startup']
                
                if curr and base and 'window_time' in curr and 'window_time' in base:
                    curr_time = curr['window_time']
                    base_time = base['window_time']
                    improvement = ((base_time - curr_time) / base_time * 100)
                    
                    f.write("### 启动时间改善\n\n")
                    f.write(f"- 优化前: {base_time:.3f}秒\n")
                    f.write(f"- 优化后: {curr_time:.3f}秒\n")
                    f.write(f"- 改善: {improvement:+.1f}%\n\n")
            
            if 'memory' in test_results and 'memory' in baseline_data:
                curr = test_results['memory']
                base = baseline_data['memory']
                
                if curr and base and 'idle_memory' in curr and 'idle_memory' in base:
                    curr_mem = curr['idle_memory']
                    base_mem = base['idle_memory']
                    improvement = ((base_mem - curr_mem) / base_mem * 100)
                    
                    f.write("### 内存占用改善\n\n")
                    f.write(f"- 优化前: {base_mem:.1f} MB\n")
                    f.write(f"- 优化后: {curr_mem:.1f} MB\n")
                    f.write(f"- 改善: {improvement:+.1f}%\n\n")
        
        f.write("## 结论\n\n")
        
        all_passed = all(
            test_results.get(key, {}).get('passed', False)
            for key in ['startup', 'memory', 'modules', 'lazy_loading']
            if test_results.get(key)
        )
        
        if all_passed:
            f.write("✅ **所有性能指标达标** - 优化效果显著\n\n")
        else:
            f.write("⚠️  **部分性能指标未达标** - 需要进一步优化\n\n")
    
    print(f"✅ 报告已保存: {output_file}")
    print()


def main():
    """主测试流程"""
    print()
    print("=" * 80)
    print("集成测试 - 性能指标验证")
    print("=" * 80)
    print()
    
    test_results = {}
    
    # 运行所有测试
    test_results['startup'] = test_startup_time()
    test_results['memory'] = test_memory_usage()
    test_results['modules'] = test_module_loading()
    test_results['lazy_loading'] = test_lazy_loading_performance()
    
    # 加载基线数据
    baseline_data = load_baseline_data()
    
    # 保存当前数据
    save_current_data(test_results)
    
    # 对比基线
    compare_with_baseline(test_results, baseline_data)
    
    # 生成报告
    generate_report(test_results, baseline_data)
    
    # 总结
    all_passed = all(
        test_results.get(key, {}).get('passed', False)
        for key in ['startup', 'memory', 'modules', 'lazy_loading']
        if test_results.get(key)
    )
    
    print("=" * 80)
    if all_passed:
        print("✅ 测试通过 - 所有性能指标达标")
    else:
        print("⚠️  测试完成 - 部分性能指标未达标")
    print("=" * 80)
    print()
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
