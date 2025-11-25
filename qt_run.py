#!/usr/bin/env python3
"""
批量OCR识别图片PDF多区域内容重命名导出表格系统 - Qt版本
主启动脚本
"""

import sys
import os

# 确保导入路径正确
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from qt_main import main

if __name__ == "__main__":
    print("=" * 60)
    print("批量OCR识别图片PDF多区域内容重命名导出表格系统 (Qt版本)")
    print("=" * 60)
    print("正在启动...")
    print()
    
    try:
        main()
    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")
