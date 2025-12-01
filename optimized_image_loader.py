"""
优化的图像加载器模块
实现智能图像缩放和内存优化的图像加载功能
"""

import gc
from typing import Optional, Tuple
from PIL import Image
from config import Config
from dependency_manager import DependencyManager


class OptimizedImageLoader:
    """
    优化的图像加载器
    
    功能:
    1. 智能缩放大图以减少内存占用
    2. 支持区域加载以提高OCR性能
    3. 自动格式优化
    4. 主动内存管理
    """
    
    # 默认最大显示尺寸 (1920x1080)
    DEFAULT_MAX_DISPLAY_SIZE = (1920, 1080)
    
    # 默认OCR处理的最大尺寸 (4K)
    DEFAULT_MAX_OCR_SIZE = (3840, 2160)
    
    @staticmethod
    def load_for_display(
        path: str,
        max_size: Optional[Tuple[int, int]] = None,
        auto_convert_rgb: bool = True
    ) -> Image.Image:
        """
        加载图像用于显示（自动缩放大图）
        
        Args:
            path: 图像文件路径
            max_size: 最大显示尺寸 (width, height)，默认为1920x1080
            auto_convert_rgb: 是否自动转换为RGB模式
            
        Returns:
            PIL Image对象
            
        验证需求: 9.2
        """
        if max_size is None:
            max_size = OptimizedImageLoader.DEFAULT_MAX_DISPLAY_SIZE
        
        # 检查是否为PDF文件
        if path.lower().endswith('.pdf'):
            return OptimizedImageLoader._load_pdf_for_display(path, max_size)
        
        # 加载图像
        img = Image.open(path)
        
        # 转换为RGB模式（如果需要）
        if auto_convert_rgb and img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 如果图像过大，缩放到合适大小
        if img.width > max_size[0] or img.height > max_size[1]:
            # 使用thumbnail保持宽高比
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        return img
    
    @staticmethod
    def load_for_ocr(
        path: str,
        region: Optional[Tuple[int, int, int, int]] = None,
        max_size: Optional[Tuple[int, int]] = None
    ) -> Image.Image:
        """
        加载图像用于OCR（仅加载需要的区域）
        
        Args:
            path: 图像文件路径
            region: 区域坐标 (x1, y1, x2, y2)，None表示全图
            max_size: 最大OCR处理尺寸，默认为3840x2160
            
        Returns:
            PIL Image对象
            
        验证需求: 9.2
        """
        if max_size is None:
            max_size = OptimizedImageLoader.DEFAULT_MAX_OCR_SIZE
        
        # 检查是否为PDF文件
        if path.lower().endswith('.pdf'):
            img = OptimizedImageLoader._load_pdf_for_ocr(path)
        else:
            img = Image.open(path)
        
        # 转换为RGB模式
        if img.mode != 'RGB':
            img = img.convert('RGB')
        
        # 如果指定了区域，裁剪
        if region:
            x1, y1, x2, y2 = region
            # 确保坐标在有效范围内
            x1 = max(0, min(x1, img.width))
            y1 = max(0, min(y1, img.height))
            x2 = max(0, min(x2, img.width))
            y2 = max(0, min(y2, img.height))
            
            if x2 > x1 and y2 > y1:
                img = img.crop((x1, y1, x2, y2))
        
        # 如果图像过大，缩放以提高OCR性能
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        return img
    
    @staticmethod
    def _load_pdf_for_display(
        pdf_path: str,
        max_size: Tuple[int, int],
        page_num: int = 0
    ) -> Image.Image:
        """
        加载PDF用于显示
        
        Args:
            pdf_path: PDF文件路径
            max_size: 最大显示尺寸
            page_num: 页码（从0开始）
            
        Returns:
            PIL Image对象
        """
        # 使用DependencyManager按需加载PyMuPDF
        fitz = DependencyManager.load_pdf_support()
        if not fitz:
            raise ImportError(
                "PDF处理功能需要PyMuPDF库。\n"
                "请安装: pip install PyMuPDF"
            )
        
        doc = fitz.open(pdf_path)
        
        # 检查页码是否有效
        if page_num >= len(doc):
            page_num = 0
        
        page = doc[page_num]
        
        # 计算合适的缩放比例
        # 先获取页面原始尺寸
        rect = page.rect
        page_width = rect.width
        page_height = rect.height
        
        # 计算缩放因子以适应max_size
        scale_w = max_size[0] / page_width
        scale_h = max_size[1] / page_height
        zoom = min(scale_w, scale_h, Config.PDF_ZOOM_FACTOR)
        
        # 设置缩放比例
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # 转换为PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        doc.close()
        
        return img
    
    @staticmethod
    def _load_pdf_for_ocr(
        pdf_path: str,
        page_num: int = 0,
        zoom: Optional[float] = None
    ) -> Image.Image:
        """
        加载PDF用于OCR
        
        Args:
            pdf_path: PDF文件路径
            page_num: 页码（从0开始）
            zoom: 缩放因子
            
        Returns:
            PIL Image对象
        """
        # 使用DependencyManager按需加载PyMuPDF
        fitz = DependencyManager.load_pdf_support()
        if not fitz:
            raise ImportError(
                "PDF处理功能需要PyMuPDF库。\n"
                "请安装: pip install PyMuPDF"
            )
        
        if zoom is None:
            zoom = Config.PDF_ZOOM_FACTOR
        
        doc = fitz.open(pdf_path)
        
        # 检查页码是否有效
        if page_num >= len(doc):
            page_num = 0
        
        page = doc[page_num]
        
        # 设置缩放比例
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # 转换为PIL Image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        doc.close()
        
        return img
    
    @staticmethod
    def release_image(img: Optional[Image.Image]) -> None:
        """
        释放图像内存
        
        Args:
            img: PIL Image对象
            
        验证需求: 9.1, 9.3
        """
        if img is not None:
            try:
                img.close()
            except:
                pass
    
    @staticmethod
    def trigger_gc() -> None:
        """
        触发垃圾回收
        
        在空闲时或切换文件后调用，以释放未使用的内存
        
        验证需求: 9.4
        """
        gc.collect()
    
    @staticmethod
    def optimize_image_format(img: Image.Image) -> Image.Image:
        """
        优化图像格式
        
        Args:
            img: PIL Image对象
            
        Returns:
            优化后的PIL Image对象
        """
        # 如果是RGBA或其他模式，转换为RGB以减少内存占用
        if img.mode not in ('RGB', 'L'):
            img = img.convert('RGB')
        
        return img
