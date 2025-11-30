"""
配置加载性能基准测试

对比JSON配置和INI配置的加载性能
"""

import sys
import os
import time
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from lightweight_config import LightweightConfig


def benchmark_json_loading(iterations=100):
    """基准测试：JSON配置加载"""
    import json
    
    # 创建临时JSON配置文件
    temp_dir = tempfile.mkdtemp()
    json_file = os.path.join(temp_dir, "config.json")
    
    config_data = {
        'APP_NAME': 'OCR系统',
        'APP_VERSION': '1.4.1',
        'WINDOW_WIDTH': 1400,
        'WINDOW_HEIGHT': 800,
        'OCR_ENGINE': 'rapid',
        'PADDLE_ENABLED': True,
        'RAPID_ENABLED': True,
    }
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(config_data, f, ensure_ascii=False, indent=2)
    
    # 基准测试
    start_time = time.time()
    for _ in range(iterations):
        with open(json_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    end_time = time.time()
    
    # 清理
    shutil.rmtree(temp_dir)
    
    return end_time - start_time


def benchmark_ini_loading(iterations=100):
    """基准测试：INI配置加载（无缓存）"""
    # 创建临时INI配置文件
    temp_dir = tempfile.mkdtemp()
    ini_file = os.path.join(temp_dir, "config.ini")
    
    with open(ini_file, 'w', encoding='utf-8') as f:
        f.write("APP_NAME = OCR系统\n")
        f.write("APP_VERSION = 1.4.1\n")
        f.write("WINDOW_WIDTH = 1400\n")
        f.write("WINDOW_HEIGHT = 800\n")
        f.write("OCR_ENGINE = rapid\n")
        f.write("PADDLE_ENABLED = True\n")
        f.write("RAPID_ENABLED = True\n")
    
    # 基准测试
    start_time = time.time()
    for _ in range(iterations):
        config = LightweightConfig._parse_config_file(ini_file)
    end_time = time.time()
    
    # 清理
    shutil.rmtree(temp_dir)
    
    return end_time - start_time


def benchmark_ini_loading_with_cache(iterations=100):
    """基准测试：INI配置加载（使用缓存）"""
    # 保存原始配置
    original_cache = LightweightConfig._config_cache
    original_mtime = LightweightConfig._config_file_mtime
    original_get_config_dir = LightweightConfig.get_config_dir
    
    # 创建临时目录
    temp_dir = tempfile.mkdtemp()
    LightweightConfig.get_config_dir = classmethod(lambda cls: temp_dir)
    
    # 保存配置
    test_config = LightweightConfig.DEFAULT_CONFIG.copy()
    LightweightConfig.save(test_config)
    
    # 基准测试
    start_time = time.time()
    for _ in range(iterations):
        config = LightweightConfig.load()
    end_time = time.time()
    
    # 恢复原始配置
    LightweightConfig._config_cache = original_cache
    LightweightConfig._config_file_mtime = original_mtime
    LightweightConfig.get_config_dir = original_get_config_dir
    
    # 清理
    shutil.rmtree(temp_dir)
    
    return end_time - start_time


if __name__ == '__main__':
    print("配置加载性能基准测试")
    print("=" * 60)
    
    iterations = 1000
    print(f"测试迭代次数: {iterations}\n")
    
    # JSON加载测试
    print("测试1: JSON配置加载（使用json模块）")
    json_time = benchmark_json_loading(iterations)
    print(f"  总时间: {json_time:.4f}秒")
    print(f"  平均时间: {json_time/iterations*1000:.4f}毫秒/次\n")
    
    # INI加载测试（无缓存）
    print("测试2: INI配置加载（无缓存）")
    ini_time = benchmark_ini_loading(iterations)
    print(f"  总时间: {ini_time:.4f}秒")
    print(f"  平均时间: {ini_time/iterations*1000:.4f}毫秒/次")
    print(f"  性能提升: {(json_time/ini_time - 1)*100:.1f}%\n")
    
    # INI加载测试（使用缓存）
    print("测试3: INI配置加载（使用缓存）")
    ini_cached_time = benchmark_ini_loading_with_cache(iterations)
    print(f"  总时间: {ini_cached_time:.4f}秒")
    print(f"  平均时间: {ini_cached_time/iterations*1000:.4f}毫秒/次")
    print(f"  相比JSON提升: {(json_time/ini_cached_time - 1)*100:.1f}%")
    print(f"  相比无缓存INI提升: {(ini_time/ini_cached_time - 1)*100:.1f}%\n")
    
    print("=" * 60)
    print("总结:")
    print(f"  INI格式（无缓存）比JSON快 {(json_time/ini_time - 1)*100:.1f}%")
    print(f"  INI格式（有缓存）比JSON快 {(json_time/ini_cached_time - 1)*100:.1f}%")
    print(f"  缓存机制带来 {(ini_time/ini_cached_time - 1)*100:.1f}% 的额外性能提升")
