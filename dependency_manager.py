"""
依赖管理器 - 管理可选依赖的延迟加载

这个模块提供了一个统一的接口来管理可选依赖的延迟加载，
避免在启动时加载所有依赖，从而提升启动速度和减少内存占用。

使用示例:
    # Excel导出
    openpyxl = DependencyManager.load_excel_support()
    if openpyxl:
        workbook = openpyxl.Workbook()
    
    # PDF处理
    fitz = DependencyManager.load_pdf_support()
    if fitz:
        doc = fitz.open(pdf_path)
    
    # 检查模块可用性
    if DependencyManager.is_available('openpyxl'):
        print("Excel支持可用")
"""

from typing import Optional, Any
import sys


class DependencyManager:
    """管理可选依赖的延迟加载"""
    
    # 缓存已加载的模块，避免重复导入
    _loaded_modules = {}
    
    @staticmethod
    def load_excel_support() -> Optional[Any]:
        """
        按需加载Excel支持（openpyxl）
        
        Returns:
            openpyxl模块，如果不可用则返回None
        
        Example:
            openpyxl = DependencyManager.load_excel_support()
            if openpyxl:
                wb = openpyxl.Workbook()
        """
        if 'openpyxl' not in DependencyManager._loaded_modules:
            try:
                import openpyxl
                DependencyManager._loaded_modules['openpyxl'] = openpyxl
                print("[DependencyManager] ✓ openpyxl 已加载")
            except ImportError as e:
                print(f"[DependencyManager] ✗ openpyxl 不可用: {e}")
                DependencyManager._loaded_modules['openpyxl'] = None
        
        return DependencyManager._loaded_modules['openpyxl']
    
    @staticmethod
    def load_pdf_support() -> Optional[Any]:
        """
        按需加载PDF支持（PyMuPDF/fitz）
        
        Returns:
            fitz模块，如果不可用则返回None
        
        Example:
            fitz = DependencyManager.load_pdf_support()
            if fitz:
                doc = fitz.open(pdf_path)
        """
        if 'fitz' not in DependencyManager._loaded_modules:
            try:
                import fitz  # PyMuPDF
                DependencyManager._loaded_modules['fitz'] = fitz
                print("[DependencyManager] ✓ PyMuPDF (fitz) 已加载")
            except ImportError as e:
                print(f"[DependencyManager] ✗ PyMuPDF 不可用: {e}")
                DependencyManager._loaded_modules['fitz'] = None
        
        return DependencyManager._loaded_modules['fitz']
    
    @staticmethod
    def load_ocr_engine() -> Optional[Any]:
        """
        按需加载OCR引擎管理器
        
        Returns:
            OCREngineManager类，如果不可用则返回None
        
        Example:
            OCREngineManager = DependencyManager.load_ocr_engine()
            if OCREngineManager:
                manager = OCREngineManager()
        """
        if 'ocr_engine_manager' not in DependencyManager._loaded_modules:
            try:
                from ocr_engine_manager import OCREngineManager
                DependencyManager._loaded_modules['ocr_engine_manager'] = OCREngineManager
                print("[DependencyManager] ✓ OCREngineManager 已加载")
            except ImportError as e:
                print(f"[DependencyManager] ✗ OCREngineManager 不可用: {e}")
                DependencyManager._loaded_modules['ocr_engine_manager'] = None
        
        return DependencyManager._loaded_modules['ocr_engine_manager']
    
    @staticmethod
    def load_aliyun_ocr() -> Optional[Any]:
        """
        按需加载阿里云OCR支持
        
        Returns:
            alibabacloud_ocr_api20210707模块，如果不可用则返回None
        
        Example:
            aliyun_ocr = DependencyManager.load_aliyun_ocr()
            if aliyun_ocr:
                client = aliyun_ocr.client.Client(config)
        """
        if 'alibabacloud_ocr_api20210707' not in DependencyManager._loaded_modules:
            try:
                import alibabacloud_ocr_api20210707
                DependencyManager._loaded_modules['alibabacloud_ocr_api20210707'] = alibabacloud_ocr_api20210707
                print("[DependencyManager] ✓ 阿里云OCR SDK 已加载")
            except ImportError as e:
                print(f"[DependencyManager] ✗ 阿里云OCR SDK 不可用: {e}")
                DependencyManager._loaded_modules['alibabacloud_ocr_api20210707'] = None
        
        return DependencyManager._loaded_modules['alibabacloud_ocr_api20210707']
    
    @staticmethod
    def load_deepseek_ocr() -> Optional[Any]:
        """
        按需加载DeepSeek OCR支持（OpenAI SDK）
        
        Returns:
            openai模块，如果不可用则返回None
        
        Example:
            openai = DependencyManager.load_deepseek_ocr()
            if openai:
                client = openai.OpenAI(api_key=key, base_url=url)
        """
        if 'openai' not in DependencyManager._loaded_modules:
            try:
                import openai
                DependencyManager._loaded_modules['openai'] = openai
                print("[DependencyManager] ✓ OpenAI SDK (DeepSeek) 已加载")
            except ImportError as e:
                print(f"[DependencyManager] ✗ OpenAI SDK 不可用: {e}")
                DependencyManager._loaded_modules['openai'] = None
        
        return DependencyManager._loaded_modules['openai']
    
    @staticmethod
    def is_available(module_name: str) -> bool:
        """
        检查模块是否可用（不导入模块）
        
        Args:
            module_name: 模块名称，如 'openpyxl', 'fitz', 'openai'
        
        Returns:
            True如果模块可用，False如果不可用
        
        Example:
            if DependencyManager.is_available('openpyxl'):
                print("Excel导出功能可用")
        """
        # 如果已经加载过，直接返回结果
        if module_name in DependencyManager._loaded_modules:
            return DependencyManager._loaded_modules[module_name] is not None
        
        # 检查模块是否可导入（不实际导入）
        try:
            # 使用importlib.util.find_spec检查模块是否存在
            import importlib.util
            spec = importlib.util.find_spec(module_name)
            return spec is not None
        except (ImportError, ModuleNotFoundError, ValueError):
            return False
    
    @staticmethod
    def get_loaded_modules():
        """
        获取已加载的模块列表
        
        Returns:
            已加载模块的字典 {module_name: module_object}
        
        Example:
            loaded = DependencyManager.get_loaded_modules()
            print(f"已加载 {len(loaded)} 个模块")
        """
        return {
            name: module 
            for name, module in DependencyManager._loaded_modules.items() 
            if module is not None
        }
    
    @staticmethod
    def clear_cache():
        """
        清除模块缓存（主要用于测试）
        
        Warning:
            这不会卸载已导入的模块，只是清除缓存记录
        """
        DependencyManager._loaded_modules.clear()
        print("[DependencyManager] 缓存已清除")
    
    @staticmethod
    def get_module_info():
        """
        获取所有可选模块的状态信息
        
        Returns:
            模块状态字典
        """
        modules = {
            'openpyxl': {
                'name': 'Excel支持',
                'loaded': 'openpyxl' in DependencyManager._loaded_modules,
                'available': DependencyManager.is_available('openpyxl'),
            },
            'fitz': {
                'name': 'PDF支持',
                'loaded': 'fitz' in DependencyManager._loaded_modules,
                'available': DependencyManager.is_available('fitz'),
            },
            'alibabacloud_ocr_api20210707': {
                'name': '阿里云OCR',
                'loaded': 'alibabacloud_ocr_api20210707' in DependencyManager._loaded_modules,
                'available': DependencyManager.is_available('alibabacloud_ocr_api20210707'),
            },
            'openai': {
                'name': 'DeepSeek OCR',
                'loaded': 'openai' in DependencyManager._loaded_modules,
                'available': DependencyManager.is_available('openai'),
            },
        }
        return modules
    
    @staticmethod
    def print_status():
        """打印所有可选模块的状态"""
        print("\n" + "=" * 60)
        print("依赖管理器状态")
        print("=" * 60)
        
        info = DependencyManager.get_module_info()
        
        for module_name, module_info in info.items():
            status = "✓ 已加载" if module_info['loaded'] else (
                "○ 可用" if module_info['available'] else "✗ 不可用"
            )
            print(f"{module_info['name']:20s} {status}")
        
        print("=" * 60)
        print()


