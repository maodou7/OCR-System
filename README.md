# 批量OCR识别图片PDF多区域内容重命名导出表格系统

一个功能强大的批量OCR识别工具，支持图片和PDF文件的多区域识别、自动重命名和Excel导出。

## 功能特点

- ✅ **批量处理** - 支持批量导入和处理多个文件
- ✅ **多格式支持** - 支持PNG、JPG、BMP、GIF、TIFF、PDF等格式
- ✅ **多区域识别** - 可在图片上框选多个区域分别识别
- ✅ **自动重命名** - 根据识别结果自动重命名文件
- ✅ **Excel导出** - 将所有识别结果导出为Excel表格
- ✅ **可视化操作** - 直观的GUI界面，鼠标拖拽框选识别区域
- ✅ **高精度识别** - 基于PaddleOCR引擎，支持中英文识别

## 安装依赖

### 方法1：使用pip安装（推荐）

```bash
pip install -r requirements.txt
```

### 方法2：手动安装

```bash
pip install paddleocr>=2.7.0
pip install paddlepaddle>=2.5.0
pip install Pillow>=10.0.0
pip install openpyxl>=3.1.0
pip install PyMuPDF>=1.23.0
pip install numpy>=1.24.0
pip install opencv-python>=4.8.0
```

## 使用说明

### 启动程序

```bash
python main.py
```

或直接运行：

```bash
python ocr_system.py
```

### 操作步骤

1. **打开文件**
   - 点击「📂 打开文件」按钮选择单个或多个文件
   - 点击「📁 打开文件夹」按钮批量导入文件夹中的所有图片/PDF

2. **框选识别区域**
   - 确保「多区域框编辑」复选框已勾选
   - 在图片上按住鼠标左键拖拽，框选需要识别的区域
   - 可以框选多个区域
   - 右键点击区域可删除

3. **开始识别**
   - 点击「🔍 开始识别」按钮
   - 等待识别完成，结果会显示在底部文本框

4. **重命名文件**
   - 识别完成后，点击「改名并下一张」按钮
   - 程序会根据第一个区域的识别结果重命名文件
   - 自动跳转到下一张图片

5. **导出Excel**
   - 点击「💾 导出Excel」按钮
   - 选择保存位置
   - 所有识别结果将导出为Excel表格

### 快捷操作

- **双击文件列表**：快速切换到指定文件
- **右键点击区域**：删除识别区域
- **清空配置**：清除所有文件和识别记录

## 文件结构

```
批量OCR识别系统/
├── main.py              # 主启动脚本
├── ocr_system.py        # GUI主程序
├── ocr_engine.py        # OCR识别引擎封装
├── utils.py             # 工具函数（文件处理、Excel导出）
├── config.py            # 配置管理
├── requirements.txt     # 依赖包列表
└── README.md           # 说明文档
```

## 技术栈

- **GUI框架**: PySide6 (Qt)
- **OCR引擎**: 
  - PaddleOCR (主要，优化版)
  - 阿里云OCR (在线服务)
  - RapidOCR (可选，快速轻量)
- **图片处理**: Pillow (PIL)
- **PDF处理**: PyMuPDF (按需导入)
- **Excel导出**: openpyxl (按需导入)
- **数值计算**: NumPy (按需导入)

## 🚀 性能优化

本系统已采用**按需导入（Lazy Import）**策略，大幅优化性能：

### 优化效果

| 指标 | 优化前 | 优化后 | 改善 |
|------|--------|--------|------|
| 打包体积 | 800MB-1.5GB | 200-500MB | **60-75%** ↓ |
| 启动时间 | 5-10秒 | 1-2秒 | **80%** ↑ |
| 初始内存 | 500-800MB | 150-250MB | **70%** ↓ |

### 优化原理

1. **重型库延迟加载**: PyMuPDF、openpyxl 等仅在使用时加载
2. **OCR引擎按需初始化**: 后台异步加载，不阻塞UI启动
3. **智能打包配置**: Nuitka仅打包必要模块

详细说明请查看 [OPTIMIZATION.md](OPTIMIZATION.md)

## 打包发布

### 使用 Nuitka 打包（推荐）

```bash
# 安装 Nuitka
pip install nuitka

# 运行打包脚本
python build_nuitka.py
```

**打包特点**：
- ✅ 体积小（200-500MB）
- ✅ 启动快（1-2秒）
- ✅ 采用按需导入优化

### 打包配置选项

**方式1：轻量打包（默认）**
- 体积最小
- 启动最快
- OCR引擎按需加载

**方式2：完整打包**
- 修改 `build_nuitka.py`，包含所有OCR引擎
- 体积较大但完全独立
- 所有功能立即可用

## 配置说明

### 基准值设置

程序支持两个基准值的设置：
- **实测基准值**：用于存储特定的基准数据
- **较深计基准值**：用于存储另一组基准数据

这些值可以在后续的数据处理中使用。

### OCR配置

在 `config.py` 中可以修改OCR相关配置：

```python
OCR_USE_ANGLE_CLS = True  # 是否使用角度分类
OCR_LANG = 'ch'          # 语言：ch=中文, en=英文
OCR_SHOW_LOG = False     # 是否显示日志
```

## 注意事项

1. **首次运行**：首次运行时，PaddleOCR会自动下载模型文件，需要等待一段时间
2. **图片质量**：识别效果受图片清晰度影响，建议使用高分辨率图片
3. **区域框选**：框选区域时尽量贴合文字边缘，避免包含过多空白
4. **文件命名**：自动重命名时会过滤掉非法字符，如遇重名会自动添加序号

## 常见问题

### Q: 提示"OCR引擎未就绪"怎么办？
A: 请确保已正确安装PaddleOCR和PaddlePaddle：
```bash
pip install paddleocr paddlepaddle
```

### Q: 识别速度慢怎么办？
A: 
- 首次识别需要加载模型，会比较慢
- 可以考虑安装GPU版本的PaddlePaddle以提升速度
- 减小图片分辨率

### Q: 识别准确率不高怎么办？
A:
- 确保图片清晰度足够
- 框选区域时尽量精确
- 避免框选模糊或倾斜的文字

### Q: 支持哪些图片格式？
A: 支持 PNG、JPG、JPEG、BMP、GIF、TIFF、TIF 和 PDF 格式

## 更新日志

### v0.02 (2025-01-21) - 性能优化版
- 🚀 **重大优化**: 采用按需导入策略
  - 打包体积减少 60-75%（从1.5GB降至200-500MB）
  - 启动速度提升 80%（从5-10秒降至1-2秒）
  - 初始内存占用降低 70%
- ⚡ OCR引擎后台异步加载，不阻塞UI启动
- 📦 优化Nuitka打包配置，智能按需包含模块
- 🔧 重型库延迟导入（PyMuPDF、openpyxl、numpy）
- 📝 新增详细优化文档 [OPTIMIZATION.md](OPTIMIZATION.md)

### v0.01 (2025-11-20)
- ✨ 初始版本发布
- ✅ 支持多区域OCR识别
- ✅ 支持批量处理
- ✅ 支持自动重命名
- ✅ 支持Excel导出
- ✅ PySide6 (Qt) GUI界面
- ✅ 多OCR引擎支持（PaddleOCR优化版、阿里云、RapidOCR）

## 开发者信息

本系统基于Python开发，使用了以下开源项目：
- [PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR) - OCR识别引擎
- [Tkinter](https://docs.python.org/3/library/tkinter.html) - GUI框架

## 许可证

本项目仅供学习和研究使用。

## 技术支持

如有问题或建议，欢迎反馈。
