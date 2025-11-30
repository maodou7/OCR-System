# OCR系统打包策略文档

## 概述

本文档描述OCR系统的打包策略，包括两种打包方案的选择和实施方法。

## 打包方案对比

### 方案1：完整版（Full Version）

**配置文件**: `ocr_system.spec`

**包含内容**:
- RapidOCR引擎（~45MB）
- PaddleOCR引擎（~350MB）
- 所有核心功能
- C++缓存引擎

**打包大小**:
- 未压缩：~600MB
- 7z压缩后：~300MB

**优点**:
- ✅ 开箱即用，包含所有引擎
- ✅ 用户无需额外下载
- ✅ 适合离线环境

**缺点**:
- ❌ 体积较大
- ❌ 下载时间长
- ❌ 包含用户可能不需要的引擎

**适用场景**:
- 企业内部部署
- 离线环境使用
- 需要最高精度识别
- 网络条件差的地区

### 方案2：核心版（Core Version）⭐ 推荐

**配置文件**: `ocr_system_core.spec`

**包含内容**:
- RapidOCR引擎（~45MB）
- 所有核心功能
- C++缓存引擎
- 引擎下载指南

**打包大小**:
- 未压缩：~250MB
- 7z压缩后：~120MB

**优点**:
- ✅ 体积小，下载快
- ✅ 满足大多数使用需求
- ✅ 支持按需下载PaddleOCR
- ✅ 节省存储空间

**缺点**:
- ⚠️ 需要高精度时需额外下载
- ⚠️ 首次使用PaddleOCR需要网络

**适用场景**:
- 个人用户
- 日常文档识别
- 网络条件良好
- 对体积敏感的场景

## 推荐策略

### 默认发布：核心版

**原因**:
1. **体积优势**: 250MB vs 600MB，减少60%
2. **下载速度**: 用户可以更快获取软件
3. **灵活性**: 用户可以按需选择引擎
4. **存储友好**: 节省用户磁盘空间

### 可选发布：完整版

**提供场景**:
1. 企业版本
2. 离线安装包
3. 特殊需求用户

## 实施方案

### 1. 构建核心版（推荐）

```bash
# Windows
cd Pack\Pyinstaller
pyinstaller ocr_system_core.spec

# Linux/macOS
cd Pack/Pyinstaller
pyinstaller ocr_system_core.spec
```

**输出**:
- `dist/OCR-System-Core/` - 核心版程序文件夹

**压缩分发**:
```bash
# 使用7-Zip最高压缩率
7z a -mx9 OCR-System-Core-v1.4.1.7z dist/OCR-System-Core/

# 预期大小：~120MB
```

### 2. 构建完整版（可选）

```bash
# Windows
cd Pack\Pyinstaller
pyinstaller ocr_system.spec

# Linux/macOS
cd Pack/Pyinstaller
pyinstaller ocr_system.spec
```

**输出**:
- `dist/OCR-System/` - 完整版程序文件夹

**压缩分发**:
```bash
# 使用7-Zip最高压缩率
7z a -mx9 OCR-System-Full-v1.4.1.7z dist/OCR-System/

# 预期大小：~300MB
```

## 引擎下载机制

### 自动下载（未来实现）

核心版用户可以通过程序内置的下载功能获取PaddleOCR引擎：

1. 启动程序
2. 选择"OCR引擎" → "PaddleOCR"
3. 系统提示下载
4. 自动下载并安装
5. 完成后可立即使用

### 手动下载（当前方案）

用户可以手动下载PaddleOCR引擎：

1. 访问下载页面
2. 下载引擎压缩包
3. 解压到 `models/PaddleOCR-json/` 目录
4. 重启程序即可使用

**详细说明**: 见 `ENGINE_DOWNLOAD_GUIDE.md`

## 配置文件说明

### ocr_system_core.spec 关键配置

```python
# 只包含RapidOCR引擎
datas = [
    (os.path.join(project_root, 'models', 'RapidOCR-json'), 'models/RapidOCR-json'),
    # PaddleOCR引擎不包含，用户可选下载
]

# 排除在线OCR依赖（进一步减小体积）
excludes = [
    'alibabacloud_ocr_api20210707',
    'openai',
    # ...
]
```

### ocr_system.spec 关键配置

```python
# 包含所有引擎
datas = [
    (os.path.join(project_root, 'models'), 'models'),
    # 包含完整models目录
]
```

## 版本命名规范

### 核心版

```
OCR-System-Core-v{version}-{platform}.{ext}

示例:
- OCR-System-Core-v1.4.1-win64.7z
- OCR-System-Core-v1.4.1-linux64.tar.gz
- OCR-System-Core-v1.4.1-macos.zip
```

### 完整版

```
OCR-System-Full-v{version}-{platform}.{ext}

示例:
- OCR-System-Full-v1.4.1-win64.7z
- OCR-System-Full-v1.4.1-linux64.tar.gz
- OCR-System-Full-v1.4.1-macos.zip
```

## 发布清单

### 核心版发布包

```
OCR-System-Core-v1.4.1/
├── OCR-System-Core.exe          # 主程序
├── config.py.example            # 配置模板
├── .env.example                 # 环境变量模板
├── ENGINE_DOWNLOAD_GUIDE.md     # 引擎下载指南
├── README.md                    # 使用说明
├── models/
│   ├── RapidOCR-json/          # RapidOCR引擎
│   ├── ocr_cache.dll           # 缓存引擎
│   └── README.md               # 模型说明
└── _internal/                   # PyInstaller内部文件
```

