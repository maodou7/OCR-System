# Nuitka编译说明

## 快速开始

### 1. 安装Nuitka
```bash
pip install nuitka
```

### 2. 运行编译脚本
```bash
python build_nuitka.py
```

### 3. 选择编译模式
- **选项1**: 单文件模式（推荐）- 生成单个可执行文件
- **选项2**: 目录模式 - 生成包含所有依赖的目录
- **选项3**: 清理构建文件

---

## 编译模式对比

| 模式 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| **单文件** | 便于分发，一个文件包含所有 | 首次启动稍慢（解压） | 分发给用户 |
| **目录** | 启动快，体积可能更小 | 文件多，需打包整个目录 | 本地使用 |

---

## 编译参数说明

### 基本参数
- `--standalone`: 独立模式，包含所有Python依赖
- `--onefile`: 打包成单个可执行文件
- `--output-dir=dist`: 输出到dist目录

### 包含模块
```python
--include-package=PySide6          # Qt GUI框架
--include-package=PIL              # 图像处理
--include-package=numpy            # 数值计算
--include-package=paddleocr        # PaddleOCR引擎
--include-package=rapidocr_onnxruntime  # RapidOCR引擎
--include-package=alibabacloud_ocr_api20210707  # 阿里云OCR
--include-package=openai           # DeepSeek OCR
--include-module=openpyxl          # Excel导出
--include-module=fitz              # PDF处理
```

### 性能优化
- `--lto=yes`: 链接时优化
- `--jobs=8`: 8线程并行编译

---

## 编译流程

### 1. 准备阶段
```bash
# 确保在虚拟环境中
source .venv/bin/activate

# 安装所有依赖
pip install -r requirements.txt

# 安装Nuitka
pip install nuitka
```

### 2. 执行编译
```bash
# 方式1: 使用编译脚本（推荐）
python build_nuitka.py

# 方式2: 直接运行Nuitka命令
python -m nuitka --standalone --onefile qt_run.py
```

### 3. 测试可执行文件
```bash
cd dist
./OCR-System
```

---

## 预期编译时间

| 环境 | 编译时间 | 包大小 |
|------|----------|--------|
| 第一次完整编译 | 10-30分钟 | 200-500MB |
| 增量编译（修改代码后） | 2-5分钟 | - |

**注意**: 首次编译会下载并编译所有依赖，需要较长时间

---

## 常见问题

### Q1: 编译提示缺少模块？
**A**: 在`build_nuitka.py`中添加对应的`--include-package`或`--include-module`

### Q2: 编译后体积很大？
**A**: 
- 使用目录模式而非单文件模式
- 移除不必要的OCR引擎依赖
- 使用`--lto=yes`优化

### Q3: 运行时提示找不到模型文件？
**A**: PaddleOCR模型文件需要确保被包含：
```python
--include-data-dir=/path/to/paddleocr=paddleocr
```

### Q4: Linux下编译后无法运行？
**A**: 添加执行权限：
```bash
chmod +x dist/OCR-System
```

---

## 高级配置

### 轻量级打包（仅PaddleOCR）
如果只需要PaddleOCR引擎，可以移除其他引擎：

```python
# 移除这些行
# --include-package=rapidocr_onnxruntime
# --include-package=alibabacloud_ocr_api20210707
# --include-package=openai
```

### 包含图标（Windows）
```python
--windows-icon-from-ico=icon.ico
```

### 禁用控制台（Windows）
```python
--windows-console-mode=disable
```

---

## 性能建议

1. **首次编译**: 使用`--show-progress`和`--show-memory监控进度
2. **增量编译**: 只修改Python代码时会快很多
3. **并行编译**: 根据CPU核心数调整`--jobs`参数
4. **清理缓存**: 遇到问题时运行"清理构建文件"

---

## 分发清单

编译完成后，分发以下文件/目录：

### 单文件模式
```
dist/
└── OCR-System        # 可执行文件（Linux/Mac）
    或 OCR-System.exe  # Windows
```

### 目录模式
```
dist/
└── OCR-System.dist/  # 整个目录都需要
    ├── OCR-System
    ├── 各种.so/.dll文件
    └── 依赖库
```

---

## 许可证说明

编译后的程序需要遵守以下许可证：
- PaddleOCR: Apache 2.0
- PySide6: LGPL
- OpenAI SDK: MIT
- 本项目: MIT

请在分发时附带LICENSE文件。
