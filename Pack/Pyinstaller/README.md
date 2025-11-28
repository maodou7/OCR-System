# OCR System - PyInstaller 打包文档

## 目录

- [简介](#简介)
- [快速开始](#快速开始)
- [运行打包脚本](#运行打包脚本)
- [构建模式选择](#构建模式选择)
- [配置管理](#配置管理)
- [常见问题排查](#常见问题排查)
- [分发方法](#分发方法)
- [打包大小说明](#打包大小说明)
- [高级配置](#高级配置)

---

## 简介

本文档介绍如何使用 PyInstaller 将 OCR 批量识别系统打包成独立的可执行文件。打包后的应用可以在没有 Python 环境的计算机上直接运行。

**项目信息**:
- **应用名称**: OCR 批量识别系统 (Qt版本)
- **版本**: v1.4.1
- **打包工具**: PyInstaller
- **支持平台**: Windows (主要), Linux/macOS (兼容)

**打包脚本**:
- `build_package.bat` - Windows CMD 脚本
- `build_package.sh` - Unix/Linux/macOS/Git Bash 脚本

---

## 快速开始

### 前置要求

1. **Python 环境**: Python 3.11 或更高版本
2. **PyInstaller**: 安装 PyInstaller 打包工具
3. **项目依赖**: 安装所有项目依赖包

### 安装 PyInstaller

```bash
# 使用 pip 安装
pip install pyinstaller

# 或使用项目中的 portable_python
.\portable_python\python.exe -m pip install pyinstaller
```

### 一键打包

**Windows 用户**:
```cmd
cd Pack\Pyinstaller
build_package.bat
```

**Unix/Linux/macOS/Git Bash 用户**:
```bash
cd Pack/Pyinstaller
chmod +x build_package.sh
./build_package.sh
```


---

## 运行打包脚本

### Windows 系统

1. **打开命令提示符 (CMD)**
   - 按 `Win + R`，输入 `cmd`，按回车
   - 或在开始菜单搜索"命令提示符"

2. **导航到打包目录**
   ```cmd
   cd /d C:\path\to\your\project\Pack\Pyinstaller
   ```

3. **运行打包脚本**
   ```cmd
   build_package.bat
   ```

4. **选择打包模式**
   - 输入 `1` - 单文件模式
   - 输入 `2` - 文件夹模式
   - 输入 `3` - 清理构建文件
   - 输入 `4` - 退出

### Unix/Linux/macOS 系统

1. **打开终端**
   - Linux: `Ctrl + Alt + T`
   - macOS: `Cmd + Space`，输入 "Terminal"

2. **导航到打包目录**
   ```bash
   cd /path/to/your/project/Pack/Pyinstaller
   ```

3. **添加执行权限（首次运行）**
   ```bash
   chmod +x build_package.sh
   ```

4. **运行打包脚本**
   ```bash
   ./build_package.sh
   ```

5. **选择打包模式**
   - 输入 `1` - 单文件模式
   - 输入 `2` - 文件夹模式
   - 输入 `3` - 清理构建文件
   - 输入 `4` - 退出

### Git Bash (Windows)

如果你在 Windows 上使用 Git Bash:

```bash
cd /c/path/to/your/project/Pack/Pyinstaller
chmod +x build_package.sh
./build_package.sh
```


---

## 构建模式选择

PyInstaller 提供两种主要的打包模式，各有优缺点。

### 单文件模式 (One-file Mode)

**特点**:
- 生成单个可执行文件 (`.exe` 或无扩展名)
- 所有依赖和资源打包在一个文件中
- 首次启动时解压到临时目录

**优点**:
- ✅ 分发简单 - 只需传输一个文件
- ✅ 看起来更专业
- ✅ 用户不会误删依赖文件

**缺点**:
- ❌ 文件体积较大 (~800MB - 1.5GB)
- ❌ 启动速度较慢（需要解压）
- ❌ 每次运行都会解压到临时目录
- ❌ 占用更多磁盘空间（临时文件）

**适用场景**:
- 需要快速分发给非技术用户
- 不在意启动速度
- 磁盘空间充足

**输出位置**: `dist/OCR-System.exe` (Windows) 或 `dist/OCR-System` (Unix)

### 文件夹模式 (One-folder Mode)

**特点**:
- 生成一个包含可执行文件和所有依赖的文件夹
- 所有文件已解压，无需临时目录

**优点**:
- ✅ 启动速度快（无需解压）
- ✅ 总体积更小 (~800MB - 1GB)
- ✅ 不占用临时目录空间
- ✅ 便于调试和查看依赖

**缺点**:
- ❌ 分发时需要打包整个文件夹
- ❌ 用户可能误删依赖文件
- ❌ 看起来不够"专业"

**适用场景**:
- 需要快速启动
- 磁盘空间有限
- 开发和测试阶段
- **推荐用于正式分发**

**输出位置**: `dist/OCR-System/` 文件夹

### 推荐选择

| 使用场景 | 推荐模式 | 原因 |
|---------|---------|------|
| 正式发布 | **文件夹模式** | 启动快，体积小，用户体验好 |
| 快速测试 | 文件夹模式 | 构建快，便于调试 |
| 演示/试用 | 单文件模式 | 分发方便 |
| 企业内部 | 文件夹模式 | 便于维护和更新 |

**建议**: 对于大多数用户，推荐使用**文件夹模式**，然后使用 7-Zip 或 WinRAR 压缩成 `.zip` 或 `.7z` 文件进行分发。


---

## 配置管理

OCR System 支持外部配置文件，允许用户在不重新打包的情况下修改应用设置。

### 配置文件位置

打包后的应用会在以下位置查找配置文件:

- **单文件模式**: 与 `.exe` 文件同目录下的 `config.py`
- **文件夹模式**: `OCR-System/` 文件夹根目录下的 `config.py`

### 首次运行

首次运行打包后的应用时，程序会自动执行以下操作:

1. 检查 `config.py` 是否存在
2. 如果不存在，从 `config.py.example` 复制生成 `config.py`
3. 加载配置并启动应用

### 修改配置

**步骤**:

1. **找到配置文件**
   - 导航到可执行文件所在目录
   - 找到 `config.py` 文件

2. **编辑配置文件**
   - 使用文本编辑器打开 `config.py`
   - 推荐使用: Notepad++, VS Code, Sublime Text
   - 不推荐使用: Windows 记事本（可能有编码问题）

3. **修改配置项**
   ```python
   # 示例配置项
   
   # OCR 引擎选择
   DEFAULT_OCR_ENGINE = "paddle"  # 可选: "paddle", "rapid", "aliyun", "deepseek"
   
   # 阿里云 OCR 配置
   ALIYUN_ACCESS_KEY_ID = "your_access_key_id"
   ALIYUN_ACCESS_KEY_SECRET = "your_access_key_secret"
   
   # DeepSeek OCR 配置
   DEEPSEEK_API_KEY = "your_api_key"
   DEEPSEEK_BASE_URL = "https://api.deepseek.com"
   
   # 缓存设置
   ENABLE_CACHE = True
   CACHE_EXPIRY_DAYS = 30
   
   # 界面设置
   DEFAULT_LANGUAGE = "zh_CN"  # 可选: "zh_CN", "en_US"
   THEME = "light"  # 可选: "light", "dark"
   ```

4. **保存并重启应用**
   - 保存 `config.py` 文件
   - 关闭并重新启动 OCR System
   - 新配置将自动生效

### 配置文件说明

| 配置项 | 说明 | 默认值 |
|-------|------|--------|
| `DEFAULT_OCR_ENGINE` | 默认 OCR 引擎 | `"paddle"` |
| `ALIYUN_ACCESS_KEY_ID` | 阿里云访问密钥 ID | `""` |
| `ALIYUN_ACCESS_KEY_SECRET` | 阿里云访问密钥 Secret | `""` |
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥 | `""` |
| `ENABLE_CACHE` | 是否启用缓存 | `True` |
| `CACHE_EXPIRY_DAYS` | 缓存过期天数 | `30` |

### 重置配置

如果配置文件损坏或需要重置:

1. 删除 `config.py` 文件
2. 重新启动应用
3. 程序会自动从 `config.py.example` 重新生成默认配置

### 注意事项

⚠️ **重要提示**:
- 不要修改 `config.py.example` 文件（这是模板文件）
- 配置文件使用 Python 语法，注意缩进和引号
- API 密钥等敏感信息不要分享给他人
- 修改配置后必须重启应用才能生效


---

## 常见问题排查

### 问题 1: PyInstaller 未安装

**症状**:
```
错误: PyInstaller 未安装
'pyinstaller' 不是内部或外部命令，也不是可运行的程序
```

**解决方法**:

1. **检查 Python 是否安装**
   ```bash
   python --version
   ```

2. **安装 PyInstaller**
   ```bash
   pip install pyinstaller
   ```

3. **验证安装**
   ```bash
   pyinstaller --version
   ```

4. **使用项目中的 portable_python**
   ```bash
   .\portable_python\python.exe -m pip install pyinstaller
   ```

### 问题 2: 缺少必需的源文件

**症状**:
```
错误: 缺少必需的源文件:
  - qt_run.py
  - qt_main.py
  - config.py
```

**解决方法**:

1. **确认当前目录**
   - 确保你在项目根目录的 `Pack/Pyinstaller/` 子目录中

2. **检查文件是否存在**
   ```bash
   # Windows
   dir ..\..\qt_run.py
   
   # Unix/Linux
   ls ../../qt_run.py
   ```

3. **从 Git 重新克隆项目**
   ```bash
   git clone <repository_url>
   cd <project_directory>
   ```

### 问题 3: 构建失败 - 模块导入错误

**症状**:
```
ModuleNotFoundError: No module named 'PySide6'
ModuleNotFoundError: No module named 'PIL'
```

**解决方法**:

1. **安装所有依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **检查依赖是否安装**
   ```bash
   pip list | grep PySide6
   pip list | grep Pillow
   ```

3. **使用虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Unix
   venv\Scripts\activate     # Windows
   pip install -r requirements.txt
   ```

### 问题 4: 打包后无法找到资源文件

**症状**:
- 打包后的应用启动失败
- 提示找不到 `models/` 文件夹
- OCR 引擎无法初始化

**解决方法**:

1. **检查 models 文件夹是否存在**
   ```bash
   ls models/PaddleOCR-json/
   ls models/RapidOCR-json/
   ```

2. **确认 spec 文件配置正确**
   - 打开 `ocr_system.spec`
   - 检查 `datas` 配置是否包含 `models` 文件夹

3. **重新构建**
   ```bash
   # 清理旧构建
   rm -rf build dist
   
   # 重新构建
   pyinstaller ocr_system.spec
   ```

### 问题 5: 打包后体积过大

**症状**:
- 单文件模式生成的 `.exe` 超过 1.5GB
- 文件夹模式生成的文件夹超过 1GB

**解决方法**:

1. **不要打包 portable_python 文件夹**
   - 编辑 `ocr_system.spec`
   - 注释掉或删除 `portable_python` 的 `datas` 配置
   ```python
   datas = [
       ('models', 'models'),
       # ('portable_python', 'portable_python'),  # 注释掉这行
       ('config.py.example', '.'),
   ]
   ```

2. **使用文件夹模式而不是单文件模式**
   - 文件夹模式通常比单文件模式小 100-200MB

3. **排除不必要的包**
   - 检查 `excludes` 列表是否包含所有不需要的包

### 问题 6: 打包后启动缓慢

**症状**:
- 双击可执行文件后需要等待 10-30 秒才能启动
- 单文件模式特别明显

**解决方法**:

1. **使用文件夹模式**
   - 文件夹模式启动速度比单文件模式快 5-10 倍

2. **使用 SSD 硬盘**
   - 将应用安装在 SSD 而不是 HDD

3. **关闭杀毒软件实时扫描**
   - 某些杀毒软件会扫描可执行文件，导致启动缓慢
   - 将应用添加到杀毒软件白名单

### 问题 7: Windows SmartScreen 警告

**症状**:
```
Windows 已保护你的电脑
Microsoft Defender SmartScreen 已阻止启动一个未识别的应用
```

**解决方法**:

1. **临时绕过（用户端）**
   - 点击"更多信息"
   - 点击"仍要运行"

2. **代码签名（开发者端）**
   - 购买代码签名证书
   - 使用 `signtool` 对 `.exe` 进行签名
   ```bash
   signtool sign /f certificate.pfx /p password /t http://timestamp.digicert.com OCR-System.exe
   ```

3. **建立信誉**
   - 让更多用户下载和运行应用
   - SmartScreen 会逐渐建立信誉

### 问题 8: 杀毒软件误报

**症状**:
- 杀毒软件将打包的 `.exe` 识别为病毒
- 文件被自动删除或隔离

**解决方法**:

1. **添加到白名单**
   - 将应用添加到杀毒软件的信任列表

2. **不使用 UPX 压缩**
   - 编辑 `ocr_system.spec`
   - 将 `upx=True` 改为 `upx=False`

3. **提交误报**
   - 向杀毒软件厂商提交误报申诉
   - 提供应用的详细信息和源代码

### 问题 9: 配置文件修改后不生效

**症状**:
- 修改了 `config.py` 但应用仍使用旧配置
- API 密钥更新后仍然无法连接

**解决方法**:

1. **确认修改了正确的文件**
   - 确保修改的是可执行文件目录下的 `config.py`
   - 不是项目源代码中的 `config.py`

2. **检查文件保存**
   - 确保文件已保存（Ctrl+S）
   - 关闭文本编辑器

3. **完全重启应用**
   - 关闭所有 OCR System 进程
   - 重新启动应用

4. **检查语法错误**
   - Python 配置文件语法错误会导致加载失败
   - 检查引号、逗号、缩进是否正确

### 问题 10: Linux/macOS 权限问题

**症状**:
```
Permission denied: ./OCR-System
bash: ./OCR-System: Permission denied
```

**解决方法**:

1. **添加执行权限**
   ```bash
   chmod +x OCR-System
   ```

2. **检查文件所有者**
   ```bash
   ls -l OCR-System
   ```

3. **使用 sudo（不推荐）**
   ```bash
   sudo ./OCR-System
   ```


---

## 分发方法

打包完成后，你可以通过多种方式分发应用给最终用户。

### 方法 1: 直接下载（推荐）

**适用场景**: 个人项目、小团队、开源软件

**步骤**:

1. **压缩打包文件**
   ```bash
   # Windows - 使用 7-Zip
   7z a OCR-System-v1.4.1-win64.7z dist/OCR-System/
   
   # Unix/Linux - 使用 tar
   tar -czf OCR-System-v1.4.1-linux64.tar.gz dist/OCR-System/
   
   # macOS - 使用 zip
   zip -r OCR-System-v1.4.1-macos.zip dist/OCR-System/
   ```

2. **上传到文件托管服务**
   - **GitHub Releases**: 适合开源项目
   - **百度网盘**: 适合国内用户
   - **Google Drive**: 适合国际用户
   - **OneDrive**: 微软用户
   - **自建服务器**: 企业用户

3. **提供下载链接**
   - 在项目 README 中添加下载链接
   - 提供多个镜像下载地址
   - 包含 SHA256 校验和

**示例 README 下载部分**:
```markdown
## 下载

### Windows 版本
- [OCR-System-v1.4.1-win64.7z](https://github.com/user/repo/releases/download/v1.4.1/OCR-System-v1.4.1-win64.7z) (800 MB)
- SHA256: `abc123...`

### Linux 版本
- [OCR-System-v1.4.1-linux64.tar.gz](https://github.com/user/repo/releases/download/v1.4.1/OCR-System-v1.4.1-linux64.tar.gz) (750 MB)
- SHA256: `def456...`

### 使用方法
1. 下载对应平台的压缩包
2. 解压到任意目录
3. 运行 `OCR-System.exe` (Windows) 或 `./OCR-System` (Linux)
```

### 方法 2: 安装程序

**适用场景**: 商业软件、企业应用、需要专业外观

**Windows - 使用 Inno Setup**:

1. **安装 Inno Setup**
   - 下载: https://jrsoftware.org/isdl.php
   - 安装到系统

2. **创建安装脚本** (`installer.iss`):
   ```ini
   [Setup]
   AppName=OCR System
   AppVersion=1.4.1
   DefaultDirName={pf}\OCR System
   DefaultGroupName=OCR System
   OutputDir=installer_output
   OutputBaseFilename=OCR-System-Setup-v1.4.1
   Compression=lzma2
   SolidCompression=yes
   
   [Files]
   Source: "dist\OCR-System\*"; DestDir: "{app}"; Flags: recursesubdirs
   
   [Icons]
   Name: "{group}\OCR System"; Filename: "{app}\OCR-System.exe"
   Name: "{commondesktop}\OCR System"; Filename: "{app}\OCR-System.exe"
   
   [Run]
   Filename: "{app}\OCR-System.exe"; Description: "启动 OCR System"; Flags: postinstall nowait skipifsilent
   ```

3. **编译安装程序**
   - 右键点击 `installer.iss`
   - 选择 "Compile"
   - 生成 `OCR-System-Setup-v1.4.1.exe`

**Windows - 使用 NSIS**:

1. **安装 NSIS**
   - 下载: https://nsis.sourceforge.io/
   - 安装到系统

2. **创建安装脚本** (`installer.nsi`):
   ```nsis
   !define APP_NAME "OCR System"
   !define APP_VERSION "1.4.1"
   
   Name "${APP_NAME}"
   OutFile "OCR-System-Setup-v${APP_VERSION}.exe"
   InstallDir "$PROGRAMFILES\${APP_NAME}"
   
   Section "Install"
     SetOutPath "$INSTDIR"
     File /r "dist\OCR-System\*.*"
     CreateShortcut "$DESKTOP\${APP_NAME}.lnk" "$INSTDIR\OCR-System.exe"
   SectionEnd
   ```

3. **编译安装程序**
   ```bash
   makensis installer.nsi
   ```

### 方法 3: 便携版（推荐）

**适用场景**: 不需要安装、U盘运行、绿色软件

**步骤**:

1. **准备便携版文件夹**
   ```
   OCR-System-Portable/
   ├── OCR-System.exe
   ├── config.py.example
   ├── README.txt
   ├── models/
   ├── portable_python/
   └── ... (其他依赖文件)
   ```

2. **创建使用说明** (`README.txt`):
   ```
   OCR System 便携版 v1.4.1
   
   使用方法:
   1. 解压到任意目录
   2. 双击 OCR-System.exe 启动
   3. 首次运行会自动创建 config.py 配置文件
   
   配置方法:
   - 编辑 config.py 文件修改设置
   - 重启应用使配置生效
   
   注意事项:
   - 不要删除 models 文件夹
   - 不要删除 portable_python 文件夹
   - 可以将整个文件夹复制到 U 盘使用
   ```

3. **压缩为便携版**
   ```bash
   # 使用 7-Zip (推荐)
   7z a -mx9 OCR-System-v1.4.1-Portable.7z OCR-System-Portable/
   
   # 使用 WinRAR
   rar a -m5 OCR-System-v1.4.1-Portable.rar OCR-System-Portable/
   
   # 使用 zip
   zip -9 -r OCR-System-v1.4.1-Portable.zip OCR-System-Portable/
   ```

### 方法 4: Docker 容器（高级）

**适用场景**: 服务器部署、云环境、容器化应用

**步骤**:

1. **创建 Dockerfile**:
   ```dockerfile
   FROM python:3.11-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt
   
   COPY . .
   
   CMD ["python", "qt_run.py"]
   ```

2. **构建 Docker 镜像**:
   ```bash
   docker build -t ocr-system:v1.4.1 .
   ```

3. **运行容器**:
   ```bash
   docker run -d -p 8080:8080 ocr-system:v1.4.1
   ```

### 分发清单

在分发前，确保包含以下内容:

- [ ] 可执行文件或安装程序
- [ ] README 文档（使用说明）
- [ ] LICENSE 文件（软件许可证）
- [ ] CHANGELOG 文件（更新日志）
- [ ] config.py.example（配置模板）
- [ ] 必要的数据文件（models 文件夹）
- [ ] 校验和文件（SHA256）

### 版本命名规范

推荐使用以下命名格式:

```
<应用名称>-v<版本号>-<平台>-<架构>.<扩展名>

示例:
- OCR-System-v1.4.1-win64.7z
- OCR-System-v1.4.1-linux64.tar.gz
- OCR-System-v1.4.1-macos-arm64.zip
- OCR-System-Setup-v1.4.1.exe (安装程序)
- OCR-System-v1.4.1-Portable.7z (便携版)
```


---

## 打包大小说明

### 预期打包大小

| 打包模式 | 预期大小 | 说明 |
|---------|---------|------|
| **单文件模式（含 portable_python）** | ~1.5 GB | 包含完整 Python 环境 |
| **单文件模式（不含 portable_python）** | ~700 MB | **推荐方式** |
| **文件夹模式（不含 portable_python）** | ~800 MB | 未压缩，启动最快 |
| **文件夹模式（压缩后）** | ~400-500 MB | 使用 7-Zip 压缩 |

### 大小分解

打包后的应用主要由以下部分组成:

| 组件 | 大小 | 说明 |
|------|------|------|
| **Python 运行时** | ~50 MB | Python 解释器和标准库 |
| **PySide6 (Qt)** | ~150 MB | Qt 图形界面框架 |
| **models/ 文件夹** | ~562 MB | OCR 引擎和模型文件 |
| **其他依赖** | ~50 MB | PIL, openpyxl, PyMuPDF 等 |
| **portable_python/** | ~870 MB | 完整 Python 环境（可选） |
| **总计（不含 portable_python）** | ~812 MB | 推荐配置 |
| **总计（含 portable_python）** | ~1682 MB | 完整配置 |

### models/ 文件夹详细大小

| 子文件夹 | 大小 | 说明 |
|---------|------|------|
| **PaddleOCR-json/** | ~350 MB | PaddleOCR C++ 引擎 |
| **RapidOCR-json/** | ~180 MB | RapidOCR C++ 引擎 |
| **cpp_engine/** | ~5 MB | 缓存引擎源代码 |
| **ocr_cache.dll** | ~2 MB | 缓存引擎库 (Windows) |
| **libocr_cache.so** | ~2 MB | 缓存引擎库 (Linux) |
| **其他文件** | ~23 MB | README, 压缩包等 |
| **总计** | ~562 MB | |

### 体积优化建议

#### 1. 不打包 portable_python 文件夹（推荐）

**节省空间**: ~870 MB

**方法**:
- 编辑 `ocr_system.spec` 文件
- 注释掉或删除 `portable_python` 的 `datas` 配置

```python
datas = [
    ('models', 'models'),
    # ('portable_python', 'portable_python'),  # 注释掉这行
    ('config.py.example', '.'),
]
```

**影响**: 无影响，PyInstaller 会自动收集必需的 Python 运行时

#### 2. 排除不必要的 Python 包

**节省空间**: ~340 MB

**方法**:
- 在 `ocr_system.spec` 中添加 `excludes` 列表

```python
excludes = [
    'tkinter',      # ~10 MB
    'matplotlib',   # ~50 MB
    'scipy',        # ~80 MB
    'pandas',       # ~100 MB
    'IPython',      # ~30 MB
    'jupyter',      # ~50 MB
    'pytest',       # ~20 MB
]
```

#### 3. 使用文件夹模式

**节省空间**: ~100-200 MB

**原因**: 文件夹模式不需要额外的压缩和解压开销

#### 4. 压缩分发包

**节省空间**: ~50%

**方法**:
```bash
# 使用 7-Zip 最高压缩率
7z a -mx9 OCR-System.7z dist/OCR-System/

# 使用 WinRAR 最佳压缩
rar a -m5 OCR-System.rar dist/OCR-System/
```

**压缩效果**:
- 原始大小: ~800 MB
- 7-Zip 压缩后: ~400-450 MB
- WinRAR 压缩后: ~420-480 MB
- ZIP 压缩后: ~500-550 MB

#### 5. 移除不需要的 OCR 引擎

**节省空间**: 根据需要

如果你只使用某一个 OCR 引擎，可以移除其他引擎:

| 移除引擎 | 节省空间 |
|---------|---------|
| PaddleOCR-json | ~350 MB |
| RapidOCR-json | ~180 MB |

**方法**:
1. 删除 `models/` 文件夹中不需要的引擎
2. 重新打包

**注意**: 确保至少保留一个本地 OCR 引擎

#### 6. 使用 UPX 压缩可执行文件

**节省空间**: ~20-30%

**方法**:
- 在 `ocr_system.spec` 中设置 `upx=True`

```python
exe = EXE(
    pyz,
    a.scripts,
    upx=True,  # 启用 UPX 压缩
    ...
)
```

**注意**: UPX 压缩可能导致:
- 杀毒软件误报
- 启动速度略微变慢
- 某些系统不兼容

### 优化后的预期大小

应用所有优化建议后:

| 配置 | 原始大小 | 优化后大小 | 节省 |
|------|---------|-----------|------|
| 单文件模式 | ~1.5 GB | ~500 MB | ~1 GB |
| 文件夹模式 | ~800 MB | ~400 MB | ~400 MB |
| 文件夹模式（压缩） | ~800 MB | ~200 MB | ~600 MB |

### 大小对比

与其他打包方案对比:

| 打包方案 | 大小 | 优点 | 缺点 |
|---------|------|------|------|
| **PyInstaller (优化后)** | ~400 MB | 简单、快速 | 体积较大 |
| **Nuitka** | ~300 MB | 体积小、速度快 | 编译慢 |
| **cx_Freeze** | ~500 MB | 跨平台 | 配置复杂 |
| **py2exe** | ~450 MB | Windows 专用 | 仅支持 Windows |

### 大小优化总结

**推荐配置**:
1. ✅ 不打包 `portable_python/` 文件夹
2. ✅ 排除不必要的 Python 包
3. ✅ 使用文件夹模式
4. ✅ 使用 7-Zip 压缩分发
5. ⚠️ 谨慎使用 UPX 压缩（可能误报）

**最终效果**:
- 打包后大小: ~400 MB
- 压缩后大小: ~200 MB
- 下载时间: 2-5 分钟（100 Mbps 网络）


---

## 高级配置

### 自定义 spec 文件

如果你需要更精细的控制，可以直接编辑 `ocr_system.spec` 文件。

#### 添加应用图标

```python
exe = EXE(
    pyz,
    a.scripts,
    icon='path/to/icon.ico',  # Windows 图标
    ...
)
```

**图标要求**:
- Windows: `.ico` 格式，推荐 256x256 像素
- macOS: `.icns` 格式
- Linux: `.png` 格式

#### 添加版本信息（Windows）

1. **创建版本信息文件** (`version_info.txt`):
   ```
   VSVersionInfo(
     ffi=FixedFileInfo(
       filevers=(1, 4, 1, 0),
       prodvers=(1, 4, 1, 0),
       mask=0x3f,
       flags=0x0,
       OS=0x40004,
       fileType=0x1,
       subtype=0x0,
       date=(0, 0)
     ),
     kids=[
       StringFileInfo(
         [
         StringTable(
           u'040904B0',
           [StringStruct(u'CompanyName', u'Your Company'),
           StringStruct(u'FileDescription', u'OCR Batch Recognition System'),
           StringStruct(u'FileVersion', u'1.4.1.0'),
           StringStruct(u'InternalName', u'OCR-System'),
           StringStruct(u'LegalCopyright', u'Copyright (C) 2024'),
           StringStruct(u'OriginalFilename', u'OCR-System.exe'),
           StringStruct(u'ProductName', u'OCR System'),
           StringStruct(u'ProductVersion', u'1.4.1.0')])
         ]),
       VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
     ]
   )
   ```

2. **在 spec 文件中引用**:
   ```python
   exe = EXE(
       pyz,
       a.scripts,
       version='version_info.txt',
       ...
   )
   ```

#### 添加隐藏导入

如果打包后出现模块导入错误，可以手动添加隐藏导入:

```python
hidden_imports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'your_missing_module',  # 添加缺失的模块
]
```

#### 添加二进制文件

如果需要包含额外的 DLL 或 SO 文件:

```python
binaries = [
    ('path/to/library.dll', '.'),
    ('path/to/library.so', '.'),
]

a = Analysis(
    ...
    binaries=binaries,
    ...
)
```

#### 添加运行时钩子

如果需要在应用启动时执行特定代码:

1. **创建钩子文件** (`runtime_hook.py`):
   ```python
   import sys
   import os
   
   # 设置环境变量
   os.environ['QT_AUTO_SCREEN_SCALE_FACTOR'] = '1'
   
   # 添加自定义路径
   sys.path.insert(0, os.path.join(sys._MEIPASS, 'custom_path'))
   ```

2. **在 spec 文件中引用**:
   ```python
   a = Analysis(
       ...
       runtime_hooks=['runtime_hook.py'],
       ...
   )
   ```

### 多平台打包

#### Windows 打包

```bash
# 在 Windows 上打包
pyinstaller ocr_system.spec
```

**注意事项**:
- 使用 Windows 10/11 进行打包
- 确保安装了 Visual C++ Redistributable
- 测试 32 位和 64 位版本

#### Linux 打包

```bash
# 在 Linux 上打包
pyinstaller ocr_system.spec

# 添加执行权限
chmod +x dist/OCR-System/OCR-System
```

**注意事项**:
- 在目标 Linux 发行版上打包
- 检查 glibc 版本兼容性
- 测试不同桌面环境（GNOME, KDE, XFCE）

#### macOS 打包

```bash
# 在 macOS 上打包
pyinstaller ocr_system.spec

# 创建 .app 包
pyinstaller --windowed ocr_system.spec
```

**注意事项**:
- 需要 macOS 开发者账号进行代码签名
- 测试 Intel 和 Apple Silicon 版本
- 处理 Gatekeeper 限制

### 持续集成 (CI/CD)

#### GitHub Actions 示例

创建 `.github/workflows/build.yml`:

```yaml
name: Build and Release

on:
  push:
    tags:
      - 'v*'

jobs:
  build-windows:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pyinstaller
      
      - name: Build with PyInstaller
        run: |
          cd Pack/Pyinstaller
          pyinstaller ocr_system.spec
      
      - name: Create archive
        run: |
          7z a OCR-System-win64.7z dist/OCR-System/
      
      - name: Upload artifact
        uses: actions/upload-artifact@v2
        with:
          name: OCR-System-win64
          path: OCR-System-win64.7z

  build-linux:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pyinstaller
      
      - name: Build with PyInstaller
        run: |
          cd Pack/Pyinstaller
          pyinstaller ocr_system.spec
      
      - name: Create archive
        run: |
          tar -czf OCR-System-linux64.tar.gz dist/OCR-System/
      
      - name: Upload artifact
        uses: actions/upload-artifact@v2
        with:
          name: OCR-System-linux64
          path: OCR-System-linux64.tar.gz
```

### 调试打包问题

#### 启用调试模式

在 spec 文件中启用调试:

```python
exe = EXE(
    pyz,
    a.scripts,
    debug=True,  # 启用调试
    console=True,  # 显示控制台
    ...
)
```

#### 查看详细日志

```bash
# 使用 --log-level 参数
pyinstaller --log-level DEBUG ocr_system.spec

# 查看分析结果
pyinstaller --log-level INFO ocr_system.spec > build.log 2>&1
```

#### 检查依赖

```bash
# 使用 pyi-archive_viewer 查看打包内容
pyi-archive_viewer dist/OCR-System.exe

# 使用 pyi-bindepend 查看二进制依赖
pyi-bindepend dist/OCR-System/OCR-System.exe
```

### 性能优化

#### 减少启动时间

1. **使用文件夹模式**
2. **延迟导入重型库**
   ```python
   # 不要在模块顶部导入
   # import heavy_library
   
   # 在需要时才导入
   def use_heavy_library():
       import heavy_library
       return heavy_library.do_something()
   ```

3. **使用多线程初始化**
   ```python
   import threading
   
   def init_ocr_engines():
       # 在后台线程初始化 OCR 引擎
       pass
   
   threading.Thread(target=init_ocr_engines, daemon=True).start()
   ```

#### 减少内存占用

1. **及时释放资源**
2. **使用生成器而不是列表**
3. **避免全局变量**

### 安全考虑

#### 保护敏感信息

1. **不要在代码中硬编码 API 密钥**
2. **使用环境变量或外部配置文件**
3. **加密敏感配置**

#### 代码混淆

虽然 PyInstaller 不提供代码混淆，但可以使用第三方工具:

```bash
# 使用 pyarmor 混淆代码
pip install pyarmor
pyarmor obfuscate qt_run.py

# 然后打包混淆后的代码
pyinstaller obfuscated/qt_run.py
```

---

## 相关文档

- [MANIFEST.md](MANIFEST.md) - 完整的打包清单
- [USAGE_CN.md](USAGE_CN.md) - 使用说明
- [TESTING_GUIDE.md](TESTING_GUIDE.md) - 测试指南
- [PyInstaller 官方文档](https://pyinstaller.org/en/stable/)

---

## 更新日志

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0 | 2024-11-28 | 初始版本，完整的打包文档 |

---

## 许可证

本文档遵循项目的开源许可证。

---

## 联系方式

如有问题或建议，请通过以下方式联系:

- **GitHub Issues**: [项目 Issues 页面]
- **Email**: [your-email@example.com]
- **文档**: [项目文档链接]

---

**感谢使用 OCR System!** 🎉
