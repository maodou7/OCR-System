"""
OCR缓存管理器 - Python封装层
使用C++引擎实现高性能、ACID安全的缓存
"""

import os
import json
import ctypes
from pathlib import Path
from typing import Dict, List, Optional
from config import OCRRect, get_resource_path, get_executable_dir


class OCRCacheManager:
    """OCR缓存管理器"""
    
    def __init__(self, db_path: str = None):
        """
        初始化缓存管理器
        :param db_path: 数据库文件路径（默认使用可执行文件目录下的.ocr_cache/ocr_cache.db）
        """
        # 如果未指定路径，使用可执行文件目录（支持PyInstaller打包）
        if db_path is None:
            exe_dir = get_executable_dir()
            db_path = os.path.join(exe_dir, ".ocr_cache", "ocr_cache.db")
        
        self.db_path = db_path
        self.engine = None
        self._lib = None
        
        # 确保缓存目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 加载C++引擎
        self._load_engine()
        
        # 初始化引擎
        if self._lib:
            self.engine = self._lib.ocr_engine_init(db_path.encode('utf-8'))
            if not self.engine:
                raise RuntimeError("Failed to initialize OCR cache engine")
    
    def _load_engine(self):
        """加载C++共享库"""
        # 根据操作系统确定库文件名
        import platform
        system = platform.system()
        
        if system == "Linux":
            lib_name = "libocr_cache.so"
        elif system == "Darwin":
            lib_name = "libocr_cache.dylib"
        elif system == "Windows":
            lib_name = "ocr_cache.dll"
        else:
            raise RuntimeError(f"Unsupported platform: {system}")
        
        # 库文件位于models目录下（支持PyInstaller打包）
        lib_path = get_resource_path(os.path.join("models", lib_name))
        
        if not os.path.exists(lib_path):
            raise FileNotFoundError(f"OCR cache engine library not found: {lib_path}")
        
        # 加载库
        self._lib = ctypes.CDLL(lib_path)
        
        # 定义函数签名
        # void* ocr_engine_init(const char* db_path)
        self._lib.ocr_engine_init.argtypes = [ctypes.c_char_p]
        self._lib.ocr_engine_init.restype = ctypes.c_void_p
        
        # int ocr_engine_save_result(void* engine, const char* file_path, const char* status,
        #                            int rect_count, const double* rect_coords, const char** rect_texts)
        self._lib.ocr_engine_save_result.argtypes = [
            ctypes.c_void_p, ctypes.c_char_p, ctypes.c_char_p,
            ctypes.c_int, ctypes.POINTER(ctypes.c_double), ctypes.POINTER(ctypes.c_char_p)
        ]
        self._lib.ocr_engine_save_result.restype = ctypes.c_int
        
        # char* ocr_engine_load_all(void* engine)
        self._lib.ocr_engine_load_all.argtypes = [ctypes.c_void_p]
        self._lib.ocr_engine_load_all.restype = ctypes.POINTER(ctypes.c_char)
        
        # int ocr_engine_save_session(void* engine, const char* files_json, int cur_index)
        self._lib.ocr_engine_save_session.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
        self._lib.ocr_engine_save_session.restype = ctypes.c_int
        
        # char* ocr_engine_load_session(void* engine)
        self._lib.ocr_engine_load_session.argtypes = [ctypes.c_void_p]
        self._lib.ocr_engine_load_session.restype = ctypes.POINTER(ctypes.c_char)
        
        # int ocr_engine_has_cache(void* engine)
        self._lib.ocr_engine_has_cache.argtypes = [ctypes.c_void_p]
        self._lib.ocr_engine_has_cache.restype = ctypes.c_int
        
        # void ocr_engine_clear(void* engine)
        self._lib.ocr_engine_clear.argtypes = [ctypes.c_void_p]
        self._lib.ocr_engine_clear.restype = None
        
        # void ocr_engine_destroy(void* engine)
        self._lib.ocr_engine_destroy.argtypes = [ctypes.c_void_p]
        self._lib.ocr_engine_destroy.restype = None
        
        # void ocr_engine_free_string(char* str)
        self._lib.ocr_engine_free_string.argtypes = [ctypes.c_void_p]
        self._lib.ocr_engine_free_string.restype = None
        
        # const char* ocr_engine_get_error(void* engine)
        self._lib.ocr_engine_get_error.argtypes = [ctypes.c_void_p]
        self._lib.ocr_engine_get_error.restype = ctypes.c_char_p
    
    def save_result(self, file_path: str, rects: List[OCRRect], status: str = "已识别") -> bool:
        """
        保存单个文件的OCR结果
        :param file_path: 文件路径
        :param rects: OCR区域列表
        :param status: 识别状态
        :return: 是否成功
        """
        if not self.engine or not self._lib:
            return False
        
        rect_count = len(rects)
        
        if rect_count == 0:
            # 没有区域，只保存文件状态
            coords = (ctypes.c_double * 0)()
            texts = (ctypes.c_char_p * 0)()
        else:
            # 准备坐标数组
            coords = (ctypes.c_double * (rect_count * 4))()
            for i, rect in enumerate(rects):
                coords[i * 4 + 0] = rect.x1
                coords[i * 4 + 1] = rect.y1
                coords[i * 4 + 2] = rect.x2
                coords[i * 4 + 3] = rect.y2
            
            # 准备文本数组
            texts = (ctypes.c_char_p * rect_count)()
            for i, rect in enumerate(rects):
                text = rect.text if rect.text else ""
                texts[i] = text.encode('utf-8')
        
        # 调用C++引擎
        result = self._lib.ocr_engine_save_result(
            self.engine,
            file_path.encode('utf-8'),
            status.encode('utf-8'),
            rect_count,
            coords,
            texts
        )
        
        return result == 0
    
    def load_all_results(self) -> Dict[str, Dict]:
        """
        加载所有OCR结果
        :return: {file_path: {"rects": [OCRRect], "status": str}}
        """
        if not self.engine or not self._lib:
            return {}
        
        # 调用C++引擎
        json_str_ptr = self._lib.ocr_engine_load_all(self.engine)
        
        if not json_str_ptr:
            return {}
        
        # 解析JSON
        try:
            # 使用ctypes.string_at安全读取字符串
            json_str = ctypes.string_at(json_str_ptr).decode('utf-8')
            data = json.loads(json_str)
            
            # 转换为OCRRect对象
            results = {}
            for file_path, file_data in data.items():
                rects = []
                for rect_data in file_data.get("rects", []):
                    rect = OCRRect(
                        rect_data["x1"],
                        rect_data["y1"],
                        rect_data["x2"],
                        rect_data["y2"]
                    )
                    rect.text = rect_data.get("text", "")
                    rects.append(rect)
                
                results[file_path] = {
                    "rects": rects,
                    "status": file_data.get("status", "")
                }
            
            return results
        except Exception as e:
            print(f"加载OCR结果失败: {e}")
            return {}
        finally:
            # 释放C++分配的字符串
            self._lib.ocr_engine_free_string(ctypes.cast(json_str_ptr, ctypes.c_void_p))
    
    def save_session(self, files: List[str], cur_index: int) -> bool:
        """
        保存会话元数据
        :param files: 文件列表
        :param cur_index: 当前索引
        :return: 是否成功
        """
        if not self.engine or not self._lib:
            return False
        
        files_json = json.dumps(files, ensure_ascii=False)
        
        result = self._lib.ocr_engine_save_session(
            self.engine,
            files_json.encode('utf-8'),
            cur_index
        )
        
        return result == 0
    
    def load_session(self) -> Optional[Dict]:
        """
        加载会话元数据
        :return: {"files": [str], "cur_index": int} 或 None
        """
        if not self.engine or not self._lib:
            return None
        
        json_str_ptr = self._lib.ocr_engine_load_session(self.engine)
        
        if not json_str_ptr:
            return None
        
        try:
            # 使用ctypes.string_at安全读取字符串
            json_str = ctypes.string_at(json_str_ptr).decode('utf-8')
            return json.loads(json_str)
        except Exception as e:
            print(f"加载会话失败: {e}")
            return None
        finally:
            self._lib.ocr_engine_free_string(ctypes.cast(json_str_ptr, ctypes.c_void_p))
    
    def has_cache(self) -> bool:
        """
        检查是否存在缓存数据
        :return: 是否存在
        """
        if not self.engine or not self._lib:
            return False
        
        return self._lib.ocr_engine_has_cache(self.engine) == 1
    
    def clear_cache(self):
        """清除所有缓存数据"""
        if self.engine and self._lib:
            self._lib.ocr_engine_clear(self.engine)
    
    def get_last_error(self) -> str:
        """获取最后的错误信息"""
        if not self.engine or not self._lib:
            return "Engine not initialized"
        
        error_ptr = self._lib.ocr_engine_get_error(self.engine)
        if error_ptr:
            return error_ptr.decode('utf-8')
        return ""
    
    def __del__(self):
        """析构函数：释放资源"""
        if self.engine and self._lib:
            self._lib.ocr_engine_destroy(self.engine)
            self.engine = None
