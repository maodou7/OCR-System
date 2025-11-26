# 打包配置指南

## 📦 打包工具选择

推荐使用 **PyInstaller** 或 **Nuitka** 进行打包。

### 方案 1：PyInstaller（推荐，简单快速）

#### 安装
```bash
pip install pyinstaller
```

#### 打包命令
```bash
# Windows
pyinstaller --name="OCR识别系统" \
  --windowed \
  --icon=icon.ico \
  --add-data "models;models" \
  --add-data "config.py.example;." \
  --hidden-import=PySide6 \
  --hidden-import=PIL \
  --hidden-import=openpyxl \
  --hidden-import=fitz \
  --hidden-import=alibabacloud_ocr_api20210707 \
  --hidden-import=openai \
  qt_run.py

# Linux
pyinstaller --name="OCR识别系统" \
  --windowed \
  --add-data "models:models" \
  --add-data "config.py.example:." \
  --hidden-import=PySide6 \
  --hidden-import=PIL \
  --hidden-import=openpyxl \
  --hidden-import=fitz \
  --hidden-import=alibabacloud_ocr_api20210707 \
  --hidden-import=openai \
  qt_run.py
```

#### 预期打包大小
- **基础包**：~200-300 MB（不含 OCR 引擎）
- **完整包**：~500-600 MB（含 PaddleOCR-json + RapidOCR-json）

---

### 方案 2：Nuitka（推荐，性能最优）

#### 安装
```bash
pip install nuitka
```

#### 打包命令
```bash
# Windows
nuitka --standalone \
  --windows-disable-console \
  --enable-plugin=pyside6 \
  --include-data-dir=models=models \
  --include-data-file=config.py.example=config.py.example \
  --output-dir=dist \
  qt_run.py

# Linux
nuitka --standalone \
  --enable-plugin=pyside6 \
  --include-data-dir=models=models \
  --include-data-file=config.py.example=config.py.example \
  --output-dir=dist \
  qt_run.py
```

#### 优势
- 启动速度更快（编译为原生代码）
- 运行性能提升 20-30%
- 体积略大但质量更好

---

## 🗂️ 打包前准备

### 1. 清理项目
```bash
# 删除 __pycache__ 和 .pyc 文件
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete

# 删除 .git 目录（可选，减小体积）
# rm -rf .git
```

### 2. 确保依赖完整
```bash
# 重新安装精简后的依赖
pip install -r requirements.txt
```

### 3. 测试运行
```bash
python qt_run.py
# 确保所有功能正常
```

---

## 📁 打包后目录结构

```
dist/
└── OCR识别系统/
    ├── OCR识别系统.exe (Windows) 或 OCR识别系统 (Linux)
    ├── models/
    │   ├── PaddleOCR-json/
    │   │   └── PaddleOCR-json_v1.4.1/
    │   │       ├── PaddleOCR-json.exe
    │   │       └── models/
    │   └── RapidOCR-json/
    │       └── RapidOCR-json_v0.2.0/
    │           ├── RapidOCR-json.exe
    │           └── models/
    ├── config.py.example
    └── _internal/ (PyInstaller) 或其他依赖文件
```

---

## ⚠️ 注意事项

### 1. OCR 引擎文件
- **PaddleOCR-json**：~300 MB
- **RapidOCR-json**：~90 MB
- 打包时需要包含在 `models/` 目录中

### 2. Wine 依赖（Linux）
如果在 Linux 上打包，运行时需要：
```bash
# 用户需要安装 Wine
sudo apt-get install wine
```

### 3. 配置文件
- 不要打包 `config.py`（包含敏感信息）
- 打包 `config.py.example` 作为模板
- 用户首次运行时需要配置 API 密钥

### 4. 测试环境
在目标系统上测试打包后的程序：
- Windows 10/11
- Linux (Ubuntu 20.04+)
- 确保所有引擎都能正常工作

---

## 🚀 优化建议

### 减小体积
1. 只打包常用引擎（例如只包含 PaddleOCR-json）
2. 使用 UPX 压缩可执行文件
   ```bash
   # PyInstaller 自动使用 UPX
   pyinstaller --upx-dir=/path/to/upx ...
   ```

### 提升性能
1. 使用 Nuitka 编译为原生代码
2. 启用优化选项：
   ```bash
   nuitka --lto=yes --plugin-enable=pyside6 ...
   ```

### 多版本发布
1. **精简版**：~200 MB（不含本地引擎，仅在线引擎）
2. **标准版**：~500 MB（含 PaddleOCR-json）
3. **完整版**：~600 MB（含所有引擎）

---

## 📋 发布清单

- [ ] 测试所有 OCR 引擎
- [ ] 测试 Excel 导出功能
- [ ] 测试文件重命名功能
- [ ] 测试在线/本地引擎切换
- [ ] 准备用户手册
- [ ] 准备 README.md
- [ ] 创建安装包/压缩包
- [ ] 测试在干净系统上运行

---

## 📞 问题排查

### 打包失败
- 检查 requirements.txt 中的所有依赖是否已安装
- 确保 Python 版本 >= 3.8
- 查看 PyInstaller 或 Nuitka 的详细日志

### 运行时错误
- 检查 `models/` 目录是否正确包含
- 检查配置文件路径
- Linux 用户确保已安装 Wine

### 体积过大
- 移除不必要的引擎
- 使用 UPX 压缩
- 考虑分离引擎作为可选下载
