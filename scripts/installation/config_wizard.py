#!/usr/bin/env python3
"""
配置向导 - 首次运行配置助手

在首次运行时引导用户完成基本配置。
"""

import os
import sys
import shutil
from pathlib import Path


def check_config_exists():
    """检查配置文件是否存在"""
    return os.path.exists('config.py')


def create_config_from_example():
    """从示例文件创建配置文件"""
    example_file = 'config.py.example'
    target_file = 'config.py'
    
    if not os.path.exists(example_file):
        print(f"错误: 找不到示例配置文件 {example_file}")
        return False
    
    try:
        shutil.copy(example_file, target_file)
        print(f"✓ 已创建配置文件: {target_file}")
        return True
    except Exception as e:
        print(f"✗ 创建配置文件失败: {e}")
        return False


def create_env_from_example():
    """从示例文件创建环境变量文件"""
    example_file = '.env.example'
    target_file = '.env'
    
    if not os.path.exists(example_file):
        print(f"提示: 找不到示例环境变量文件 {example_file}")
        return False
    
    if os.path.exists(target_file):
        print(f"提示: 环境变量文件已存在: {target_file}")
        return True
    
    try:
        shutil.copy(example_file, target_file)
        print(f"✓ 已创建环境变量文件: {target_file}")
        return True
    except Exception as e:
        print(f"✗ 创建环境变量文件失败: {e}")
        return False


def show_welcome():
    """显示欢迎信息"""
    print("=" * 60)
    print("欢迎使用 OCR 系统")
    print("=" * 60)
    print()
    print("这是您第一次运行本程序，让我们完成基本配置。")
    print()


def show_engine_info():
    """显示OCR引擎信息"""
    print("OCR引擎说明:")
    print()
    print("1. RapidOCR (推荐，默认)")
    print("   - 轻量级，启动快")
    print("   - 体积小 (~45MB)")
    print("   - 适合日常使用")
    print()
    print("2. PaddleOCR (可选下载)")
    print("   - 高精度")
    print("   - 体积较大 (~562MB)")
    print("   - 适合高精度需求")
    print()
    print("3. 在线OCR (可选)")
    print("   - 阿里云OCR")
    print("   - DeepSeek OCR")
    print("   - 需要配置API密钥")
    print()


def configure_engines():
    """配置OCR引擎"""
    print("配置OCR引擎:")
    print()
    
    # 检查RapidOCR
    rapid_path = os.path.join('models', 'RapidOCR-json')
    rapid_exists = os.path.exists(rapid_path)
    
    if rapid_exists:
        print("✓ RapidOCR 已安装")
    else:
        print("⚠ RapidOCR 未安装")
        print("  请从以下地址下载:")
        print("  https://github.com/hiroi-sora/RapidOCR-json/releases")
    
    print()
    
    # 检查PaddleOCR
    paddle_path = os.path.join('models', 'PaddleOCR-json')
    paddle_exists = os.path.exists(paddle_path)
    
    if paddle_exists:
        print("✓ PaddleOCR 已安装")
    else:
        print("⚠ PaddleOCR 未安装 (可选)")
        print("  如需高精度识别，可从以下地址下载:")
        print("  https://github.com/hiroi-sora/PaddleOCR-json/releases")
    
    print()


def configure_online_ocr():
    """配置在线OCR"""
    print("在线OCR配置 (可选):")
    print()
    print("如果您需要使用在线OCR服务，请:")
    print()
    print("1. 编辑 .env 文件")
    print("2. 填写您的API密钥")
    print("3. 在 config.py 中启用对应的引擎")
    print()
    print("详细说明请参考 config.py 中的注释")
    print()


def show_completion():
    """显示完成信息"""
    print("=" * 60)
    print("配置完成!")
    print("=" * 60)
    print()
    print("您现在可以:")
    print()
    print("1. 运行程序: python qt_run.py")
    print("2. 或双击: 启动程序点这.bat")
    print()
    print("如需修改配置，请编辑 config.py 文件")
    print()


def run_wizard():
    """运行配置向导"""
    show_welcome()
    
    # 创建配置文件
    if not check_config_exists():
        print("正在创建配置文件...")
        if not create_config_from_example():
            print()
            print("配置向导失败，请手动复制 config.py.example 为 config.py")
            return False
        print()
    else:
        print("✓ 配置文件已存在")
        print()
    
    # 创建环境变量文件
    create_env_from_example()
    print()
    
    # 显示引擎信息
    show_engine_info()
    
    # 配置引擎
    configure_engines()
    
    # 配置在线OCR
    configure_online_ocr()
    
    # 显示完成信息
    show_completion()
    
    return True


def main():
    """主函数"""
    # 检查是否需要运行向导
    if check_config_exists():
        print("配置文件已存在，无需运行配置向导")
        print()
        print("如需重新配置，请删除 config.py 后重新运行此脚本")
        return
    
    # 运行向导
    run_wizard()


if __name__ == '__main__':
    main()
