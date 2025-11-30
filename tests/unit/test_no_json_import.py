"""
验证轻量级配置管理器不会在启动时导入json模块
"""

import sys
import os

# 确保可以导入模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 记录启动时已加载的模块
initial_modules = set(sys.modules.keys())

# 导入轻量级配置管理器
from lightweight_config import LightweightConfig

# 检查是否导入了json模块
current_modules = set(sys.modules.keys())
new_modules = current_modules - initial_modules

if 'json' in new_modules:
    print("✗ 失败：导入LightweightConfig时加载了json模块")
    print(f"新加载的模块: {new_modules}")
    sys.exit(1)
else:
    print("✓ 成功：导入LightweightConfig时没有加载json模块")

# 加载配置
config = LightweightConfig.load()

# 再次检查
current_modules = set(sys.modules.keys())
new_modules = current_modules - initial_modules

if 'json' in new_modules:
    print("✗ 失败：加载配置时加载了json模块")
    print(f"新加载的模块: {new_modules}")
    sys.exit(1)
else:
    print("✓ 成功：加载配置时没有加载json模块")

print(f"\n配置项数量: {len(config)}")
print("轻量级配置管理器成功避免了json模块的导入！")
