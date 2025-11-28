# -*- mode: python ; coding: utf-8 -*-

"""
PyInstaller spec file for OCR System
This file defines the build configuration for packaging the OCR System application.
"""

import os
import sys

# Get the project root directory (two levels up from this spec file)
spec_dir = os.path.dirname(os.path.abspath(SPECPATH))
project_root = os.path.dirname(os.path.dirname(spec_dir))

# Define hidden imports that PyInstaller may not automatically detect
hidden_imports = [
    # PySide6 (Qt framework)
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    
    # PIL/Pillow
    'PIL',
    'PIL._tkinter_finder',
    'PIL.Image',
    'PIL.ImageQt',
    
    # Excel export
    'openpyxl',
    'openpyxl.cell._writer',
    
    # PDF processing
    'fitz',  # PyMuPDF
    
    # OCR engines - Aliyun
    'alibabacloud_ocr_api20210707',
    'alibabacloud_ocr_api20210707.client',
    'alibabacloud_ocr_api20210707.models',
    'alibabacloud_tea_openapi',
    'alibabacloud_tea_openapi.client',
    'alibabacloud_tea_openapi.models',
    'alibabacloud_tea_util',
    'alibabacloud_openapi_util',
    
    # OCR engines - OpenAI/DeepSeek
    'openai',
    
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
    
    # Environment template
    (os.path.join(project_root, '.env.example'), '.'),
]

# Define binaries to exclude (reduce package size)
excludes = [
    'tkinter',      # Not used
    'matplotlib',   # Not used
    'scipy',        # Not used
    'pandas',       # Not used
    'IPython',      # Not used
    'jupyter',      # Not used
    'notebook',     # Not used
    'pytest',       # Not used
    'setuptools',   # Not needed at runtime
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
    upx=True,
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
    upx=True,
    upx_exclude=[],
    name='OCR-System',
)
