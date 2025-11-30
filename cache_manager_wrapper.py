"""
缓存管理器安全包装层
提供自动降级策略和健康检查功能
"""

import logging
import threading
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from ocr_cache_manager import OCRCacheManager, CacheInitError
from config import OCRRect

# 配置日志
logger = logging.getLogger(__name__)


@dataclass
class CacheStatus:
    """缓存状态信息"""
    is_available: bool
    backend_type: str  # "cpp_engine", "memory", "disabled"
    init_error: Optional[CacheInitError]
    fallback_active: bool
    message: str


class CacheManagerWrapper:
    """
    缓存管理器安全包装层
    
    提供以下功能：
    1. 自动降级策略：当C++引擎不可用时，使用内存缓存
    2. 安全包装：所有缓存操作都不会抛出异常
    3. 健康检查：提供缓存状态查询接口
    4. 线程安全：使用锁保护并发访问
    """
    
    def __init__(self, db_path: str = None):
        """
        初始化缓存管理器包装层
        :param db_path: 数据库文件路径（可选）
        """
        self.backend: Optional[OCRCacheManager] = None
        self.fallback_cache: Dict = {
            "results": {},  # {file_path: {"rects": [OCRRect], "status": str}}
            "session": None  # {"files": [str], "cur_index": int}
        }
        self.is_available = False
        self.init_error: Optional[CacheInitError] = None
        self.backend_type = "disabled"
        self._lock = threading.RLock()  # 可重入锁，支持同一线程多次获取
        
        # 尝试初始化真实的缓存引擎
        self._try_init_backend(db_path)
    
    def _try_init_backend(self, db_path: Optional[str]):
        """
        尝试初始化后端引擎
        :param db_path: 数据库路径
        """
        try:
            logger.info("尝试初始化C++缓存引擎")
            self.backend = OCRCacheManager(db_path)
            self.is_available = True
            self.backend_type = "cpp_engine"
            logger.info("C++缓存引擎初始化成功")
        except CacheInitError as e:
            # 捕获初始化错误，记录详细信息
            logger.warning(f"C++缓存引擎初始化失败，将使用内存缓存")
            logger.debug(str(e))
            self.init_error = e
            self.backend = None
            self.is_available = False
            self.backend_type = "memory"
            logger.info("已降级到内存缓存模式")
        except Exception as e:
            # 捕获其他未预期的异常
            logger.error(f"初始化缓存引擎时发生未预期的异常: {e}")
            self.init_error = CacheInitError(
                error_type="unexpected_wrapper_error",
                error_message=str(e),
                error_details={"exception_type": type(e).__name__},
                suggestions=["这是一个未预期的错误，请查看日志"]
            )
            self.backend = None
            self.is_available = False
            self.backend_type = "memory"
            logger.info("已降级到内存缓存模式")
    
    def save_result(self, file_path: str, rects: List[OCRRect], status: str = "已识别") -> bool:
        """
        保存OCR结果（自动降级）
        :param file_path: 文件路径
        :param rects: OCR区域列表
        :param status: 识别状态
        :return: 是否成功
        """
        with self._lock:
            try:
                if self.backend and self.backend_type == "cpp_engine":
                    # 尝试使用C++引擎
                    success = self.backend.save_result(file_path, rects, status)
                    if success:
                        return True
                    else:
                        # C++引擎失败，降级到内存缓存
                        logger.debug(f"C++引擎保存失败，降级到内存缓存: {file_path}")
                
                # 使用内存缓存
                self.fallback_cache["results"][file_path] = {
                    "rects": rects,
                    "status": status
                }
                return True
                
            except Exception as e:
                # 捕获所有异常，确保不影响应用程序
                logger.error(f"保存结果时发生异常: {e}")
                # 尝试使用内存缓存作为最后的降级
                try:
                    self.fallback_cache["results"][file_path] = {
                        "rects": rects,
                        "status": status
                    }
                    return True
                except Exception as e2:
                    logger.error(f"内存缓存也失败: {e2}")
                    return False
    
    def load_all_results(self) -> Dict[str, Dict]:
        """
        加载所有OCR结果（自动降级）
        :return: {file_path: {"rects": [OCRRect], "status": str}}
        """
        with self._lock:
            try:
                if self.backend and self.backend_type == "cpp_engine":
                    # 尝试使用C++引擎
                    results = self.backend.load_all_results()
                    if results:
                        return results
                    else:
                        # C++引擎返回空，可能失败，降级到内存缓存
                        logger.debug("C++引擎加载失败或无数据，使用内存缓存")
                
                # 使用内存缓存
                return dict(self.fallback_cache["results"])
                
            except Exception as e:
                # 捕获所有异常
                logger.error(f"加载结果时发生异常: {e}")
                # 返回内存缓存
                try:
                    return dict(self.fallback_cache["results"])
                except Exception as e2:
                    logger.error(f"读取内存缓存也失败: {e2}")
                    return {}
    
    def save_session(self, files: List[str], cur_index: int) -> bool:
        """
        保存会话元数据（自动降级）
        :param files: 文件列表
        :param cur_index: 当前索引
        :return: 是否成功
        """
        with self._lock:
            try:
                if self.backend and self.backend_type == "cpp_engine":
                    # 尝试使用C++引擎
                    success = self.backend.save_session(files, cur_index)
                    if success:
                        return True
                    else:
                        logger.debug("C++引擎保存会话失败，降级到内存缓存")
                
                # 使用内存缓存
                self.fallback_cache["session"] = {
                    "files": files,
                    "cur_index": cur_index
                }
                return True
                
            except Exception as e:
                logger.error(f"保存会话时发生异常: {e}")
                # 尝试使用内存缓存
                try:
                    self.fallback_cache["session"] = {
                        "files": files,
                        "cur_index": cur_index
                    }
                    return True
                except Exception as e2:
                    logger.error(f"内存缓存也失败: {e2}")
                    return False
    
    def load_session(self) -> Optional[Dict]:
        """
        加载会话元数据（自动降级）
        :return: {"files": [str], "cur_index": int} 或 None
        """
        with self._lock:
            try:
                if self.backend and self.backend_type == "cpp_engine":
                    # 尝试使用C++引擎
                    session = self.backend.load_session()
                    if session:
                        return session
                    else:
                        logger.debug("C++引擎加载会话失败或无数据，使用内存缓存")
                
                # 使用内存缓存
                return self.fallback_cache["session"]
                
            except Exception as e:
                logger.error(f"加载会话时发生异常: {e}")
                # 返回内存缓存
                try:
                    return self.fallback_cache["session"]
                except Exception as e2:
                    logger.error(f"读取内存缓存也失败: {e2}")
                    return None
    
    def has_cache(self) -> bool:
        """
        检查是否存在缓存数据（自动降级）
        :return: 是否存在
        """
        with self._lock:
            try:
                if self.backend and self.backend_type == "cpp_engine":
                    # 尝试使用C++引擎
                    return self.backend.has_cache()
                
                # 检查内存缓存
                return bool(self.fallback_cache["results"]) or bool(self.fallback_cache["session"])
                
            except Exception as e:
                logger.error(f"检查缓存时发生异常: {e}")
                # 检查内存缓存
                try:
                    return bool(self.fallback_cache["results"]) or bool(self.fallback_cache["session"])
                except Exception as e2:
                    logger.error(f"检查内存缓存也失败: {e2}")
                    return False
    
    def clear_cache(self):
        """清除所有缓存数据（自动降级）"""
        with self._lock:
            try:
                if self.backend and self.backend_type == "cpp_engine":
                    # 清除C++引擎缓存
                    self.backend.clear_cache()
                
                # 清除内存缓存
                self.fallback_cache["results"].clear()
                self.fallback_cache["session"] = None
                
            except Exception as e:
                logger.error(f"清除缓存时发生异常: {e}")
                # 至少清除内存缓存
                try:
                    self.fallback_cache["results"].clear()
                    self.fallback_cache["session"] = None
                except Exception as e2:
                    logger.error(f"清除内存缓存也失败: {e2}")
    
    def is_cache_available(self) -> bool:
        """
        检查缓存是否可用
        :return: 是否可用（包括内存缓存）
        """
        # 只要有任何形式的缓存（C++或内存），就认为可用
        return True
    
    def is_cpp_engine_available(self) -> bool:
        """
        检查C++引擎是否可用
        :return: 是否可用
        """
        return self.backend_type == "cpp_engine" and self.backend is not None
    
    def get_status(self) -> CacheStatus:
        """
        获取缓存状态
        :return: CacheStatus对象
        """
        with self._lock:
            fallback_active = self.backend_type == "memory"
            
            if self.backend_type == "cpp_engine":
                message = "C++缓存引擎运行正常"
            elif self.backend_type == "memory":
                message = "使用内存缓存（C++引擎不可用）"
            else:
                message = "缓存功能已禁用"
            
            return CacheStatus(
                is_available=self.is_cache_available(),
                backend_type=self.backend_type,
                init_error=self.init_error,
                fallback_active=fallback_active,
                message=message
            )
    
    def get_status_message(self) -> str:
        """
        获取状态消息
        :return: 状态消息字符串
        """
        status = self.get_status()
        msg = status.message
        
        if status.init_error:
            msg += f"\n初始化错误: {status.init_error.error_type}"
            if status.init_error.suggestions:
                msg += f"\n建议: {status.init_error.suggestions[0]}"
        
        return msg
    
    def health_check(self) -> Dict:
        """
        健康检查
        :return: 健康检查信息
        """
        with self._lock:
            status = self.get_status()
            
            health_info = {
                "cache_available": status.is_available,
                "backend_type": status.backend_type,
                "fallback_active": status.fallback_active,
                "message": status.message,
                "timestamp": datetime.now().isoformat()
            }
            
            if self.backend and self.backend_type == "cpp_engine":
                health_info["db_path"] = self.backend.db_path
                try:
                    health_info["has_data"] = self.backend.has_cache()
                except Exception:
                    health_info["has_data"] = False
            
            if status.init_error:
                health_info["init_error"] = {
                    "type": status.init_error.error_type,
                    "message": status.init_error.error_message,
                    "suggestions": status.init_error.suggestions
                }
            
            # 内存缓存统计
            health_info["memory_cache"] = {
                "results_count": len(self.fallback_cache["results"]),
                "has_session": self.fallback_cache["session"] is not None
            }
            
            return health_info
    
    def __del__(self):
        """析构函数：清理资源"""
        try:
            # backend的析构函数会自动清理C++资源
            pass
        except Exception as e:
            logger.debug(f"清理包装层资源时发生错误: {e}")
