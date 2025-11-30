"""
模型文件压缩工具

使用7z最高压缩率压缩OCR模型文件，减小分发体积。
支持自动检测和压缩PaddleOCR和RapidOCR模型。
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


class ModelCompressor:
    """模型文件压缩器"""
    
    # 7z可执行文件路径
    SEVEN_ZIP_PATH = "Pack/7z-Self-Extracting/7zr.exe"
    
    # 模型目录配置
    MODELS_DIR = "models"
    PADDLE_MODEL_DIR = "PaddleOCR-json/PaddleOCR-json_v1.4.1"
    RAPID_MODEL_DIR = "RapidOCR-json/RapidOCR-json_v0.2.0"
    
    def __init__(self):
        """初始化压缩器"""
        self.project_root = Path(__file__).parent
        self.models_path = self.project_root / self.MODELS_DIR
        self.seven_zip = self.project_root / self.SEVEN_ZIP_PATH
        
        if not self.seven_zip.exists():
            raise FileNotFoundError(f"7z可执行文件不存在: {self.seven_zip}")
    
    def get_dir_size(self, path: Path) -> int:
        """
        获取目录大小（字节）
        
        :param path: 目录路径
        :return: 大小（字节）
        """
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size
    
    def format_size(self, size_bytes: int) -> str:
        """
        格式化文件大小
        
        :param size_bytes: 字节数
        :return: 格式化字符串
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} TB"
    
    def compress_directory(self, source_dir: Path, output_file: Path, 
                          compression_level: int = 9) -> bool:
        """
        压缩目录为7z文件
        
        :param source_dir: 源目录
        :param output_file: 输出文件路径
        :param compression_level: 压缩级别 (0-9, 9为最高)
        :return: 是否成功
        """
        if not source_dir.exists():
            print(f"❌ 源目录不存在: {source_dir}")
            return False
        
        # 删除已存在的压缩文件
        if output_file.exists():
            output_file.unlink()
        
        print(f"\n正在压缩: {source_dir.name}")
        print(f"压缩级别: {compression_level} (最高)")
        
        # 获取原始大小
        original_size = self.get_dir_size(source_dir)
        print(f"原始大小: {self.format_size(original_size)}")
        
        # 构建7z命令
        # -mx9: 最高压缩率
        # -mmt=on: 多线程压缩
        # -ms=on: 固实压缩（提高压缩率）
        # -mfb=273: 快速字节数（最大值，提高压缩率）
        # -md=128m: 字典大小（128MB，提高压缩率）
        cmd = [
            str(self.seven_zip),
            'a',  # 添加到压缩包
            f'-mx={compression_level}',  # 压缩级别
            '-mmt=on',  # 多线程
            '-ms=on',  # 固实压缩
            '-mfb=273',  # 快速字节数
            '-md=128m',  # 字典大小
            str(output_file),  # 输出文件
            str(source_dir / '*')  # 源文件
        ]
        
        try:
            # 在源目录的父目录中执行命令
            result = subprocess.run(
                cmd,
                cwd=source_dir.parent,
                capture_output=True,
                text=True,
                check=True
            )
            
            if output_file.exists():
                compressed_size = output_file.stat().st_size
                ratio = (1 - compressed_size / original_size) * 100
                
                print(f"✓ 压缩完成")
                print(f"压缩后大小: {self.format_size(compressed_size)}")
                print(f"压缩率: {ratio:.1f}%")
                print(f"输出文件: {output_file}")
                return True
            else:
                print(f"❌ 压缩失败: 输出文件不存在")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ 压缩失败: {e}")
            print(f"错误输出: {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ 压缩失败: {e}")
            return False
    
    def compress_paddle_models(self) -> bool:
        """
        压缩PaddleOCR模型
        
        :return: 是否成功
        """
        paddle_dir = self.models_path / self.PADDLE_MODEL_DIR
        if not paddle_dir.exists():
            print(f"⚠ PaddleOCR模型目录不存在: {paddle_dir}")
            return False
        
        output_file = self.models_path / "PaddleOCR-json" / "PaddleOCR-json_v1.4.1.7z"
        return self.compress_directory(paddle_dir, output_file)
    
    def compress_rapid_models(self) -> bool:
        """
        压缩RapidOCR模型
        
        :return: 是否成功
        """
        rapid_dir = self.models_path / self.RAPID_MODEL_DIR
        if not rapid_dir.exists():
            print(f"⚠ RapidOCR模型目录不存在: {rapid_dir}")
            return False
        
        output_file = self.models_path / "RapidOCR-json" / "RapidOCR-json_v0.2.0.7z"
        return self.compress_directory(rapid_dir, output_file)
    
    def compress_all_models(self) -> dict:
        """
        压缩所有模型
        
        :return: 结果字典 {'paddle': bool, 'rapid': bool}
        """
        print("="*60)
        print("开始压缩OCR模型文件")
        print("="*60)
        
        results = {}
        
        # 压缩PaddleOCR
        print("\n[1/2] PaddleOCR模型")
        results['paddle'] = self.compress_paddle_models()
        
        # 压缩RapidOCR
        print("\n[2/2] RapidOCR模型")
        results['rapid'] = self.compress_rapid_models()
        
        # 总结
        print("\n" + "="*60)
        print("压缩完成")
        print("="*60)
        
        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)
        
        print(f"\n成功: {success_count}/{total_count}")
        
        for engine, success in results.items():
            status = "✓" if success else "✗"
            print(f"  {status} {engine}")
        
        return results


def main():
    """主函数"""
    try:
        compressor = ModelCompressor()
        results = compressor.compress_all_models()
        
        # 返回退出码
        if all(results.values()):
            print("\n✓ 所有模型压缩成功")
            return 0
        elif any(results.values()):
            print("\n⚠ 部分模型压缩成功")
            return 1
        else:
            print("\n❌ 所有模型压缩失败")
            return 2
            
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 3


if __name__ == '__main__':
    sys.exit(main())
