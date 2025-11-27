# 从零开始设置OCR系统

本文档说明如何从GitHub仓库克隆后完整设置系统。

## 📋 前置要求

- **Python**: 3.8+
- **操作系统**: Linux / macOS / Windows
- **编译工具** (仅Linux/macOS需要):
  - CMake 3.10+
  - g++ 或 clang++
  - make

## 🚀 快速开始

### 1. 克隆仓库

```bash
git clone https://github.com/maodou7/OCR-System.git
cd OCR-System
```

### 2. 创建Python虚拟环境（推荐）

```bash
python3 -m venv .venv

# Linux/macOS
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. 安装Python依赖

```bash
pip install -r requirements.txt
```

### 4. 编译C++缓存引擎

#### Linux系统

```bash
# 安装编译依赖
sudo apt-get update
sudo apt-get install cmake g++ make

# 编译C++引擎
cd models/cpp_engine
chmod +x build.sh
./build.sh
cd ../..
```

**说明**：
- 编译会自动下载SQLite源码（约8.8MB）
- 编译输出：`models/libocr_cache.so`（约1.8MB）
- 编译时间：约30-60秒

#### macOS系统

```bash
# 安装Xcode命令行工具（如果未安装）
xcode-select --install

# 安装CMake（使用Homebrew）
brew install cmake

# 编译C++引擎
cd models/cpp_engine
chmod +x build.sh
./build.sh
cd ../..
```

#### Windows系统

**方式1：使用Visual Studio**
```cmd
cd models\cpp_engine
mkdir build && cd build
cmake .. -G "Visual Studio 16 2019"
cmake --build . --config Release
cd ..\..\..
```

**方式2：使用MinGW**
```cmd
cd models\cpp_engine
mkdir build && cd build
cmake .. -G "MinGW Makefiles"
cmake --build . --config Release
cd ..\..\..
```

### 5. 下载OCR引擎（可选但推荐）

#### PaddleOCR-json（高精度）

1. 下载：[PaddleOCR-json v1.4.1](https://github.com/hiroi-sora/PaddleOCR-json/releases/download/v1.4.1/PaddleOCR-json_v1.4.1_windows_x64.7z)
2. 解压到 `models/PaddleOCR-json/` 目录

#### RapidOCR-json（轻量级）

1. 下载：[RapidOCR-json v0.2.0](https://github.com/hiroi-sora/RapidOCR-json/releases/download/v0.2.0/RapidOCR-json_v0.2.0_windows_x64.7z)
2. 解压到 `models/RapidOCR-json/` 目录

**Linux用户额外步骤**：
```bash
# 安装Wine
sudo apt-get install wine

# 首次运行会自动创建.exe.sh包装脚本
```

### 6. 配置API密钥（可选）

如果需要使用在线OCR引擎：

**方式1：环境变量（推荐）**
```bash
# Linux/macOS
export ALIYUN_ACCESS_KEY_ID='your_key_id'
export ALIYUN_ACCESS_KEY_SECRET='your_secret'
export DEEPSEEK_API_KEY='your_api_key'

# Windows PowerShell
$env:ALIYUN_ACCESS_KEY_ID='your_key_id'
$env:ALIYUN_ACCESS_KEY_SECRET='your_secret'
$env:DEEPSEEK_API_KEY='your_api_key'
```

**方式2：配置文件**
```bash
# 复制配置示例
cp config.py.example config.py

# 编辑config.py，填入你的密钥
vim config.py  # 或使用其他编辑器
```

### 7. 启动程序

```bash
python qt_run.py
```

## ✅ 验证安装

### 检查C++缓存引擎

```bash
python3 -c "from ocr_cache_manager import OCRCacheManager; cache = OCRCacheManager('.test/test.db'); print('✓ 缓存引擎加载成功')"
```

预期输出：
```
✓ 缓存引擎加载成功
```

### 检查OCR引擎

启动程序后：
1. 在工具栏查看"OCR引擎"下拉菜单
2. 选择一个引擎
3. 状态栏应显示"✓ 就绪"

## 📁 最终目录结构

```
OCR-System/
├── .venv/                      # Python虚拟环境（本地）
├── models/
│   ├── libocr_cache.so         # 编译输出（本地）
│   ├── cpp_engine/
│   │   ├── build/              # 编译目录（本地）
│   │   ├── sqlite3.c/h/ext.h   # SQLite源码（自动下载）
│   │   ├── ocr_cache_engine.h  # ✓ 已提交
│   │   ├── ocr_cache_engine.cpp# ✓ 已提交
│   │   ├── CMakeLists.txt      # ✓ 已提交
│   │   └── build.sh            # ✓ 已提交
│   ├── PaddleOCR-json/         # OCR引擎（手动下载）
│   └── RapidOCR-json/          # OCR引擎（手动下载）
├── config.py                   # 本地配置（不提交）
├── config.py.example           # ✓ 已提交
├── ocr_cache_manager.py        # ✓ 已提交
├── qt_main.py                  # ✓ 已提交
└── ...                         # 其他源码文件
```

## 🛠️ 常见问题

### Q1: 编译C++引擎失败

**A**: 检查依赖是否安装：
```bash
# Linux
cmake --version  # 应该 >= 3.10
g++ --version    # 应该支持C++17

# 如果缺少
sudo apt-get install cmake g++ make
```

### Q2: Python依赖安装失败

**A**: 尝试升级pip：
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Q3: 缓存引擎加载失败

**A**: 确保libocr_cache.so已编译：
```bash
ls -lh models/libocr_cache.so
# 应该显示约1.8MB的文件
```

### Q4: OCR引擎未就绪

**A**: 
- 本地引擎：检查是否已下载并解压到正确目录
- 在线引擎：检查API密钥是否正确配置

### Q5: Wine相关错误（Linux）

**A**: 
```bash
# 安装Wine
sudo apt-get install wine

# 配置Wine
winecfg
```

## 📚 进一步阅读

- [README.md](README.md) - 功能介绍和使用指南
- [更新日志.txt](更新日志.txt) - 版本更新历史
- [models/cpp_engine/README.md](models/cpp_engine/README.md) - C++引擎技术文档

## 🤝 需要帮助？

- 提交Issue: https://github.com/maodou7/OCR-System/issues
- 查看文档: https://github.com/maodou7/OCR-System

---

**现在你可以开始使用OCR系统了！** 🎉
