"""
模型文件自动解压模块

在程序运行时自动检测并解压压缩的OCR模型文件。
支持PaddleOCR和RapidOCR模型的自动解压。
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from typing import Optional, Tuple


class ModelDecompressor:
    """模型文件解压器"""
    
    # 7z可执行文件路径
    SEVEN_ZIP_PATH = "Pack/7z-Self-Extracting/7zr.exe"
    
    # 模型目录配置
    MODELS_DIR = "models"
    
    # 引擎配置
    ENGINES = {
        'paddle': {
            'name': 'PaddleOCR',
            'archive': 'PaddleOCR-json/PaddleOCR-json_v1.4.1.7z',
            'target_dir': 'PaddleOCR-json/PaddleOCR-json_v1.4.1',
            'marker_file': 'PaddleOCR-json/PaddleOCR-json_v1.4.1/PaddleOCR-json.exe'
        },
        'rapid': {
            'name': 'RapidOCR',
            'archive': 'RapidOCR-json/RapidOCR-json_v0.2.0.7z',
            'target_dir': 'RapidOCR-json/RapidOCR-json_v0.2.0',
            'marker_file': 'RapidOCR-json/RapidOCR-json_v0.2.0/RapidOCR-json.exe'
        }
    }
    
    def __init__(self):
        """初始化解压器"""
        # 获取资源路径（支持PyInstaller打包）
        if getattr(sys, 'frozen', False):
            # 打包环境
            self.project_root = Path(sys._MEIPASS)
        else:
            # 开发环境
            self.project_root = Path(__file__).parent
        
        self.models_path = self.project_root / self.MODELS_DIR
        self.seven_zip = self.project_root / self.SEVEN_ZIP_PATH
    
    def is_engine_extracted(self, engine_type: str) -> bool:
        """
        检查引擎是否已解压
        
        :param engine_type: 引擎类型 ('paddle' 或 'rapid')
        :return: 是否已解压
        """
        if engine_type not in self.ENGINES:
            return False
        
        config = self.ENGINES[engine_type]
        marker_file = self.models_path / config['marker_file']
        
        return marker_file.exists()
    
    def get_archive_path(self, engine_type: str) -> Optional[Path]:
        """
        获取压缩包路径
        
        :param engine_type: 引擎类型
        :return: 压缩包路径，不存在返回None
        """
        if engine_type not in self.ENGINES:
            return None
        
        config = self.ENGINES[engine_type]
        archive_path = self.models_path / config['archive']
        
        return archive_path if archive_path.exists() else None
    
    def extract_engine(self, engine_type: str, progress_callback=None) -> Tuple[bool, str]:
        """
        解压引擎模型
        
        :param engine_type: 引擎类型 ('paddle' 或 'rapid')
        :param progress_callback: 进度回调函数 callback(message: str)
        :return: (是否成功, 消息)
        """
        if engine_type not in self.ENGINES:
            return False, f"不支持的引擎类型: {engine_type}"
        
        config = self.ENGINES[engine_type]
        engine_name = config['name']
        
        # 检查是否已解压
        if self.is_engine_extracted(engine_type):
            msg = f"{engine_name} 模型已存在，无需解压"
            if progress_callback:
                progress_callback(msg)
            return True, msg
        
        # 检查压缩包是否存在
        archive_path = self.get_archive_path(engine_type)
        if not archive_path:
            msg = f"{engine_name} 压缩包不存在: {config['archive']}"
            if progress_callback:
                progress_callback(msg)
            return False, msg
        
        # 检查7z工具
        if not self.seven_zip.exists():
            msg = f"7z工具不存在: {self.seven_zip}"
            if progress_callback:
                progress_callback(msg)
            return False, msg
        
        # 开始解压
        target_dir = self.models_path / config['target_dir']
        target_parent = target_dir.parent
        
        # 确保目标目录的父目录存在
        target_parent.mkdir(parents=True, exist_ok=True)
        
        if progress_callback:
            progress_callback(f"正在解压 {engine_name} 模型...")
        
        # 构建7z解压命令
        # -o: 输出目录
        # -y: 自动确认所有提示
        cmd = [
            str(self.seven_zip),
            'x',  # 解压
            str(archive_path),  # 压缩包路径
            f'-o{target_parent}',  # 输出目录
            '-y'  # 自动确认
        ]
        
        try:
            start_time = time.time()
            
            # 执行解压
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )
            
            elapsed_time = time.time() - start_time
            
            # 验证解压结果
            if self.is_engine_extracted(engine_type):
                msg = f"✓ {engine_name} 模型解压成功 (耗时: {elapsed_time:.1f}秒)"
                if progress_callback:
                    progress_callback(msg)
                return True, msg
            else:
                msg = f"✗ {engine_name} 模型解压失败: 标记文件不存在"
                if progress_callback:
                    progress_callback(msg)
                return False, msg
                
        except subprocess.CalledProcessError as e:
            msg = f"✗ {engine_name} 模型解压失败: {e.stderr}"
            if progress_callback:
                progress_callback(msg)
            return False, msg
        except Exception as e:
            msg = f"✗ {engine_name} 模型解压失败: {e}"
            if progress_callback:
                progress_callback(msg)
            return False, msg
    
    def ensure_engine_available(self, engine_type: str, progress_callback=None) -> bool:
        """
        确保引擎可用（自动解压如果需要）
        
        :param engine_type: 引擎类型
        :param progress_callback: 进度回调函数
        :return: 是否可用
        """
        # 如果已解压，直接返回
        if self.is_engine_extracted(engine_type):
            return True
        
        # 尝试解压
        success, msg = self.extract_engine(engine_type, progress_callback)
        return success
    
    def get_engine_status(self, engine_type: str) -> dict:
        """
        获取引擎状态
        
        :param engine_type: 引擎类型
        :return: 状态字典
        """
        if engine_type not in self.ENGINES:
            return {
                'exists': False,
                'extracted': False,
                'archive_exists': False,
                'message': '不支持的引擎类型'
            }
        
        config = self.ENGINES[engine_type]
        extracted = self.is_engine_extracted(engine_type)
        archive_path = self.get_archive_path(engine_type)
        
        status = {
            'name': config['name'],
            'extracted': extracted,
            'archive_exists': archive_path is not None,
            'archive_path': str(archive_path) if archive_path else None,
            'target_dir': str(self.models_path / config['target_dir'])
        }
        
        if extracted:
            status['message'] = f"{config['name']} 已就绪"
        elif archive_path:
            status['message'] = f"{config['name']} 需要解压"
        else:
            status['message'] = f"{config['name']} 压缩包不存在"
        
        return status
    
    def print_status(self):
        """打印所有引擎状态"""
        print("\n" + "="*60)
        print("OCR 模型状态")
        print("="*60)
        
        for engine_type in self.ENGINES.keys():
            status = self.get_engine_status(engine_type)
            print(f"\n{status['name']}:")
            print(f"  已解压: {'✓' if status['extracted'] else '✗'}")
            print(f"  压缩包存在: {'✓' if status['archive_exists'] else '✗'}")
            print(f"  状态: {status['message']}")
        
        print("\n" + "="*60)


# 全局实例
_decompressor = None


def get_decompressor() -> ModelDecompressor:
    """获取全局解压器实例"""
    global _decompressor
    if _decompressor is None:
        _decompressor = ModelDecompressor()
    return _decompressor


def ensure_engine_available(engine_type: str, progress_callback=None) -> bool:
    """
    确保引擎可用（便捷函数）
    
    :param engine_type: 引擎类型 ('paddle' 或 'rapid')
    :param progress_callback: 进度回调函数
    :return: 是否可用
    """
    decompressor = get_decompressor()
    return decompressor.ensure_engine_available(engine_type, progress_callback)


def is_engine_extracted(engine_type: str) -> bool:
    """
    检查引擎是否已解压（便捷函数）
    
    :param engine_type: 引擎类型
    :return: 是否已解压
    """
    decompressor = get_decompressor()
    return decompressor.is_engine_extracted(engine_type)


def main():
    """主函数 - 用于测试"""
    decompressor = ModelDecompressor()
    decompressor.print_status()
    
    # 测试解压
    print("\n测试解压功能:")
    for engine_type in ['paddle', 'rapid']:
        if not decompressor.is_engine_extracted(engine_type):
            print(f"\n尝试解压 {engine_type}...")
            success, msg = decompressor.extract_engine(
                engine_type,
                progress_callback=lambda m: print(f"  {m}")
            )
            if not success:
                print(f"  失败: {msg}")


if __name__ == '__main__':
    main()
