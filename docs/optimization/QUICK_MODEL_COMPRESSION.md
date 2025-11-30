# 模型压缩快速指南

## 🚀 快速开始

### 压缩模型

```bash
python model_compressor.py
```

### 测试功能

```bash
python test_model_decompression_only.py
```

## 📊 压缩效果

| 模型 | 原始 | 压缩后 | 节省 |
|------|------|--------|------|
| PaddleOCR | 260 MB | 59 MB | 77% |
| RapidOCR | 53 MB | 36 MB | 31% |
| **总计** | **313 MB** | **95 MB** | **70%** |

## ✨ 主要特性

- ✅ 最高压缩率（7z -mx9）
- ✅ 自动解压（运行时）
- ✅ 透明集成（无需手动操作）
- ✅ 性能优化（解压<10秒）

## 🔧 使用方法

### 1. 开发环境

压缩模型后，程序会自动检测并解压。无需额外配置。

### 2. 打包环境

在spec文件中只包含压缩包：

```python
datas = [
    ('models/PaddleOCR-json/*.7z', 'models/PaddleOCR-json'),
    ('models/RapidOCR-json/*.7z', 'models/RapidOCR-json'),
]
```

### 3. 用户体验

- **首次启动**: 自动解压（3-6秒）
- **后续启动**: 直接使用（无延迟）

## 📝 注意事项

1. 需要7z工具（Pack/7z-Self-Extracting/7zr.exe）
2. 首次启动会自动解压，需要几秒钟
3. 解压后的文件会保留，后续启动无延迟
4. 压缩包可以在解压后删除（可选）

## 🔍 验证

运行测试确认功能正常：

```bash
python test_model_decompression_only.py
```

预期输出：
```
✓ 导入测试: 通过
✓ 状态检查: 通过
✓ 引擎检测: 通过
✓ OCR集成: 通过

总计: 4/4 测试通过
```

## 📚 详细文档

- [完整使用指南](MODEL_COMPRESSION_GUIDE.md)
- [实施总结](MODEL_COMPRESSION_SUMMARY.md)
