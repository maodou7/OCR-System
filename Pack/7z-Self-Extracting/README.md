# 7-Zip 自解压程序制作工具

## 简介

本工具用于将 PyInstaller 打包好的 OCR System 应用程序制作成 Windows 自解压安装包（.exe）。用户只需双击运行即可自动解压安装，无需额外的解压软件。

## 目录结构

```
Pack/7z-Self-Extracting/
├── 7z.sfx              # 7-Zip 自解压模块
├── 7zr.exe             # 7-Zip 命令行工具
├── create_sfx.bat      # Windows 批处理脚本
├── create_sfx.sh       # Linux/macOS Shell 脚本
└── README.md           # 本文档
```

## 前置要求

### 1. 完成应用打包

在使用本工具之前，必须先使用 PyInstaller 打包应用程序：

```bash
# Windows
cd Pack\Pyinstaller
build_package.bat

# Linux/macOS
cd Pack/Pyinstaller
./build_package.sh
```

打包完成后，会在 `dist/` 目录生成以下内容之一：
- `dist/OCR-System/` - 文件夹模式（推荐）
- `dist/OCR-System.exe` - 单文件模式

### 2. 确保工具文件完整

确保以下文件存在：
- `7z.sfx` - 自解压模块
- `7zr.exe` - 7-Zip 压缩工具

## ✨ 新功能 (v1.1)

### 智能压缩级别选择

脚本现在支持：
- 🎯 **4 种压缩级别** - 从快速到最高，满足不同需求
- ⏱️ **智能时间预估** - 根据文件大小和 CPU 性能自动计算
- 📊 **实时统计** - 显示压缩率、实际用时等详细信息
- 🖥️ **CPU 检测** - 自动检测 CPU 核心数优化预估

详细说明请查看 [压缩级别选择指南](COMPRESSION_GUIDE.md)

## 使用方法

### Windows 系统

1. **打开命令提示符**
   ```cmd
   cd Pack\7z-Self-Extracting
   ```

2. **运行脚本**
   ```cmd
   create_sfx.bat
   ```

3. **按照提示操作**
   - 选择要打包的目录（文件夹模式或单文件模式）
   - 等待处理完成

4. **获取输出文件**
   - 输出文件：`OCR-System-v1.4.1-Setup.exe`
   - 位置：`Pack/7z-Self-Extracting/` 目录

### Linux/macOS 系统

1. **打开终端**
   ```bash
   cd Pack/7z-Self-Extracting
   ```

2. **添加执行权限（首次运行）**
   ```bash
   chmod +x create_sfx.sh
   ```

3. **运行脚本**
   ```bash
   ./create_sfx.sh
   ```

4. **按照提示操作**
   - 选择要打包的目录
   - 等待处理完成

5. **获取输出文件**
   - 输出文件：`OCR-System-v1.4.1-Setup.exe`
   - 位置：`Pack/7z-Self-Extracting/` 目录

> **注意**：Linux/macOS 需要安装 Wine 来运行 7zr.exe

## 脚本功能

### 自动化流程

脚本会自动执行以下步骤：

1. **环境检查**
   - 检查 7z.sfx 和 7zr.exe 是否存在
   - 检查 dist 目录是否存在
   - 验证打包输出是否可用

2. **源目录选择**
   - 自动检测可用的打包输出
   - 提供交互式选择菜单

3. **文件准备**
   - 创建临时目录
   - 复制应用程序文件
   - 添加配置文件示例（config.py.example, .env.example）
   - 生成用户说明文档（README.txt）

4. **创建压缩包**
   - 使用最高压缩率（-mx9）
   - 生成 .7z 压缩包

5. **生成自解压程序**
   - 创建自解压配置
   - 合并 sfx 模块、配置和压缩包
   - 生成最终的 .exe 文件

6. **清理临时文件**
   - 删除临时目录
   - 删除中间文件
   - 保留最终输出

### 自解压配置

生成的自解压程序具有以下特性：

- **友好的安装界面**
  - 欢迎提示
  - 进度显示
  - 路径选择

- **默认安装路径**
  - `C:\Program Files\OCR-System`
  - 用户可自定义

- **智能覆盖处理**
  - 提示用户确认覆盖
  - 保护现有文件

## 输出文件说明

### 文件命名

```
OCR-System-v1.4.1-Setup.exe
```

格式：`<应用名称>-<版本号>-Setup.exe`

### 文件大小

