# 字体文件使用分析报告

## 1. 字体文件扫描结果

✓ **未发现内嵌字体文件**

## 2. 代码中的字体使用分析

### 2.1 QFont使用情况

发现 10 处QFont使用:

- **.\analyze_font_usage.py** (行 61)
  ```python
  if 'QFont' in line and not line.strip().startswith('#'):
  ```

- **.\analyze_font_usage.py** (行 130)
  ```python
  report.append("### 2.1 QFont使用情况")
  ```

- **.\analyze_font_usage.py** (行 133)
  ```python
  report.append(f"发现 {len(font_usage['qfont_usage'])} 处QFont使用:")
  ```

- **.\analyze_font_usage.py** (行 142)
  ```python
  report.append("未发现QFont使用")
  ```

- **.\analyze_font_usage.py** (行 218)
  ```python
  report.append("- 代码中使用了QFont，但未指定特定字体族")
  ```

- **.\analyze_font_usage.py** (行 267)
  ```python
  print(f"   - QFont使用: {len(font_usage['qfont_usage'])} 处")
  ```

- **.\qt_main.py** (行 166)
  ```python
  from PySide6.QtGui import QFont, QBrush, QColor
  ```

- **.\qt_main.py** (行 167)
  ```python
  font = QFont()
  ```

- **.\dist\OCR-System\_internal\portable_python\Lib\site-packages\PySide6\scripts\qtpy2cpp_lib\qt.py** (行 50)
  ```python
  "QFontDialog": ClassFlag.INSTANTIATE_ON_STACK,
  ```

- **.\portable_python\Lib\site-packages\PySide6\scripts\qtpy2cpp_lib\qt.py** (行 50)
  ```python
  "QFontDialog": ClassFlag.INSTANTIATE_ON_STACK,
  ```

### 2.2 字体族设置

发现 1 处字体族设置:

- **.\analyze_font_usage.py** (行 69)
  ```python
  if 'setFamily' in line or 'FontFamily' in line:
  ```

### 2.3 字体文件引用

发现 29 处字体文件引用:

- **.\analyze_font_usage.py** (行 15)
  ```python
  font_extensions = ['.ttf', '.otf', '.woff', '.woff2', '.eot']
  ```

- **.\analyze_font_usage.py** (行 78)
  ```python
  if any(ext in line for ext in ['.ttf', '.otf', '.woff']):
  ```

- **.\evaluate_mobile_vs_server_models.py** (行 176)
  ```python
  for font_name in ["msyh.ttc", "simhei.ttf", "simsun.ttc", "arial.ttf"]:
  ```

- **.\evaluate_mobile_vs_server_models.py** (行 183)
  ```python
  font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
  ```

- **.\ocr_engine_deepseek.py** (行 310)
  ```python
  font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
  ```

- **.\dist\OCR-System\_internal\portable_python\Lib\site-packages\PIL\ImageDraw.py** (行 115)
  ```python
  draw.font = ImageFont.truetype("Tests/fonts/FreeMono.ttf")
  ```

- **.\dist\OCR-System\_internal\portable_python\Lib\site-packages\PIL\ImageDraw.py** (行 120)
  ```python
  ImageDraw.ImageDraw.font = ImageFont.truetype("Tests/fonts/FreeMono.ttf")
  ```

- **.\dist\OCR-System\_internal\portable_python\Lib\site-packages\PIL\ImageFont.py** (行 899)
  ```python
  if os.path.splitext(fontpath)[1] == ".ttf":
  ```

- **.\dist\OCR-System\_internal\portable_python\Lib\site-packages\pip\_vendor\rich\_export_format.py** (行 28)
  ```python
  url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff2/FiraCode-Regular.woff2") format("woff2"),
  ```

- **.\dist\OCR-System\_internal\portable_python\Lib\site-packages\pip\_vendor\rich\_export_format.py** (行 29)
  ```python
  url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff/FiraCode-Regular.woff") format("woff");
  ```

- **.\dist\OCR-System\_internal\portable_python\Lib\site-packages\pip\_vendor\rich\_export_format.py** (行 36)
  ```python
  url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff2/FiraCode-Bold.woff2") format("woff2"),
  ```

- **.\dist\OCR-System\_internal\portable_python\Lib\site-packages\pip\_vendor\rich\_export_format.py** (行 37)
  ```python
  url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff/FiraCode-Bold.woff") format("woff");
  ```

- **.\dist\OCR-System\_internal\portable_python\Lib\site-packages\PyInstaller\loader\pyimod02_importers.py** (行 580)
  ```python
  (importlib_resources tries to use 'fonts/wx_symbols.ttf' as a temporary filename suffix, which fails as it contains
  ```

