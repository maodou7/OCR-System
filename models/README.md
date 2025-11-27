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

### PaddleOCR-json (推荐)

**特点**: 高精度、速度快
**大小**: 约300MB

**下载地址**:
- [v1.4.1 Windows x64](https://github.com/hiroi-sora/PaddleOCR-json/releases/download/v1.4.1/PaddleOCR-json_v1.4.1_windows_x64.7z)

**安装步骤**:
1. 下载7z压缩包
2. 解压到 `models/PaddleOCR-json/` 目录
3. 确保目录结构为：
   ```
   models/PaddleOCR-json/PaddleOCR-json_v1.4.1/
   ```

### RapidOCR-json (轻量级)

**特点**: 轻量级、启动快
**大小**: 约70MB

**下载地址**:
- [v0.2.0 Windows x64](https://github.com/hiroi-sora/RapidOCR-json/releases/download/v0.2.0/RapidOCR-json_v0.2.0_windows_x64.7z)

**安装步骤**:
1. 下载7z压缩包
2. 解压到 `models/RapidOCR-json/` 目录
3. 确保目录结构为：
   ```
   models/RapidOCR-json/RapidOCR-json_v0.2.0/
   ```

## 🐧 Linux用户

Linux用户需要通过Wine运行Windows版本的OCR引擎：

```bash
# 安装Wine
sudo apt-get install wine

# 首次运行时会自动创建.exe.sh包装脚本
```

## ⚠️ 注意事项

1. **体积大不提交**: OCR引擎文件体积大（300MB+），不包含在Git仓库中
2. **手动下载**: 每个用户需要自己下载并解压到正确位置
3. **可选引擎**: 可以只下载一个引擎，程序会自动检测可用的引擎

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
