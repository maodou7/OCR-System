# 批量OCR识别图片PDF多区域内容重命名导出表格系统

<div align="center">

![Version](https://img.shields.io/badge/version-v1.4.1-blue)
![Python](https://img.shields.io/badge/python-3.8+-brightgreen)
![License](https://img.shields.io/badge/license-MIT-orange)

一个功能强大的批量OCR识别工具，支持**4种OCR引擎**、图片和PDF文件的多区域识别、自动重命名和Excel导出。内置**C++高性能缓存引擎**，支持自动保存和会话恢复。

[功能特点](#功能特点) • [快速开始](#快速开始) • [OCR引擎](#ocr引擎对比) • [使用指南](#使用指南) • [配置说明](#配置说明)

</div>

---

## ✨ 功能特点

### 核心功能
- 🎯 **多引擎支持** - 集成4种OCR引擎，GUI一键切换
- 📦 **批量处理** - 支持批量导入和处理多个文件
- 🖼️ **多格式支持** - PNG、JPG、BMP、GIF、TIFF、PDF等
- 🔲 **多区域识别** - 可视化框选，支持一张图片多个区域
- ✏️ **自动重命名** - 根据识别结果智能重命名文件
- 📊 **Excel导出** - 将所有识别结果导出为Excel表格（支持动态列数）
- 🎨 **可视化操作** - 直观的Qt GUI界面，鼠标拖拽框选
- ⚡ **极速启动** - 启动仅需0.1-0.2秒，OCR引擎后台异步初始化
- 💾 **智能缓存** - C++缓存引擎实时保存，自动降级保证稳定性
- 🔄 **会话恢复** - 意外退出后自动恢复进度
- 🛡️ **鲁棒性强** - 缓存失败自动降级，核心功能不受影响

### 🆕 v1.4.2 优化特性
- 📦 **按需下载** - OCR引擎可选下载，程序内一键安装
- 🔌 **插件化架构** - 在线OCR设计为可选插件，按需加载
- 🚀 **极致轻量** - 核心版本仅250MB，完整版600MB
- ⚡ **闪电启动** - 0.1秒显示窗口，0.2秒完全就绪
- 💾 **低内存占用** - 空闲时内存<200MB
- 🧹 **智能清理** - 自动清理缓存和临时文件
- 📊 **完整测试** - 5个集成测试脚本，全面验证优化效果

### 性能优化
| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| 打包体积（核心版） | 800MB-1.5GB | 250MB | **↓ 83%** |
| 打包体积（完整版） | 800MB-1.5GB | 600MB | **↓ 60%** |
| 启动时间（窗口显示） | 5-10秒 | 0.086秒 | **↑ 99%** |
| 启动时间（完全就绪） | 5-10秒 | 0.182秒 | **↑ 98%** |
| 初始内存 | 500-800MB | 150-200MB | **↓ 75%** |
| 空闲内存 | 400-600MB | <200MB | **↓ 67%** |

### 🆕 最新更新（v1.4.2 - 极致优化版）
- 🚀 **体积优化**：核心版本仅250MB，相比优化前减少83%
- ⚡ **启动优化**：启动时间从5-10秒优化到0.1-0.2秒，提升99%
- 💾 **内存优化**：空闲内存占用降至200MB以下，减少67%
- 📦 **按需下载**：OCR引擎可选下载，用户按需安装
- 🔌 **插件化**：在线OCR设计为可选插件，核心程序更轻量
- 🧹 **自动清理**：打包前自动清理缓存和临时文件
- 🛡️ **缓存鲁棒性**：智能降级策略，缓存失败不影响使用
- ✅ **全面测试**：完整的集成测试和性能验证

---

## 🚀 快速开始

### 环境要求
- Python 3.8 或更高版本
- 操作系统：Windows / Linux / macOS

### 安装步骤

#### 1. 克隆仓库
```bash
git clone https://github.com/maodou7/OCR-System.git
cd OCR-System
```

#### 2. 创建虚拟环境（推荐）
```bash
python -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

#### 3. 安装依赖
```bash
pip install -r requirements.txt
```

#### 4. 下载 OCR 引擎（可选，推荐）

**🆕 v1.4.2 新特性：程序内一键下载！**

程序首次启动时会自动检测OCR引擎，如果未安装会提示下载。你也可以：

**方式1：程序内下载（推荐）**
1. 启动程序后，点击工具栏的"下载引擎"按钮
2. 选择需要的引擎（RapidOCR或PaddleOCR）
3. 点击"开始下载"，等待下载完成
4. 自动配置并启用引擎

**方式2：手动下载**

**下载 RapidOCR-json（推荐，轻量级）：**
- 大小：45MB
- [下载 RapidOCR-json v0.2.0 Windows 版](https://github.com/hiroi-sora/RapidOCR-json/releases/download/v0.2.0/RapidOCR-json_v0.2.0_windows_x64.7z)
- 解压到 `models/RapidOCR-json/` 目录

**下载 PaddleOCR-json（高精度）：**
- 大小：562MB
- [下载 PaddleOCR-json v1.4.1 Windows 版](https://github.com/hiroi-sora/PaddleOCR-json/releases/download/v1.4.1/PaddleOCR-json_v1.4.1_windows_x64.7z)
- 解压到 `models/PaddleOCR-json/` 目录

**Linux 用户额外步骤：**
1. 安装 Wine：`sudo apt-get install wine`
2. 下载 Windows 版本（同上）
3. 首次运行时会自动创建 Wine 包装脚本

> 💡 **提示**：核心版本不包含OCR引擎，体积仅250MB。首次启动时会提示下载，也可以稍后手动下载。

#### 5. 配置在线OCR（可选插件）

**🆕 v1.4.2：在线OCR现在是可选插件！**

在线OCR（阿里云、DeepSeek）现在设计为可选插件，不使用时不会加载，进一步减小程序体积和内存占用。

**安装在线OCR插件：**

**方式1：使用插件管理器（推荐）**
1. 启动程序后，点击"工具" → "插件管理"
2. 选择需要的在线OCR插件
3. 点击"安装"按钮
4. 按照提示配置API密钥

**方式2：命令行安装**
```bash
# 安装阿里云OCR插件
python install_online_ocr_plugin.py --aliyun

# 安装DeepSeek OCR插件
python install_online_ocr_plugin.py --deepseek

# 安装所有插件
python install_online_ocr_plugin.py --all
```

**配置API密钥：**

编辑 `config.py` 文件：
```python
# 阿里云OCR配置
ALIYUN_ENABLED = True  # 改为True启用
ALIYUN_ACCESS_KEY_ID = 'your_key_id'
ALIYUN_ACCESS_KEY_SECRET = 'your_secret'

# DeepSeek OCR配置
DEEPSEEK_ENABLED = True  # 改为True启用
DEEPSEEK_API_KEY = 'your_api_key'
```

> 💡 **提示**：如果只使用本地引擎（PaddleOCR或RapidOCR），无需安装在线OCR插件

#### 6. 启动程序
```bash
python qt_run.py
```

**首次启动提示：**
- 如果未安装OCR引擎，程序会提示下载
- 推荐下载RapidOCR（45MB，轻量快速）
- 也可以选择"稍后下载"，之后手动安装

---

## 🔍 OCR引擎对比

本系统集成了**4种主流OCR引擎**，可在GUI中一键切换：

| 引擎 | 类型 | 速度 | 精度 | 成本 | 特点 |
|------|------|------|------|------|------|
| **PaddleOCR-json** 🔥 | 本地 | ⚡⚡⚡⚡⚡ 极快 | ⭐⭐⭐⭐⭐ 极高 | 免费 | **C++高性能引擎**，速度提升3-5倍，内存占用降低50% |
| **RapidOCR-json** 🆕 | 本地 | ⚡⚡⚡⚡⚡ 极快 | ⭐⭐⭐ 中 | 免费 | **C++轻量级引擎**，基于ONNX Runtime，启动极快，内存极低 |
| **阿里云OCR** | 在线 | ⚡⚡ 中 | ⭐⭐⭐⭐ 高 | 付费 | 支持多种证件识别，云端服务 |
| **DeepSeek OCR** | 在线 | ⚡⚡⚡ 快 | ⭐⭐⭐⭐ 高 | 限免 | 硅基流动平台，当前限免测试 |

### 🆕 v1.3.0 重大升级
**本地引擎全面升级为高性能 C++ 版本！**
- 🔥 **PaddleOCR-json**：识别速度提升 **3-5倍**，内存占用降低 **50%+**
- 🆕 **RapidOCR-json**：轻量级C++引擎，启动极快，内存占用极低
- 💪 基于 [hiroi-sora/PaddleOCR-json](https://github.com/hiroi-sora/PaddleOCR-json) 和 [hiroi-sora/RapidOCR-json](https://github.com/hiroi-sora/RapidOCR-json)
- 📦 解压即用，无需配置Python环境
- 🖥️ 跨平台：Windows 原生运行，Linux 通过 Wine 运行

### 引擎选择建议

- **🏆 推荐首选** → PaddleOCR-json（高性能C++引擎，速度+精度双优）
- **轻量快速** → RapidOCR-json（轻量级C++引擎，启动快，内存低）
- **特殊证件** → 阿里云OCR（多证件类型支持）
- **测试新技术** → DeepSeek OCR（AI前沿技术）

---

## 📖 使用指南

### 1. 启动程序并选择引擎

在工具栏的"OCR引擎"下拉菜单中选择需要的引擎。

### 2. 打开文件

- **单个/多个文件**：点击 `📂 打开文件`
- **批量文件夹**：点击 `📁 打开文件夹`

支持格式：PNG、JPG、JPEG、BMP、GIF、TIFF、TIF、PDF

### 3. 框选识别区域

- 在图片上**按住鼠标左键拖拽**，框选需要识别的区域
- 可以框选**多个区域**
- **右键点击区域**可删除
- 支持自动识别（无需框选）

### 4. 开始识别

点击 `🔍 开始识别` 按钮，等待识别完成。

识别结果会显示在底部文本框中。

### 5. 文件重命名（可选）

点击 `✏️ 改名并下一张`：
- 程序会根据第一个区域的识别结果重命名文件
- 自动跳转到下一张图片
- 重名时自动添加序号

### 6. 导出Excel

点击 `💾 导出Excel`，选择保存位置。

所有识别结果将导出为Excel表格，包含：
- 文件名
- 识别区域
- 识别内容
- 处理状态

---

## ⚙️ 配置说明

### OCR引擎配置

#### PaddleOCR-json（本地引擎，推荐首选）
高性能C++引擎，识别速度极快，内存占用低，精度极高。

**配置要求：**
- 下载并解压 PaddleOCR-json 到 `models/PaddleOCR-json/` 目录
- Linux 用户需要安装 Wine
- 无需其他配置，解压即用

#### RapidOCR-json（本地引擎，轻量级）
轻量级C++引擎，基于ONNX Runtime，启动极快，内存占用极低。

**配置要求：**
- 下载并解压 RapidOCR-json 到 `models/RapidOCR-json/` 目录
- Linux 用户需要安装 Wine
- 无需其他配置，解压即用
- 适合低配环境或需要快速启动的场景

#### 阿里云OCR（需要API密钥）
1. 访问 [阿里云OCR控制台](https://www.aliyun.com/product/ocr)
2. 开通服务并创建AccessKey
3. 在 `config.py` 或环境变量中配置密钥

```python
ALIYUN_ACCESS_KEY_ID = 'your_key_id'
ALIYUN_ACCESS_KEY_SECRET = 'your_secret'
```

#### DeepSeek OCR（需要API密钥）
1. 访问 [硅基流动平台](https://cloud.siliconflow.cn/)
2. 注册/登录并创建API密钥
3. 在 `config.py` 或环境变量中配置密钥

```python
DEEPSEEK_API_KEY = 'sk-xxxxxx'
```

### 高级配置

编辑 `config.py` 文件可自定义：

```python
# OCR参数
OCR_USE_ANGLE_CLS = True  # 角度分类（处理旋转文字）
OCR_LANG = 'ch'           # 语言：ch=中英文, en=英文
OCR_SHOW_LOG = False      # 显示详细日志

# DeepSeek OCR Prompt
DEEPSEEK_OCR_PROMPT = '<image>\nFree OCR.'  # Free OCR模式
```

---

## 📁 项目结构

```
OCR-System/
├── qt_run.py                   # 主启动脚本
├── qt_run_silent.pyw           # 静默启动（无控制台）
├── qt_main.py                  # GUI主程序
├── config.py                   # 配置管理
├── utils.py                    # 工具函数
│
├── ocr_engine_manager.py       # OCR引擎管理器
├── ocr_engine_paddle.py        # PaddleOCR引擎
├── ocr_engine_rapid.py         # RapidOCR引擎
├── ocr_engine_aliyun_new.py    # 阿里云OCR引擎
├── ocr_engine_deepseek.py      # DeepSeek OCR引擎
│
├── ocr_cache_manager.py        # Python缓存管理器
├── models/                     # 模型和引擎目录
│   ├── libocr_cache.so         # C++缓存引擎（Linux）
│   ├── ocr_cache.dll           # C++缓存引擎（Windows）
│   ├── cpp_engine/             # C++引擎源码
│   │   ├── ocr_cache_engine.h  #     C API接口
│   │   ├── ocr_cache_engine.cpp#     核心实现
│   │   ├── sqlite3.c/h         #     嵌入式SQLite
│   │   ├── CMakeLists.txt      #     构建配置
│   │   ├── build.sh            #     编译脚本（Linux/macOS）
│   │   └── README.md           #     技术文档
│   ├── PaddleOCR-json/         # PaddleOCR引擎模型
│   └── RapidOCR-json/          # RapidOCR引擎模型
│
├── Pack/                       # 打包配置目录
│   └── Pyinstaller/            # PyInstaller打包配置
│       ├── ocr_system.spec     # 打包规格文件
│       ├── build_package.bat   # Windows打包脚本
│       ├── build_package.sh    # Linux/macOS打包脚本
│       └── README.md           # 打包说明文档
│
├── requirements.txt            # 依赖列表
├── .env.example                # 环境变量示例
├── .gitignore                  # Git忽略配置
├── README.md                   # 本文档
└── 更新日志.txt                # 版本更新记录
```

---

## 💾 缓存系统

### 智能缓存引擎

本系统采用**三级缓存架构**，确保在任何情况下都能稳定运行：

#### 1. C++缓存引擎（正常模式）
- **高性能**：基于SQLite，识别结果实时保存（<5ms）
- **持久化**：数据永久保存，支持会话恢复
- **ACID保证**：事务机制确保数据完整性

#### 2. 内存缓存（降级模式）
- **自动降级**：C++引擎不可用时自动启用
- **零配置**：无需任何设置，自动工作
- **功能完整**：所有OCR功能正常使用
- **唯一限制**：关闭程序后数据丢失

#### 3. 禁用模式（可选）
- **完全禁用**：不使用任何缓存
- **适用场景**：临时使用或测试

### 鲁棒性特性

- ✅ **自动降级**：缓存失败不影响OCR功能
- ✅ **自动恢复**：数据库损坏时自动重建
- ✅ **详细诊断**：提供完整的错误信息和解决建议
- ✅ **线程安全**：支持并发操作
- ✅ **跨平台**：Windows/Linux/macOS全支持

### 故障排除

如果遇到缓存相关问题，请参考：
- **故障排除指南**：[CACHE_TROUBLESHOOTING.md](CACHE_TROUBLESHOOTING.md)
- **架构文档**：[CACHE_ARCHITECTURE.md](CACHE_ARCHITECTURE.md)（开发者）

**常见问题快速解决：**
```bash
# 重置缓存（解决大部分问题）
rm -rf .ocr_cache  # Linux/macOS
rmdir /s /q .ocr_cache  # Windows

# 安装Visual C++运行库（Windows）
# 下载：https://aka.ms/vs/17/release/vc_redist.x64.exe
```

---

## 🛠️ 技术栈

- **GUI框架**: PySide6 (Qt 6.6+)
- **OCR引擎**: 
  - PaddleOCR-json v1.4.1（C++高性能引擎）
  - RapidOCR-json v0.2.0（C++轻量级引擎）
  - 阿里云OCR API 2021-07-07
  - DeepSeek OCR（OpenAI兼容接口）
- **缓存引擎**: C++ + SQLite3（嵌入式数据库）
- **图片处理**: Pillow 10.0+
- **PDF处理**: PyMuPDF 1.23+（按需导入）
- **Excel导出**: openpyxl 3.1+（按需导入）
- **数值计算**: NumPy 1.24+（按需导入）
- **打包工具**: PyInstaller 6.0+

---

## 📝 更新日志

### v1.4.2 (2024-11-30) - 🔥 极致优化版
- 🚀 **体积优化**：核心版本250MB，完整版600MB，减少60-83%
- ⚡ **启动优化**：启动时间0.1-0.2秒，提升99%
- 💾 **内存优化**：空闲内存<200MB，减少67%
- 📦 **按需下载**：OCR引擎可选下载，程序内一键安装
- 🔌 **插件化**：在线OCR设计为可选插件
- 🧹 **自动清理**：打包前自动清理缓存
- 🛡️ **缓存鲁棒性**：智能降级策略，自动恢复机制
- 📊 **完整测试**：5个集成测试脚本，全面验证
- 📖 **文档完善**：详细的优化报告和使用指南

### v1.4.1 (2024-11-27)
- 🐛 **Bug修复**：修复删除区域时所有文本被清空的问题
- ✅ **信号优化**：临时断开textChanged信号避免误触发
- 💾 **自动保存**：删除区域后立即保存到缓存
- 📁 **目录优化**：C++引擎移动到models/目录

### v1.4.0 (2025-11-27) - 🔥 重大更新
- 🐛 **严重Bug修复**：修复Excel导出只写入最后一张图片的bug
- 🚀 **C++缓存引擎**：性能提升100倍，内存减少70%
- 💾 **自动保存**：识别后自动保存（<5ms）
- 🔄 **会话恢复**：启动时检测并恢复未完成任务
- 📊 **动态列数**：支持不固定的区域列数量
- ✅ **ACID事务**：数据永不丢失

### v1.3.1 (2025-11-26)
- ✅ Bug修复：引擎接口完善
- ✨ 体验优化：多行文本合并显示
- 📊 Excel优化：追加模式智能处理

### v1.3.0 (2025-11-26)
- 🔥 PaddleOCR/RapidOCR升级为C++版本
- ⚡ 识别速度提升3-5倍
- 💾 内存占用降低50%+

### v1.2.0 (2025-11-26)
- ✏️ 识别结果可编辑
- 🎨 UI界面优化

### v1.1.0 (2025-11-26)
- 📊 Excel追加模式
- 🔢 智能文件命名

### v0.0.5 (2025-11-25)
- 🆕 DeepSeek OCR引擎集成
- 🔒 安全性增强

### v0.0.4 (2025-11-22)
- ⚡ 异步初始化优化

### v0.0.3 (2025-11-21)
- ✅ PaddleOCR 3.x完整适配
- ✅ RapidOCR引擎实现

### v0.02 (2025-01-21)
- 🚀 按需导入策略
- ⏱️ 启动速度提升80%

### v0.01 (2025-11-20)
- ✨ 初始版本发布

---

## 📦 打包部署

本项目支持使用PyInstaller打包为独立可执行文件，无需Python环境即可运行。

### 打包说明

详细的打包配置和说明文档位于 `Pack/Pyinstaller/` 目录：

- **ocr_system.spec** - PyInstaller打包规格文件
- **build_package.bat** - Windows一键打包脚本
- **build_package.sh** - Linux/macOS一键打包脚本
- **README.md** - 完整的打包使用指南

### 快速打包

**Windows:**
```bash
cd Pack/Pyinstaller
build_package.bat
```

**Linux/macOS:**
```bash
cd Pack/Pyinstaller
chmod +x build_package.sh
./build_package.sh
```

打包后的可执行文件位于 `Pack/Pyinstaller/dist/` 目录。

更多详细信息请参考 `Pack/Pyinstaller/README.md`。

---

## ❓ 常见问题

### Q1: 缓存引擎初始化失败怎么办？
**A:** 不用担心！系统会自动降级到内存缓存模式，所有OCR功能都能正常使用。
- **自动降级**：缓存失败时自动使用内存缓存
- **不影响使用**：OCR识别、重命名、导出等功能完全正常
- **唯一区别**：关闭程序后，识别结果不会保存（但可以导出Excel）

**常见原因和解决方案：**
- **缺少运行库（Windows）**：安装 [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe)
- **数据库损坏**：删除 `.ocr_cache` 文件夹，重新启动程序
- **权限不足**：以管理员身份运行程序

详细的故障排除指南请参考：[CACHE_TROUBLESHOOTING.md](CACHE_TROUBLESHOOTING.md)

### Q2: 提示"OCR引擎未就绪"？
**A:** 确保已安装相应引擎的依赖：
```bash
# PaddleOCR
pip install paddleocr paddlepaddle

# RapidOCR
pip install rapidocr-onnxruntime

# DeepSeek OCR
pip install openai
```

### Q3: 什么是内存缓存模式？
**A:** 当C++缓存引擎不可用时，系统会自动使用内存缓存：
- **优点**：不需要任何配置，自动启用
- **缺点**：关闭程序后数据丢失
- **建议**：及时导出Excel保存结果

### Q4: DeepSeek OCR返回带标记的文本？
**A:** 系统已自动清理。如仍有问题，检查 `config.py` 中的Prompt设置：
```python
DEEPSEEK_OCR_PROMPT = '<image>\nFree OCR.'  # 确保使用Free OCR模式
```

### Q5: 识别速度慢？
**A:** 
- **首次加载较慢**：模型初始化需要时间，后续会快
- **切换到GPU**：安装GPU版PaddlePaddle
- **使用RapidOCR**：更快但精度稍低

### Q6: 如何提高识别准确率？
**A:**
- 使用高分辨率图片
- 框选区域尽量精确，贴合文字边缘
- 优先选择PaddleOCR引擎（最高精度）
- 避免框选模糊、倾斜的文字

### Q7: 支持哪些图片格式？
**A:** PNG、JPG、JPEG、BMP、GIF、TIFF、TIF、PDF

---

## 🤝 贡献指南

欢迎提交Issue和Pull Request！

### 提交Issue
- Bug报告：请提供错误信息、操作步骤、系统环境
- 功能建议：描述需求场景和期望效果

### 提交PR
1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

---

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

---

## 🙏 致谢

本项目使用了以下优秀的开源项目：

- [PaddleOCR-json](https://github.com/hiroi-sora/PaddleOCR-json) - 高性能C++版PaddleOCR封装
- [RapidOCR-json](https://github.com/hiroi-sora/RapidOCR-json) - 轻量级C++版RapidOCR封装
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 百度飞桨OCR框架
- [RapidOCR](https://github.com/RapidAI/RapidOCR) - 快速OCR引擎
- [SQLite](https://www.sqlite.org/) - 嵌入式数据库引擎
- [PySide6](https://www.qt.io/qt-for-python) - Qt for Python
- [OpenAI Python SDK](https://github.com/openai/openai-python) - API接口库

特别感谢：
- 硅基流动平台提供的DeepSeek OCR限免服务
- hiroi-sora 提供的高性能C++引擎封装

---

## 📧 联系方式

- GitHub: [@maodou7](https://github.com/maodou7)
- 项目地址: [OCR-System](https://github.com/maodou7/OCR-System)
- 问题反馈: [Issues](https://github.com/maodou7/OCR-System/issues)

---

<div align="center">

**⭐ 如果这个项目对你有帮助，请给个Star！⭐**

Made with ❤️ by maodou7

</div>
