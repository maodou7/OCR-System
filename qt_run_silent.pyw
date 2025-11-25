#!/usr/bin/env python3
"""
批量OCR识别图片PDF多区域内容重命名导出表格系统 - Qt版本
静默启动脚本（无控制台）
"""

import sys
import os

# 确保导入路径正确
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qt_main import main

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # 静默模式，错误也不显示
        pass
