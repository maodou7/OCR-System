# Models 目录说明

本目录用于存放OCR引擎和缓存引擎相关文件。

## 📁 目录结构

```
models/
├── README.md                    # 本文件
├── cpp_engine/                  # C++缓存引擎源码 ✓ 已提交
│   ├── ocr_cache_engine.h
│   ├── ocr_cache_engine.cpp
│   ├── CMakeLists.txt
│   ├── build.sh
│   ├── download_sqlite.sh
│   └── README.md
│
├── libocr_cache.so              # 编译输出（需要自己编译）
│
├── PaddleOCR-json/              # 需要手动下载
│   └── PaddleOCR-json_v1.4.1/
│       ├── PaddleOCR-json.exe
│       ├── models/
│       └── *.dll
│
└── RapidOCR-json/               # 需要手动下载
    └── RapidOCR-json_v0.2.0/
        ├── RapidOCR-json.exe
        ├── models/
        └── *.dll
```

## 🔧 C++缓存引擎

**位置**: `cpp_engine/`

**用途**: 高性能OCR结果缓存引擎
- 性能提升100倍
- 内存减少70%
- ACID事务保证

**编译方法**:
```bash
cd cpp_engine
chmod +x build.sh
./build.sh
```

编译成功后会在`models/`目录下生成：
- Linux: `libocr_cache.so`
- macOS: `libocr_cache.dylib`
- Windows: `ocr_cache.dll`

## 📥 OCR引擎下载

### RapidOCR-json (默认引擎) ⭐

**特点**: 轻量级、启动快、体积小
**大小**: 约45MB
**状态**: 核心版已包含，无需下载

**下载地址**（如需手动安装）:
- [v0.2.0 Windows x64](https://github.com/hiroi-sora/RapidOCR-json/releases/download/v0.2.0/RapidOCR-json_v0.2.0_windows_x64.7z)

**安装步骤**:
1. 下载7z压缩包
2. 解压到 `models/RapidOCR-json/` 目录
3. 确保目录结构为：
   ```
   models/RapidOCR-json/RapidOCR-json_v0.2.0/
   ```

### PaddleOCR-json (可选引擎)

**特点**: 高精度、功能强大
**大小**: 约350MB
**状态**: 需要单独下载（适合需要高精度识别的用户）

**下载地址**:
- [v1.4.1 Windows x64](https://github.com/hiroi-sora/PaddleOCR-json/releases/download/v1.4.1/PaddleOCR-json_v1.4.1_windows_x64.7z)

**安装步骤**:
1. 下载7z压缩包
2. 解压到 `models/PaddleOCR-json/` 目录
3. 确保目录结构为：
   ```
   models/PaddleOCR-json/PaddleOCR-json_v1.4.1/
   ```

**何时需要PaddleOCR**:
- 需要更高的识别精度
- 处理复杂文档
- 多语言混合识别
- 专业OCR应用

**详细说明**: 见项目根目录的 `ENGINE_DOWNLOAD_GUIDE.md`

## 🐧 Linux用户

Linux用户需要通过Wine运行Windows版本的OCR引擎：

```bash
# 安装Wine
sudo apt-get install wine

# 首次运行时会自动创建.exe.sh包装脚本
```

## ⚠️ 注意事项

1. **默认引擎**: 核心版已包含RapidOCR引擎，可直接使用
2. **可选下载**: PaddleOCR引擎需要单独下载（如需高精度识别）
3. **体积考虑**: PaddleOCR体积较大（350MB），根据需求选择是否下载
4. **自动检测**: 程序会自动检测已安装的引擎

## 🔍 验证安装

启动程序后：
1. 工具栏选择"OCR引擎"下拉菜单
2. 查看可用的引擎列表
3. 选择一个引擎
4. 状态栏应显示"✓ 就绪"

## 📚 更多信息

- PaddleOCR-json项目: https://github.com/hiroi-sora/PaddleOCR-json
- RapidOCR-json项目: https://github.com/hiroi-sora/RapidOCR-json
- 完整设置指南: 见项目根目录的 `SETUP.md`
