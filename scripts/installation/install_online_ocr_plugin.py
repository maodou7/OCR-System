#!/usr/bin/env python3
"""
在线OCR插件安装脚本

此脚本用于安装在线OCR服务的依赖包（可选插件）。
核心版本不包含这些依赖，用户可按需安装。

支持的在线OCR服务：
1. 阿里云OCR - 支持多种证件识别
2. DeepSeek OCR - AI大模型驱动的OCR服务

使用方法：
    python install_online_ocr_plugin.py --all          # 安装所有在线OCR插件
    python install_online_ocr_plugin.py --aliyun       # 仅安装阿里云OCR
    python install_online_ocr_plugin.py --deepseek     # 仅安装DeepSeek OCR
    python install_online_ocr_plugin.py --list         # 列出所有可用插件
"""

import sys
import subprocess
import argparse
from typing import List, Dict


class OnlineOCRPluginInstaller:
    """在线OCR插件安装器"""
    
    # 插件依赖定义
    PLUGINS = {
        'aliyun': {
            'name': '阿里云OCR',
            'description': '阿里云在线OCR服务，支持多种特殊证件识别',
            'packages': [
                'alibabacloud-ocr-api20210707>=1.0.0',
                'alibabacloud-tea-openapi>=0.3.0',
                'alibabacloud-tea-util>=0.3.0',
                'alibabacloud-openapi-util>=0.2.0',
            ],
            'config_required': [
                'ALIYUN_ENABLED = True',
                'ALIYUN_ACCESS_KEY_ID = "your_key_id"',
                'ALIYUN_ACCESS_KEY_SECRET = "your_key_secret"',
            ]
        },
        'deepseek': {
            'name': 'DeepSeek OCR',
            'description': '硅基流动DeepSeek-OCR服务，AI大模型驱动',
            'packages': [
                'openai>=1.0.0',
            ],
            'config_required': [
                'DEEPSEEK_ENABLED = True',
                'DEEPSEEK_API_KEY = "your_api_key"',
            ]
        }
    }
    
    def __init__(self):
        """初始化安装器"""
        self.python_cmd = sys.executable
    
    def list_plugins(self):
        """列出所有可用插件"""
        print("\n" + "="*60)
        print("可用的在线OCR插件")
        print("="*60)
        
        for plugin_id, info in self.PLUGINS.items():
            print(f"\n插件ID: {plugin_id}")
            print(f"名称: {info['name']}")
            print(f"描述: {info['description']}")
            print(f"依赖包数量: {len(info['packages'])}")
            
            # 检查是否已安装
            installed = self.check_plugin_installed(plugin_id)
            status = "✓ 已安装" if installed else "✗ 未安装"
            print(f"状态: {status}")
        
        print("\n" + "="*60)
        print("\n使用方法:")
        print("  python install_online_ocr_plugin.py --aliyun    # 安装阿里云OCR")
        print("  python install_online_ocr_plugin.py --deepseek  # 安装DeepSeek OCR")
        print("  python install_online_ocr_plugin.py --all       # 安装所有插件")
        print()
    
    def check_plugin_installed(self, plugin_id: str) -> bool:
        """
        检查插件是否已安装
        
        :param plugin_id: 插件ID
        :return: 是否已安装
        """
        if plugin_id not in self.PLUGINS:
            return False
        
        packages = self.PLUGINS[plugin_id]['packages']
        
        for package in packages:
            # 提取包名（去除版本号）
            package_name = package.split('>=')[0].split('==')[0].split('<')[0]
            
            try:
                # 尝试导入包
                __import__(package_name.replace('-', '_'))
            except ImportError:
                return False
        
        return True
    
    def install_plugin(self, plugin_id: str) -> bool:
        """
        安装指定插件
        
        :param plugin_id: 插件ID
        :return: 是否安装成功
        """
        if plugin_id not in self.PLUGINS:
            print(f"错误: 未知的插件ID '{plugin_id}'")
            return False
        
        plugin_info = self.PLUGINS[plugin_id]
        
        print("\n" + "="*60)
        print(f"安装插件: {plugin_info['name']}")
        print("="*60)
        print(f"描述: {plugin_info['description']}")
        print(f"依赖包: {len(plugin_info['packages'])} 个")
        print()
        
        # 检查是否已安装
        if self.check_plugin_installed(plugin_id):
            print(f"✓ {plugin_info['name']} 已经安装")
            return True
        
        # 安装依赖包
        print("正在安装依赖包...")
        print()
        
        for package in plugin_info['packages']:
            print(f"  安装: {package}")
            
            try:
                result = subprocess.run(
                    [self.python_cmd, '-m', 'pip', 'install', package],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"  ✓ {package} 安装成功")
            except subprocess.CalledProcessError as e:
                print(f"  ✗ {package} 安装失败")
                print(f"  错误: {e.stderr}")
                return False
        
        print()
        print(f"✓ {plugin_info['name']} 安装完成!")
        print()
        
        # 显示配置说明
        self.show_config_instructions(plugin_id)
        
        return True
    
    def show_config_instructions(self, plugin_id: str):
        """
        显示配置说明
        
        :param plugin_id: 插件ID
        """
        if plugin_id not in self.PLUGINS:
            return
        
        plugin_info = self.PLUGINS[plugin_id]
        
        print("配置说明:")
        print("-" * 60)
        print(f"请在 config.py 中添加以下配置:")
        print()
        
        for config_line in plugin_info['config_required']:
            print(f"  {config_line}")
        
        print()
        print("或使用环境变量（推荐）:")
        print()
        
        if plugin_id == 'aliyun':
            print("  export ALIYUN_ACCESS_KEY_ID='your_key_id'")
            print("  export ALIYUN_ACCESS_KEY_SECRET='your_key_secret'")
        elif plugin_id == 'deepseek':
            print("  export DEEPSEEK_API_KEY='your_api_key'")
        
        print()
        print("配置完成后，重启程序即可使用在线OCR服务。")
        print("="*60)
        print()
    
    def install_all_plugins(self) -> bool:
        """
        安装所有插件
        
        :return: 是否全部安装成功
        """
        print("\n" + "="*60)
        print("安装所有在线OCR插件")
        print("="*60)
        print()
        
        success_count = 0
        total_count = len(self.PLUGINS)
        
        for plugin_id in self.PLUGINS.keys():
            if self.install_plugin(plugin_id):
                success_count += 1
            print()
        
        print("="*60)
        print(f"安装完成: {success_count}/{total_count} 个插件安装成功")
        print("="*60)
        print()
        
        return success_count == total_count
    
    def uninstall_plugin(self, plugin_id: str) -> bool:
        """
        卸载指定插件
        
        :param plugin_id: 插件ID
        :return: 是否卸载成功
        """
        if plugin_id not in self.PLUGINS:
            print(f"错误: 未知的插件ID '{plugin_id}'")
            return False
        
        plugin_info = self.PLUGINS[plugin_id]
        
        print("\n" + "="*60)
        print(f"卸载插件: {plugin_info['name']}")
        print("="*60)
        print()
        
        # 检查是否已安装
        if not self.check_plugin_installed(plugin_id):
            print(f"✓ {plugin_info['name']} 未安装，无需卸载")
            return True
        
        # 卸载依赖包
        print("正在卸载依赖包...")
        print()
        
        for package in plugin_info['packages']:
            package_name = package.split('>=')[0].split('==')[0].split('<')[0]
            print(f"  卸载: {package_name}")
            
            try:
                result = subprocess.run(
                    [self.python_cmd, '-m', 'pip', 'uninstall', '-y', package_name],
                    capture_output=True,
                    text=True,
                    check=True
                )
                print(f"  ✓ {package_name} 卸载成功")
            except subprocess.CalledProcessError as e:
                print(f"  ✗ {package_name} 卸载失败")
                print(f"  错误: {e.stderr}")
                return False
        
        print()
        print(f"✓ {plugin_info['name']} 卸载完成!")
        print()
        
        return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='在线OCR插件安装工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s --list              列出所有可用插件
  %(prog)s --aliyun            安装阿里云OCR插件
  %(prog)s --deepseek          安装DeepSeek OCR插件
  %(prog)s --all               安装所有插件
  %(prog)s --uninstall aliyun  卸载阿里云OCR插件
        """
    )
    
    parser.add_argument('--list', action='store_true',
                        help='列出所有可用插件')
    parser.add_argument('--aliyun', action='store_true',
                        help='安装阿里云OCR插件')
    parser.add_argument('--deepseek', action='store_true',
                        help='安装DeepSeek OCR插件')
    parser.add_argument('--all', action='store_true',
                        help='安装所有插件')
    parser.add_argument('--uninstall', type=str, metavar='PLUGIN_ID',
                        help='卸载指定插件')
    
    args = parser.parse_args()
    
    # 创建安装器
    installer = OnlineOCRPluginInstaller()
    
    # 处理命令
    if args.list:
        installer.list_plugins()
    elif args.uninstall:
        installer.uninstall_plugin(args.uninstall)
    elif args.all:
        installer.install_all_plugins()
    elif args.aliyun:
        installer.install_plugin('aliyun')
    elif args.deepseek:
        installer.install_plugin('deepseek')
    else:
        # 没有指定参数，显示帮助
        parser.print_help()
        print()
        installer.list_plugins()


if __name__ == '__main__':
    main()
