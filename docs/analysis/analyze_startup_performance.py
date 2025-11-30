#!/usr/bin/env python3
"""
启动性能分析工具

使用cProfile分析程序启动流程，识别性能瓶颈
验证需求: 8.1
"""

import cProfile
import pstats
import io
import sys
import os
import time
from pathlib import Path

# 确保导入路径正确
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def analyze_startup():
    """
    分析启动性能
    
    使用cProfile记录启动过程中的函数调用和耗时
    生成详细的性能报告
    """
    print("=" * 60)
    print("启动性能分析")
    print("=" * 60)
    print()
    
    # 创建性能分析器
    profiler = cProfile.Profile()
    
    # 记录启动开始时间
    start_time = time.time()
    
    # 开始性能分析
    profiler.enable()
    
    try:
        # 导入主模块（这会触发所有顶层导入）
        print("阶段1: 导入主模块...")
        import_start = time.time()
        from qt_main import MainWindow
        from PySide6.QtWidgets import QApplication
        import_time = time.time() - import_start
        print(f"  ✓ 导入耗时: {import_time:.3f}秒")
        print()
        
        # 创建应用
        print("阶段2: 创建QApplication...")
        app_start = time.time()
        import sys as sys_module
        app = QApplication(sys_module.argv)
        app_time = time.time() - app_start
        print(f"  ✓ QApplication创建耗时: {app_time:.3f}秒")
        print()
        
        # 创建主窗口
        print("阶段3: 创建主窗口...")
        window_start = time.time()
        win = MainWindow()
        window_time = time.time() - window_start
        print(f"  ✓ 主窗口创建耗时: {window_time:.3f}秒")
        print()
        
        # 显示窗口
        print("阶段4: 显示窗口...")
        show_start = time.time()
        win.show()
        show_time = time.time() - show_start
        print(f"  ✓ 窗口显示耗时: {show_time:.3f}秒")
        print()
        
        # 处理事件循环（让窗口完全渲染）
        print("阶段5: 处理事件循环...")
        event_start = time.time()
        app.processEvents()
        event_time = time.time() - event_start
        print(f"  ✓ 事件处理耗时: {event_time:.3f}秒")
        print()
        
        # 停止性能分析
        profiler.disable()
        
        # 计算总启动时间
        total_time = time.time() - start_time
        
        # 生成报告
        print("=" * 60)
        print("启动性能总结")
        print("=" * 60)
        print(f"总启动时间: {total_time:.3f}秒")
        print()
        print("各阶段耗时:")
        print(f"  1. 导入模块:     {import_time:.3f}秒 ({import_time/total_time*100:.1f}%)")
        print(f"  2. 创建应用:     {app_time:.3f}秒 ({app_time/total_time*100:.1f}%)")
        print(f"  3. 创建窗口:     {window_time:.3f}秒 ({window_time/total_time*100:.1f}%)")
        print(f"  4. 显示窗口:     {show_time:.3f}秒 ({show_time/total_time*100:.1f}%)")
        print(f"  5. 事件处理:     {event_time:.3f}秒 ({event_time/total_time*100:.1f}%)")
        print()
        
        # 性能评估
        print("性能评估:")
        if total_time < 1.0:
            print("  ✓ 优秀: 启动时间 < 1秒")
        elif total_time < 3.0:
            print("  ⚠ 良好: 启动时间 < 3秒")
        else:
            print("  ✗ 需要优化: 启动时间 > 3秒")
        print()
        
        # 生成详细的性能报告
        print("=" * 60)
        print("详细性能报告（按累计时间排序，前30个函数）")
        print("=" * 60)
        print()
        
        # 创建统计对象
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s)
        
        # 按累计时间排序，显示前30个函数
        ps.sort_stats('cumulative')
        ps.print_stats(30)
        
        # 输出报告
        report = s.getvalue()
        print(report)
        
        # 保存报告到文件
        report_path = Path(__file__).parent / "startup_performance_report.txt"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("启动性能分析报告\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"总启动时间: {total_time:.3f}秒\n\n")
            f.write("各阶段耗时:\n")
            f.write(f"  1. 导入模块:     {import_time:.3f}秒 ({import_time/total_time*100:.1f}%)\n")
            f.write(f"  2. 创建应用:     {app_time:.3f}秒 ({app_time/total_time*100:.1f}%)\n")
            f.write(f"  3. 创建窗口:     {window_time:.3f}秒 ({window_time/total_time*100:.1f}%)\n")
            f.write(f"  4. 显示窗口:     {show_time:.3f}秒 ({show_time/total_time*100:.1f}%)\n")
            f.write(f"  5. 事件处理:     {event_time:.3f}秒 ({event_time/total_time*100:.1f}%)\n\n")
            f.write("=" * 60 + "\n")
            f.write("详细性能报告\n")
            f.write("=" * 60 + "\n\n")
            f.write(report)
        
        print(f"✓ 详细报告已保存到: {report_path}")
        print()
        
        # 识别性能瓶颈
        print("=" * 60)
        print("性能瓶颈识别")
        print("=" * 60)
        print()
        
        # 分析最耗时的函数
        ps_bottleneck = pstats.Stats(profiler)
        ps_bottleneck.sort_stats('cumulative')
        
        # 获取统计数据
        stats = ps_bottleneck.stats
        
        # 找出耗时超过0.1秒的函数
        bottlenecks = []
        for func, (cc, nc, tt, ct, callers) in stats.items():
            if ct > 0.1:  # 累计时间超过0.1秒
                func_name = f"{func[0]}:{func[1]}({func[2]})"
                bottlenecks.append((func_name, ct, cc))
        
        # 按耗时排序
        bottlenecks.sort(key=lambda x: x[1], reverse=True)
        
        if bottlenecks:
            print("发现以下性能瓶颈（累计时间 > 0.1秒）:")
            print()
            for i, (func_name, cumtime, calls) in enumerate(bottlenecks[:10], 1):
                print(f"{i}. {func_name}")
                print(f"   累计时间: {cumtime:.3f}秒, 调用次数: {calls}")
                print()
        else:
            print("未发现明显的性能瓶颈")
            print()
        
        # 分析模块导入
        print("=" * 60)
        print("模块导入分析")
        print("=" * 60)
        print()
        
        # 检查启动时加载的模块
        import sys as sys_module
        loaded_modules = list(sys_module.modules.keys())
        
        print(f"启动时加载的模块总数: {len(loaded_modules)}")
        print()
        
        # 分类统计
        stdlib_count = 0
        third_party_count = 0
        local_count = 0
        
        for module_name in loaded_modules:
            if module_name.startswith('_') or '.' in module_name:
                continue
            
            # 尝试获取模块对象
            try:
                module = sys_module.modules[module_name]
                if hasattr(module, '__file__') and module.__file__:
                    module_path = module.__file__
                    if 'site-packages' in module_path or 'dist-packages' in module_path:
                        third_party_count += 1
                    elif sys_module.prefix in module_path:
                        stdlib_count += 1
                    else:
                        local_count += 1
                else:
                    stdlib_count += 1
            except:
                pass
        
        print(f"标准库模块: {stdlib_count}")
        print(f"第三方库模块: {third_party_count}")
        print(f"本地模块: {local_count}")
        print()
        
        # 列出关键的第三方模块
        print("关键第三方模块:")
        key_modules = ['PySide6', 'PIL', 'numpy', 'openpyxl', 'fitz']
        for key_module in key_modules:
            if key_module in loaded_modules:
                print(f"  ✓ {key_module} (已加载)")
            else:
                print(f"  ✗ {key_module} (未加载)")
        print()
        
        # 优化建议
        print("=" * 60)
        print("优化建议")
        print("=" * 60)
        print()
        
        suggestions = []
        
        if import_time > total_time * 0.5:
            suggestions.append("• 模块导入占用了超过50%的启动时间，建议使用延迟导入")
        
        if window_time > 0.5:
            suggestions.append("• 主窗口创建耗时较长，建议延迟创建非关键组件")
        
        if 'openpyxl' in loaded_modules:
            suggestions.append("• openpyxl在启动时被加载，建议改为按需导入")
        
        if 'fitz' in loaded_modules:
            suggestions.append("• PyMuPDF(fitz)在启动时被加载，建议改为按需导入")
        
        if 'numpy' in loaded_modules:
            suggestions.append("• numpy在启动时被加载，检查是否必需")
        
        if total_time > 3.0:
            suggestions.append("• 总启动时间超过3秒，需要进行全面优化")
        
        if suggestions:
            for suggestion in suggestions:
                print(suggestion)
        else:
            print("✓ 启动性能良好，无明显优化建议")
        
        print()
        print("=" * 60)
        
        # 关闭应用（不进入事件循环）
        app.quit()
        
        return total_time
        
    except Exception as e:
        profiler.disable()
        print(f"✗ 分析失败: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    analyze_startup()