### 完整版发布包

```
OCR-System-Full-v1.4.1/
├── OCR-System.exe               # 主程序
├── config.py.example            # 配置模板
├── .env.example                 # 环境变量模板
├── README.md                    # 使用说明
├── models/
│   ├── PaddleOCR-json/         # PaddleOCR引擎
│   ├── RapidOCR-json/          # RapidOCR引擎
│   ├── ocr_cache.dll           # 缓存引擎
│   └── README.md               # 模型说明
└── _internal/                   # PyInstaller内部文件
```

## 下载页面建议

### GitHub Releases 页面

```markdown
## 下载

### 核心版（推荐）⭐
适合大多数用户，体积小，启动快

- [Windows 64位](链接) - 120MB
- [Linux 64位](链接) - 110MB
- [macOS](链接) - 115MB

### 完整版
包含所有OCR引擎，适合离线环境

- [Windows 64位](链接) - 300MB
- [Linux 64位](链接) - 280MB
- [macOS](链接) - 290MB

### 引擎单独下载
如果您使用核心版，可以按需下载：

- [PaddleOCR引擎](链接) - 350MB

## 如何选择？

- **日常使用**: 下载核心版即可
- **高精度需求**: 下载核心版 + PaddleOCR引擎
- **离线环境**: 下载完整版
```

## 用户引导流程

### 首次启动（核心版）

1. 用户启动程序
2. 系统检测到只有RapidOCR引擎
3. 显示欢迎提示：
   ```
   欢迎使用OCR系统！
   
   当前使用RapidOCR引擎（轻量级，适合日常使用）
   
   如需更高精度识别，可以下载PaddleOCR引擎：
   - 在"OCR引擎"菜单中选择"下载PaddleOCR"
   - 或访问：[下载链接]
   
   [不再提示] [了解更多] [开始使用]
   ```

### 切换引擎时（未安装）

1. 用户选择"PaddleOCR"引擎
2. 系统检测到未安装
3. 显示下载提示：
   ```
   PaddleOCR引擎未安装
   
   PaddleOCR提供更高的识别精度，适合复杂文档。
   大小：约350MB
   
   [自动下载] [手动下载] [取消]
   ```

## 测试清单

### 核心版测试

- [ ] 程序正常启动
- [ ] RapidOCR引擎可用
- [ ] 基本OCR功能正常
- [ ] 文件大小符合预期（~250MB）
- [ ] 压缩后大小符合预期（~120MB）
- [ ] 引擎下载指南文件存在

### 完整版测试

- [ ] 程序正常启动
- [ ] RapidOCR引擎可用
- [ ] PaddleOCR引擎可用
- [ ] 引擎切换正常
- [ ] 文件大小符合预期（~600MB）
- [ ] 压缩后大小符合预期（~300MB）

### 引擎下载测试

- [ ] 手动下载PaddleOCR成功
- [ ] 解压到正确位置
- [ ] 程序识别新引擎
- [ ] 引擎切换成功
- [ ] OCR功能正常

## 性能对比

| 指标 | 核心版 | 完整版 |
|------|--------|--------|
| 下载大小 | 120MB | 300MB |
| 安装大小 | 250MB | 600MB |
| 启动时间 | 1-2秒 | 1-2秒 |
| 内存占用 | 150MB | 150MB |
| 可用引擎 | 1个 | 2个 |

## 成本效益分析

### 核心版优势

1. **带宽节省**: 每次下载节省180MB
2. **存储节省**: 每个安装节省350MB
3. **用户体验**: 更快的下载和安装
4. **灵活性**: 用户按需选择

### 完整版优势

1. **即用性**: 无需额外下载
2. **离线友好**: 适合无网络环境
3. **功能完整**: 包含所有引擎

## 建议

### 对于开发者

1. **默认构建**: 使用核心版配置
2. **定期构建**: 同时提供完整版
3. **文档完善**: 提供清晰的引擎下载指南
4. **自动化**: 考虑实现自动下载功能

### 对于用户

1. **首选核心版**: 满足大多数需求
2. **按需下载**: 需要时再获取PaddleOCR
3. **网络条件**: 根据网络情况选择版本
4. **存储空间**: 考虑可用磁盘空间

## 未来改进

### 短期（v1.5）

- [ ] 实现程序内自动下载PaddleOCR
- [ ] 添加下载进度显示
- [ ] 支持断点续传
- [ ] 提供多个下载源

### 中期（v2.0）

- [ ] 实现引擎管理器
- [ ] 支持更多引擎选择
- [ ] 引擎版本管理
- [ ] 自动更新检测

### 长期（v3.0）

- [ ] 云端引擎库
- [ ] 一键安装所有引擎
- [ ] 引擎性能对比工具
- [ ] 智能引擎推荐

## 相关文档

- [ENGINE_DOWNLOAD_GUIDE.md](../../ENGINE_DOWNLOAD_GUIDE.md) - 引擎下载指南
- [README.md](README.md) - 打包文档
- [models/README.md](../../models/README.md) - 模型说明

## 更新日志

| 版本 | 日期 | 更新内容 |
|------|------|----------|
| v1.0 | 2024-11-28 | 初始版本，定义核心版和完整版打包策略 |

---

**推荐**: 优先使用核心版进行分发，为用户提供更好的下载体验。