- **.\dist\OCR-System\_internal\portable_python\Lib\site-packages\pymupdf\__init__.py** (行 7578)
  ```python
  oldfont_path = f"{tmp_dir}/oldfont.ttf"
  ```

- **.\dist\OCR-System\_internal\portable_python\Lib\site-packages\pymupdf\__init__.py** (行 7579)
  ```python
  newfont_path = f"{tmp_dir}/newfont.ttf"
  ```

- **.\dist\OCR-System\_internal\portable_python\Lib\site-packages\_pyinstaller_hooks_contrib\stdhooks\hook-cv2.py** (行 161)
  ```python
  for font_file in qt_fonts_dir.rglob('*.ttf')
  ```

- **.\dist\OCR-System\_internal\portable_python\Lib\site-packages\_pyinstaller_hooks_contrib\stdhooks\hook-z3c.rml.py** (行 23)
  ```python
  "fonts/Vera*.ttf",
  ```

- **.\portable_python\Lib\site-packages\PIL\ImageDraw.py** (行 115)
  ```python
  draw.font = ImageFont.truetype("Tests/fonts/FreeMono.ttf")
  ```

- **.\portable_python\Lib\site-packages\PIL\ImageDraw.py** (行 120)
  ```python
  ImageDraw.ImageDraw.font = ImageFont.truetype("Tests/fonts/FreeMono.ttf")
  ```

- **.\portable_python\Lib\site-packages\PIL\ImageFont.py** (行 899)
  ```python
  if os.path.splitext(fontpath)[1] == ".ttf":
  ```

- **.\portable_python\Lib\site-packages\pip\_vendor\rich\_export_format.py** (行 28)
  ```python
  url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff2/FiraCode-Regular.woff2") format("woff2"),
  ```

- **.\portable_python\Lib\site-packages\pip\_vendor\rich\_export_format.py** (行 29)
  ```python
  url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff/FiraCode-Regular.woff") format("woff");
  ```

- **.\portable_python\Lib\site-packages\pip\_vendor\rich\_export_format.py** (行 36)
  ```python
  url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff2/FiraCode-Bold.woff2") format("woff2"),
  ```

- **.\portable_python\Lib\site-packages\pip\_vendor\rich\_export_format.py** (行 37)
  ```python
  url("https://cdnjs.cloudflare.com/ajax/libs/firacode/6.2.0/woff/FiraCode-Bold.woff") format("woff");
  ```

- **.\portable_python\Lib\site-packages\PyInstaller\loader\pyimod02_importers.py** (行 580)
  ```python
  (importlib_resources tries to use 'fonts/wx_symbols.ttf' as a temporary filename suffix, which fails as it contains
  ```

- **.\portable_python\Lib\site-packages\pymupdf\__init__.py** (行 7578)
  ```python
  oldfont_path = f"{tmp_dir}/oldfont.ttf"
  ```

- **.\portable_python\Lib\site-packages\pymupdf\__init__.py** (行 7579)
  ```python
  newfont_path = f"{tmp_dir}/newfont.ttf"
  ```

- **.\portable_python\Lib\site-packages\_pyinstaller_hooks_contrib\stdhooks\hook-cv2.py** (行 161)
  ```python
  for font_file in qt_fonts_dir.rglob('*.ttf')
  ```

- **.\portable_python\Lib\site-packages\_pyinstaller_hooks_contrib\stdhooks\hook-z3c.rml.py** (行 23)
  ```python
  "fonts/Vera*.ttf",
  ```

## 3. PySide6字体机制

- **使用系统字体**: True
- **说明**: PySide6/Qt默认使用系统字体，无需内嵌字体文件

## 4. 优化建议

### ✓ 无内嵌字体文件

**当前状态**: 项目未内嵌字体文件，使用系统字体

**优势**:

1. **体积小**: 无需打包字体文件
2. **兼容性好**: 使用用户系统的字体，显示效果更自然
3. **维护简单**: 无需管理字体文件版本

**建议**: 保持当前方案，继续使用系统字体

### 代码优化建议

**当前字体使用方式**:

- 代码中使用了QFont，但未指定特定字体族
- 这是推荐的做法，让Qt使用系统默认字体

**建议**: 保持当前实现，无需修改

## 5. 总结

⚠ **需要优化**

- 发现 29 处字体文件引用

**验证需求 5.2**: ⚠ 需要优化 - 建议移除内嵌字体文件

---

*报告生成时间: 2025-11-28 23:58:58*