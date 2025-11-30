#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR模型文件大小分析工具

分析PaddleOCR和RapidOCR模型目录,识别各语言模型的大小
"""

import os
from pathlib import Path


def get_dir_size(path):
    """计算目录大小(MB)"""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_file(follow_symlinks=False):
                total += entry.stat().st_size
            elif entry.is_dir(follow_symlinks=False):
                total += get_dir_size(entry.path)
    except (PermissionError, FileNotFoundError):
        pass
    return total


def format_size(size_bytes):
    """格式化文件大小"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def analyze_paddle_models():
    """分析PaddleOCR模型"""
    print("=" * 80)
    print("PaddleOCR模型分析")
    print("=" * 80)
    
    paddle_base = Path("models/PaddleOCR-json/PaddleOCR-json_v1.4.1")
    
    if not paddle_base.exists():
        print("未找到PaddleOCR模型目录")
        return
    
    models_dir = paddle_base / "models"
    
    # 分析各个模型目录
    model_sizes = []
    
    if models_dir.exists():
        for item in sorted(models_dir.iterdir()):
            if item.is_dir():
                size = get_dir_size(item)
                model_sizes.append({
                    'name': item.name,
                    'size': size,
                    'path': str(item.relative_to(Path("models")))
                })
    
    # 按大小排序
    model_sizes.sort(key=lambda x: x['size'], reverse=True)
    
    print(f"\n模型目录: {models_dir.relative_to(Path('models'))}")
    print(f"{'模型名称':<50} {'大小':>15}")
    print("-" * 80)
    
    total_size = 0
    for model in model_sizes:
        print(f"{model['name']:<50} {format_size(model['size']):>15}")
        total_size += model['size']
    
    print("-" * 80)
    print(f"{'总计':<50} {format_size(total_size):>15}")
    
    # 分析DLL文件
    print(f"\n\nDLL文件分析:")
    print(f"{'文件名':<50} {'大小':>15}")
    print("-" * 80)
    
    dll_files = []
    for item in paddle_base.iterdir():
        if item.is_file() and item.suffix.lower() in ['.dll', '.exe']:
            size = item.stat().st_size
            dll_files.append({
                'name': item.name,
                'size': size
            })
    
    dll_files.sort(key=lambda x: x['size'], reverse=True)
    dll_total = 0
    for dll in dll_files:
        print(f"{dll['name']:<50} {format_size(dll['size']):>15}")
        dll_total += dll['size']
    
    print("-" * 80)
    print(f"{'DLL总计':<50} {format_size(dll_total):>15}")
    
    # 分析配置文件
    print(f"\n\n配置文件:")
    config_files = list(models_dir.glob("config_*.txt"))
    dict_files = list(models_dir.glob("dict_*.txt"))
    
    print(f"  配置文件: {len(config_files)} 个")
    for cf in sorted(config_files):
        print(f"    - {cf.name}")
    
    print(f"  字典文件: {len(dict_files)} 个")
    for df in sorted(dict_files):
        print(f"    - {df.name}")
    
    # 识别语言
    print(f"\n\n支持的语言:")
    languages = {
        'chinese': '简体中文',
        'chinese_cht': '繁体中文',
        'en': '英文',
        'japan': '日文',
        'korean': '韩文',
        'cyrillic': '俄文(西里尔字母)'
    }
    
    for key, name in languages.items():
        has_model = any(key in m['name'] for m in model_sizes)
        has_config = (models_dir / f"config_{key}.txt").exists()
        has_dict = (models_dir / f"dict_{key}.txt").exists()
        
        status = "✓" if (has_model or has_config or has_dict) else "✗"
        print(f"  {status} {name} ({key})")
        if has_model:
            model = next(m for m in model_sizes if key in m['name'])
            print(f"      模型大小: {format_size(model['size'])}")
    
    # 总结
    print(f"\n\n总体统计:")
    print(f"  模型总大小: {format_size(total_size)}")
    print(f"  DLL总大小: {format_size(dll_total)}")
    print(f"  PaddleOCR总大小: {format_size(total_size + dll_total)}")
    
    return model_sizes, dll_files


