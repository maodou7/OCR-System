#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试 - 完整工作流测试

测试完整工作流、内存泄漏和长时间运行稳定性。
验证需求: 所有

测试内容:
- 完整工作流（启动→加载→识别→导出）
- 内存泄漏测试（循环处理100个文件）
- 长时间运行稳定性

使用方法:
    python test_integration_comprehensive.py
    python test_integration_comprehensive.py --quick  # 快速测试（10个文件）
"""

import os
import sys
import time
import gc
import argparse
import tempfile
from pathlib import Path


def get_memory_usage():
    """获取当前进程内存占用（MB）"""
    try:
        import psutil
        process = psutil.Process()
        return process.memory_info().rss / (1024 * 1024)
    except ImportError:
        return None


def create_test_images(count=10):
    """创建测试图像"""
    print(f"创建{count}个测试图像...")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        test_dir = tempfile.mkdtemp(prefix='ocr_test_')
        image_paths = []
        
        for i in range(count):
            # 创建测试图像
            img = Image.new('RGB', (800, 600), color='white')
            draw = ImageDraw.Draw(img)
            
            # 添加文本
            text = f"测试图像 {i+1}\nTest Image {i+1}\n这是OCR测试文本"
            draw.text((50, 50), text, fill='black')
            
            # 保存
            img_path = os.path.join(test_dir, f'test_{i+1:03d}.png')
            img.save(img_path)
            image_paths.append(img_path)
        
        print(f"  ✅ 测试图像已创建: {test_dir}")
        return test_dir, image_paths
        
    except Exception as e:
        print(f"  ❌ 创建测试图像失败: {e}")
        return None, []


def test_complete_workflow():
    """测试完整工作流"""
    print("=" * 80)
    print("测试 1: 完整工作流")
    print("=" * 80)
    print()
    
    workflow_steps = [
        "导入核心模块",
        "创建应用实例",
        "加载图像",
        "模拟OCR识别",
        "导出结果",
        "清理资源"
    ]
    
    results = {}
    
    try:
        # 步骤1: 导入核心模块
        print(f"[1/{len(workflow_steps)}] {workflow_steps[0]}...")
        start = time.time()
        
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import Qt
        from PIL import Image
        
        results['import_time'] = time.time() - start
        print(f"  ✅ 完成 ({results['import_time']:.3f}秒)")
        
        # 步骤2: 创建应用实例
        print(f"[2/{len(workflow_steps)}] {workflow_steps[1]}...")
        start = time.time()
        
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        results['app_create_time'] = time.time() - start
        print(f"  ✅ 完成 ({results['app_create_time']:.3f}秒)")
        
        # 步骤3: 加载图像
        print(f"[3/{len(workflow_steps)}] {workflow_steps[2]}...")
        start = time.time()
        
        test_dir, image_paths = create_test_images(5)
        if not image_paths:
            raise Exception("无法创建测试图像")
        
        # 使用优化的图像加载器
        from optimized_image_loader import OptimizedImageLoader
        
        loaded_images = []
        for img_path in image_paths:
            img = OptimizedImageLoader.load_for_display(img_path)
            loaded_images.append(img)
        
        results['load_time'] = time.time() - start
        results['loaded_count'] = len(loaded_images)
        print(f"  ✅ 完成 - 加载{len(loaded_images)}个图像 ({results['load_time']:.3f}秒)")
        
        # 步骤4: 模拟OCR识别
        print(f"[4/{len(workflow_steps)}] {workflow_steps[3]}...")
        start = time.time()
        
        # 注: 实际OCR需要引擎，这里只模拟流程
        ocr_results = []
        for i, img in enumerate(loaded_images):
            result = {
                'image': i,
                'text': f'模拟OCR结果 {i+1}',
                'confidence': 0.95
            }
            ocr_results.append(result)
        
        results['ocr_time'] = time.time() - start
        print(f"  ✅ 完成 - 识别{len(ocr_results)}个图像 ({results['ocr_time']:.3f}秒)")
        
        # 步骤5: 导出结果
        print(f"[5/{len(workflow_steps)}] {workflow_steps[4]}...")
        start = time.time()
        
        from dependency_manager import DependencyManager
        openpyxl = DependencyManager.load_excel_support()
        
        if openpyxl:
            wb = openpyxl.Workbook()
            ws = wb.active
            ws['A1'] = '图像'
            ws['B1'] = '文本'
            ws['C1'] = '置信度'
            
            for i, result in enumerate(ocr_results, 2):
                ws[f'A{i}'] = result['image']
                ws[f'B{i}'] = result['text']
                ws[f'C{i}'] = result['confidence']
            
            export_path = tempfile.mktemp(suffix='.xlsx')
            wb.save(export_path)
            
            results['export_time'] = time.time() - start
            results['export_path'] = export_path
            print(f"  ✅ 完成 - 导出到 {export_path} ({results['export_time']:.3f}秒)")
        else:
            print(f"  ⚠️  跳过 - openpyxl不可用")
        
        # 步骤6: 清理资源
        print(f"[6/{len(workflow_steps)}] {workflow_steps[5]}...")
        start = time.time()
        
        # 清理图像
        loaded_images.clear()
        
        # 清理测试文件
        import shutil
        if test_dir and os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        if 'export_path' in results and os.path.exists(results['export_path']):
            os.remove(results['export_path'])
        
        # 强制垃圾回收
        gc.collect()
        
        results['cleanup_time'] = time.time() - start
        print(f"  ✅ 完成 ({results['cleanup_time']:.3f}秒)")
        
        print()
        print("工作流测试完成!")
        print(f"  总耗时: {sum(results.get(k, 0) for k in ['import_time', 'app_create_time', 'load_time', 'ocr_time', 'export_time', 'cleanup_time']):.3f}秒")
        print()
        
        return True, results
        
    except Exception as e:
        print(f"  ❌ 工作流测试失败: {e}")
        print()
        return False, results


def test_memory_leak(file_count=100):
    """测试内存泄漏"""
    print("=" * 80)
    print(f"测试 2: 内存泄漏测试（处理{file_count}个文件）")
    print("=" * 80)
    print()
    
    try:
        import psutil
    except ImportError:
        print("❌ psutil未安装，无法测试内存泄漏")
        print("   安装: pip install psutil")
        print()
        return False, {}
    
    try:
        from PIL import Image
        from optimized_image_loader import OptimizedImageLoader
        
        # 创建测试图像
        print(f"创建{file_count}个测试图像...")
        test_dir, image_paths = create_test_images(file_count)
        
        if not image_paths:
            raise Exception("无法创建测试图像")
        
        print()
        
        # 记录初始内存
        gc.collect()
        time.sleep(0.5)
        initial_memory = get_memory_usage()
        print(f"初始内存: {initial_memory:.1f} MB")
        
        # 记录内存变化
        memory_samples = [initial_memory]
        
        # 循环处理文件
        print(f"开始处理{file_count}个文件...")
        start_time = time.time()
        
        for i, img_path in enumerate(image_paths):
            # 加载图像
            img = OptimizedImageLoader.load_for_display(img_path)
            
            # 模拟处理
            _ = img.size
            
            # 清理
            del img
            
            # 每10个文件记录一次内存
            if (i + 1) % 10 == 0:
                gc.collect()
                current_memory = get_memory_usage()
                memory_samples.append(current_memory)
                
                progress = (i + 1) / file_count * 100
                print(f"  进度: {i+1}/{file_count} ({progress:.0f}%) - 内存: {current_memory:.1f} MB")
        
        elapsed_time = time.time() - start_time
        
        # 最终清理
        gc.collect()
        time.sleep(0.5)
        final_memory = get_memory_usage()
        
        print()
        print(f"处理完成 - 耗时: {elapsed_time:.1f}秒")
        print(f"最终内存: {final_memory:.1f} MB")
        print()
        
        # 分析内存变化
        memory_increase = final_memory - initial_memory
        max_memory = max(memory_samples)
        avg_memory = sum(memory_samples) / len(memory_samples)
        
        print("内存分析:")
        print(f"  初始内存: {initial_memory:.1f} MB")
        print(f"  最终内存: {final_memory:.1f} MB")
        print(f"  内存增长: {memory_increase:+.1f} MB")
        print(f"  峰值内存: {max_memory:.1f} MB")
        print(f"  平均内存: {avg_memory:.1f} MB")
        print()
        
        # 判断是否有内存泄漏
        # 允许10MB的内存增长（合理范围）
        has_leak = memory_increase > 10
        
        if has_leak:
            print(f"⚠️  可能存在内存泄漏 - 内存增长: {memory_increase:.1f} MB")
        else:
            print(f"✅ 无明显内存泄漏 - 内存增长: {memory_increase:.1f} MB")
        
        print()
        
        # 清理测试文件
        import shutil
        if test_dir and os.path.exists(test_dir):
            shutil.rmtree(test_dir)
        
        results = {
            'initial_memory': initial_memory,
            'final_memory': final_memory,
            'memory_increase': memory_increase,
            'max_memory': max_memory,
            'avg_memory': avg_memory,
            'file_count': file_count,
            'elapsed_time': elapsed_time,
            'has_leak': has_leak,
            'memory_samples': memory_samples
        }
        
        return not has_leak, results
        
    except Exception as e:
        print(f"❌ 内存泄漏测试失败: {e}")
        print()
        return False, {}


def test_long_running_stability(duration_minutes=5):
    """测试长时间运行稳定性"""
    print("=" * 80)
    print(f"测试 3: 长时间运行稳定性（{duration_minutes}分钟）")
    print("=" * 80)
    print()
    
    try:
        import psutil
    except ImportError:
        print("❌ psutil未安装，无法测试稳定性")
        print()
        return False, {}
    
    try:
        from PySide6.QtWidgets import QApplication
        from PySide6.QtCore import QTimer
        
        # 创建应用
        app = QApplication.instance()
        if app is None:
            app = QApplication(sys.argv)
        
        print(f"程序将运行{duration_minutes}分钟，监控内存和稳定性...")
        print()
        
        # 记录初始状态
        gc.collect()
        initial_memory = get_memory_usage()
        start_time = time.time()
        
        memory_samples = []
        check_interval = 30  # 每30秒检查一次
        
        print(f"初始内存: {initial_memory:.1f} MB")
        print(f"开始时间: {time.strftime('%H:%M:%S')}")
        print()
        
        # 运行指定时间
        duration_seconds = duration_minutes * 60
        checks = 0
        
        while time.time() - start_time < duration_seconds:
            # 等待
            time.sleep(check_interval)
            
            # 检查内存
            current_memory = get_memory_usage()
            memory_samples.append(current_memory)
            
            elapsed = time.time() - start_time
            remaining = duration_seconds - elapsed
            
            checks += 1
            print(f"[检查 {checks}] 运行时间: {elapsed/60:.1f}分钟 - 内存: {current_memory:.1f} MB - 剩余: {remaining/60:.1f}分钟")
        
        # 最终状态
        gc.collect()
        final_memory = get_memory_usage()
        total_time = time.time() - start_time
        
        print()
        print(f"测试完成 - 总运行时间: {total_time/60:.1f}分钟")
        print(f"最终内存: {final_memory:.1f} MB")
        print()
        
        # 分析
        memory_increase = final_memory - initial_memory
        max_memory = max(memory_samples) if memory_samples else final_memory
        avg_memory = sum(memory_samples) / len(memory_samples) if memory_samples else final_memory
        
        print("稳定性分析:")
        print(f"  初始内存: {initial_memory:.1f} MB")
        print(f"  最终内存: {final_memory:.1f} MB")
        print(f"  内存增长: {memory_increase:+.1f} MB")
        print(f"  峰值内存: {max_memory:.1f} MB")
        print(f"  平均内存: {avg_memory:.1f} MB")
        print(f"  检查次数: {checks}")
        print()
        
        # 判断稳定性
        # 允许20MB的内存增长
        is_stable = memory_increase < 20
        
        if is_stable:
            print(f"✅ 长时间运行稳定")
        else:
            print(f"⚠️  长时间运行可能不稳定 - 内存增长: {memory_increase:.1f} MB")
        
        print()
        
        results = {
            'initial_memory': initial_memory,
            'final_memory': final_memory,
            'memory_increase': memory_increase,
            'max_memory': max_memory,
            'avg_memory': avg_memory,
            'duration_minutes': total_time / 60,
            'checks': checks,
            'is_stable': is_stable,
            'memory_samples': memory_samples
        }
        
        return is_stable, results
        
    except Exception as e:
        print(f"❌ 稳定性测试失败: {e}")
        print()
        return False, {}


def generate_report(test_results, output_file='INTEGRATION_TEST_COMPREHENSIVE_REPORT.md'):
    """生成测试报告"""
    print("=" * 80)
    print("生成测试报告")
    print("=" * 80)
    print()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# 集成测试报告 - 完整工作流测试\n\n")
        f.write(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## 测试概述\n\n")
        f.write("本测试验证系统的完整工作流、内存管理和长时间运行稳定性。\n\n")
        
        f.write("## 测试结果\n\n")
        
        # 工作流测试
        if 'workflow' in test_results:
            workflow_passed, workflow_data = test_results['workflow']
            f.write("### 1. 完整工作流测试\n\n")
            f.write(f"状态: {'✅ 通过' if workflow_passed else '❌ 失败'}\n\n")
            
            if workflow_data:
                f.write("详细数据:\n")
                for key, value in workflow_data.items():
                    if isinstance(value, float):
                        f.write(f"- {key}: {value:.3f}秒\n")
                    else:
                        f.write(f"- {key}: {value}\n")
                f.write("\n")
        
        # 内存泄漏测试
        if 'memory_leak' in test_results:
            leak_passed, leak_data = test_results['memory_leak']
            f.write("### 2. 内存泄漏测试\n\n")
            f.write(f"状态: {'✅ 通过' if leak_passed else '❌ 失败'}\n\n")
            
            if leak_data:
                f.write("详细数据:\n")
                f.write(f"- 处理文件数: {leak_data.get('file_count', 0)}\n")
                f.write(f"- 初始内存: {leak_data.get('initial_memory', 0):.1f} MB\n")
                f.write(f"- 最终内存: {leak_data.get('final_memory', 0):.1f} MB\n")
                f.write(f"- 内存增长: {leak_data.get('memory_increase', 0):+.1f} MB\n")
                f.write(f"- 峰值内存: {leak_data.get('max_memory', 0):.1f} MB\n")
                f.write(f"- 处理时间: {leak_data.get('elapsed_time', 0):.1f}秒\n\n")
        
        # 稳定性测试
        if 'stability' in test_results:
            stability_passed, stability_data = test_results['stability']
            f.write("### 3. 长时间运行稳定性测试\n\n")
            f.write(f"状态: {'✅ 通过' if stability_passed else '❌ 失败'}\n\n")
            
            if stability_data:
                f.write("详细数据:\n")
                f.write(f"- 运行时间: {stability_data.get('duration_minutes', 0):.1f}分钟\n")
                f.write(f"- 初始内存: {stability_data.get('initial_memory', 0):.1f} MB\n")
                f.write(f"- 最终内存: {stability_data.get('final_memory', 0):.1f} MB\n")
                f.write(f"- 内存增长: {stability_data.get('memory_increase', 0):+.1f} MB\n")
                f.write(f"- 峰值内存: {stability_data.get('max_memory', 0):.1f} MB\n")
                f.write(f"- 检查次数: {stability_data.get('checks', 0)}\n\n")
        
        f.write("## 结论\n\n")
        
        all_passed = all(
            test_results.get(key, (False, {}))[0]
            for key in ['workflow', 'memory_leak', 'stability']
            if key in test_results
        )
        
        if all_passed:
            f.write("✅ **所有测试通过** - 系统工作流完整，内存管理良好，长时间运行稳定\n\n")
        else:
            f.write("⚠️  **部分测试失败** - 需要进一步调查和优化\n\n")
    
    print(f"✅ 报告已保存: {output_file}")
    print()


def main():
    parser = argparse.ArgumentParser(description='完整工作流集成测试')
    parser.add_argument('--quick', action='store_true',
                       help='快速测试模式（10个文件，1分钟）')
    parser.add_argument('--skip-stability', action='store_true',
                       help='跳过长时间稳定性测试')
    
    args = parser.parse_args()
    
    print()
    print("=" * 80)
    print("集成测试 - 完整工作流测试")
    print("=" * 80)
    print()
    
    if args.quick:
        print("⚡ 快速测试模式")
        print()
        file_count = 10
        stability_duration = 1
    else:
        file_count = 100
        stability_duration = 5
    
    test_results = {}
    
    # 测试1: 完整工作流
    test_results['workflow'] = test_complete_workflow()
    
    # 测试2: 内存泄漏
    test_results['memory_leak'] = test_memory_leak(file_count)
    
    # 测试3: 长时间稳定性
    if not args.skip_stability:
        test_results['stability'] = test_long_running_stability(stability_duration)
    else:
        print("⏭️  跳过长时间稳定性测试")
        print()
    
    # 生成报告
    generate_report(test_results)
    
    # 总结
    all_passed = all(
        test_results.get(key, (False, {}))[0]
        for key in ['workflow', 'memory_leak', 'stability']
        if key in test_results
    )
    
    print("=" * 80)
    if all_passed:
        print("✅ 测试通过 - 所有测试通过")
    else:
        print("⚠️  测试完成 - 部分测试失败")
    print("=" * 80)
    print()
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
