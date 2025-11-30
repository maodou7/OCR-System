"""
OCR缓存管理器 - Python封装层
使用C++引擎实现高性能、ACID安全的缓存
"""

import os
import json
import ctypes
import logging
import platform
import traceback
import shutil
import sqlite3
import time
import threading
import weakref
import atexit
from pathlib import Path
from typing import Dict, List, Optional
from config import OCRRect, get_resource_path, get_executable_dir

# 配置日志
logger = logging.getLogger(__name__)

# 全局锁用于保护引擎实例的创建和销毁
_global_engine_lock = threading.RLock()

# 全局引擎实例注册表（使用弱引用）
_engine_registry = weakref.WeakValueDictionary()

# 引擎实例引用计数
_engine_ref_counts = {}
_ref_count_lock = threading.Lock()


def _cleanup_all_engines():
    """
    清理所有引擎实例
    在程序退出时调用
    """
    logger.debug("程序退出，清理所有引擎实例")
    with _global_engine_lock:
        # 复制注册表以避免在迭代时修改
        engines = list(_engine_registry.values())
        for engine_manager in engines:
            try:
                engine_manager.close()
            except Exception as e:
                logger.debug(f"清理引擎实例时发生错误: {e}")


# 注册退出时的清理函数
atexit.register(_cleanup_all_engines)


class CacheInitError(Exception):
    """缓存初始化错误信息"""
    
    def __init__(self, error_type: str, error_message: str, error_details: Dict, suggestions: List[str]):
        self.error_type = error_type
        self.error_message = error_message
        self.error_details = error_details
        self.suggestions = suggestions
        super().__init__(str(self))
    
    def __str__(self):
        msg = f"缓存引擎初始化失败\n"
        msg += f"错误类型: {self.error_type}\n"
        msg += f"错误信息: {self.error_message}\n"
        if self.error_details:
            msg += f"详细信息:\n"
            for key, value in self.error_details.items():
                msg += f"  {key}: {value}\n"
        if self.suggestions:
            msg += f"可能的解决方案:\n"
            for i, suggestion in enumerate(self.suggestions, 1):
                msg += f"  {i}. {suggestion}\n"
        return msg