# 便捷函数
def require_excel():
    """
    确保Excel支持可用，如果不可用则抛出异常
    
    Raises:
        ImportError: 如果openpyxl不可用
    """
    openpyxl = DependencyManager.load_excel_support()
    if not openpyxl:
        raise ImportError(
            "Excel导出功能需要openpyxl库。\n"
            "请安装: pip install openpyxl"
        )
    return openpyxl


def require_pdf():
    """
    确保PDF支持可用，如果不可用则抛出异常
    
    Raises:
        ImportError: 如果PyMuPDF不可用
    """
    fitz = DependencyManager.load_pdf_support()
    if not fitz:
        raise ImportError(
            "PDF处理功能需要PyMuPDF库。\n"
            "请安装: pip install PyMuPDF"
        )
    return fitz


def require_aliyun_ocr():
    """
    确保阿里云OCR支持可用，如果不可用则抛出异常
    
    Raises:
        ImportError: 如果阿里云SDK不可用
    """
    aliyun = DependencyManager.load_aliyun_ocr()
    if not aliyun:
        raise ImportError(
            "阿里云OCR功能需要阿里云SDK。\n"
            "请安装: pip install alibabacloud-ocr-api20210707"
        )
    return aliyun


def require_deepseek_ocr():
    """
    确保DeepSeek OCR支持可用，如果不可用则抛出异常
    
    Raises:
        ImportError: 如果OpenAI SDK不可用
    """
    openai = DependencyManager.load_deepseek_ocr()
    if not openai:
        raise ImportError(
            "DeepSeek OCR功能需要OpenAI SDK。\n"
            "请安装: pip install openai"
        )
    return openai


if __name__ == '__main__':
    # 测试代码
    print("测试 DependencyManager\n")
    
    # 打印初始状态
    DependencyManager.print_status()
    
    # 测试加载
    print("测试加载模块...")
    DependencyManager.load_excel_support()
    DependencyManager.load_pdf_support()
    
    # 打印加载后状态
    DependencyManager.print_status()
    
    # 测试已加载模块
    loaded = DependencyManager.get_loaded_modules()
    print(f"已加载 {len(loaded)} 个模块: {list(loaded.keys())}")
