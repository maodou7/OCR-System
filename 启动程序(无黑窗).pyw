#!/usr/bin/env python3
"""
批量OCR识别图片PDF多区域内容重命名导出表格系统 - Qt版本
静默启动脚本（无控制台）
"""

import os
import subprocess
import sys

if __name__ == "__main__":
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # portable_python 路径
    python_exe = os.path.join(script_dir, "portable_python", "python.exe")
    
    # qt_run.py 路径
    qt_run_py = os.path.join(script_dir, "qt_run.py")
    
    # 使用 portable_python 启动 qt_run.py
    # CREATE_NO_WINDOW 标志确保不显示控制台窗口
    try:
        subprocess.Popen(
            [python_exe, qt_run_py],
            cwd=script_dir,
            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
        )
    except Exception:
        # 静默模式，错误也不显示
        pass
