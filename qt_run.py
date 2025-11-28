#!/usr/bin/env python3
"""
批量OCR识别图片PDF多区域内容重命名导出表格系统 - Qt版本
主启动脚本
"""

import sys
import os
import shutil

# 确保导入路径正确
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def ensure_config_file():
    """
    确保config.py文件存在
    
    如果config.py不存在，从config.py.example复制一份。
    这允许用户在打包后修改配置文件而无需重新构建应用。
    
    支持PyInstaller打包环境：
    - 开发环境：在脚本所在目录查找config.py
    - 打包环境：在可执行文件所在目录查找config.py
    """
    # 获取可执行文件所在目录
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        # PyInstaller打包环境
        exe_dir = os.path.dirname(os.path.abspath(sys.executable))
        # config.py.example在打包的资源中
        config_example_path = os.path.join(sys._MEIPASS, 'config.py.example')
    else:
        # 开发环境
        exe_dir = os.path.dirname(os.path.abspath(__file__))
        config_example_path = os.path.join(exe_dir, 'config.py.example')
    
    # config.py应该在可执行文件目录（外部，用户可修改）
    config_path = os.path.join(exe_dir, 'config.py')
    
    # 如果config.py不存在，从config.py.example复制
    if not os.path.exists(config_path):
        if os.path.exists(config_example_path):
            try:
                shutil.copy2(config_example_path, config_path)
                print(f"首次运行：已从 config.py.example 创建 config.py")
                print(f"配置文件位置: {config_path}")
                print()
            except Exception as e:
                print(f"警告：无法创建config.py文件: {e}")
                print(f"将使用默认配置")
                print()
        else:
            print(f"警告：找不到 config.py.example 模板文件")
            print(f"将使用默认配置")
            print()
    
    # 确保config.py在导入路径中（外部配置文件优先）
    if exe_dir not in sys.path:
        sys.path.insert(0, exe_dir)


from qt_main import main

if __name__ == "__main__":
    print("=" * 60)
    print("批量OCR识别图片PDF多区域内容重命名导出表格系统 (Qt版本)")
    print("=" * 60)
    print("正在启动...")
    print()
    
    # 确保配置文件存在
    ensure_config_file()
    
    try:
        main()
    except Exception as e:
        print(f"程序运行出错: {e}")
        import traceback
        traceback.print_exc()
        input("按回车键退出...")