| 打包模式 | 压缩前 | 压缩后 | 压缩率 |
|---------|--------|--------|--------|
| 文件夹模式 | ~800 MB | ~400 MB | ~50% |
| 单文件模式 | ~700 MB | ~350 MB | ~50% |

### 包含内容

自解压程序包含以下文件：

```
OCR-System/
├── OCR-System.exe          # 主程序
├── config.py.example       # 配置文件示例
├── .env.example            # 环境变量示例
├── README.txt              # 用户说明文档
├── models/                 # OCR 引擎和模型
├── portable_python/        # Python 运行时（可选）
└── ... (其他依赖文件)
```

## 用户使用流程

### 安装步骤

1. **下载自解压程序**
   - 获取 `OCR-System-v1.4.1-Setup.exe`

2. **运行安装程序**
   - 双击 .exe 文件
   - 可能触发 Windows SmartScreen 警告（点击"更多信息" -> "仍要运行"）

3. **选择安装路径**
   - 默认：`C:\Program Files\OCR-System`
   - 或自定义路径

4. **等待解压完成**
   - 自动解压所有文件
   - 显示进度条

5. **启动程序**
   - 进入安装目录
   - 双击 `OCR-System.exe`

### 首次运行

首次运行时，程序会自动：
1. 检查配置文件
2. 从 `config.py.example` 生成 `config.py`
3. 初始化 OCR 引擎
4. 显示主界面

## 高级配置

### 自定义安装配置

编辑脚本中的配置部分可自定义：

**Windows (create_sfx.bat):**
```batch
set "APP_NAME=OCR-System"
set "APP_VERSION=v1.4.1"
```

**Linux/macOS (create_sfx.sh):**
```bash
APP_NAME="OCR-System"
APP_VERSION="v1.4.1"
```

### 修改自解压配置

在脚本中找到配置文件生成部分，可修改：

```
Title="OCR System v1.4.1 安装程序"
BeginPrompt="欢迎安装 OCR System v1.4.1..."
InstallPath="C:\\Program Files\\OCR-System"
```

可配置项：
- `Title` - 安装程序标题
- `BeginPrompt` - 欢迎提示文本
- `ExtractDialogText` - 解压进度文本
- `ExtractPathText` - 路径选择标签
- `InstallPath` - 默认安装路径
- `GUIFlags` - 界面标志（控制显示元素）
- `GUIMode` - 界面模式（1=GUI, 2=静默）
- `OverwriteMode` - 覆盖模式（0=询问, 1=覆盖, 2=跳过）

### GUIFlags 说明

GUIFlags 是一个位标志组合：

| 标志 | 值 | 说明 |
|------|-----|------|
| 无标题栏 | 1 | 移除标题栏 |
| 无进度条 | 2 | 隐藏进度条 |
| 无路径选择 | 4 | 禁用路径选择 |
| 显示开始提示 | 8 | 显示欢迎对话框 |
| 显示完成提示 | 16 | 显示完成对话框 |
| 显示错误提示 | 32 | 显示错误对话框 |
| 显示取消按钮 | 64 | 显示取消按钮 |
| 自动关闭 | 128 | 完成后自动关闭 |
| 显示路径 | 256 | 显示解压路径 |
| 无覆盖提示 | 512 | 不提示覆盖 |
| 创建快捷方式 | 4096 | 创建桌面快捷方式 |

当前配置：`8+32+64+256+4096` = 4456
- 显示开始提示
- 显示错误提示
- 显示取消按钮
- 显示路径
- 创建快捷方式

## 代码签名（推荐）

为避免 Windows SmartScreen 警告，建议对生成的 .exe 进行代码签名。

### 获取代码签名证书

1. **购买证书**
   - DigiCert
   - Sectigo (原 Comodo)
   - GlobalSign

2. **申请流程**
   - 提供公司信息
   - 验证身份
   - 获取证书文件（.pfx 或 .p12）

### 签名步骤

**使用 SignTool (Windows SDK):**

```cmd
signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com OCR-System-v1.4.1-Setup.exe
```

参数说明：
- `/f` - 证书文件路径
- `/p` - 证书密码
- `/t` - 时间戳服务器（确保签名长期有效）

**验证签名:**

```cmd
signtool verify /pa OCR-System-v1.4.1-Setup.exe
```

## 常见问题

### Q1: 提示"找不到 7zr.exe"？

**A:** 确保 `7zr.exe` 文件存在于 `Pack/7z-Self-Extracting/` 目录。

