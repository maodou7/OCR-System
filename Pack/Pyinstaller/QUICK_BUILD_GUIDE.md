# 快速构建指南

## 选择打包版本

### 核心版（推荐）⭐
```bash
pyinstaller ocr_system_core.spec
```
- 体积：~250MB（未压缩），~120MB（压缩）
- 包含：RapidOCR引擎
- 适合：大多数用户

### 完整版
```bash
pyinstaller ocr_system.spec
```
- 体积：~600MB（未压缩），~300MB（压缩）
- 包含：RapidOCR + PaddleOCR引擎
- 适合：离线环境、企业部署

## 构建步骤

### 1. 准备环境
```bash
# 安装依赖
pip install -r requirements.txt
pip install pyinstaller
```

### 2. 清理旧构建
```bash
# Windows
rmdir /s /q build dist

# Linux/macOS
rm -rf build dist
```

### 3. 执行构建
```bash
# 进入打包目录
cd Pack/Pyinstaller

# 构建核心版
pyinstaller --clean ocr_system_core.spec

# 或构建完整版
pyinstaller --clean ocr_system.spec
```

### 4. 压缩分发
```bash
# 核心版
7z a -mx9 OCR-System-Core-v1.4.1.7z dist/OCR-System-Core/

# 完整版
7z a -mx9 OCR-System-Full-v1.4.1.7z dist/OCR-System/
```

## 输出位置

### 核心版
```
dist/OCR-System-Core/
├── OCR-System-Core.exe
├── models/
│   └── RapidOCR-json/
└── _internal/
```

### 完整版
```
dist/OCR-System/
├── OCR-System.exe
├── models/
│   ├── RapidOCR-json/
│   └── PaddleOCR-json/
└── _internal/
```

## 测试

### 基本测试
```bash
# 运行程序
cd dist/OCR-System-Core
./OCR-System-Core.exe

# 检查引擎
# 应该能看到RapidOCR引擎可用
```

### 体积检查
```bash
# Windows
dir dist\OCR-System-Core

# Linux/macOS
du -sh dist/OCR-System-Core
```

## 常见问题

### Q: 构建失败？
A: 检查依赖是否完整安装
```bash
pip list | grep -E "PySide6|Pillow|openpyxl|PyMuPDF"
```

### Q: 体积过大？
A: 确认使用的是 `ocr_system_core.spec`

### Q: 引擎不可用？
A: 检查 models 目录是否正确打包

## 发布清单

- [ ] 构建核心版
- [ ] 构建完整版（可选）
- [ ] 压缩打包
- [ ] 测试运行
- [ ] 检查体积
- [ ] 准备发布说明
- [ ] 上传到发布平台

## 相关文档

- [PACKAGING_STRATEGY.md](PACKAGING_STRATEGY.md) - 详细打包策略
- [README.md](README.md) - 完整打包文档
- [ENGINE_DOWNLOAD_GUIDE.md](../../ENGINE_DOWNLOAD_GUIDE.md) - 引擎下载指南

---

**提示**: 优先构建和发布核心版，为用户提供最佳体验。
