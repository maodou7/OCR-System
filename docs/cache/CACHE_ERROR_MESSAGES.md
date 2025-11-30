# 缓存引擎错误消息参考

本文档列出所有可能的缓存引擎错误消息及其解决方案。

## 错误消息格式

```
缓存引擎初始化失败
错误类型: <error_type>
错误信息: <error_message>
[详细信息]

可能的解决方案:
1. <suggestion_1>
2. <suggestion_2>
...

系统将使用内存缓存继续运行，但缓存数据不会持久化。
```

---

## 错误类型列表

### 1. library_load_failed

**错误消息示例：**
```
缓存引擎初始化失败
错误类型: library_load_failed
错误信息: 找不到指定的模块
库路径: models/ocr_cache.dll

可能的解决方案:
1. 检查是否缺少Visual C++运行库（需要msvcr140.dll）
2. 确认库文件存在于指定路径
3. 尝试重新安装应用程序
4. 检查防病毒软件是否阻止了DLL加载
```

**原因：**
- 库文件不存在
- 缺少依赖库（如msvcr140.dll）
- 库文件损坏
- 权限不足

**解决方案：**
1. **Windows用户**：安装 [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
2. **检查文件**：确认 `models/ocr_cache.dll` 或 `models/libocr_cache.so` 存在
3. **重新安装**：重新下载并安装应用程序

---

### 2. engine_init_failed

**错误消息示例：**
```
缓存引擎初始化失败
错误类型: engine_init_failed
错误信息: access violation writing 0x0000000000000000
数据库路径: .ocr_cache/ocr_cache.db

可能的解决方案:
1. 删除损坏的数据库文件
2. 检查磁盘空间是否充足
3. 确认数据库目录可写
4. 尝试使用其他数据库路径
```

**原因：**
- C++引擎返回NULL指针
- 数据库文件损坏
- 内存不足
- 磁盘空间不足

**解决方案：**
1. **删除数据库**：
   ```bash
   rm -rf .ocr_cache  # Linux/macOS
   rmdir /s /q .ocr_cache  # Windows
   ```
2. **检查磁盘空间**：确保至少有100MB可用空间
3. **重新启动程序**

---

### 3. db_corrupt

**错误消息示例：**
```
缓存引擎初始化失败
错误类型: db_corrupt
错误信息: database disk image is malformed
数据库路径: .ocr_cache/ocr_cache.db

可能的解决方案:
1. 系统将自动尝试恢复数据库
2. 如果自动恢复失败，请手动删除数据库文件
3. 检查磁盘是否有错误
```

**原因：**
- 数据库文件损坏（异常关闭、磁盘错误等）
- 数据库架构版本不匹配
- 文件系统错误

**解决方案：**
1. **自动恢复**：系统会自动尝试恢复，备份文件保存在 `.ocr_cache/ocr_cache.db.backup`
2. **手动恢复**：
   ```bash
   # 备份现有数据库
   cp .ocr_cache/ocr_cache.db .ocr_cache/ocr_cache.db.manual_backup
   
   # 删除损坏的数据库
   rm .ocr_cache/ocr_cache.db
   
   # 重新启动程序
   ```
3. **检查磁盘**：运行磁盘检查工具（Windows: chkdsk, Linux: fsck）

---

### 4. permission_denied

**错误消息示例：**
```
缓存引擎初始化失败
错误类型: permission_denied
错误信息: unable to open database file
数据库路径: .ocr_cache/ocr_cache.db

可能的解决方案:
1. 以管理员身份运行程序
2. 检查数据库目录的写入权限
3. 确认文件未被其他程序锁定
4. 尝试使用其他数据库路径
```

**原因：**
- 数据库目录不可写
- 文件被其他进程锁定
- 用户权限不足

**解决方案：**
1. **Windows**：
   - 右键点击程序，选择"以管理员身份运行"
   - 检查 `.ocr_cache` 文件夹权限
2. **Linux/macOS**：
   ```bash
   chmod 755 .ocr_cache
   chmod 644 .ocr_cache/ocr_cache.db
   ```
3. **检查锁定**：关闭其他可能使用数据库的程序

---

### 5. encoding_error

**错误消息示例：**
```
缓存引擎初始化失败
错误类型: encoding_error
错误信息: 'utf-8' codec can't decode byte 0xff
数据库路径: C:\我的文档\OCR系统\.ocr_cache\ocr_cache.db

可能的解决方案:
1. 使用不含特殊字符的路径
2. 设置环境变量 PYTHONIOENCODING=utf-8
3. 将应用程序移动到英文路径
```

**原因：**
- 数据库路径包含特殊字符
- 系统编码设置不正确
- 文件名编码问题

**解决方案：**
1. **使用英文路径**：将应用程序移动到不含中文或特殊字符的路径
   - 推荐：`C:\OCR\` 或 `/home/user/ocr/`
   - 避免：`C:\我的文档\OCR系统\` 或 `/home/用户/文档/`
2. **设置环境变量**（Windows）：
   ```bash
   set PYTHONIOENCODING=utf-8
   python qt_run.py
   ```

---

### 6. ctypes_call_failed

**错误消息示例：**
```
缓存引擎初始化失败
错误类型: ctypes_call_failed
错误信息: [WinError 126] 找不到指定的模块
函数: ocr_engine_init

可能的解决方案:
1. 检查库文件是否存在
2. 确认所有依赖库都已安装
3. 尝试重新安装Visual C++运行库
4. 检查库文件是否损坏
```

**原因：**
- ctypes无法调用C++函数
- 函数签名不匹配
- 库文件损坏

**解决方案：**
1. **检查库文件**：确认文件存在且完整
2. **重新安装运行库**：安装最新的Visual C++ Redistributable
3. **重新下载**：重新下载应用程序

---

### 7. unexpected_wrapper_error

**错误消息示例：**
```
缓存引擎初始化失败
错误类型: unexpected_wrapper_error
错误信息: <异常消息>

可能的解决方案:
1. 这是一个未预期的错误，请查看日志
2. 尝试重新启动程序
3. 如果问题持续，请提交Issue
```

**原因：**
- 未预期的异常
- 代码bug
- 环境问题

**解决方案：**
1. **查看日志**：检查 `cache_debug.log` 文件
2. **重新启动**：关闭并重新启动程序
3. **提交Issue**：如果问题持续，请在GitHub提交Issue，附带日志文件

---

## 系统消息

### 自动降级消息

```
C++缓存引擎初始化失败，将使用内存缓存
系统将使用内存缓存继续运行，但缓存数据不会持久化。
```

**含义：**
- C++引擎不可用，系统自动切换到内存缓存模式
- 所有OCR功能正常工作
- 关闭程序后，识别结果不会保存

**建议：**
- 及时导出Excel保存结果
- 查看日志了解失败原因
- 参考故障排除指南解决问题

### 自动恢复消息

```
数据库损坏，尝试自动恢复
已备份数据库到: .ocr_cache/ocr_cache.db.backup
已删除损坏的数据库
数据库自动恢复成功
```

**含义：**
- 系统检测到数据库损坏
- 自动备份并重建数据库
- 恢复成功，可以继续使用

**注意：**
- 旧的缓存数据已丢失（但有备份）
- 如需恢复旧数据，可以尝试修复备份文件

---

## 日志级别

### ERROR（错误）

严重错误，需要关注：
```
ERROR - 缓存引擎初始化失败: library_load_failed
ERROR - 保存结果时发生异常: <异常信息>
ERROR - 数据库自动恢复失败: <错误信息>
```

### WARNING（警告）

警告信息，系统已处理：
```
WARNING - C++缓存引擎初始化失败，将使用内存缓存
WARNING - 数据库损坏，尝试自动恢复
WARNING - C++引擎保存失败，降级到内存缓存
```

### INFO（信息）

一般信息：
```
INFO - 尝试初始化C++缓存引擎
INFO - C++缓存引擎初始化成功
INFO - 已降级到内存缓存模式
INFO - 数据库自动恢复成功
```

### DEBUG（调试）

详细调试信息：
```
DEBUG - 库文件路径: models/ocr_cache.dll
DEBUG - 数据库路径: .ocr_cache/ocr_cache.db
DEBUG - 使用降级实现
DEBUG - 清理资源时发生错误: <错误信息>
```

---

## 快速诊断

### 检查缓存状态

```python
from cache_manager_wrapper import CacheManagerWrapper

wrapper = CacheManagerWrapper()
status = wrapper.get_status()

print(f"缓存可用: {status.is_available}")
print(f"后端类型: {status.backend_type}")
print(f"状态消息: {status.message}")

if status.init_error:
    print(f"错误类型: {status.init_error.error_type}")
    print(f"错误消息: {status.init_error.error_message}")
    print(f"建议: {status.init_error.suggestions}")
```

### 查看健康检查

```python
health = wrapper.health_check()
import json
print(json.dumps(health, indent=2, ensure_ascii=False))
```

**输出示例：**
```json
{
  "cache_available": true,
  "backend_type": "memory",
  "fallback_active": true,
  "message": "使用内存缓存（C++引擎不可用）",
  "timestamp": "2024-11-30T10:30:00",
  "init_error": {
    "type": "library_load_failed",
    "message": "找不到指定的模块",
    "suggestions": [
      "检查是否缺少Visual C++运行库（需要msvcr140.dll）",
      "确认库文件存在于指定路径"
    ]
  },
  "memory_cache": {
    "results_count": 0,
    "has_session": false
  }
}
```

---

## 相关文档

- [故障排除指南](CACHE_TROUBLESHOOTING.md) - 详细的问题诊断和解决方案
- [架构文档](CACHE_ARCHITECTURE.md) - 开发者技术文档
- [README](README.md) - 项目主文档

---

**最后更新：** 2024-11-30
