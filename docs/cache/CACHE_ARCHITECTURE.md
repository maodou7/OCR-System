# 缓存引擎架构文档

本文档面向开发者，详细说明OCR缓存引擎的架构设计、实现细节和扩展指南。

## 目录

- [架构概述](#架构概述)
- [核心组件](#核心组件)
- [错误处理机制](#错误处理机制)
- [降级策略](#降级策略)
- [并发安全](#并发安全)
- [扩展指南](#扩展指南)

---

## 架构概述

### 设计原则

1. **防御性编程** - 在每个可能失败的点添加检查和错误处理
2. **优雅降级** - 缓存失败时使用内存缓存或禁用缓存功能
3. **详细诊断** - 提供足够的信息帮助定位问题根源
4. **自动恢复** - 尝试自动修复常见问题

### 架构层次

```
应用层 (qt_main.py)
    ↓
安全包装层 (CacheManagerWrapper)
    ↓
Python封装层 (OCRCacheManager)
    ↓ ctypes
C++引擎 (ocr_cache.dll/so)
    ↓
SQLite数据库
```


### 各层职责

**应用层 (qt_main.py)**
- 使用缓存管理器保存和加载OCR结果
- 不需要处理缓存错误（由包装层处理）
- 可以检查缓存状态（可选）

**安全包装层 (CacheManagerWrapper)**
- 提供统一的缓存接口
- 实现自动降级策略
- 捕获所有异常，确保不影响应用程序
- 提供健康检查和状态查询

**Python封装层 (OCRCacheManager)**
- 通过ctypes调用C++引擎
- 实现NULL指针检查和编码处理
- 提供详细的错误信息
- 实现数据库自动恢复

**C++引擎 (ocr_cache.dll/so)**
- 高性能的SQLite操作
- 提供C API接口
- 实现ACID事务保证
- 返回详细的错误信息

---

## 核心组件

### 1. CacheManagerWrapper

**文件：** `cache_manager_wrapper.py`

**核心功能：**
- 自动降级策略
- 线程安全的缓存操作
- 健康检查和状态报告

**关键方法：**

```python
class CacheManagerWrapper:
    def __init__(self, db_path: str = None)
    def save_result(self, file_path: str, rects: List[OCRRect], status: str) -> bool
    def load_all_results(self) -> Dict[str, Dict]
    def save_session(self, files: List[str], cur_index: int) -> bool
    def load_session(self) -> Optional[Dict]
    def has_cache(self) -> bool
    def clear_cache(self)
    def is_cache_available(self) -> bool
    def is_cpp_engine_available(self) -> bool
    def get_status(self) -> CacheStatus
    def health_check(self) -> Dict
```


**降级逻辑：**

```python
def save_result(self, file_path, rects, status):
    try:
        if self.backend and self.backend_type == "cpp_engine":
            # 尝试使用C++引擎
            if self.backend.save_result(file_path, rects, status):
                return True
        
        # 降级到内存缓存
        self.fallback_cache["results"][file_path] = {
            "rects": rects,
            "status": status
        }
        return True
    except Exception as e:
        # 捕获所有异常，确保不影响应用程序
        logger.error(f"保存结果时发生异常: {e}")
        return False
```

### 2. OCRCacheManager

**文件：** `ocr_cache_manager.py`

**核心功能：**
- ctypes接口封装
- NULL指针检查
- 编码处理
- 数据库自动恢复

**初始化流程：**

```python
def __init__(self, db_path: str = None):
    # 1. 路径验证和准备
    self.db_path = self._prepare_db_path(db_path)
    
    # 2. 加载C++库
    self.lib = self._load_library()
    
    # 3. 定义函数签名
    self._define_function_signatures()
    
    # 4. 初始化引擎
    self.engine = self._init_engine()
    
    # 5. 验证引擎
    self._validate_engine()
```


**错误检测：**

```python
def _init_engine(self):
    try:
        db_path_bytes = self.db_path.encode('utf-8')
        engine = self.lib.ocr_engine_init(db_path_bytes)
        
        # NULL指针检查
        if not engine:
            error_msg = self.lib.ocr_engine_get_error()
            raise CacheInitError(
                error_type="engine_init_failed",
                error_message=error_msg.decode('utf-8'),
                error_details={"db_path": self.db_path},
                suggestions=["检查数据库路径", "检查磁盘空间"]
            )
        
        return engine
    except OSError as e:
        # ctypes调用失败
        raise CacheInitError(
            error_type="ctypes_call_failed",
            error_message=str(e),
            error_details={"function": "ocr_engine_init"},
            suggestions=["检查库文件是否存在", "检查依赖库"]
        )
```

### 3. CacheInitError

**文件：** `ocr_cache_manager.py`

**数据结构：**

```python
@dataclass
class CacheInitError(Exception):
    error_type: str          # 错误类型
    error_message: str       # 错误消息
    error_details: Dict      # 详细信息
    suggestions: List[str]   # 修复建议
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
```

**错误类型：**
- `library_load_failed` - 库文件加载失败
- `engine_init_failed` - 引擎初始化失败
- `db_corrupt` - 数据库损坏
- `permission_denied` - 权限不足
- `encoding_error` - 编码错误
- `ctypes_call_failed` - ctypes调用失败


---

## 错误处理机制

### 错误分类

1. **库加载错误**
   - 库文件不存在
   - 缺少依赖库
   - 版本不兼容

2. **引擎初始化错误**
   - NULL指针返回
   - 数据库路径无效
   - 权限不足

3. **数据库错误**
   - 数据库损坏
   - 磁盘空间不足
   - 文件被锁定

4. **运行时错误**
   - ctypes调用失败
   - 编码转换错误
   - 并发冲突

### 错误恢复策略

```python
# 错误恢复决策树
if library_load_failed:
    log_error_with_suggestions()
    use_memory_cache()

elif engine_init_failed:
    if db_corrupt:
        try_auto_recover()
        if recovery_failed:
            use_memory_cache()
    elif permission_denied:
        try_alternative_path()
        if still_failed:
            use_memory_cache()
    else:
        use_memory_cache()

elif runtime_error:
    log_error_with_stack_trace()
    disable_cache_for_this_operation()
    continue_with_core_functionality()
```


### 数据库自动恢复

**实现位置：** `OCRCacheManager._recover_database()`

**恢复流程：**

```python
def _recover_database(self):
    """尝试自动恢复损坏的数据库"""
    try:
        # 1. 检查数据库完整性
        if not self._check_db_integrity():
            logger.warning("数据库损坏，尝试自动恢复")
            
            # 2. 备份现有数据库
            backup_path = f"{self.db_path}.backup"
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"已备份数据库到: {backup_path}")
            
            # 3. 删除损坏的数据库
            os.remove(self.db_path)
            logger.info("已删除损坏的数据库")
            
            # 4. 重新初始化引擎（会创建新数据库）
            self.engine = self._init_engine()
            logger.info("数据库自动恢复成功")
            
            return True
    except Exception as e:
        logger.error(f"数据库自动恢复失败: {e}")
        return False
```

---

## 降级策略

### 三级降级模式

1. **C++引擎模式（正常）**
   - 使用高性能C++引擎
   - 数据持久化到SQLite
   - 支持会话恢复

2. **内存缓存模式（降级）**
   - 使用Python字典存储
   - 数据仅在内存中
   - 关闭程序后丢失

3. **禁用模式（完全降级）**
   - 不使用任何缓存
   - 每次都是全新状态


### 降级触发条件

**自动降级到内存缓存：**
- 库文件加载失败
- 引擎初始化失败
- 数据库损坏且无法恢复
- 权限不足

**手动禁用缓存：**
```python
# 在qt_main.py中
self.cache_manager = None
```

### 内存缓存实现

```python
fallback_cache = {
    "results": {
        "file_path": {
            "rects": [OCRRect, ...],
            "status": str
        }
    },
    "session": {
        "files": [str, ...],
        "cur_index": int
    }
}
```

**特点：**
- 简单的Python字典
- 无需外部依赖
- 性能足够（小规模数据）
- 不持久化

---

## 并发安全

### 线程安全机制

**使用可重入锁（RLock）：**

```python
class CacheManagerWrapper:
    def __init__(self):
        self._lock = threading.RLock()
    
    def save_result(self, ...):
        with self._lock:
            # 线程安全的操作
            ...
```


**为什么使用RLock：**
- 支持同一线程多次获取锁
- 避免死锁
- 适合递归调用

**C++层的并发安全：**
- SQLite本身是线程安全的（使用互斥锁）
- 每个操作都在事务中执行
- ACID保证数据一致性

### 资源清理

**Python层：**

```python
def __del__(self):
    """析构函数：清理资源"""
    try:
        if self.engine:
            self.lib.ocr_engine_destroy(self.engine)
            self.engine = None
    except Exception as e:
        logger.debug(f"清理资源时发生错误: {e}")
```

**C++层：**

```cpp
void ocr_engine_destroy(void* engine) {
    if (engine) {
        OCRCacheEngine* eng = static_cast<OCRCacheEngine*>(engine);
        delete eng;
    }
}
```

---

## 扩展指南

### 添加新的缓存操作

**步骤 1：在C++引擎中添加函数**

```cpp
// ocr_cache_engine.cpp
extern "C" int ocr_engine_custom_operation(void* engine, const char* param) {
    if (!engine) return 0;
    OCRCacheEngine* eng = static_cast<OCRCacheEngine*>(engine);
    // 实现自定义操作
    return 1;
}
```


**步骤 2：在OCRCacheManager中封装**

```python
# ocr_cache_manager.py
class OCRCacheManager:
    def _define_function_signatures(self):
        # 添加新函数签名
        self.lib.ocr_engine_custom_operation.argtypes = [c_void_p, c_char_p]
        self.lib.ocr_engine_custom_operation.restype = c_int
    
    def custom_operation(self, param: str) -> bool:
        """自定义操作"""
        try:
            param_bytes = param.encode('utf-8')
            result = self.lib.ocr_engine_custom_operation(self.engine, param_bytes)
            return result == 1
        except Exception as e:
            logger.error(f"自定义操作失败: {e}")
            return False
```

**步骤 3：在CacheManagerWrapper中添加降级逻辑**

```python
# cache_manager_wrapper.py
class CacheManagerWrapper:
    def custom_operation(self, param: str) -> bool:
        """自定义操作（自动降级）"""
        with self._lock:
            try:
                if self.backend and self.backend_type == "cpp_engine":
                    return self.backend.custom_operation(param)
                
                # 降级实现
                logger.debug("使用降级实现")
                return self._fallback_custom_operation(param)
            except Exception as e:
                logger.error(f"自定义操作异常: {e}")
                return False
```


### 添加新的错误类型

**步骤 1：定义错误类型**

```python
# ocr_cache_manager.py
# 在CacheInitError的error_type中添加新类型
ERROR_TYPES = [
    "library_load_failed",
    "engine_init_failed",
    "db_corrupt",
    "permission_denied",
    "encoding_error",
    "ctypes_call_failed",
    "custom_error_type"  # 新增
]
```

**步骤 2：在适当的位置抛出错误**

```python
raise CacheInitError(
    error_type="custom_error_type",
    error_message="自定义错误消息",
    error_details={"key": "value"},
    suggestions=["建议1", "建议2"]
)
```

**步骤 3：更新故障排除文档**

在 `CACHE_TROUBLESHOOTING.md` 中添加新错误的说明和解决方案。

### 实现新的降级策略

**示例：Redis缓存降级**

```python
class CacheManagerWrapper:
    def __init__(self, db_path: str = None, redis_url: str = None):
        self.backend = None
        self.redis_client = None
        self.fallback_cache = {}
        
        # 尝试初始化C++引擎
        if not self._try_init_backend(db_path):
            # 尝试初始化Redis
            if not self._try_init_redis(redis_url):
                # 最后降级到内存缓存
                self.backend_type = "memory"
```


---

## 测试策略

### 单元测试

**文件：** `test_cache_engine_unit_tests.py`

**测试内容：**
- OCRCacheManager初始化
- 各种错误场景
- 数据库自动恢复
- 编码处理

### 属性测试

**文件：** `test_cache_wrapper_properties.py`

**使用Hypothesis库进行属性测试：**

```python
from hypothesis import given, strategies as st

@given(st.text(), st.lists(st.builds(OCRRect)))
def test_save_result_never_crashes(file_path, rects):
    """属性1: 保存结果永不崩溃"""
    wrapper = CacheManagerWrapper()
    # 无论输入什么，都不应该崩溃
    wrapper.save_result(file_path, rects)
```

### 集成测试

**文件：** `test_cache_robustness_integration.py`

**测试场景：**
- 完整的应用启动流程
- 缓存失败时的OCR工作流
- 各种环境下的行为

---

## 性能优化

### 初始化性能

- 正常初始化: < 100ms
- 自动恢复: < 500ms
- 降级到内存缓存: < 10ms

### 缓存操作性能

- 保存结果: < 5ms
- 加载结果: < 10ms
- 保存会话: < 5ms


### 内存使用

- C++引擎: ~5MB
- 内存缓存: ~1MB (1000个文件)
- 总开销: < 10MB

### 优化建议

1. **使用连接池**（如果实现多后端）
2. **批量操作**（减少ctypes调用次数）
3. **异步操作**（不阻塞主线程）
4. **缓存预热**（启动时加载常用数据）

---

## 调试技巧

### 启用详细日志

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 使用诊断脚本

```bash
python diagnose_cache.py
```

### 检查健康状态

```python
wrapper = CacheManagerWrapper()
health = wrapper.health_check()
print(json.dumps(health, indent=2, ensure_ascii=False))
```

### 模拟错误场景

```python
# 模拟库文件不存在
os.rename("models/ocr_cache.dll", "models/ocr_cache.dll.bak")

# 模拟数据库损坏
with open(".ocr_cache/ocr_cache.db", "wb") as f:
    f.write(b"corrupted data")

# 模拟权限不足
os.chmod(".ocr_cache", 0o444)
```

---

## 最佳实践

### 1. 始终使用包装层

```python
# 推荐
self.cache_manager = CacheManagerWrapper()

# 不推荐（直接使用OCRCacheManager）
self.cache_manager = OCRCacheManager()
```


### 2. 检查缓存状态（可选）

```python
if not self.cache_manager.is_cpp_engine_available():
    logger.warning("C++引擎不可用，使用内存缓存")
```

### 3. 不要依赖缓存可用性

```python
# 推荐：缓存失败不影响核心功能
result = ocr_engine.recognize(image)
self.cache_manager.save_result(file_path, result)  # 可能失败，但不影响result

# 不推荐：依赖缓存
if self.cache_manager.is_available():
    result = ocr_engine.recognize(image)
```

### 4. 定期清理缓存

```python
# 在适当的时候清理
if cache_size > MAX_SIZE:
    self.cache_manager.clear_cache()
```

### 5. 提供用户反馈

```python
status = self.cache_manager.get_status()
if status.fallback_active:
    self.show_warning("缓存引擎不可用，使用内存缓存模式")
```

---

## 常见陷阱

### 1. 不要在循环中频繁初始化

```python
# 错误
for file in files:
    cache = CacheManagerWrapper()  # 每次都初始化
    cache.save_result(file, result)

# 正确
cache = CacheManagerWrapper()  # 只初始化一次
for file in files:
    cache.save_result(file, result)
```


### 2. 不要忽略返回值

```python
# 错误
cache.save_result(file, result)  # 忽略返回值

# 正确
if not cache.save_result(file, result):
    logger.warning(f"保存缓存失败: {file}")
```

### 3. 不要在异常处理中抛出新异常

```python
# 错误
try:
    cache.save_result(file, result)
except Exception as e:
    raise RuntimeError("缓存失败")  # 会导致应用崩溃

# 正确
try:
    cache.save_result(file, result)
except Exception as e:
    logger.error(f"缓存失败: {e}")  # 记录日志，继续运行
```

### 4. 不要在多线程中共享未加锁的缓存

```python
# 错误
cache = CacheManagerWrapper()
threads = [Thread(target=cache.save_result, args=(f, r)) for f, r in items]

# 正确（包装层已经实现了线程安全）
cache = CacheManagerWrapper()  # 内部使用RLock
threads = [Thread(target=cache.save_result, args=(f, r)) for f, r in items]
```

---

## 版本兼容性

### C++引擎版本

- **v1.0** - 初始版本
- **v1.1** - 添加健康检查函数
- **v1.2** - 添加自动恢复功能

### Python接口版本

- **v1.0** - 基础接口
- **v1.1** - 添加CacheManagerWrapper
- **v1.2** - 添加健康检查和状态查询


### 向后兼容性

**保证：**
- Python接口保持向后兼容
- 数据库架构自动迁移
- 旧版本数据可以被新版本读取

**不保证：**
- C++引擎的ABI兼容性（需要重新编译）
- 内部实现细节

---

## 贡献指南

### 提交代码

1. Fork仓库
2. 创建特性分支
3. 编写测试
4. 提交PR

### 代码规范

- 遵循PEP 8
- 添加类型注解
- 编写文档字符串
- 添加单元测试

### 测试要求

- 单元测试覆盖率 > 90%
- 所有属性测试通过
- 集成测试通过

---

## 参考资料

### 相关文档

- [故障排除指南](CACHE_TROUBLESHOOTING.md)
- [设计文档](.kiro/specs/cache-engine-robustness/design.md)
- [需求文档](.kiro/specs/cache-engine-robustness/requirements.md)

### 外部资源

- [SQLite文档](https://www.sqlite.org/docs.html)
- [ctypes文档](https://docs.python.org/3/library/ctypes.html)
- [Hypothesis文档](https://hypothesis.readthedocs.io/)

---

**最后更新：** 2024-11-30
**版本：** 1.4.2
