# 批量OCR识别图片PDF多区域内容重命名导出表格系统

<div align="center">

![Version](https://img.shields.io/badge/version-v1.3.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-brightgreen)
![License](https://img.shields.io/badge/license-MIT-orange)

一个功能强大的批量OCR识别工具，支持**4种OCR引擎**、图片和PDF文件的多区域识别、自动重命名和Excel导出。

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
- 📊 **Excel导出** - 将所有识别结果导出为Excel表格
- 🎨 **可视化操作** - 直观的Qt GUI界面，鼠标拖拽框选
- ⚡ **按需加载** - 启动仅需1-2秒，OCR引擎后台异步初始化

### 性能优化
| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| 打包体积 | 800MB-1.5GB | 200-500MB | **↓ 60-75%** |
| 启动时间 | 5-10秒 | 1-2秒 | **↑ 80%** |
| 初始内存 | 500-800MB | 150-250MB | **↓ 70%** |

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

#### 4. 下载 PaddleOCR-json 引擎（推荐）

**Windows 用户：**
1. 下载 [PaddleOCR-json v1.4.1 Windows 版](https://github.com/hiroi-sora/PaddleOCR-json/releases/download/v1.4.1/PaddleOCR-json_v1.4.1_windows_x64.7z)
2. 解压到 `models/PaddleOCR-json/` 目录

**Linux 用户：**
1. 安装 Wine：`sudo apt-get install wine`
2. 下载 Windows 版本（同上）
3. 解压到 `models/PaddleOCR-json/` 目录
4. 首次运行时会自动创建 Wine 包装脚本

> 💡 **提示**：PaddleOCR-json 是高性能C++引擎，识别速度极快。如果跳过此步骤，将自动降级使用其他引擎。

#### 5. 配置API密钥（可选）

如果需要使用阿里云OCR或DeepSeek OCR，需要配置API密钥：

**方式1：环境变量（推荐）**
```bash
# Linux/macOS
export ALIYUN_ACCESS_KEY_ID='your_aliyun_key_id'
export ALIYUN_ACCESS_KEY_SECRET='your_aliyun_secret'
export DEEPSEEK_API_KEY='your_deepseek_api_key'

# Windows (PowerShell)
$env:ALIYUN_ACCESS_KEY_ID='your_aliyun_key_id'
$env:ALIYUN_ACCESS_KEY_SECRET='your_aliyun_secret'
$env:DEEPSEEK_API_KEY='your_deepseek_api_key'
```

**方式2：修改config.py**
```python
# 在 config.py 中找到以下配置并填写（仅本地使用，不要提交到Git）
ALIYUN_ACCESS_KEY_ID = 'your_key_here'
ALIYUN_ACCESS_KEY_SECRET = 'your_secret_here'
DEEPSEEK_API_KEY = 'your_api_key_here'
```

> 💡 **提示**：如果只使用PaddleOCR-json或RapidOCR（本地引擎），可跳过API配置

#### 6. 启动程序
```bash
python qt_run.py
```

---

## 🔍 OCR引擎对比

本系统集成了**4种主流OCR引擎**，可在GUI中一键切换：

| 引擎 | 类型 | 速度 | 精度 | 成本 | 特点 |
|------|------|------|------|------|------|
| **PaddleOCR-json** 🔥 | 本地 | ⚡⚡⚡⚡⚡ 极快 | ⭐⭐⭐⭐⭐ 极高 | 免费 | **C++高性能引擎**，速度提升3-5倍，内存占用降低50% |
| **RapidOCR** | 本地 | ⚡⚡⚡ 快 | ⭐⭐⭐ 中 | 免费 | 轻量级，无需GPU，启动快速 |
| **阿里云OCR** | 在线 | ⚡⚡ 中 | ⭐⭐⭐⭐ 高 | 付费 | 支持多种证件识别，云端服务 |
| **DeepSeek OCR** | 在线 | ⚡⚡⚡ 快 | ⭐⭐⭐⭐ 高 | 限免 | 硅基流动平台，当前限免测试 |

### 🆕 v1.3.0 重大升级
**PaddleOCR 引擎全面升级为 C++ 版 PaddleOCR-json！**
- ✨ 识别速度提升 **3-5倍**
- 🚀 内存占用降低 **50%+**
- 💪 基于 [hiroi-sora/PaddleOCR-json](https://github.com/hiroi-sora/PaddleOCR-json)
- 📦 解压即用，无需配置Python环境
- 🖥️ 跨平台：Windows 原生运行，Linux 通过 Wine 运行

### 引擎选择建议

- **🏆 推荐首选** → PaddleOCR-json（高性能C++引擎，速度+精度双优）
- **快速轻量** → RapidOCR（轻量级，低配环境友好）
- **特殊证件** → 阿里云OCR（多证件类型支持）
- **测试新技术** → DeepSeek OCR（AI前沿技术）

---

## 📖 使用指南

### 1. 启动程序并选择引擎

![选择引擎](docs/images/engine-selection.png)

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

#### PaddleOCR-json（本地引擎，推荐）
高性能C++引擎，识别速度极快，内存占用低。

**配置要求：**
- 下载并解压 PaddleOCR-json 到 `models/PaddleOCR-json/` 目录
- Linux 用户需要安装 Wine
- 无需其他配置，解压即用

#### RapidOCR（本地引擎，无需配置）
轻量级ONNX Runtime引擎，快速启动。

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
├── requirements.txt            # 依赖列表
├── .env.example                # 环境变量示例
├── .gitignore                  # Git忽略配置
├── README.md                   # 本文档
└── 更新日志.txt                # 版本更新记录
```

---

## 🛠️ 技术栈

- **GUI框架**: PySide6 (Qt 6.6+)
- **OCR引擎**: 
  - PaddleOCR 2.7+ / 3.x（智能版本适配）
  - RapidOCR (ONNX Runtime)
  - 阿里云OCR API 2021-07-07
  - DeepSeek OCR（OpenAI兼容接口）
- **图片处理**: Pillow 10.0+
- **PDF处理**: PyMuPDF 1.23+（按需导入）
- **Excel导出**: openpyxl 3.1+（按需导入）
- **数值计算**: NumPy 1.24+（按需导入）

---

## 📝 更新日志

### v0.0.4 (2025-11-25) - DeepSeek OCR集成
- 🆕 **新增DeepSeek OCR引擎**（硅基流动平台）
  - 使用OpenAI兼容接口
  - 智能文本清理，提取纯文本
  - Free OCR模式优化
- ✨ 支持4种OCR引擎一键切换
- 📄 完善的环境变量配置
- 🔒 移除敏感信息，增强安全性

### v0.0.3 (2025-11-21)
- ✅ PaddleOCR 3.x完整适配
- ✅ RapidOCR引擎实现
- 🔧 智能版本检测和参数降级

### v0.02 (2025-01-21) - 性能优化版
- 🚀 采用按需导入策略
- ⏱️ 启动速度提升80%
- 💾 打包体积减少60-75%
- 🧵 OCR引擎后台异步加载

### v0.01 (2025-11-20)
- ✨ 初始版本发布
- ✅ 多区域OCR识别
- ✅ PySide6 GUI界面
- ✅ 多OCR引擎支持

---

## ❓ 常见问题

### Q1: 提示"OCR引擎未就绪"？
**A:** 确保已安装相应引擎的依赖：
```bash
# PaddleOCR
pip install paddleocr paddlepaddle

# RapidOCR
pip install rapidocr-onnxruntime

# DeepSeek OCR
pip install openai
```

### Q2: DeepSeek OCR返回带标记的文本？
**A:** 系统已自动清理。如仍有问题，检查 `config.py` 中的Prompt设置：
```python
DEEPSEEK_OCR_PROMPT = '<image>\nFree OCR.'  # 确保使用Free OCR模式
```

### Q3: 识别速度慢？
**A:** 
- **首次加载较慢**：模型初始化需要时间，后续会快
- **切换到GPU**：安装GPU版PaddlePaddle
- **使用RapidOCR**：更快但精度稍低

### Q4: 如何提高识别准确率？
**A:**
- 使用高分辨率图片
- 框选区域尽量精确，贴合文字边缘
- 优先选择PaddleOCR引擎（最高精度）
- 避免框选模糊、倾斜的文字

### Q5: 支持哪些图片格式？
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

- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - 百度飞桨OCR框架
- [RapidOCR](https://github.com/RapidAI/RapidOCR) - 快速OCR引擎
- [PySide6](https://www.qt.io/qt-for-python) - Qt for Python
- [OpenAI Python SDK](https://github.com/openai/openai-python) - API接口库

特别感谢硅基流动平台提供的DeepSeek OCR限免服务！

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