def analyze_rapid_models():
    """分析RapidOCR模型"""
    print("\n\n" + "=" * 80)
    print("RapidOCR模型分析")
    print("=" * 80)
    
    rapid_base = Path("models/RapidOCR-json")
    
    if not rapid_base.exists():
        print("未找到RapidOCR模型目录")
        return
    
    # 计算整个目录大小
    total_size = get_dir_size(rapid_base)
    print(f"\nRapidOCR总大小: {format_size(total_size)}")
    
    # 列出主要文件
    print(f"\n主要文件:")
    for item in sorted(rapid_base.rglob("*")):
        if item.is_file():
            size = item.stat().st_size
            if size > 1024 * 1024:  # 大于1MB
                rel_path = item.relative_to(rapid_base)
                print(f"  {str(rel_path):<50} {format_size(size):>15}")


def analyze_compressed_archives():
    """分析压缩包"""
    print("\n\n" + "=" * 80)
    print("压缩包分析")
    print("=" * 80)
    
    models_dir = Path("models")
    archives = list(models_dir.glob("*.7z")) + list(models_dir.glob("*.zip"))
    
    if not archives:
        print("未找到压缩包")
        return
    
    print(f"\n{'文件名':<50} {'大小':>15}")
    print("-" * 80)
    
    for archive in sorted(archives):
        size = archive.stat().st_size
        print(f"{archive.name:<50} {format_size(size):>15}")


def check_config_usage():
    """检查配置文件中实际使用的模型"""
    print("\n\n" + "=" * 80)
    print("配置文件使用情况")
    print("=" * 80)
    
    # 检查Python代码中的配置
    config_files = [
        "config.py",
        "ocr_engine_paddle.py",
        "ocr_engine_rapid.py",
        "ocr_engine_manager.py"
    ]
    
    for config_file in config_files:
        if not os.path.exists(config_file):
            continue
        
        print(f"\n{config_file}:")
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 查找语言相关配置
            if 'chinese' in content.lower():
                print("  - 使用中文模型")
            if 'english' in content.lower() or 'en_' in content.lower():
                print("  - 使用英文模型")
            if 'japan' in content.lower():
                print("  - 使用日文模型")
            if 'korean' in content.lower():
                print("  - 使用韩文模型")
            if 'cyrillic' in content.lower():
                print("  - 使用俄文模型")


def main():
    """主函数"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "OCR模型文件大小分析报告" + " " * 34 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    # 分析PaddleOCR
    paddle_models, paddle_dlls = analyze_paddle_models()
    
    # 分析RapidOCR
    analyze_rapid_models()
    
    # 分析压缩包
    analyze_compressed_archives()
    
    # 检查配置使用情况
    check_config_usage()
    
    # 优化建议
    print("\n\n" + "=" * 80)
    print("优化建议")
    print("=" * 80)
    
    print("\n1. 可移除的语言模型:")
    removable_langs = ['japan', 'korean', 'cyrillic', 'chinese_cht']
    for lang in removable_langs:
        models = [m for m in paddle_models if lang in m['name']]
        if models:
            total = sum(m['size'] for m in models)
            lang_names = {
                'japan': '日文',
                'korean': '韩文',
                'cyrillic': '俄文',
                'chinese_cht': '繁体中文'
            }
            print(f"   - {lang_names[lang]}: {format_size(total)}")
    
    print("\n2. 大型DLL文件:")
    large_dlls = [d for d in paddle_dlls if d['size'] > 10 * 1024 * 1024]
    for dll in large_dlls[:5]:
        print(f"   - {dll['name']}: {format_size(dll['size'])}")
    
    print("\n3. 压缩包:")
    print("   - 考虑在打包时排除.7z压缩包")
    print("   - 仅保留解压后的模型文件")
    
    print("\n" + "=" * 80)


if __name__ == '__main__':
    main()
