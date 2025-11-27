# PaddleOCR-json 引擎目录

本目录用于存放 PaddleOCR-json OCR引擎文件。

## 📥 下载安装

### 1. 下载引擎

**推荐版本**: v1.4.1

**下载地址**:
- [Windows x64](https://github.com/hiroi-sora/PaddleOCR-json/releases/download/v1.4.1/PaddleOCR-json_v1.4.1_windows_x64.7z) (约300MB)

### 2. 解压到本目录

解压后的目录结构应该是：
```
models/PaddleOCR-json/
├── README.md                           # 本文件
└── PaddleOCR-json_v1.4.1/              # 解压出来的文件夹
    ├── PaddleOCR-json.exe              # 主程序
    ├── models/                         # 识别模型
    │   ├── config.txt
    │   ├── det/                        # 检测模型
    │   ├── cls/                        # 分类模型
    │   └── rec/                        # 识别模型
    └── *.dll                           # 依赖库
```

### 3. Linux用户

Linux系统需要通过Wine运行：

```bash
# 安装Wine
sudo apt-get install wine

# 首次运行时会自动创建.exe.sh包装脚本
```

## ✨ 引擎特点

- **高精度**: 基于PaddleOCR v2.8
- **高性能**: C++实现，速度提升3-5倍
- **低内存**: 相比Python版本内存占用减少50%+
- **稳定性**: 进程隔离，更加稳定

## 🔍 验证安装

启动主程序后：
1. 工具栏选择"OCR引擎"
2. 选择"PaddleOCR-json (高性能C++)"
3. 状态栏应显示"[本地] PaddleOCR-json (高性能C++) ✓ 就绪"

## 📚 更多信息

- **项目地址**: https://github.com/hiroi-sora/PaddleOCR-json
- **Release页面**: https://github.com/hiroi-sora/PaddleOCR-json/releases

## ⚠️ 注意

由于文件体积较大（约300MB），引擎文件不包含在Git仓库中。
每个用户需要自行下载并解压到此目录。
