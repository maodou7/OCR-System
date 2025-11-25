#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Nuitka编译脚本 - 批量OCR识别系统
支持编译出单文件可执行程序或目录模式
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

def build_with_nuitka():
    """使用Nuitka编译项目"""
    
    print("=" * 60)
    print("Nuitka编译 - OCR识别系统")
    print("=" * 60)
    
    # 检查Nuitka是否安装
    try:
        subprocess.run(["python", "-m", "nuitka", "--version"], 
                      check=True, capture_output=True)
    except subprocess.CalledProcessError:
        print("❌ Nuitka未安装，正在安装...")
        subprocess.run([sys.executable, "-m", "pip", "install", "nuitka"], check=True)
    
    # 编译参数
    nuitka_args = [
        sys.executable, "-m", "nuitka",
        
        # === 基本选项 ===
        "--standalone",  # 独立模式，包含所有依赖
        "--onefile",  # 打包成单个可执行文件（可选，注释掉则为目录模式）
        
        # === 输出配置 ===
        "--output-dir=dist",  # 输出目录
        "--output-filename=OCR-System",  # 输出文件名（Linux）
        # "--windows-console-mode=disable",  # Windows下隐藏控制台（仅Windows）
        
        # === Python优化 ===
        "--python-flag=no_site",  # 不导入site模块
        "--python-flag=no_warnings",  # 禁用警告
        
        # === 包含必要模块 ===
        "--include-package=PySide6",  # Qt GUI框架
        "--include-package=PIL",  # Pillow图像处理
        "--include-package=numpy",  # 数值计算
        "--include-package=cv2",  # OpenCV
        "--include-module=openpyxl",  # Excel导出
        
        # === OCR引擎模块 ===
        "--include-package=paddleocr",  # PaddleOCR
        "--include-package=paddlepaddle",  # PaddlePaddle
        "--include-package=rapidocr_onnxruntime",  # RapidOCR
        "--include-package=alibabacloud_ocr_api20210707",  # 阿里云OCR
        "--include-package=openai",  # DeepSeek OCR (OpenAI SDK)
        
        # === PDF处理 ===
        "--include-module=fitz",  # PyMuPDF
        
        # === 数据文件（PaddleOCR模型等）===
        # Nuitka会自动包含这些包的数据文件
        "--include-data-dir={paddle_base}=paddleocr".format(
            paddle_base=get_package_path("paddleocr")
        ) if get_package_path("paddleocr") else "",
        
        # === 性能优化 ===
        "--lto=yes",  # 链接时优化
        "--jobs=8",  # 并行编译（8线程）
        
        # === 其他优化 ===
        "--assume-yes-for-downloads",  # 自动下载依赖
        "--show-progress",  # 显示进度
        "--show-memory",  # 显示内存使用
        
        # === 主程序 ===
        "qt_run.py"  # 主入口文件
    ]
    
    # 过滤空参数
    nuitka_args = [arg for arg in nuitka_args if arg]
    
    print("\n编译配置:")
    print(f"  主程序: qt_run.py")
    print(f"  模式: {'单文件' if '--onefile' in nuitka_args else '目录模式'}")
    print(f"  输出目录: dist/")
    print(f"  并行线程: 8")
    
    # 确认编译
    response = input("\n是否开始编译？(y/n): ")
    if response.lower() != 'y':
        print("取消编译")
        return
    
    print("\n开始编译...")
    print("-" * 60)
    
    try:
        # 执行编译
        subprocess.run(nuitka_args, check=True)
        
        print("-" * 60)
        print("✅ 编译成功！")
        print(f"\n可执行文件位置: dist/OCR-System")
        print("\n运行方式:")
        print("  cd dist")
        print("  ./OCR-System")
        
    except subprocess.CalledProcessError as e:
        print("-" * 60)
        print(f"❌ 编译失败: {e}")
        sys.exit(1)

def get_package_path(package_name):
    """获取Python包的安装路径"""
    try:
        import importlib.util
        spec = importlib.util.find_spec(package_name)
        if spec and spec.origin:
            return str(Path(spec.origin).parent)
    except:
        pass
    return None

def clean_build():
    """清理构建文件"""
    print("\n清理旧的构建文件...")
    
    dirs_to_remove = ["build", "dist", "OCR-System.build", "OCR-System.dist", "OCR-System.onefile-build"]
    
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            print(f"  删除: {dir_name}")
            shutil.rmtree(dir_name)
    
    print("清理完成")

if __name__ == "__main__":
    print("\nOCR识别系统 - Nuitka编译工具\n")
    
    # 菜单选择
    print("请选择操作:")
    print("  1. 编译（单文件模式）")
    print("  2. 编译（目录模式）")
    print("  3. 清理构建文件")
    print("  4. 退出")
    
    choice = input("\n请输入选项 (1-4): ")
    
    if choice == "1":
        print("\n选择: 单文件模式编译")
        build_with_nuitka()
    elif choice == "2":
        print("\n选择: 目录模式编译")
        print("⚠️ 请手动编辑脚本，注释掉 '--onefile' 参数")
    elif choice == "3":
        clean_build()
    elif choice == "4":
        print("退出")
    else:
        print("无效选项")
