# 缓存引擎故障排除指南

本指南帮助您诊断和解决OCR缓存引擎相关的问题。

## 目录

- [常见错误](#常见错误)
- [诊断步骤](#诊断步骤)
- [解决方案](#解决方案)
- [高级诊断](#高级诊断)
- [联系支持](#联系支持)

---

## 常见错误

### 1. Access Violation (访问违规错误)

**错误信息示例：**
```
缓存引擎初始化失败
错误类型: engine_init_failed
错误信息: access violation writing 0x0000000000000000
```

**原因：**
- C++引擎返回了NULL指针
- 数据库文件损坏
- 库文件版本不兼容
- 内存不足

**解决方案：**
1. **自动降级**：系统会自动使用内存缓存，不影响OCR功能
2. **删除数据库**：删除 `.ocr_cache/ocr_cache.db` 文件，让系统重新创建
3. **重新安装**：重新下载并安装应用程序
4. **检查磁盘空间**：确保有足够的磁盘空间（至少100MB）

---

### 2. Library Load Failed (库文件加载失败)

**错误信息示例：**
```
缓存引擎初始化失败
错误类型: library_load_failed
错误信息: 找不到指定的模块
库路径: models/ocr_cache.dll
```

**原因：**
- 缺少Visual C++运行库（Windows）
- 库文件不存在或损坏
- 权限不足

**解决方案：**

**Windows用户：**
1. **安装Visual C++ Redistributable**
   - 下载并安装 [Microsoft Visual C++ 2015-2022 Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
   - 这会安装必需的 `msvcr140.dll` 和其他依赖库

2. **检查库文件**
   ```bash
   # 确认文件存在
   dir models\ocr_cache.dll
   ```

3. **重新安装应用**
   - 如果库文件损坏，重新下载应用程序

**Linux用户：**
1. **检查库文件权限**
   ```bash
   ls -l models/libocr_cache.so
   chmod +x models/libocr_cache.so
   ```

2. **检查依赖**
   ```bash
   ldd models/libocr_cache.so
   ```

---

### 3. Database Corrupt (数据库损坏)

**错误信息示例：**
```
缓存引擎初始化失败
错误类型: db_corrupt
错误信息: database disk image is malformed
```

**原因：**
- 数据库文件损坏（异常关闭、磁盘错误等）
- 数据库架构版本不匹配

**解决方案：**

**自动恢复（推荐）：**
系统会自动尝试恢复：
1. 备份损坏的数据库到 `.ocr_cache/ocr_cache.db.backup`
2. 删除损坏的数据库
3. 创建新的数据库

**手动恢复：**
```bash
# 1. 备份现有数据库
cp .ocr_cache/ocr_cache.db .ocr_cache/ocr_cache.db.backup

# 2. 删除损坏的数据库
rm .ocr_cache/ocr_cache.db

# 3. 重新启动应用程序
python qt_run.py
```

---

### 4. Permission Denied (权限不足)

**错误信息示例：**
```
缓存引擎初始化失败
错误类型: permission_denied
错误信息: unable to open database file
```

**原因：**
- 数据库目录不可写
- 文件被其他进程锁定
- 用户权限不足

**解决方案：**

**Windows：**
1. **以管理员身份运行**
   - 右键点击程序，选择"以管理员身份运行"

2. **检查文件夹权限**
   - 右键点击 `.ocr_cache` 文件夹
   - 属性 → 安全 → 编辑
   - 确保当前用户有"完全控制"权限

**Linux/macOS：**
```bash
# 检查权限
ls -ld .ocr_cache

# 修改权限
chmod 755 .ocr_cache
chmod 644 .ocr_cache/ocr_cache.db
```

---

### 5. Encoding Error (编码错误)

**错误信息示例：**
```
缓存引擎初始化失败
错误类型: encoding_error
错误信息: 'utf-8' codec can't decode byte
```

**原因：**
- 数据库路径包含特殊字符
- 系统编码设置不正确

**解决方案：**

1. **使用英文路径**
   - 将应用程序移动到不含中文或特殊字符的路径
   - 例如：`C:\OCR\` 而不是 `C:\我的文档\OCR系统\`

2. **设置环境变量**（Windows）
   ```bash
   set PYTHONIOENCODING=utf-8
   python qt_run.py
   ```

---

## 诊断步骤

### 步骤 1: 检查缓存状态

在应用程序中查看缓存状态：

```python
# 在Python控制台中运行
from cache_manager_wrapper import CacheManagerWrapper

wrapper = CacheManagerWrapper()
status = wrapper.health_check()
print(status)
```

**输出示例：**
```json
{
  "cache_available": true,
  "backend_type": "memory",
  "fallback_active": true,
  "message": "使用内存缓存（C++引擎不可用）",
  "init_error": {
    "type": "library_load_failed",
    "message": "找不到指定的模块",
    "suggestions": ["检查是否缺少Visual C++运行库"]
  }
}
```

### 步骤 2: 查看日志文件

日志文件位置：`cache_debug.log`

```bash
# 查看最近的日志
tail -n 50 cache_debug.log

# Windows
type cache_debug.log
```

**关键日志信息：**
- `ERROR` - 严重错误
- `WARNING` - 警告（如降级到内存缓存）
- `INFO` - 一般信息
- `DEBUG` - 详细调试信息

### 步骤 3: 测试基本功能

即使缓存引擎不可用，OCR核心功能应该正常工作：

1. 打开一张图片
2. 框选区域
3. 点击"开始识别"
4. 检查是否能正常识别

**如果OCR功能正常：**
- 缓存问题不影响使用，可以继续工作
- 数据会保存在内存中（关闭程序后丢失）

**如果OCR功能异常：**
- 这不是缓存问题，请检查OCR引擎配置

---

## 解决方案

### 方案 1: 使用内存缓存模式

**适用场景：**
- C++引擎无法初始化
- 临时使用，不需要持久化缓存

**操作：**
无需任何操作，系统会自动降级到内存缓存模式。

**限制：**
- 缓存数据不会持久化
- 关闭程序后数据丢失
- 无法恢复会话

---

### 方案 2: 重置缓存引擎

**适用场景：**
- 数据库损坏
- 缓存数据异常

**操作步骤：**

1. **关闭应用程序**

2. **删除缓存目录**
   ```bash
   # Windows
   rmdir /s /q .ocr_cache
   
   # Linux/macOS
   rm -rf .ocr_cache
   ```

3. **重新启动应用程序**
   ```bash
   python qt_run.py
   ```

系统会自动创建新的缓存数据库。

---

### 方案 3: 禁用缓存功能

**适用场景：**
- 不需要缓存功能
- 缓存引擎持续出现问题

**操作步骤：**

编辑 `qt_main.py`，修改缓存初始化代码：

```python
# 找到这一行
self.cache_manager = CacheManagerWrapper()

# 替换为
self.cache_manager = None
```

**影响：**
- 不会保存识别结果
- 不会保存会话信息
- 每次启动都是全新状态

---

### 方案 4: 重新安装Visual C++运行库（Windows）

**适用场景：**
- Windows系统
- 提示缺少DLL文件

**操作步骤：**

1. **下载运行库**
   - [Visual C++ 2015-2022 x64](https://aka.ms/vs/17/release/vc_redist.x64.exe)
   - [Visual C++ 2015-2022 x86](https://aka.ms/vs/17/release/vc_redist.x86.exe)

2. **安装运行库**
   - 双击下载的文件
   - 按照提示完成安装
   - 可能需要重启计算机

3. **重新启动应用程序**

---

## 高级诊断

### 使用诊断脚本

创建 `diagnose_cache.py` 文件：

```python
"""缓存引擎诊断脚本"""
import os
import sys
import platform
from cache_manager_wrapper import CacheManagerWrapper

def diagnose():
    print("=" * 60)
    print("缓存引擎诊断报告")
    print("=" * 60)
    
    # 系统信息
    print("\n[系统信息]")
    print(f"操作系统: {platform.system()} {platform.release()}")
    print(f"Python版本: {sys.version}")
    print(f"工作目录: {os.getcwd()}")
    
    # 检查库文件
    print("\n[库文件检查]")
    if platform.system() == "Windows":
        lib_path = "models/ocr_cache.dll"
    else:
        lib_path = "models/libocr_cache.so"
    
    if os.path.exists(lib_path):
        print(f"✓ 库文件存在: {lib_path}")
        print(f"  文件大小: {os.path.getsize(lib_path)} 字节")
    else:
        print(f"✗ 库文件不存在: {lib_path}")
    
    # 检查数据库目录
    print("\n[数据库目录检查]")
    db_dir = ".ocr_cache"
    if os.path.exists(db_dir):
        print(f"✓ 数据库目录存在: {db_dir}")
        print(f"  可写: {os.access(db_dir, os.W_OK)}")
        
        db_file = os.path.join(db_dir, "ocr_cache.db")
        if os.path.exists(db_file):
            print(f"✓ 数据库文件存在: {db_file}")
            print(f"  文件大小: {os.path.getsize(db_file)} 字节")
        else:
            print(f"  数据库文件不存在（首次运行正常）")
    else:
        print(f"  数据库目录不存在（首次运行正常）")
    
    # 测试缓存初始化
    print("\n[缓存初始化测试]")
    try:
        wrapper = CacheManagerWrapper()
        health = wrapper.health_check()
        
        print(f"缓存可用: {health['cache_available']}")
        print(f"后端类型: {health['backend_type']}")
        print(f"降级模式: {health['fallback_active']}")
        print(f"状态消息: {health['message']}")
        
        if 'init_error' in health:
            print(f"\n[初始化错误]")
            print(f"错误类型: {health['init_error']['type']}")
            print(f"错误消息: {health['init_error']['message']}")
            print(f"建议:")
            for suggestion in health['init_error']['suggestions']:
                print(f"  - {suggestion}")
    
    except Exception as e:
        print(f"✗ 初始化失败: {e}")
    
    print("\n" + "=" * 60)
    print("诊断完成")
    print("=" * 60)

if __name__ == "__main__":
    diagnose()
```

运行诊断：
```bash
python diagnose_cache.py
```

---

### 启用详细日志

编辑 `cache_logging_config.py`，设置日志级别为 `DEBUG`：

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,  # 改为DEBUG
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cache_debug.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
```

重新启动应用程序，查看详细日志。

---

## 性能优化建议

### 1. 定期清理缓存

缓存数据库会随着使用增长，建议定期清理：

```python
# 在应用程序中
self.cache_manager.clear_cache()
```

或手动删除：
```bash
rm .ocr_cache/ocr_cache.db
```

### 2. 使用SSD存储

将应用程序和缓存数据库放在SSD上，可以显著提升性能。

### 3. 调整数据库位置

如果默认位置有问题，可以指定其他位置：

```python
# 在qt_main.py中
self.cache_manager = CacheManagerWrapper(db_path="/path/to/custom/cache.db")
```

---

## 联系支持

如果以上方法都无法解决问题，请联系技术支持：

### 提交Issue

访问 [GitHub Issues](https://github.com/maodou7/OCR-System/issues)

**请提供以下信息：**
1. 操作系统和版本
2. Python版本
3. 错误信息截图
4. `cache_debug.log` 日志文件
5. 诊断脚本输出

### 临时解决方案

在等待支持的同时，您可以：
1. 使用内存缓存模式继续工作
2. 禁用缓存功能
3. 手动保存识别结果（导出Excel）

---

## 常见问题FAQ

### Q: 缓存引擎失败会影响OCR功能吗？

**A:** 不会。系统会自动降级到内存缓存模式，所有OCR功能都能正常使用。唯一的区别是：
- 关闭程序后，识别结果不会保存
- 无法恢复上次的工作会话

### Q: 内存缓存模式有什么限制？

**A:** 
- 数据只保存在内存中，关闭程序后丢失
- 无法持久化保存识别结果
- 无法恢复会话
- 但所有OCR功能都正常工作

### Q: 如何知道当前使用的是哪种缓存模式？

**A:** 查看日志文件 `cache_debug.log`：
- `C++缓存引擎初始化成功` → C++引擎模式
- `已降级到内存缓存模式` → 内存缓存模式

### Q: 可以完全禁用缓存功能吗？

**A:** 可以。编辑 `qt_main.py`，将 `self.cache_manager = CacheManagerWrapper()` 改为 `self.cache_manager = None`。

### Q: 缓存数据库会占用多少空间？

**A:** 取决于使用情况：
- 空数据库：约100KB
- 1000张图片的缓存：约10-50MB
- 建议定期清理旧数据

### Q: 为什么有时候缓存引擎会突然失败？

**A:** 可能的原因：
- 磁盘空间不足
- 数据库文件被其他程序锁定
- 系统资源不足
- 数据库文件损坏

系统会自动降级到内存缓存，不影响使用。

---

## 版本历史

- **v1.4.2** - 添加自动降级和健康检查功能
- **v1.4.0** - 引入C++缓存引擎
- **v1.3.0** - 初始缓存功能

---

**最后更新：** 2024-11-30
