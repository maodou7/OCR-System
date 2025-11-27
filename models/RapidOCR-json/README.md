# RapidOCR-json 引擎目录

本目录用于存放 RapidOCR-json OCR引擎文件。

## 📥 下载安装

### 1. 下载引擎

**推荐版本**: v0.2.0

**下载地址**:
- [Windows x64](https://github.com/hiroi-sora/RapidOCR-json/releases/download/v0.2.0/RapidOCR-json_v0.2.0_windows_x64.7z) (约70MB)

### 2. 解压到本目录

解压后的目录结构应该是：
```
models/RapidOCR-json/
├── README.md                           # 本文件
└── RapidOCR-json_v0.2.0/               # 解压出来的文件夹
    ├── RapidOCR-json.exe               # 主程序
    ├── models/                         # 识别模型
    │   ├── config.txt
    │   ├── det.onnx                    # 检测模型
    │   ├── cls.onnx                    # 分类模型
    │   └── rec.onnx                    # 识别模型
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

- **轻量级**: 体积小（约70MB）
- **快速启动**: 启动速度极快
- **低内存**: 内存占用极低
- **基于ONNX**: 使用ONNX Runtime，跨平台性好

## 🔍 验证安装

启动主程序后：
1. 工具栏选择"OCR引擎"
2. 选择"RapidOCR-json (高性能C++)"
3. 状态栏应显示"[本地] RapidOCR-json (高性能C++) ✓ 就绪"

## 📊 与PaddleOCR对比

| 特性 | RapidOCR | PaddleOCR |
|------|----------|-----------|
| 体积 | 70MB | 300MB |
| 启动速度 | ⚡⚡⚡⚡⚡ 极快 | ⚡⚡⚡⚡ 快 |
| 识别精度 | ⭐⭐⭐ 中等 | ⭐⭐⭐⭐⭐ 极高 |
| 内存占用 | 低 | 中等 |
| 适用场景 | 快速识别、低配环境 | 高精度要求 |

## 📚 更多信息

- **项目地址**: https://github.com/hiroi-sora/RapidOCR-json
- **Release页面**: https://github.com/hiroi-sora/RapidOCR-json/releases
- **原始项目**: https://github.com/RapidAI/RapidOCR

## ⚠️ 注意

由于文件体积较大（约70MB），引擎文件不包含在Git仓库中。
每个用户需要自行下载并解压到此目录。
