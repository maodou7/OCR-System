# PySide6 依赖分析报告

## 分析日期
2025-11-28

## 使用的 PySide6 模块

### QtCore
- Qt (枚举和常量)
- QRect (矩形)
- QPoint (点)
- Signal (信号)
- QObject (对象基类)
- QSize (尺寸)
- QThread (线程)
- QTimer (定时器)

### QtGui
- QAction (动作)
- QPixmap (像素图)
- QPainter (绘图)
- QPen (画笔)
- QGuiApplication (GUI应用)
- QFont (字体)
- QBrush (画刷)
- QColor (颜色)
- QImage (图像)

### QtWidgets
- QApplication (应用程序)
- QMainWindow (主窗口)
- QWidget (控件)
- QFileDialog (文件对话框)
- QVBoxLayout (垂直布局)
- QHBoxLayout (水平布局)
- QLabel (标签)
- QSplitter (分割器)
- QTableWidget (表格控件)
- QTableWidgetItem (表格项)
- QToolBar (工具栏)
- QPushButton (按钮)
- QHeaderView (表头视图)
- QComboBox (下拉框)
- QTextEdit (文本编辑器)
- QMessageBox (消息框)

## 评估结果

### 1. 是否可以使用更轻量的Qt绑定？

#### PyQt6-lite
- **不存在**: PyQt6没有官方的"lite"版本
- **PyQt6 vs PySide6**: 两者功能相同，体积相近
- **结论**: 不存在更轻量的替代方案

#### PyQt5
- **体积**: 与PySide6相近
- **功能**: 较旧的Qt5版本
- **结论**: 不推荐降级，无明显体积优势

### 2. 为什么不能使用更轻量的方案？

#### 系统需求分析
本系统是一个**完整的GUI应用程序**，需要：

1. **复杂的窗口管理**
   - 主窗口（QMainWindow）
   - 工具栏（QToolBar）
   - 分割器（QSplitter）
   - 多种布局（QVBoxLayout, QHBoxLayout）

2. **丰富的控件**
   - 表格控件（QTableWidget）- 显示识别结果
   - 文本编辑器（QTextEdit）- 编辑识别文本
   - 图像显示（QLabel + QPixmap）- 显示图片
   - 文件对话框（QFileDialog）- 选择文件
   - 下拉框（QComboBox）- 选择OCR引擎

3. **高级功能**
   - 自定义绘图（QPainter）- 绘制识别框
   - 鼠标事件处理 - 框选区域
   - 多线程（QThread）- 异步OCR识别
   - 信号槽机制（Signal）- 事件通信

#### 轻量级GUI框架对比

| 框架 | 体积 | 功能 | 适用场景 | 是否适合本项目 |
|------|------|------|----------|---------------|
| **PySide6/PyQt6** | ~100MB | 完整 | 复杂GUI应用 | ✅ 适合 |
| **PyQt5/PySide2** | ~100MB | 完整 | 复杂GUI应用 | ⚠️ 较旧，无优势 |
| **Tkinter** | ~5MB | 基础 | 简单GUI | ❌ 功能不足 |
| **wxPython** | ~50MB | 较完整 | 中等GUI | ❌ 功能不足 |
| **Kivy** | ~30MB | 触摸优先 | 移动应用 | ❌ 不适合桌面 |
| **PySimpleGUI** | ~5MB | 简化封装 | 简单GUI | ❌ 功能不足 |

**结论**: 
- Tkinter、wxPython等轻量级框架**无法满足**本系统的复杂需求
- 本系统需要：表格控件、自定义绘图、多线程、丰富的事件处理
- PySide6是**最合适**的选择

### 3. 优化方案

虽然不能替换PySide6，但可以通过以下方式优化：

#### 3.1 打包时优化（推荐）

在PyInstaller打包时，仅包含使用的Qt模块：

```python
# ocr_system.spec
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui', 
    'PySide6.QtWidgets',
]

# 排除未使用的Qt模块
excludes = [
    'PySide6.QtNetwork',      # 网络模块（未使用）
    'PySide6.QtWebEngine',    # Web引擎（未使用）
    'PySide6.QtMultimedia',   # 多媒体（未使用）
    'PySide6.QtSql',          # SQL（未使用）
    'PySide6.Qt3D',           # 3D（未使用）
    'PySide6.QtCharts',       # 图表（未使用）
    'PySide6.QtDataVisualization',  # 数据可视化（未使用）
]
```

**预计节省**: 30-50MB

#### 3.2 排除Qt插件和翻译文件

```python
# 排除未使用的Qt插件
datas = [
    # 仅包含必需的Qt插件
    ('venv/Lib/site-packages/PySide6/plugins/platforms', 'PySide6/plugins/platforms'),
    ('venv/Lib/site-packages/PySide6/plugins/styles', 'PySide6/plugins/styles'),
]

# 排除翻译文件（如果不需要多语言）
excludes += [
    'PySide6.translations',
]
```

**预计节省**: 10-20MB

#### 3.3 使用UPX压缩

```python
# 启用UPX压缩
upx = True
upx_exclude = [
    'Qt6Core.dll',  # Qt核心库不压缩（避免启动变慢）
    'Qt6Gui.dll',
    'Qt6Widgets.dll',
]
```

**预计节省**: 20-40MB

### 4. 总结

#### 评估结论
- ❌ **不能**使用更轻量的Qt绑定（不存在或功能不足）
- ✅ **必须**保留PySide6（系统核心依赖）
- ✅ **可以**通过打包优化减小体积

#### 优化建议
1. ✅ 保留PySide6作为GUI框架
2. ✅ 在打包时排除未使用的Qt模块
3. ✅ 排除未使用的Qt插件和翻译文件
4. ✅ 使用UPX压缩（部分DLL）

#### 预计优化效果
- 打包体积减少: 50-100MB
- 功能: 完全保留
- 性能: 无影响或略有提升

## 下一步行动

1. ✅ 记录PySide6为核心依赖，必须保留
2. 更新PyInstaller配置，排除未使用的Qt模块
3. 测试打包后的程序功能完整性
