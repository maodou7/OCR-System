"""
快速集成测试：验证config模块正常工作
"""

import sys
import os

# 确保可以导入config模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import Config, OCRRect, get_resource_path, get_executable_dir
    print("✓ Config模块导入成功")
    
    # 测试Config类属性
    print(f"✓ APP_NAME: {Config.APP_NAME}")
    print(f"✓ APP_VERSION: {Config.APP_VERSION}")
    print(f"✓ OCR_ENGINE: {Config.OCR_ENGINE}")
    
    # 测试加载配置
    config = Config.load_user_config()
    print(f"✓ 加载用户配置成功，配置项数量: {len(config)}")
    
    # 测试新的辅助方法
    width = Config.get_config_int('WINDOW_WIDTH', 1400)
    print(f"✓ get_config_int工作正常: WINDOW_WIDTH = {width}")
    
    enabled = Config.get_config_bool('PADDLE_ENABLED', True)
    print(f"✓ get_config_bool工作正常: PADDLE_ENABLED = {enabled}")
    
    # 测试OCRRect类
    rect = OCRRect(0, 0, 100, 100, "test")
    print(f"✓ OCRRect类工作正常: {rect.get_coords()}")
    
    # 测试辅助函数
    exe_dir = get_executable_dir()
    print(f"✓ get_executable_dir工作正常: {exe_dir}")
    
    print("\n所有集成测试通过！配置管理优化成功！")
    
except Exception as e:
    print(f"✗ 集成测试失败: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
