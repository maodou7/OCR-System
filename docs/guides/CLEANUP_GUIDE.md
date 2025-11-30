# 打包前清理指南

## 概述

本指南介绍如何使用打包前清理工具来清理缓存、临时文件和构建产物，以确保打包体积最小化。

## 清理内容

清理脚本会自动清理以下内容：

### 1. Python 缓存文件
- `__pycache__/` 目录
- `*.pyc` 编译文件
- `*.pyo` 优化文件

### 2. 缓存数据库
- `.ocr_cache/` 目录及其中的 SQLite 数据库
- `.ocr_system_config/` 配置缓存目录
- 项目根目录下的 `*.db` 文件（不包括 models 目录）
- `*.db-journal` 日志文件

### 3. 构建产物
- `build/` 目录
- `dist/` 目录
- `Pack/Pyinstaller/build/` 目录
- `Pack/Pyinstaller/dist/` 目录
- `.pytest_cache/` 测试缓存
- `.coverage` 覆盖率文件
- `htmlcov/` 覆盖率报告
- `*.egg-info/` 包信息

### 4. 临时文件
- `*.tmp` 临时文件
- `*.temp` 临时文件
- `*.log` 日志文件
- `*.bak` 备份文件
- `*.swp` Vim 交换文件
- `*.swo` Vim 交换文件
- `*~` 编辑器备份文件
- `.DS_Store` macOS 系统文件
- `Thumbs.db` Windows 缩略图缓存

### 5. 开发配置检查
- 检查 `config.py` 是否存在（不应打包）
- 检查 `.env` 是否存在（不应打包）
- 提示打包策略说明

## 使用方法

### 方法 1: 独立运行清理脚本

```bash
# 交互式运行（会提示确认）
python cleanup_before_packaging.py

# 自动运行（不提示确认）
python cleanup_before_packaging.py --auto
```

### 方法 2: 通过打包脚本运行

#### Windows (build_package.bat)

```batch
cd Pack\Pyinstaller
build_package.bat
```

在菜单中选择选项 4：
```
4. 清理缓存和临时文件 (推荐打包前执行)
```

#### Unix/Linux/macOS (build_package.sh)

```bash
cd Pack/Pyinstaller
./build_package.sh
```

在菜单中选择选项 4：
```
4. 清理缓存和临时文件 (推荐打包前执行)
```

## 清理报告

清理完成后，会在项目根目录生成 `CLEANUP_REPORT.md` 文件，包含：

- 清理项目数统计
- 释放空间大小
- 清理详情列表（前 50 项）
- 验证需求确认

示例报告：

```markdown
# 打包前清理报告

## 清理摘要

- **清理项目数**: 15
- **释放空间**: 25.43 MB

## 清理详情

已清理的文件和目录:

  - C:\Project\__pycache__
  - C:\Project\test.pyc
  - C:\Project\.ocr_cache
  - C:\Project\build
  - C:\Project\dist
  ...

## 验证需求

**需求 5.4, 5.5**: ✓ 已完成

- ✓ 清理 __pycache__ 目录
- ✓ 清理 .pyc 文件
- ✓ 清理 .db 缓存文件
- ✓ 清理构建产物
- ✓ 清理临时文件
```

## 推荐工作流

### 打包前清理流程

1. **开发完成后**
   ```bash
   # 提交代码到版本控制
   git add .
   git commit -m "完成功能开发"
   ```

2. **执行清理**
   ```bash
   # 运行清理脚本
   python cleanup_before_packaging.py --auto
   ```

3. **检查清理报告**
   ```bash
   # 查看清理报告
   cat CLEANUP_REPORT.md
   ```

4. **执行打包**
   ```bash
   # 运行打包脚本
   cd Pack/Pyinstaller
   ./build_package.sh  # 或 build_package.bat
   ```

5. **验证打包结果**
   ```bash
   # 检查打包体积
   du -sh dist/OCR-System/
   
   # 测试打包后的程序
   ./dist/OCR-System/OCR-System
   ```

## 注意事项

### 1. 虚拟环境保护

清理脚本会自动跳过以下目录：
- `venv/`
- `env/`
- `.venv/`
- `.git/`
- `portable_python/`
- `models/`

### 2. 开发配置文件

清理脚本会检查但不会删除以下文件：
- `config.py` - 开发环境配置
- `.env` - 环境变量

这些文件已在 `.gitignore` 中排除，不会被版本控制。
打包时只会包含 `config.py.example` 和 `.env.example`。

### 3. 模型文件保护

清理脚本不会删除 `models/` 目录下的任何文件，包括：
- OCR 引擎可执行文件
- 模型文件
- 配置文件

### 4. 安全性

- 清理操作不可逆，请确保重要文件已备份
- 建议在清理前提交代码到版本控制
- 清理脚本会跳过虚拟环境和关键目录

## 测试

运行测试以验证清理功能：

```bash
python test_cleanup_before_packaging.py
```

测试覆盖：
- ✓ 清理 __pycache__ 目录
- ✓ 清理 .pyc 文件
- ✓ 清理缓存数据库
- ✓ 清理构建产物
- ✓ 清理临时文件
- ✓ 生成清理报告
- ✓ 完整清理流程

## 验证需求

本清理工具满足以下需求：

- **需求 5.4**: ✓ 清理缓存和临时文件
  - 清理 __pycache__ 目录
  - 清理 .pyc 文件
  - 清理 .db 缓存文件
  - 清理临时文件

- **需求 5.5**: ✓ 清理构建产物
  - 清理 build/ 目录
  - 清理 dist/ 目录
  - 清理测试缓存
  - 清理覆盖率报告

## 故障排除

### 问题 1: 权限错误

**症状**: 无法删除某些文件或目录

**解决方案**:
```bash
# Windows: 以管理员身份运行
# Unix/Linux: 使用 sudo
sudo python cleanup_before_packaging.py --auto
```

### 问题 2: 清理脚本找不到

**症状**: `ModuleNotFoundError: No module named 'cleanup_before_packaging'`

**解决方案**:
```bash
# 确保在项目根目录运行
cd /path/to/OCR-System
python cleanup_before_packaging.py
```

### 问题 3: 清理后程序无法运行

**症状**: 清理后开发环境无法运行

**解决方案**:
```bash
# 重新生成配置文件
cp config.py.example config.py

# 重新初始化缓存
python qt_run.py
```

## 相关文件

- `cleanup_before_packaging.py` - 清理脚本主程序
- `test_cleanup_before_packaging.py` - 清理功能测试
- `Pack/Pyinstaller/build_package.bat` - Windows 打包脚本（集成清理）
- `Pack/Pyinstaller/build_package.sh` - Unix/Linux 打包脚本（集成清理）
- `CLEANUP_REPORT.md` - 清理报告（自动生成）

## 更新日志

### v1.0.0 (2024-11-29)
- ✓ 实现基础清理功能
- ✓ 集成到打包脚本
- ✓ 添加清理报告生成
- ✓ 添加测试覆盖
- ✓ 完善文档说明

---

*最后更新: 2024-11-29*