如果缺失，可以：
1. 从 [7-Zip 官网](https://www.7-zip.org/) 下载
2. 解压后复制 `7zr.exe` 到本目录

### Q2: Linux 提示"wine: command not found"？

**A:** 需要安装 Wine：

```bash
# Ubuntu/Debian
sudo apt-get install wine

# Fedora
sudo dnf install wine

# macOS
brew install wine-stable
```

### Q3: 生成的 .exe 文件过大？

**A:** 
- 使用文件夹模式打包（比单文件模式小）
- 移除不必要的文件（如 portable_python）
- 已使用最高压缩率（-mx9）

### Q4: 用户运行时提示 SmartScreen 警告？

**A:** 
- **临时方案**：点击"更多信息" -> "仍要运行"
- **永久方案**：购买代码签名证书并签名

### Q5: 如何修改默认安装路径？

**A:** 编辑脚本中的配置：

```
InstallPath="C:\\Program Files\\OCR-System"
```

改为你想要的路径，例如：

```
InstallPath="%USERPROFILE%\\OCR-System"
```

### Q6: 可以静默安装吗？

**A:** 可以。修改配置：

```
GUIMode="2"
```

然后用户可以使用命令行参数：

```cmd
OCR-System-v1.4.1-Setup.exe -o"C:\CustomPath" -y
```

参数说明：
- `-o` - 指定输出路径
- `-y` - 自动确认所有提示

### Q7: 如何添加安装后自动运行？

**A:** 在配置文件中添加：

```
RunProgram="OCR-System.exe"
```

### Q8: 压缩时间太长？

**A:** 
- 当前使用最高压缩率（-mx9）
- 可以降低压缩率以加快速度：
  - `-mx9` - 最高（最慢）
  - `-mx7` - 高（推荐）
  - `-mx5` - 中等（快速）
  - `-mx3` - 低（最快）

修改脚本中的压缩命令：

```bash
# 从
7zr.exe a -mx9 archive.7z *

# 改为
7zr.exe a -mx7 archive.7z *
```

## 分发建议

### 文件命名

使用清晰的命名格式：

```
OCR-System-v1.4.1-Setup-Win64.exe
OCR-System-v1.4.1-Portable-Win64.7z
```

### 提供校验和

生成 SHA256 校验和：

**Windows:**
```cmd
certutil -hashfile OCR-System-v1.4.1-Setup.exe SHA256
```

**Linux/macOS:**
```bash
sha256sum OCR-System-v1.4.1-Setup.exe
```

### 发布说明

在 GitHub Release 或下载页面提供：

```markdown
## OCR System v1.4.1

### 下载

- [OCR-System-v1.4.1-Setup.exe](link) (400 MB)
  - SHA256: `abc123...`
  - 自解压安装包，双击运行即可

### 系统要求

- Windows 7/8/10/11 (64位)
- 2GB RAM
- 1GB 磁盘空间

### 安装说明

1. 下载 .exe 文件
2. 双击运行
3. 选择安装路径
4. 等待解压完成
5. 启动程序

### 首次运行可能触发 SmartScreen 警告

点击"更多信息" -> "仍要运行"即可
```

## 技术细节

### 7-Zip SFX 模块

`7z.sfx` 是 7-Zip 提供的自解压模块，特点：

- 体积小（~160 KB）
- 支持 GUI 界面
- 支持配置文件
- 支持多种压缩格式
- 开源免费

### 文件合并原理

自解压程序由三部分组成：

```
[7z.sfx 模块] + [配置文件] + [7z 压缩包] = [自解压程序.exe]
```

运行时：
1. 读取配置
2. 显示安装界面
3. 解压压缩包到指定目录
4. 执行后续操作（如创建快捷方式）

### 压缩算法

使用 LZMA2 算法：
- 压缩率高（通常 40-60%）
- 解压速度快
- 内存占用适中

## 相关文档

- [PyInstaller 打包文档](../Pyinstaller/README.md)
- [7-Zip 官方文档](https://www.7-zip.org/sdk.html)
- [7-Zip SFX 配置说明](https://sevenzip.osdn.jp/chm/cmdline/switches/sfx.htm)

## 更新日志

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0 | 2025-11-28 | 初始版本，支持 Windows 和 Linux/macOS |

## 许可证

本工具遵循项目的 MIT 许可证。

7-Zip 及其 SFX 模块采用 LGPL 许可证。

## 联系方式

- GitHub: [@maodou7](https://github.com/maodou7)
- 项目地址: [OCR-System](https://github.com/maodou7/OCR-System)
- 问题反馈: [Issues](https://github.com/maodou7/OCR-System/issues)

---

**感谢使用 OCR System 自解压制作工具！** 🎉
