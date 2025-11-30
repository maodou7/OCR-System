# OCR引擎下载指南

## 概述

OCR系统支持两种本地OCR引擎，您可以根据需求选择下载：

| 引擎 | 特点 | 大小 | 推荐场景 |
|------|------|------|----------|
| **RapidOCR** | 轻量级、启动快、体积小 | ~45MB | 默认打包，适合日常使用 |
| **PaddleOCR** | 高精度、功能强大 | ~350MB | 可选下载，需要高精度识别 |

## 默认配置

核心版本（Core Version）默认只包含 **RapidOCR** 引擎，这是一个轻量级的OCR引擎，适合大多数使用场景。

## 下载PaddleOCR引擎

如果您需要更高的识别精度，可以下载PaddleOCR引擎：

### 方法1：自动下载（推荐）

1. 启动OCR系统
2. 在工具栏选择"OCR引擎"下拉菜单
3. 选择"PaddleOCR（高性能C++版）"
4. 系统会提示下载，点击"确定"
5. 等待下载和安装完成
6. 自动切换到PaddleOCR引擎

### 方法2：手动下载

#### Windows系统

1. **下载引擎包**
   - 访问：https://github.com/hiroi-sora/PaddleOCR-json/releases
   - 下载：`PaddleOCR-json_v1.4.1_windows_x64.7z` (约350MB)

2. **解压到正确位置**
   ```
   OCR-System/
   └── models/
       └── PaddleOCR-json/
           └── PaddleOCR-json_v1.4.1/
               ├── PaddleOCR-json.exe
               ├── models/
               └── *.dll
   ```

3. **验证安装**
   - 重启OCR系统
   - 在"OCR引擎"下拉菜单中应该能看到"PaddleOCR（高性能C++版）"
   - 选择该引擎，状态栏应显示"✓ 就绪"

#### Linux系统

1. **下载引擎包**
   - 访问：https://github.com/hiroi-sora/PaddleOCR-json/releases
   - 下载对应Linux版本

2. **安装Wine（如果使用Windows版本）**
   ```bash
   sudo apt-get install wine
   ```

3. **解压到正确位置**
   ```bash
   cd OCR-System/models/
   7z x PaddleOCR-json_v1.4.1_windows_x64.7z
   ```

4. **验证安装**
   ```bash
   ./OCR-System
   ```

## 引擎对比

### RapidOCR（默认）

**优点**：
- ✅ 体积小（45MB）
- ✅ 启动快
- ✅ 内存占用低
- ✅ 适合日常使用

**缺点**：
- ⚠️ 精度略低于PaddleOCR
- ⚠️ 对复杂场景支持较弱

**适用场景**：
- 日常文档识别
- 简单图片文字提取
- 对体积和速度有要求

### PaddleOCR（可选）

**优点**：
- ✅ 识别精度极高
- ✅ 支持复杂场景
- ✅ 支持多种语言
- ✅ 功能强大

**缺点**：
- ⚠️ 体积较大（350MB）
- ⚠️ 启动稍慢
- ⚠️ 内存占用较高

**适用场景**：
- 需要高精度识别
- 复杂文档处理
- 多语言混合识别
- 专业OCR应用

## 引擎切换

安装多个引擎后，可以随时切换：

1. 点击工具栏的"OCR引擎"下拉菜单
2. 选择想要使用的引擎
3. 系统会自动切换并初始化
4. 状态栏显示"✓ 就绪"表示切换成功

## 配置说明

### 启用/禁用引擎

编辑 `config.py` 文件：

```python
# 本地OCR引擎配置
PADDLE_ENABLED = True   # 启用PaddleOCR
RAPID_ENABLED = True    # 启用RapidOCR
```

### 设置默认引擎

```python
# 默认使用的引擎
OCR_ENGINE = 'rapid'  # 可选: 'paddle', 'rapid'
```

## 存储空间要求

| 配置 | 所需空间 |
|------|---------|
| 仅RapidOCR（默认） | ~250MB |
| RapidOCR + PaddleOCR | ~600MB |
| 完整版（含在线OCR） | ~650MB |

## 网络要求

### 自动下载

- 需要稳定的网络连接
- 下载速度取决于网络带宽
- 支持断点续传（部分实现）

### 手动下载

- 可以在任何有网络的地方下载
- 通过U盘等方式传输到目标机器
- 适合网络受限环境

## 常见问题

### Q1: 下载失败怎么办？

**A**: 尝试以下方法：
1. 检查网络连接
2. 使用手动下载方式
3. 从备用下载源获取
4. 联系技术支持

### Q2: 引擎无法启动？

**A**: 检查以下项：
1. 文件是否完整解压
2. 目录结构是否正确
3. 是否有执行权限（Linux）
4. 是否缺少运行库（Windows需要VC++ Redistributable）

### Q3: 如何卸载引擎？

**A**: 直接删除对应文件夹：
```
models/PaddleOCR-json/  # 删除此文件夹即可卸载PaddleOCR
models/RapidOCR-json/   # 删除此文件夹即可卸载RapidOCR
```

### Q4: 可以同时使用两个引擎吗？

**A**: 可以！系统支持安装多个引擎，可以随时切换使用。

### Q5: 哪个引擎更好？

**A**: 取决于您的需求：
- 日常使用：RapidOCR（快速、轻量）
- 专业应用：PaddleOCR（高精度）
- 建议：先使用RapidOCR，如果精度不够再下载PaddleOCR

## 技术支持

如有问题，请：
1. 查看 `models/README.md` 文件
2. 访问项目GitHub页面
3. 提交Issue反馈

## 更新日志

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0 | 2024-11-28 | 初始版本，支持引擎可选下载 |

---

**提示**: 建议先使用默认的RapidOCR引擎，如果识别效果不满意，再下载PaddleOCR引擎。