class OCRCacheManager:
    """OCR缓存管理器"""
    
    def __init__(self, db_path: str = None):
        """
        初始化缓存管理器
        :param db_path: 数据库文件路径（默认使用可执行文件目录下的.ocr_cache/ocr_cache.db）
        :raises CacheInitError: 初始化失败时抛出详细错误信息
        """
        self.db_path = None
        self.engine = None
        self._lib = None
        self._last_init_error = None
        self._instance_lock = threading.RLock()  # 实例级别的锁
        self._is_destroyed = False  # 标记引擎是否已销毁
        self._operation_timeout = 30.0  # 操作超时时间（秒）
        
        try:
            # 使用全局锁保护初始化过程，防止并发初始化冲突
            with _global_engine_lock:
                # 步骤1: 路径验证和准备
                logger.info("开始初始化OCR缓存管理器")
                self.db_path = self._validate_and_prepare_path(db_path)
                logger.debug(f"数据库路径: {self.db_path}")
                
                # 步骤2: 加载C++库
                logger.debug("加载C++引擎库")
                self._load_engine()
                
                # 步骤3: 初始化引擎
                logger.debug("初始化C++引擎")
                self._initialize_engine()
                
                # 步骤4: 验证引擎
                logger.debug("验证引擎功能")
                self._validate_engine()
                
                # 步骤5: 注册引擎实例
                self._register_engine_instance()
                
                logger.info("OCR缓存管理器初始化成功")
            
        except CacheInitError:
            # 清理资源
            self._cleanup_on_error()
            raise
        except Exception as e:
            # 捕获未预期的异常
            logger.error(f"初始化过程中发生未预期的异常: {e}")
            logger.debug(traceback.format_exc())
            self._cleanup_on_error()
            
            error = CacheInitError(
                error_type="unexpected_error",
                error_message=str(e),
                error_details={
                    "exception_type": type(e).__name__,
                    "stack_trace": traceback.format_exc()
                },
                suggestions=[
                    "这是一个未预期的错误，请检查日志获取详细信息",
                    "尝试重新启动应用程序",
                    "如果问题持续存在，请联系技术支持"
                ]
            )
            self._last_init_error = error
            raise error
    
    def _validate_and_prepare_path(self, db_path: Optional[str]) -> str:
        """
        验证和准备数据库路径
        :param db_path: 用户提供的路径或None
        :return: 验证后的绝对路径
        :raises CacheInitError: 路径验证失败
        """
        try:
            # 如果未指定路径，使用可执行文件目录
            if db_path is None:
                exe_dir = get_executable_dir()
                db_path = os.path.join(exe_dir, ".ocr_cache", "ocr_cache.db")
            
            # 转换为绝对路径
            db_path = os.path.abspath(db_path)
            
            # 验证路径不包含危险字符
            if ".." in db_path or db_path.startswith("/"):
                if not os.path.isabs(db_path):
                    raise ValueError("路径包含潜在的安全风险")
            
            # 确保目录存在
            db_dir = os.path.dirname(db_path)
            try:
                os.makedirs(db_dir, exist_ok=True)
            except OSError as e:
                raise CacheInitError(
                    error_type="path_creation_failed",
                    error_message=f"无法创建缓存目录: {e}",
                    error_details={
                        "db_path": db_path,
                        "db_dir": db_dir,
                        "os_error": str(e)
                    },
                    suggestions=[
                        "检查目录权限",
                        "确保磁盘空间充足",
                        "尝试使用其他路径"
                    ]
                )
            
            # 检查目录是否可写
            if not os.access(db_dir, os.W_OK):
                raise CacheInitError(
                    error_type="permission_denied",
                    error_message="缓存目录不可写",
                    error_details={
                        "db_path": db_path,
                        "db_dir": db_dir
                    },
                    suggestions=[
                        "检查目录权限",
                        "以管理员权限运行应用程序",
                        "选择其他可写目录"
                    ]
                )
            
            # 验证路径编码（确保可以正确编码为UTF-8）
            try:
                db_path.encode('utf-8')
            except UnicodeEncodeError as e:
                raise CacheInitError(
                    error_type="encoding_error",
                    error_message="路径包含无法编码的字符",
                    error_details={
                        "db_path": db_path,
                        "encoding_error": str(e)
                    },
                    suggestions=[
                        "使用只包含ASCII字符的路径",
                        "避免使用特殊字符"
                    ]
                )
            
            return db_path
            
        except CacheInitError:
            raise
        except Exception as e:
            raise CacheInitError(
                error_type="path_validation_failed",
                error_message=f"路径验证失败: {e}",
                error_details={
                    "db_path": db_path,
                    "exception": str(e)
                },
                suggestions=[
                    "检查路径格式是否正确",
                    "使用默认路径（不指定db_path参数）"
                ]
            )
    
    def _check_database_health(self) -> bool:
        """
        检查数据库健康状态
        :return: True表示健康，False表示需要恢复
        """
        if not os.path.exists(self.db_path):
            logger.debug("数据库文件不存在，将创建新数据库")
            return True  # 不存在的数据库会被自动创建
        
        # 检查是否是目录而不是文件
        if os.path.isdir(self.db_path):
            logger.warning(f"数据库路径是目录而不是文件: {self.db_path}")
            return False
        
        conn = None
        try:
            # 使用SQLite直接检查数据库完整性
            conn = sqlite3.connect(self.db_path, timeout=5.0)
            cursor = conn.cursor()
            
            # 执行完整性检查
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            if result and result[0] == "ok":
                logger.debug("数据库完整性检查通过")
                return True
            else:
                logger.warning(f"数据库完整性检查失败: {result}")
                return False
                
        except sqlite3.DatabaseError as e:
            logger.warning(f"数据库损坏: {e}")
            return False
        except sqlite3.OperationalError as e:
            # 可能是文件被锁定或权限问题
            logger.warning(f"数据库操作错误: {e}")
            if "locked" in str(e).lower():
                # 文件被锁定，尝试等待
                return self._wait_for_database_unlock()
            return False
        except Exception as e:
            logger.warning(f"数据库健康检查失败: {e}")
            return False
        finally:
            # 确保连接被关闭
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass
    
    def _wait_for_database_unlock(self, max_wait_seconds: int = 5) -> bool:
        """
        等待数据库解锁
        :param max_wait_seconds: 最大等待时间（秒）
        :return: True表示解锁成功，False表示超时
        """
        logger.info(f"数据库被锁定，等待最多{max_wait_seconds}秒...")
        start_time = time.time()
        
        while time.time() - start_time < max_wait_seconds:
            try:
                # 尝试打开数据库
                conn = sqlite3.connect(self.db_path, timeout=1.0)
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                conn.close()
                logger.info("数据库已解锁")
                return True
            except sqlite3.OperationalError:
                time.sleep(0.5)
                continue
            except Exception as e:
                logger.debug(f"等待解锁时发生错误: {e}")
                return False
        
        logger.warning("等待数据库解锁超时")
        return False
    
    def _backup_database(self) -> Optional[str]:
        """
        备份数据库文件
        :return: 备份文件路径，失败返回None
        """
        if not os.path.exists(self.db_path):
            logger.debug("数据库文件不存在，无需备份")
            return None
        
        try:
            # 生成备份文件名（带时间戳）
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_path = f"{self.db_path}.backup_{timestamp}"
            
            # 复制文件
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"数据库已备份到: {backup_path}")
            
            return backup_path
            
        except IOError as e:
            logger.error(f"备份数据库失败: {e}")
            return None
        except Exception as e:
            logger.error(f"备份数据库时发生未预期的错误: {e}")
            return None
    
    def _rebuild_database(self) -> bool:
        """
        重建数据库（删除旧数据库并创建新数据库）
        :return: True表示成功，False表示失败
        """
        try:
            # 检查路径是否是目录
            if os.path.isdir(self.db_path):
                raise CacheInitError(
                    error_type="invalid_db_path",
                    error_message="数据库路径是目录而不是文件",
                    error_details={
                        "db_path": self.db_path
                    },
                    suggestions=[
                        "指定一个文件路径而不是目录路径",
                        "使用默认路径（不指定db_path参数）"
                    ]
                )
            
            # 先备份
            backup_path = self._backup_database()
            if backup_path:
                logger.info(f"旧数据库已备份，开始重建")
            
            # 删除损坏的数据库
            if os.path.exists(self.db_path):
                try:
                    os.remove(self.db_path)
                    logger.info(f"已删除损坏的数据库: {self.db_path}")
                except PermissionError as e:
                    logger.error(f"无法删除数据库文件（权限不足）: {e}")
                    raise CacheInitError(
                        error_type="permission_denied",
                        error_message="无法删除损坏的数据库文件",
                        error_details={
                            "db_path": self.db_path,
                            "backup_path": backup_path,
                            "error": str(e)
                        },
                        suggestions=[
                            "检查文件权限",
                            "关闭其他可能占用数据库的程序",
                            "以管理员权限运行应用程序",
                            f"手动删除文件: {self.db_path}"
                        ]
                    )
                except Exception as e:
                    logger.error(f"删除数据库文件失败: {e}")
                    raise CacheInitError(
                        error_type="database_delete_failed",
                        error_message=f"无法删除损坏的数据库文件: {e}",
                        error_details={
                            "db_path": self.db_path,
                            "backup_path": backup_path,
                            "error": str(e)
                        },
                        suggestions=[
                            "检查文件是否被其他进程占用",
                            "尝试重新启动计算机",
                            f"手动删除文件: {self.db_path}"
                        ]
                    )
            
            logger.info("数据库重建完成，C++引擎将创建新数据库")
            return True
            
        except CacheInitError:
            raise
        except Exception as e:
            logger.error(f"重建数据库时发生未预期的错误: {e}")
            return False
    
    def _check_disk_space(self) -> bool:
        """
        检查磁盘空间是否充足
        :return: True表示空间充足，False表示空间不足
        """
        try:
            db_dir = os.path.dirname(self.db_path)
            
            # 获取磁盘使用情况
            if platform.system() == "Windows":
                import ctypes
                free_bytes = ctypes.c_ulonglong(0)
                ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                    ctypes.c_wchar_p(db_dir),
                    None,
                    None,
                    ctypes.pointer(free_bytes)
                )
                free_space_mb = free_bytes.value / (1024 * 1024)
            else:
                # Linux/macOS
                stat = os.statvfs(db_dir)
                free_space_mb = (stat.f_bavail * stat.f_frsize) / (1024 * 1024)
            
            # 至少需要10MB空间
            min_required_mb = 10
            
            if free_space_mb < min_required_mb:
                logger.error(f"磁盘空间不足: {free_space_mb:.2f}MB < {min_required_mb}MB")
                return False
            
            logger.debug(f"磁盘可用空间: {free_space_mb:.2f}MB")
            return True
            
        except Exception as e:
            logger.warning(f"检查磁盘空间失败: {e}")
            # 无法检查时假设空间充足
            return True
    
    def _auto_recover_database(self) -> bool:
        """
        自动恢复数据库
        :return: True表示恢复成功或不需要恢复，False表示恢复失败
        """
        logger.info("开始数据库自动恢复流程")
        
        # 1. 检查磁盘空间
        if not self._check_disk_space():
            raise CacheInitError(
                error_type="insufficient_disk_space",
                error_message="磁盘空间不足",
                error_details={
                    "db_path": self.db_path,
                    "db_dir": os.path.dirname(self.db_path)
                },
                suggestions=[
                    "清理磁盘空间",
                    "选择其他磁盘位置存储数据库",
                    "删除不需要的文件释放空间"
                ]
            )
        
        # 2. 检查数据库健康状态
        is_healthy = self._check_database_health()
        
        if is_healthy:
            logger.info("数据库健康，无需恢复")
            return True
        
        # 3. 数据库不健康，尝试重建
        logger.warning("检测到数据库损坏，尝试自动恢复")
        
        try:
            success = self._rebuild_database()
            
            if success:
                logger.info("数据库自动恢复成功")
                return True
            else:
                logger.error("数据库自动恢复失败")
                return False
                
        except CacheInitError:
            raise
        except Exception as e:
            logger.error(f"数据库自动恢复过程中发生错误: {e}")
            logger.debug(traceback.format_exc())
            return False
    
    def _initialize_engine(self):
        """
        初始化C++引擎
        :raises CacheInitError: 引擎初始化失败
        """
        if not self._lib:
            raise CacheInitError(
                error_type="library_not_loaded",
                error_message="C++库未加载",
                error_details={},
                suggestions=["先调用_load_engine()加载库"]
            )
        
        # 在初始化引擎前，先尝试自动恢复数据库
        # 但只在数据库路径看起来有效时才进行恢复
        if os.path.isfile(self.db_path) or (not os.path.exists(self.db_path) and not os.path.isdir(self.db_path)):
            try:
                self._auto_recover_database()
            except CacheInitError:
                # 如果恢复失败，继续抛出错误
                raise
            except Exception as e:
                logger.warning(f"数据库自动恢复失败，将尝试继续初始化: {e}")
        
        try:
            # 编码路径为UTF-8
            db_path_bytes = self.db_path.encode('utf-8')
            
            # 调用C++引擎初始化函数
            logger.debug(f"调用ocr_engine_init，路径: {self.db_path}")
            self.engine = self._lib.ocr_engine_init(db_path_bytes)
            
            # NULL指针检查
            if not self.engine or self.engine == 0:
                # 尝试获取错误信息
                error_msg = "引擎返回NULL指针"
                try:
                    if hasattr(self._lib, 'ocr_engine_get_last_error'):
                        error_ptr = self._lib.ocr_engine_get_last_error()
                        if error_ptr:
                            error_msg = ctypes.string_at(error_ptr).decode('utf-8', errors='replace')
                except Exception as e:
                    logger.debug(f"无法获取C++错误信息: {e}")
                
                raise CacheInitError(
                    error_type="null_pointer",
                    error_message=error_msg,
                    error_details={
                        "db_path": self.db_path,
                        "platform": platform.system(),
                        "engine_pointer": str(self.engine)
                    },
                    suggestions=[
                        "数据库文件可能已损坏，尝试删除并重新创建",
                        "检查SQLite是否正确编译到引擎中",
                        "检查磁盘空间是否充足",
                        "查看日志文件获取更多信息"
                    ]
                )
            
            logger.debug(f"引擎初始化成功，指针: {hex(self.engine)}")
            
        except CacheInitError:
            raise
        except OSError as e:
            # ctypes调用失败
            raise CacheInitError(
                error_type="ctypes_call_failed",
                error_message=f"ctypes调用失败: {e}",
                error_details={
                    "function": "ocr_engine_init",
                    "db_path": self.db_path,
                    "os_error": str(e),
                    "error_code": getattr(e, 'errno', None)
                },
                suggestions=[
                    "C++库可能与系统不兼容",
                    "检查是否缺少运行时依赖（如msvcr140.dll）",
                    "尝试重新安装应用程序"
                ]
            )
        except Exception as e:
            raise CacheInitError(
                error_type="engine_init_failed",
                error_message=f"引擎初始化失败: {e}",
                error_details={
                    "db_path": self.db_path,
                    "exception": str(e),
                    "exception_type": type(e).__name__
                },
                suggestions=[
                    "检查数据库文件是否被其他进程占用",
                    "尝试删除数据库文件并重新创建",
                    "查看日志获取详细信息"
                ]
            )
    
    def _validate_engine(self):
        """
        验证引擎是否正确初始化
        :raises CacheInitError: 验证失败
        """
        if not self.engine or self.engine == 0:
            raise CacheInitError(
                error_type="engine_not_initialized",
                error_message="引擎未初始化",
                error_details={},
                suggestions=["先调用_initialize_engine()初始化引擎"]
            )
        
        # 测试基本操作
        try:
            # 尝试调用has_cache检查引擎是否响应
            result = self._lib.ocr_engine_has_cache(self.engine)
            logger.debug(f"引擎验证成功，has_cache返回: {result}")
        except Exception as e:
            raise CacheInitError(
                error_type="engine_validation_failed",
                error_message=f"引擎验证失败: {e}",
                error_details={
                    "exception": str(e),
                    "engine_pointer": hex(self.engine) if self.engine else None
                },
                suggestions=[
                    "引擎可能未正确初始化",
                    "尝试重新启动应用程序",
                    "检查数据库文件完整性"
                ]
            )
    
    def _register_engine_instance(self):
        """注册引擎实例到全局注册表"""
        if self.engine and self.engine != 0:
            with _ref_count_lock:
                engine_id = id(self)
                _engine_registry[engine_id] = self
                _engine_ref_counts[engine_id] = 1
                logger.debug(f"注册引擎实例 {engine_id}, 引用计数: 1")
    
    def _increment_ref_count(self):
        """增加引擎实例的引用计数"""
        with _ref_count_lock:
            engine_id = id(self)
            if engine_id in _engine_ref_counts:
                _engine_ref_counts[engine_id] += 1
                logger.debug(f"引擎实例 {engine_id} 引用计数增加到: {_engine_ref_counts[engine_id]}")
    
    def _decrement_ref_count(self) -> int:
        """
        减少引擎实例的引用计数
        :return: 当前引用计数
        """
        with _ref_count_lock:
            engine_id = id(self)
            if engine_id in _engine_ref_counts:
                _engine_ref_counts[engine_id] -= 1
                count = _engine_ref_counts[engine_id]
                logger.debug(f"引擎实例 {engine_id} 引用计数减少到: {count}")
                
                if count <= 0:
                    # 清理引用计数记录
                    del _engine_ref_counts[engine_id]
                    logger.debug(f"引擎实例 {engine_id} 引用计数已清零，从注册表移除")
                
                return count
            return 0
    
    def _cleanup_on_error(self):
        """清理初始化失败时的资源"""
        try:
            if self.engine and self._lib:
                logger.debug("清理失败的引擎实例")
                self._lib.ocr_engine_destroy(self.engine)
        except Exception as e:
            logger.debug(f"清理资源时发生错误: {e}")
        finally:
            self.engine = None
            self._is_destroyed = True
    
    def _load_engine(self):
        """
        加载C++共享库
        :raises CacheInitError: 库加载失败
        """
        try:
            # 根据操作系统确定库文件名
            system = platform.system()
            
            if system == "Linux":
                lib_name = "libocr_cache.so"
            elif system == "Darwin":
                lib_name = "libocr_cache.dylib"
            elif system == "Windows":
                lib_name = "ocr_cache.dll"
            else:
                raise CacheInitError(
                    error_type="unsupported_platform",
                    error_message=f"不支持的操作系统: {system}",
                    error_details={
                        "platform": system,
                        "platform_release": platform.release(),
                        "platform_version": platform.version()
                    },
                    suggestions=[
                        "当前仅支持Windows、Linux和macOS",
                        "请在支持的平台上运行应用程序"
                    ]
                )
            
            # 库文件位于models目录下（支持PyInstaller打包）
            lib_path = get_resource_path(os.path.join("models", lib_name))
            logger.debug(f"库文件路径: {lib_path}")
            
            # 检查库文件是否存在
            if not os.path.exists(lib_path):
                raise CacheInitError(
                    error_type="library_not_found",
                    error_message="找不到C++引擎库文件",
                    error_details={
                        "lib_path": lib_path,
                        "lib_name": lib_name,
                        "platform": system,
                        "models_dir_exists": os.path.exists(os.path.dirname(lib_path))
                    },
                    suggestions=[
                        "检查应用程序安装是否完整",
                        "尝试重新安装应用程序",
                        f"确保{lib_name}文件存在于models目录下",
                        "如果使用PyInstaller打包，检查spec文件是否包含该库"
                    ]
                )
            
            # 检查库文件是否可读
            if not os.access(lib_path, os.R_OK):
                raise CacheInitError(
                    error_type="library_not_readable",
                    error_message="无法读取C++引擎库文件",
                    error_details={
                        "lib_path": lib_path,
                        "file_permissions": oct(os.stat(lib_path).st_mode)
                    },
                    suggestions=[
                        "检查文件权限",
                        "以管理员权限运行应用程序"
                    ]
                )
            
            # 加载库
            try:
                logger.debug(f"加载库: {lib_path}")
                self._lib = ctypes.CDLL(lib_path)
                logger.debug("库加载成功")
            except OSError as e:
                # Windows特定错误提示
                suggestions = [
                    "库文件可能已损坏，尝试重新安装",
                    "检查是否缺少依赖库"
                ]
                
                if system == "Windows":
                    suggestions.extend([
                        "安装Visual C++ Redistributable (需要msvcr140.dll)",
                        "从Microsoft官网下载: https://aka.ms/vs/17/release/vc_redist.x64.exe"
                    ])
                elif system == "Linux":
                    suggestions.append("运行 ldd 命令检查缺少的依赖: ldd " + lib_path)
                
                raise CacheInitError(
                    error_type="library_load_failed",
                    error_message=f"加载C++库失败: {e}",
                    error_details={
                        "lib_path": lib_path,
                        "platform": system,
                        "os_error": str(e),
                        "error_code": getattr(e, 'errno', None)
                    },
                    suggestions=suggestions
                )
            
            # 定义函数签名
            self._define_function_signatures()
            
        except CacheInitError:
            raise
        except Exception as e:
            raise CacheInitError(
                error_type="library_load_unexpected",
                error_message=f"加载库时发生未预期的错误: {e}",
                error_details={
                    "exception": str(e),
                    "exception_type": type(e).__name__,
                    "stack_trace": traceback.format_exc()
                },
                suggestions=[
                    "这是一个未预期的错误",
                    "请查看日志获取详细信息",
                    "尝试重新启动应用程序"
                ]
            )
    
    def _define_function_signatures(self):
        """定义C++函数签名"""
        try:
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
            
            logger.debug("函数签名定义完成")
            
        except AttributeError as e:
            raise CacheInitError(
                error_type="function_not_found",
                error_message=f"库中缺少必需的函数: {e}",
                error_details={
                    "missing_function": str(e),
                    "library_loaded": self._lib is not None
                },
                suggestions=[
                    "库文件版本可能不匹配",
                    "尝试重新编译C++引擎",
                    "确保使用正确版本的库文件"
                ]
            )
        except Exception as e:
            raise CacheInitError(
                error_type="signature_definition_failed",
                error_message=f"定义函数签名失败: {e}",
                error_details={
                    "exception": str(e),
                    "exception_type": type(e).__name__
                },
                suggestions=[
                    "这可能是库文件损坏导致的",
                    "尝试重新安装应用程序"
                ]
            )
        
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
    
    def get_detailed_error(self) -> Optional[CacheInitError]:
        """
        获取详细的初始化错误信息
        :return: CacheInitError对象或None
        """
        return self._last_init_error
    
    def _with_timeout(self, operation_name: str, func, *args, **kwargs):
        """
        使用超时保护执行操作
        :param operation_name: 操作名称（用于日志）
        :param func: 要执行的函数
        :param args: 函数参数
        :param kwargs: 函数关键字参数
        :return: 函数返回值
        :raises TimeoutError: 操作超时
        """
        result = [None]
        exception = [None]
        
        def target():
            try:
                result[0] = func(*args, **kwargs)
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        thread.join(timeout=self._operation_timeout)
        
        if thread.is_alive():
            logger.error(f"操作 {operation_name} 超时（{self._operation_timeout}秒）")
            raise TimeoutError(f"操作 {operation_name} 超时")
        
        if exception[0]:
            raise exception[0]
        
        return result[0]
    
    def save_result(self, file_path: str, rects: List[OCRRect], status: str = "已识别") -> bool:
        """
        保存单个文件的OCR结果
        :param file_path: 文件路径
        :param rects: OCR区域列表
        :param status: 识别状态
        :return: 是否成功
        """
        # 使用实例锁保护操作
        with self._instance_lock:
            if self._is_destroyed:
                logger.warning("引擎已销毁，无法保存结果")
                return False
            
            if not self.engine or not self._lib:
                logger.warning("引擎未初始化，无法保存结果")
                return False
            
            # NULL指针检查
            if self.engine == 0:
                logger.error("引擎指针为NULL")
                return False
        
        try:
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
                    # 编码处理：确保正确转换为UTF-8
                    try:
                        texts[i] = text.encode('utf-8')
                    except UnicodeEncodeError as e:
                        logger.warning(f"文本编码失败，使用替换字符: {e}")
                        texts[i] = text.encode('utf-8', errors='replace')
            
            # 编码文件路径
            try:
                file_path_bytes = file_path.encode('utf-8')
                status_bytes = status.encode('utf-8')
            except UnicodeEncodeError as e:
                logger.error(f"路径或状态编码失败: {e}")
                return False
            
            # 调用C++引擎
            result = self._lib.ocr_engine_save_result(
                self.engine,
                file_path_bytes,
                status_bytes,
                rect_count,
                coords,
                texts
            )
            
            if result != 0:
                error_msg = self.get_last_error()
                logger.warning(f"保存结果失败: {error_msg}")
            
            return result == 0
            
        except OSError as e:
            logger.error(f"ctypes调用失败: {e}")
            return False
        except Exception as e:
            logger.error(f"保存结果时发生异常: {e}")
            logger.debug(traceback.format_exc())
            return False
    
    def load_all_results(self) -> Dict[str, Dict]:
        """
        加载所有OCR结果
        :return: {file_path: {"rects": [OCRRect], "status": str}}
        """
        with self._instance_lock:
            if self._is_destroyed:
                logger.warning("引擎已销毁，无法加载结果")
                return {}
            
            if not self.engine or not self._lib:
                logger.warning("引擎未初始化，无法加载结果")
                return {}
            
            # NULL指针检查
            if self.engine == 0:
                logger.error("引擎指针为NULL")
                return {}
        
        try:
            # 调用C++引擎
            json_str_ptr = self._lib.ocr_engine_load_all(self.engine)
        except OSError as e:
            logger.error(f"ctypes调用失败: {e}")
            return {}
        except Exception as e:
            logger.error(f"加载结果时发生异常: {e}")
            return {}
        
        # NULL指针检查
        if not json_str_ptr:
            logger.debug("load_all返回NULL")
            return {}
        
        # 解析JSON
        try:
            # 使用ctypes.string_at安全读取字符串
            json_str = ctypes.string_at(json_str_ptr).decode('utf-8', errors='replace')
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
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            return {}
        except Exception as e:
            logger.error(f"加载OCR结果失败: {e}")
            logger.debug(traceback.format_exc())
            return {}
        finally:
            # 释放C++分配的字符串
            try:
                self._lib.ocr_engine_free_string(ctypes.cast(json_str_ptr, ctypes.c_void_p))
            except Exception as e:
                logger.debug(f"释放字符串时发生错误: {e}")
    
    def save_session(self, files: List[str], cur_index: int) -> bool:
        """
        保存会话元数据
        :param files: 文件列表
        :param cur_index: 当前索引
        :return: 是否成功
        """
        with self._instance_lock:
            if self._is_destroyed:
                logger.warning("引擎已销毁，无法保存会话")
                return False
            
            if not self.engine or not self._lib:
                logger.warning("引擎未初始化，无法保存会话")
                return False
            
            # NULL指针检查
            if self.engine == 0:
                logger.error("引擎指针为NULL")
                return False
        
        try:
            files_json = json.dumps(files, ensure_ascii=False)
            
            result = self._lib.ocr_engine_save_session(
                self.engine,
                files_json.encode('utf-8'),
                cur_index
            )
            
            if result != 0:
                error_msg = self.get_last_error()
                logger.warning(f"保存会话失败: {error_msg}")
            
            return result == 0
            
        except OSError as e:
            logger.error(f"ctypes调用失败: {e}")
            return False
        except Exception as e:
            logger.error(f"保存会话时发生异常: {e}")
            logger.debug(traceback.format_exc())
            return False
    
    def load_session(self) -> Optional[Dict]:
        """
        加载会话元数据
        :return: {"files": [str], "cur_index": int} 或 None
        """
        with self._instance_lock:
            if self._is_destroyed:
                logger.warning("引擎已销毁，无法加载会话")
                return None
            
            if not self.engine or not self._lib:
                logger.warning("引擎未初始化，无法加载会话")
                return None
            
            # NULL指针检查
            if self.engine == 0:
                logger.error("引擎指针为NULL")
                return None
        
        try:
            json_str_ptr = self._lib.ocr_engine_load_session(self.engine)
        except OSError as e:
            logger.error(f"ctypes调用失败: {e}")
            return None
        except Exception as e:
            logger.error(f"加载会话时发生异常: {e}")
            return None
        
        # NULL指针检查
        if not json_str_ptr:
            logger.debug("load_session返回NULL")
            return None
        
        try:
            # 使用ctypes.string_at安全读取字符串
            json_str = ctypes.string_at(json_str_ptr).decode('utf-8', errors='replace')
            return json.loads(json_str)
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}")
            return None
        except Exception as e:
            logger.error(f"加载会话失败: {e}")
            logger.debug(traceback.format_exc())
            return None
        finally:
            try:
                self._lib.ocr_engine_free_string(ctypes.cast(json_str_ptr, ctypes.c_void_p))
            except Exception as e:
                logger.debug(f"释放字符串时发生错误: {e}")
    
    def has_cache(self) -> bool:
        """
        检查是否存在缓存数据
        :return: 是否存在
        """
        with self._instance_lock:
            if self._is_destroyed:
                return False
            
            if not self.engine or not self._lib:
                return False
            
            # NULL指针检查
            if self.engine == 0:
                return False
        
        try:
            return self._lib.ocr_engine_has_cache(self.engine) == 1
        except OSError as e:
            logger.error(f"ctypes调用失败: {e}")
            return False
        except Exception as e:
            logger.error(f"检查缓存时发生异常: {e}")
            return False
    
    def clear_cache(self):
        """清除所有缓存数据"""
        with self._instance_lock:
            if self._is_destroyed:
                logger.warning("引擎已销毁，无法清除缓存")
                return
            
            if not self.engine or not self._lib:
                logger.warning("引擎未初始化，无法清除缓存")
                return
            
            # NULL指针检查
            if self.engine == 0:
                logger.error("引擎指针为NULL")
                return
        
        try:
            self._lib.ocr_engine_clear(self.engine)
        except OSError as e:
            logger.error(f"ctypes调用失败: {e}")
        except Exception as e:
            logger.error(f"清除缓存时发生异常: {e}")
            logger.debug(traceback.format_exc())
    
    def get_last_error(self) -> str:
        """获取最后的错误信息"""
        if not self.engine or not self._lib:
            return "Engine not initialized"
        
        # NULL指针检查
        if self.engine == 0:
            return "Engine pointer is NULL"
        
        try:
            error_ptr = self._lib.ocr_engine_get_error(self.engine)
            if error_ptr:
                return error_ptr.decode('utf-8', errors='replace')
            return ""
        except OSError as e:
            return f"ctypes call failed: {e}"
        except Exception as e:
            return f"Error getting error message: {e}"
    
    def close(self):
        """
        显式关闭并释放资源
        推荐在不再使用缓存管理器时调用此方法
        """
        with self._instance_lock:
            if self._is_destroyed:
                logger.debug("引擎已经被销毁")
                return
            
            try:
                # 减少引用计数
                ref_count = self._decrement_ref_count()
                
                # 只有当引用计数为0时才真正销毁引擎
                if ref_count <= 0:
                    if self.engine and self._lib and self.engine != 0:
                        logger.debug(f"释放OCR缓存引擎资源 (引擎指针: {hex(self.engine)})")
                        
                        # 使用全局锁保护销毁操作
                        with _global_engine_lock:
                            try:
                                self._lib.ocr_engine_destroy(self.engine)
                                logger.info("OCR缓存引擎资源已成功释放")
                            except Exception as e:
                                logger.error(f"调用ocr_engine_destroy失败: {e}")
                        
                        self.engine = None
                else:
                    logger.debug(f"引擎仍有 {ref_count} 个引用，暂不销毁")
                
                self._is_destroyed = True
                
            except Exception as e:
                logger.error(f"释放资源时发生错误: {e}")
                logger.debug(traceback.format_exc())
    
    def __del__(self):
        """析构函数：释放资源"""
        try:
            # 调用close方法进行清理
            self.close()
        except Exception as e:
            # 析构函数中不应该抛出异常
            logger.debug(f"析构函数中释放资源时发生错误: {e}")
    
    def __enter__(self):
        """上下文管理器入口"""
        self._increment_ref_count()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器出口"""
        self.close()
        return False
