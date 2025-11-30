"""
OCR引擎下载器模块

实现OCR引擎的在线下载、安装和管理功能。
支持PaddleOCR和RapidOCR引擎的按需下载。

验证需求: 6.1, 6.2, 6.3, 6.4, 6.5
"""

import os
import sys
import subprocess
import time
import urllib.request
import urllib.error
from pathlib import Path
from typing import Optional, Callable, Dict, Tuple


class OCREngineDownloader:
    """
    OCR引擎下载器
    
    功能:
    - 检查引擎是否已安装
    - 下载引擎压缩包（支持进度回调）
    - 解压引擎文件
    - 下载失败重试机制
    
    验证需求: 6.2, 6.3
    """
    
    # 引擎配置
    ENGINES = {
        'paddle': {
            'name': 'PaddleOCR-json',
            'display_name': 'PaddleOCR（高精度C++版）',
            'url': 'https://github.com/hiroi-sora/PaddleOCR-json/releases/download/v1.4.1/PaddleOCR-json_v1.4.1_windows_x64.7z',
            'size_mb': 562,  # 压缩包大小（MB）
            'archive_name': 'PaddleOCR-json_v1.4.1.7z',
            'target_dir': 'models/PaddleOCR-json/PaddleOCR-json_v1.4.1',
            'marker_file': 'models/PaddleOCR-json/PaddleOCR-json_v1.4.1/PaddleOCR-json.exe'
        },
        'rapid': {
            'name': 'RapidOCR-json',
            'display_name': 'RapidOCR（轻量级C++版）',
            'url': 'https://github.com/hiroi-sora/RapidOCR-json/releases/download/v0.2.0/RapidOCR-json_v0.2.0_windows_x64.7z',
            'size_mb': 45,  # 压缩包大小（MB）
            'archive_name': 'RapidOCR-json_v0.2.0.7z',
            'target_dir': 'models/RapidOCR-json/RapidOCR-json_v0.2.0',
            'marker_file': 'models/RapidOCR-json/RapidOCR-json_v0.2.0/RapidOCR-json.exe'
        }
    }
    
    # 7z解压工具路径
    SEVEN_ZIP_PATH = "Pack/7z-Self-Extracting/7zr.exe"
    
    # 下载配置
    MAX_RETRIES = 3  # 最大重试次数
    RETRY_DELAY = 2  # 重试延迟（秒）
    CHUNK_SIZE = 8192  # 下载块大小（字节）
    
    def __init__(self):
        """初始化下载器"""
        # 获取项目根目录（支持PyInstaller打包）
        if getattr(sys, 'frozen', False):
            # 打包环境：使用可执行文件所在目录
            self.project_root = Path(sys.executable).parent
        else:
            # 开发环境：使用脚本所在目录
            self.project_root = Path(__file__).parent
        
        self.models_dir = self.project_root / "models"
        self.seven_zip = self.project_root / self.SEVEN_ZIP_PATH
        
        # 确保models目录存在
        self.models_dir.mkdir(parents=True, exist_ok=True)
    
    def is_installed(self, engine_type: str) -> bool:
        """
        检查引擎是否已安装
        
        :param engine_type: 引擎类型 ('paddle' 或 'rapid')
        :return: 是否已安装
        
        验证需求: 6.2
        """
        if engine_type not in self.ENGINES:
            return False
        
        config = self.ENGINES[engine_type]
        marker_file = self.project_root / config['marker_file']
        
        return marker_file.exists()
    
    def get_engine_info(self, engine_type: str) -> Optional[Dict]:
        """
        获取引擎信息
        
        :param engine_type: 引擎类型
        :return: 引擎信息字典，不存在返回None
        """
        if engine_type not in self.ENGINES:
            return None
        
        config = self.ENGINES[engine_type].copy()
        config['installed'] = self.is_installed(engine_type)
        
        return config
    
    def download(
        self,
        engine_type: str,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Tuple[bool, str]:
        """
        下载OCR引擎（支持进度回调和失败重试）
        
        :param engine_type: 引擎类型 ('paddle' 或 'rapid')
        :param progress_callback: 进度回调函数 callback(downloaded_mb, total_mb, message)
        :return: (是否成功, 消息)
        
        验证需求: 6.2, 6.3
        """
        if engine_type not in self.ENGINES:
            return False, f"不支持的引擎类型: {engine_type}"
        
        config = self.ENGINES[engine_type]
        engine_name = config['display_name']
        
        # 检查是否已安装
        if self.is_installed(engine_type):
            msg = f"{engine_name} 已安装，无需下载"
            if progress_callback:
                progress_callback(0, 0, msg)
            return True, msg
        
        # 准备下载路径
        archive_name = config['archive_name']
        archive_path = self.models_dir / engine_type / archive_name
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 如果压缩包已存在，跳过下载
        if archive_path.exists():
            msg = f"{engine_name} 压缩包已存在，跳过下载"
            if progress_callback:
                progress_callback(config['size_mb'], config['size_mb'], msg)
            return True, msg
        
        # 下载URL
        url = config['url']
        total_size_mb = config['size_mb']
        
        # 重试下载
        for attempt in range(1, self.MAX_RETRIES + 1):
            try:
                if progress_callback:
                    progress_callback(0, total_size_mb, f"正在下载 {engine_name} (尝试 {attempt}/{self.MAX_RETRIES})...")
                
                # 开始下载
                success, msg = self._download_file(
                    url,
                    archive_path,
                    total_size_mb,
                    progress_callback
                )
                
                if success:
                    return True, msg
                else:
                    # 下载失败，准备重试
                    if attempt < self.MAX_RETRIES:
                        retry_msg = f"下载失败，{self.RETRY_DELAY}秒后重试... ({msg})"
                        if progress_callback:
                            progress_callback(0, total_size_mb, retry_msg)
                        time.sleep(self.RETRY_DELAY)
                    else:
                        # 最后一次尝试失败
                        return False, f"下载失败（已重试{self.MAX_RETRIES}次）: {msg}"
            
            except Exception as e:
                error_msg = str(e)
                if attempt < self.MAX_RETRIES:
                    retry_msg = f"下载出错，{self.RETRY_DELAY}秒后重试... ({error_msg})"
                    if progress_callback:
                        progress_callback(0, total_size_mb, retry_msg)
                    time.sleep(self.RETRY_DELAY)
                else:
                    return False, f"下载失败（已重试{self.MAX_RETRIES}次）: {error_msg}"
        
        return False, "下载失败"
    
    def _download_file(
        self,
        url: str,
        dest_path: Path,
        total_size_mb: int,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Tuple[bool, str]:
        """
        下载文件（内部方法）
        
        :param url: 下载URL
        :param dest_path: 目标文件路径
        :param total_size_mb: 文件总大小（MB）
        :param progress_callback: 进度回调
        :return: (是否成功, 消息)
        """
        try:
            # 创建请求
            req = urllib.request.Request(url)
            req.add_header('User-Agent', 'Mozilla/5.0')
            
            # 打开连接
            with urllib.request.urlopen(req, timeout=30) as response:
                # 获取文件大小
                content_length = response.getheader('Content-Length')
                if content_length:
                    total_size = int(content_length)
                else:
                    total_size = total_size_mb * 1024 * 1024  # 使用预估大小
                
                # 下载文件
                downloaded = 0
                start_time = time.time()
                
                with open(dest_path, 'wb') as f:
                    while True:
                        chunk = response.read(self.CHUNK_SIZE)
                        if not chunk:
                            break
                        
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        # 计算进度
                        downloaded_mb = downloaded / (1024 * 1024)
                        total_mb = total_size / (1024 * 1024)
                        percent = (downloaded / total_size * 100) if total_size > 0 else 0
                        
                        # 计算速度
                        elapsed = time.time() - start_time
                        speed_mbps = (downloaded_mb / elapsed) if elapsed > 0 else 0
                        
                        # 回调进度
                        if progress_callback:
                            msg = f"下载中... {downloaded_mb:.1f}/{total_mb:.1f} MB ({percent:.1f}%) - {speed_mbps:.1f} MB/s"
                            progress_callback(int(downloaded_mb), int(total_mb), msg)
                
                # 下载完成
                elapsed_time = time.time() - start_time
                msg = f"✓ 下载完成 (耗时: {elapsed_time:.1f}秒)"
                if progress_callback:
                    progress_callback(int(downloaded_mb), int(total_mb), msg)
                
                return True, msg
        
        except urllib.error.URLError as e:
            # 清理不完整的文件
            if dest_path.exists():
                dest_path.unlink()
            return False, f"网络错误: {e.reason}"
        
        except Exception as e:
            # 清理不完整的文件
            if dest_path.exists():
                dest_path.unlink()
            return False, str(e)
    
    def extract(
        self,
        engine_type: str,
        progress_callback: Optional[Callable[[str], None]] = None
    ) -> Tuple[bool, str]:
        """
        解压引擎文件
        
        :param engine_type: 引擎类型 ('paddle' 或 'rapid')
        :param progress_callback: 进度回调函数 callback(message)
        :return: (是否成功, 消息)
        
        验证需求: 6.3
        """
        if engine_type not in self.ENGINES:
            return False, f"不支持的引擎类型: {engine_type}"
        
        config = self.ENGINES[engine_type]
        engine_name = config['display_name']
        
        # 检查是否已安装
        if self.is_installed(engine_type):
            msg = f"{engine_name} 已安装，无需解压"
            if progress_callback:
                progress_callback(msg)
            return True, msg
        
        # 检查压缩包是否存在
        archive_name = config['archive_name']
        archive_path = self.models_dir / engine_type / archive_name
        
        if not archive_path.exists():
            msg = f"{engine_name} 压缩包不存在: {archive_path}"
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
        target_dir = self.project_root / config['target_dir']
        target_parent = target_dir.parent
        
        # 确保目标目录的父目录存在
        target_parent.mkdir(parents=True, exist_ok=True)
        
        if progress_callback:
            progress_callback(f"正在解压 {engine_name}...")
        
        # 构建7z解压命令
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
            if self.is_installed(engine_type):
                msg = f"✓ {engine_name} 解压成功 (耗时: {elapsed_time:.1f}秒)"
                if progress_callback:
                    progress_callback(msg)
                return True, msg
            else:
                msg = f"✗ {engine_name} 解压失败: 标记文件不存在"
                if progress_callback:
                    progress_callback(msg)
                return False, msg
        
        except subprocess.CalledProcessError as e:
            msg = f"✗ {engine_name} 解压失败: {e.stderr}"
            if progress_callback:
                progress_callback(msg)
            return False, msg
        
        except Exception as e:
            msg = f"✗ {engine_name} 解压失败: {e}"
            if progress_callback:
                progress_callback(msg)
            return False, msg
    
    def download_and_install(
        self,
        engine_type: str,
        download_progress_callback: Optional[Callable[[int, int, str], None]] = None,
        extract_progress_callback: Optional[Callable[[str], None]] = None
    ) -> Tuple[bool, str]:
        """
        下载并安装引擎（一站式方法）
        
        :param engine_type: 引擎类型
        :param download_progress_callback: 下载进度回调
        :param extract_progress_callback: 解压进度回调
        :return: (是否成功, 消息)
        
        验证需求: 6.2, 6.3
        """
        # 步骤1: 下载
        success, msg = self.download(engine_type, download_progress_callback)
        if not success:
            return False, msg
        
        # 步骤2: 解压
        success, msg = self.extract(engine_type, extract_progress_callback)
        if not success:
            return False, msg
        
        return True, f"✓ {self.ENGINES[engine_type]['display_name']} 安装成功"
    
    def get_all_engines_status(self) -> Dict[str, Dict]:
        """
        获取所有引擎的状态
        
        :return: 引擎状态字典
        """
        status = {}
        for engine_type in self.ENGINES.keys():
            status[engine_type] = self.get_engine_info(engine_type)
        return status
    
    def print_status(self):
        """打印所有引擎状态"""
        print("\n" + "="*60)
        print("OCR 引擎下载器状态")
        print("="*60)
        
        for engine_type, config in self.ENGINES.items():
            installed = self.is_installed(engine_type)
            print(f"\n{config['display_name']}:")
            print(f"  类型: {engine_type}")
            print(f"  已安装: {'✓' if installed else '✗'}")
            print(f"  大小: {config['size_mb']} MB")
            print(f"  下载地址: {config['url']}")
        
        print("\n" + "="*60)


# 全局实例
_downloader = None


def get_downloader() -> OCREngineDownloader:
    """获取全局下载器实例"""
    global _downloader
    if _downloader is None:
        _downloader = OCREngineDownloader()
    return _downloader


def main():
    """主函数 - 用于测试"""
    downloader = OCREngineDownloader()
    downloader.print_status()
    
    # 测试下载（仅显示状态，不实际下载）
    print("\n测试下载功能:")
    for engine_type in ['paddle', 'rapid']:
        if not downloader.is_installed(engine_type):
            print(f"\n{engine_type} 未安装")
            print(f"可以使用 download('{engine_type}') 下载")


if __name__ == '__main__':
    main()
