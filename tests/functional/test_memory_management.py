"""
内存管理的属性测试
验证内存释放的正确性和空闲时内存占用符合要求
"""

import os
import sys
import time
import unittest
import tempfile
from pathlib import Path
from PIL import Image

# 尝试导入psutil，如果不可用则跳过内存测试
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("警告: psutil未安装，内存测试将被跳过")
    print("安装命令: pip install psutil")

from optimized_image_loader import OptimizedImageLoader


class TestMemoryManagement(unittest.TestCase):
    """内存管理属性测试"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试类"""
        # 创建临时目录
        cls.temp_dir = tempfile.mkdtemp()
        
        # 创建测试图像
        img = Image.new('RGB', (1920, 1080), color='white')
        cls.test_image_path = os.path.join(cls.temp_dir, "test_image.png")
        img.save(cls.test_image_path)
        
        # 创建大尺寸测试图像
        large_img = Image.new('RGB', (3840, 2160), color='blue')
        cls.large_test_image_path = os.path.join(cls.temp_dir, "large_test_image.png")
        large_img.save(cls.large_test_image_path)
    
    @classmethod
    def tearDownClass(cls):
        """清理测试类"""
        import shutil
        if os.path.exists(cls.temp_dir):
            shutil.rmtree(cls.temp_dir)
    
    def get_process_memory_mb(self):
        """获取当前进程的内存占用（MB）"""
        if not PSUTIL_AVAILABLE:
            self.skipTest("psutil未安装，跳过内存测试")
        process = psutil.Process()
        return process.memory_info().rss / 1024 / 1024
    
    def test_property_3_memory_release_correctness(self):
        """
        **Feature: ocr-system-optimization, Property 3: 内存释放正确性**
        
        属性: 对于任何文件切换操作，切换后前一个文件的图像数据应从内存中释放，
        内存占用应回到基线水平（±10MB容差）
        
        **Validates: Requirements 9.1, 9.3, 9.4**
        """
        # 记录基线内存
        OptimizedImageLoader.trigger_gc()
        time.sleep(0.5)
        baseline_memory = self.get_process_memory_mb()
        
        # 加载大图像以确保内存变化可检测
        images = []
        for _ in range(10):
            img = OptimizedImageLoader.load_for_display(self.large_test_image_path)
            images.append(img)
        
        memory_after_load = self.get_process_memory_mb()
        
        # 验证加载后内存增加
        memory_increase = memory_after_load - baseline_memory
        print(f"\n内存变化: 基线={baseline_memory:.2f}MB, 加载后={memory_after_load:.2f}MB, 增加={memory_increase:.2f}MB")
        
        # 释放所有图像
        for img in images:
            OptimizedImageLoader.release_image(img)
        images.clear()
        
        # 触发垃圾回收
        OptimizedImageLoader.trigger_gc()
        time.sleep(0.5)
        
        # 检查内存是否回到基线水平（±10MB容差）
        memory_after_release = self.get_process_memory_mb()
        memory_diff = abs(memory_after_release - baseline_memory)
        
        print(f"释放后: {memory_after_release:.2f}MB, 差异={memory_diff:.2f}MB")
        
        self.assertLessEqual(
            memory_diff, 10,
            f"释放图像后内存应回到基线水平（±10MB容差）。"
            f"基线: {baseline_memory:.2f}MB, "
            f"释放后: {memory_after_release:.2f}MB, "
            f"差异: {memory_diff:.2f}MB"
        )
    
    def test_property_3_multiple_file_switches(self):
        """
        **Feature: ocr-system-optimization, Property 3: 内存释放正确性（多次切换）**
        
        属性: 对于任何多次文件切换操作，每次切换后内存应正确释放
        
        **Validates: Requirements 9.1, 9.3, 9.4**
        """
        # 记录基线内存
        OptimizedImageLoader.trigger_gc()
        time.sleep(0.5)
        baseline_memory = self.get_process_memory_mb()
        
        # 模拟多次文件切换
        for i in range(5):
            # 加载第一个图像
            img1 = OptimizedImageLoader.load_for_display(self.test_image_path)
            
            # 释放并加载第二个图像
            OptimizedImageLoader.release_image(img1)
            img1 = None
            OptimizedImageLoader.trigger_gc()
            
            img2 = OptimizedImageLoader.load_for_display(self.large_test_image_path)
            
            # 释放第二个图像
            OptimizedImageLoader.release_image(img2)
            img2 = None
            OptimizedImageLoader.trigger_gc()
        
        # 最终检查内存
        time.sleep(0.5)
        final_memory = self.get_process_memory_mb()
        memory_diff = abs(final_memory - baseline_memory)
        
        # 允许更大的容差（20MB），因为多次操作可能有累积
        self.assertLessEqual(
            memory_diff, 20,
            f"多次切换后内存应回到基线水平（±20MB容差）。"
            f"基线: {baseline_memory:.2f}MB, "
            f"最终: {final_memory:.2f}MB, "
            f"差异: {memory_diff:.2f}MB"
        )
    
    def test_property_4_idle_memory_upper_bound(self):
        """
        **Feature: ocr-system-optimization, Property 4: 空闲内存上界**
        
        属性: 对于任何空闲状态（无文件加载，无OCR任务），
        程序的内存占用应低于200MB
        
        **Validates: Requirements 9.5**
        
        注意: 这个测试在完整应用程序中运行时更有意义。
        在单元测试环境中，我们验证基本的内存管理机制。
        """
        # 触发垃圾回收，模拟空闲状态
        OptimizedImageLoader.trigger_gc()
        time.sleep(1)
        
        # 获取当前内存占用
        idle_memory = self.get_process_memory_mb()
        
        # 在单元测试环境中，我们期望内存占用较低
        # 完整应用程序的200MB限制在集成测试中验证
        self.assertLess(
            idle_memory, 200,
            f"空闲状态下内存占用应低于200MB。"
            f"当前: {idle_memory:.2f}MB"
        )
    
    def test_image_loading_memory_efficiency(self):
        """
        测试图像加载的内存效率
        
        验证大图像被正确缩放，不会占用过多内存
        """
        # 记录加载前内存
        OptimizedImageLoader.trigger_gc()
        time.sleep(0.5)
        memory_before = self.get_process_memory_mb()
        
        # 加载大图像（应该被自动缩放）
        img = OptimizedImageLoader.load_for_display(self.large_test_image_path)
        
        # 验证图像被缩放
        self.assertLessEqual(img.width, 1920, "图像宽度应该被缩放")
        self.assertLessEqual(img.height, 1080, "图像高度应该被缩放")
        
        # 记录加载后内存
        memory_after = self.get_process_memory_mb()
        memory_increase = memory_after - memory_before
        
        # 验证内存增加合理（缩放后的图像不应占用太多内存）
        # 1920x1080 RGB图像约6MB，允许一些开销
        self.assertLess(
            memory_increase, 50,
            f"加载缩放后的图像不应占用过多内存。"
            f"内存增加: {memory_increase:.2f}MB"
        )
        
        # 清理
        OptimizedImageLoader.release_image(img)
    
    def test_region_loading_memory_efficiency(self):
        """
        测试区域加载的内存效率
        
        验证区域加载只加载需要的部分
        """
        # 记录加载前内存
        OptimizedImageLoader.trigger_gc()
        time.sleep(0.5)
        memory_before = self.get_process_memory_mb()
        
        # 加载小区域（左上角100x100）
        region = (0, 0, 100, 100)
        img = OptimizedImageLoader.load_for_ocr(self.large_test_image_path, region=region)
        
        # 验证只加载了指定区域
        self.assertEqual(img.width, 100, "应该只加载指定区域的宽度")
        self.assertEqual(img.height, 100, "应该只加载指定区域的高度")
        
        # 记录加载后内存
        memory_after = self.get_process_memory_mb()
        memory_increase = memory_after - memory_before
        
        # 验证内存增加很小（100x100 RGB图像约30KB）
        self.assertLess(
            memory_increase, 10,
            f"加载小区域不应占用太多内存。"
            f"内存增加: {memory_increase:.2f}MB"
        )
        
        # 清理
        OptimizedImageLoader.release_image(img)
    
    def test_gc_trigger_effectiveness(self):
        """
        测试垃圾回收触发的有效性
        
        验证trigger_gc()能有效释放内存
        """
        # 创建多个图像对象
        images = []
        for _ in range(10):
            img = OptimizedImageLoader.load_for_display(self.test_image_path)
            images.append(img)
        
        memory_with_images = self.get_process_memory_mb()
        
        # 释放所有图像
        for img in images:
            OptimizedImageLoader.release_image(img)
        images.clear()
        
        # 不触发GC，内存可能还未释放
        memory_before_gc = self.get_process_memory_mb()
        
        # 触发GC
        OptimizedImageLoader.trigger_gc()
        time.sleep(0.5)
        
        # 检查内存是否减少
        memory_after_gc = self.get_process_memory_mb()
        
        # GC应该释放一些内存
        self.assertLessEqual(
            memory_after_gc, memory_before_gc,
            f"触发GC后内存应该减少或保持不变。"
            f"GC前: {memory_before_gc:.2f}MB, "
            f"GC后: {memory_after_gc:.2f}MB"
        )


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)
