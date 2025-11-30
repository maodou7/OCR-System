#!/usr/bin/env python3
"""
启动性能属性测试

**Feature: ocr-system-optimization, Property 2: 启动时间上界**
**Validates: Requirements 8.1, 8.5**

属性2: 启动时间上界
对于任何启动场景，从程序启动到主窗口显示的时间应小于1秒，
从启动到完全就绪（不含OCR引擎）的时间应小于3秒。

验证需求: 8.1, 8.5
"""

import sys
import os
import time
import unittest
from PySide6.QtWidgets import QApplication

# 确保导入路径正确
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class TestStartupPerformance(unittest.TestCase):
    """
    启动性能属性测试
    
    测试启动时间是否符合性能要求
    """
    
    @classmethod
    def setUpClass(cls):
        """设置测试类（只创建一次QApplication）"""
        # 检查是否已经存在 QApplication 实例
        cls.app = QApplication.instance()
        if cls.app is None:
            cls.app = QApplication(sys.argv)
    
    @classmethod
    def tearDownClass(cls):
        """清理测试类"""
        # 不要退出 QApplication，因为可能被其他测试使用
        # 只处理待处理的事件
        if cls.app:
            cls.app.processEvents()
    
    def setUp(self):
        """设置每个测试"""
        # QApplication 已在 setUpClass 中创建，这里只需要确保它存在
        pass
    
    def tearDown(self):
        """清理每个测试"""
        # 处理事件循环，清理窗口
        if self.app:
            self.app.processEvents()
    
    def test_property_2_startup_time_window_display(self):
        """
        属性2: 启动时间上界 - 窗口显示
        
        **Feature: ocr-system-optimization, Property 2: 启动时间上界**
        **Validates: Requirements 8.1**
        
        测试从程序启动到主窗口显示的时间应小于1秒
        """
        print("\n" + "=" * 60)
        print("测试: 启动到窗口显示 < 1秒")
        print("=" * 60)
        
        # 记录启动开始时间
        start_time = time.time()
        
        # 导入模块
        from qt_main import MainWindow
        
        # 创建主窗口
        win = MainWindow()
        
        # 显示窗口
        win.show()
        
        # 处理事件循环（让窗口完全渲染）
        self.app.processEvents()
        
        # 计算启动时间
        elapsed_time = time.time() - start_time
        
        print(f"启动到窗口显示耗时: {elapsed_time:.3f}秒")
        
        # 关闭窗口
        win.close()
        
        # 验证启动时间 < 1秒
        self.assertLess(
            elapsed_time, 
            1.0, 
            f"启动到窗口显示耗时 {elapsed_time:.3f}秒，超过1秒限制"
        )
        
        print(f"✓ 测试通过: 启动时间 {elapsed_time:.3f}秒 < 1秒")
    
    def test_property_2_startup_time_fully_ready(self):
        """
        属性2: 启动时间上界 - 完全就绪
        
        **Feature: ocr-system-optimization, Property 2: 启动时间上界**
        **Validates: Requirements 8.5**
        
        测试从启动到完全就绪（不含OCR引擎）的时间应小于3秒
        """
        print("\n" + "=" * 60)
        print("测试: 启动到完全就绪 < 3秒")
        print("=" * 60)
        
        # 记录启动开始时间
        start_time = time.time()
        
        # 导入模块
        from qt_main import MainWindow
        
        # 创建主窗口
        win = MainWindow()
        
        # 显示窗口
        win.show()
        
        # 处理事件循环（让窗口完全渲染）
        self.app.processEvents()
        
        # 等待所有延迟初始化完成（不含OCR引擎）
        # 使用QTimer.singleShot(0, ...)的组件会在下一个事件循环中初始化
        for _ in range(10):  # 处理多次事件循环，确保所有延迟初始化完成
            self.app.processEvents()
            time.sleep(0.01)
        
        # 计算启动时间
        elapsed_time = time.time() - start_time
        
        print(f"启动到完全就绪耗时: {elapsed_time:.3f}秒")
        
        # 关闭窗口
        win.close()
        
        # 验证启动时间 < 3秒
        self.assertLess(
            elapsed_time, 
            3.0, 
            f"启动到完全就绪耗时 {elapsed_time:.3f}秒，超过3秒限制"
        )
        
        print(f"✓ 测试通过: 启动时间 {elapsed_time:.3f}秒 < 3秒")
    
    def test_property_2_startup_time_consistency(self):
        """
        属性2: 启动时间上界 - 一致性测试
        
        **Feature: ocr-system-optimization, Property 2: 启动时间上界**
        **Validates: Requirements 8.1, 8.5**
        
        测试多次启动的时间一致性（排除首次启动的模块加载时间）
        """
        print("\n" + "=" * 60)
        print("测试: 启动时间一致性")
        print("=" * 60)
        
        # 预热：首次导入模块（会被缓存）
        print("\n预热阶段：首次导入模块...")
        from qt_main import MainWindow
        warmup_win = MainWindow()
        warmup_win.show()
        self.app.processEvents()
        warmup_win.close()
        self.app.processEvents()
        del warmup_win
        import gc
        gc.collect()
        time.sleep(0.5)
        print("✓ 预热完成，开始正式测试\n")
        
        startup_times = []
        num_runs = 3  # 运行3次测试
        
        for i in range(num_runs):
            print(f"第 {i+1}/{num_runs} 次启动测试...")
            
            # 记录启动开始时间
            start_time = time.time()
            
            # 创建主窗口（模块已缓存）
            win = MainWindow()
            
            # 显示窗口
            win.show()
            
            # 处理事件循环
            self.app.processEvents()
            
            # 计算启动时间
            elapsed_time = time.time() - start_time
            startup_times.append(elapsed_time)
            
            print(f"  启动耗时: {elapsed_time:.3f}秒")
            
            # 关闭窗口
            win.close()
            
            # 处理事件循环，清理窗口
            self.app.processEvents()
            
            # 清理窗口对象
            del win
            
            # 强制垃圾回收
            gc.collect()
            
            # 等待一下再进行下一次测试
            time.sleep(0.5)
        
        # 计算平均值和标准差
        import statistics
        avg_time = statistics.mean(startup_times)
        std_dev = statistics.stdev(startup_times) if len(startup_times) > 1 else 0
        
        print(f"\n启动时间统计（预热后）:")
        print(f"  平均值: {avg_time:.3f}秒")
        print(f"  标准差: {std_dev:.3f}秒")
        print(f"  最小值: {min(startup_times):.3f}秒")
        print(f"  最大值: {max(startup_times):.3f}秒")
        
        # 验证平均启动时间 < 1秒
        self.assertLess(
            avg_time, 
            1.0, 
            f"平均启动时间 {avg_time:.3f}秒，超过1秒限制"
        )
        
        # 验证标准差 < 0.2秒（预热后启动时间应该非常稳定）
        self.assertLess(
            std_dev, 
            0.2, 
            f"启动时间标准差 {std_dev:.3f}秒过大，启动性能不稳定"
        )
        
        print(f"✓ 测试通过: 平均启动时间 {avg_time:.3f}秒 < 1秒，标准差 {std_dev:.3f}秒 < 0.2秒")


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    suite = unittest.TestLoader().loadTestsFromTestCase(TestStartupPerformance)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回测试结果
    return result.wasSuccessful()


if __name__ == "__main__":
    print("=" * 60)
    print("启动性能属性测试")
    print("=" * 60)
    print()
    print("属性2: 启动时间上界")
    print("  - 启动到窗口显示 < 1秒")
    print("  - 启动到完全就绪 < 3秒")
    print()
    
    success = run_tests()
    
    print()
    print("=" * 60)
    if success:
        print("✓ 所有测试通过")
    else:
        print("✗ 部分测试失败")
    print("=" * 60)
    
    sys.exit(0 if success else 1)
