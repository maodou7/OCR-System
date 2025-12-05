# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller spec file for OCR System - Full Version
This file defines the build configuration for packaging the OCR System application.

PACKAGING OPTIONS:
1. Full Version (this file): Includes both PaddleOCR and RapidOCR engines (~600MB)
2. Core Version (ocr_system_core.spec): Only RapidOCR engine (~250MB, recommended)

For minimal size distribution, use ocr_system_core.spec instead.
Users can download PaddleOCR engine separately if needed.
"""

import os
import sys

# Get the project root directory
# SPECPATH is the directory containing this spec file (Pack/Pyinstaller/)
# We need to go up two levels to reach the project root
if os.path.isabs(SPECPATH):
    # SPECPATH is absolute path
    project_root = os.path.dirname(os.path.dirname(SPECPATH))
else:
    # SPECPATH is relative path, resolve it first
    spec_abs_path = os.path.abspath(SPECPATH)
    project_root = os.path.dirname(os.path.dirname(spec_abs_path))

print(f"[DEBUG] SPECPATH: {SPECPATH}")
print(f"[DEBUG] Project root: {project_root}")
print(f"[DEBUG] Entry point: {os.path.join(project_root, 'qt_run.py')}")
print(f"[DEBUG] Entry point exists: {os.path.exists(os.path.join(project_root, 'qt_run.py'))}")

# Define hidden imports that PyInstaller may not automatically detect
hidden_imports = [
    # PySide6 (Qt framework) - 只包含实际使用的模块
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    
    # PIL/Pillow
    'PIL',
    'PIL._tkinter_finder',
    'PIL.Image',
    'PIL.ImageQt',
    
    # Excel export (延迟加载，但需要在hiddenimports中)
    'openpyxl',
    'openpyxl.cell._writer',
    'openpyxl.styles',
    
    # PDF processing (延迟加载，但需要在hiddenimports中)
    'fitz',  # PyMuPDF
    
    # OCR engines - Aliyun (延迟加载，但需要在hiddenimports中)
    'alibabacloud_ocr_api20210707',
    'alibabacloud_ocr_api20210707.client',
    'alibabacloud_ocr_api20210707.models',
    'alibabacloud_tea_openapi',
    'alibabacloud_tea_openapi.client',
    'alibabacloud_tea_openapi.models',
    'alibabacloud_tea_util',
    'alibabacloud_openapi_util',
    
    # OCR engines - OpenAI/DeepSeek (延迟加载，但需要在hiddenimports中)
    'openai',
    
    # Dependency manager
    'dependency_manager',
    
    # Standard library (sometimes needed)
    'json',
    'base64',
    'socket',
    'subprocess',
    'ctypes',
]

# Define data files to include in the package
datas = [
    # OCR engine models and binaries
    (os.path.join(project_root, 'models'), 'models'),
    
    # Portable Python distribution
    (os.path.join(project_root, 'portable_python'), 'portable_python'),
    
    # Configuration template (NOT config.py - that should be external)
    (os.path.join(project_root, 'config.py.example'), '.'),
    
    # Configuration wizard for first-run setup
    
    # Environment template
    (os.path.join(project_root, '.env.example'), '.'),
]

# Define binaries to exclude (reduce package size)
excludes = [
    # GUI frameworks (not used)
    'tkinter',
    'wx',
    'PyQt5',
    'PyQt6',
    
    # PySide6 modules (not used) - 只保留QtCore, QtGui, QtWidgets
    'PySide6.Qt3DAnimation',
    'PySide6.Qt3DCore',
    'PySide6.Qt3DExtras',
    'PySide6.Qt3DInput',
    'PySide6.Qt3DLogic',
    'PySide6.Qt3DRender',
    'PySide6.QtBluetooth',
    'PySide6.QtCharts',
    'PySide6.QtConcurrent',
    'PySide6.QtDataVisualization',
    'PySide6.QtDBus',
    'PySide6.QtDesigner',
    'PySide6.QtHelp',
    'PySide6.QtLocation',
    'PySide6.QtMultimedia',
    'PySide6.QtMultimediaWidgets',
    'PySide6.QtNetwork',
    'PySide6.QtNetworkAuth',
    'PySide6.QtNfc',
    'PySide6.QtOpenGL',
    'PySide6.QtOpenGLWidgets',
    'PySide6.QtPositioning',
    'PySide6.QtPrintSupport',
    'PySide6.QtQml',
    'PySide6.QtQuick',
    'PySide6.QtQuick3D',
    'PySide6.QtQuickControls2',
    'PySide6.QtQuickWidgets',
    'PySide6.QtRemoteObjects',
    'PySide6.QtScxml',
    'PySide6.QtSensors',
    'PySide6.QtSerialPort',
    'PySide6.QtSql',
    'PySide6.QtStateMachine',
    'PySide6.QtSvg',
    'PySide6.QtSvgWidgets',
    'PySide6.QtTest',
    'PySide6.QtTextToSpeech',
    'PySide6.QtUiTools',
    'PySide6.QtWebChannel',
    'PySide6.QtWebEngine',
    'PySide6.QtWebEngineCore',
    'PySide6.QtWebEngineWidgets',
    'PySide6.QtWebSockets',
    'PySide6.QtXml',
    
    # Scientific computing (not used)
    'matplotlib',
    'scipy',
    'pandas',
    'numpy.testing',
    'numpy.distutils',
    
    # Development tools (not needed at runtime)
    'IPython',
    'jupyter',
    'notebook',
    'pytest',
    'unittest',
    'doctest',
    'pdb',
    'pydoc',
    'setuptools',
    'pip',
    'wheel',
    'distutils',
    
    # Web frameworks (not used)
    'flask',
    'django',
    'tornado',
    'aiohttp',
    
    # Database drivers (not used, we use SQLite via ctypes)
    'psycopg2',
    'pymysql',
    'sqlalchemy',
    
    # XML processing (not used)
    'lxml',
    'xml.dom',
    'xml.sax',
    
    # Compression (not used, we use built-in)
    'bz2',
    'lzma',
    
    # Networking (not used directly)
    'asyncio',
    'email',
    'ftplib',
    'http.server',
    'xmlrpc',
    
    # Multimedia (not used)
    'wave',
    'audioop',
    'aifc',
    'sunau',
    
    # Other unused modules
    'curses',
    'readline',
    'rlcompleter',
]

# Analysis: Scan the application and collect all dependencies
a = Analysis(
    [os.path.join(project_root, 'qt_run.py')],  # Entry point
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

# PYZ: Create a Python archive
pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None,
)

# UPX exclusions: Files that should not be compressed
# Some files may not work correctly when compressed with UPX
upx_exclude_list = [
    # Qt libraries - compression can cause issues with Qt plugins
    'Qt6Core.dll',
    'Qt6Gui.dll',
    'Qt6Widgets.dll',
    
    # Python DLLs - core Python runtime should not be compressed
    'python3.dll',
    'python311.dll',
    'python*.dll',
    
    # OCR engine executables - already optimized, compression may cause issues
    'PaddleOCR-json.exe',
    'RapidOCR-json.exe',
    
    # Large ML/AI libraries - compression provides minimal benefit
    'mkldnn.dll',
    'mklml.dll',
    'onnxruntime.dll',
    'paddle_inference.dll',
    'opencv_world*.dll',
    
    # System libraries - should not be compressed
    'vcruntime*.dll',
    'msvcp*.dll',
    'concrt*.dll',
    
    # SQLite and cache engine
    'sqlite3.dll',
    'ocr_cache.dll',
    'libocr_cache.so',
]

# EXE: Create the executable
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,  # onefolder mode
    name='OCR-System',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # Enable UPX compression for size reduction
    console=False,  # Hide console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon path here if available
)

# COLLECT: Collect all files for onefolder distribution
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,  # Enable UPX compression for binaries
    upx_exclude=upx_exclude_list,  # Exclude problematic files from compression
    name='OCR-System',
)
