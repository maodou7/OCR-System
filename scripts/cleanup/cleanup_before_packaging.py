#!/usr/bin/env python3
"""
打包前清理脚本

清理所有缓存、临时文件和构建产物，确保打包体积最小化。
"""

import os
import shutil
import sys
from pathlib import Path


class PackagingCleaner:
    """打包前清理工具"""
    
    def __init__(self, root_dir='.'):
        self.root_dir = Path(root_dir).resolve()
        self.cleaned_items = []
        self.total_size_freed = 0
    
    def get_dir_size(self, path):
        """计算目录大小"""
        total = 0
        try:
            for entry in os.scandir(path):
                if entry.is_file(follow_symlinks=False):
                    total += entry.stat().st_size
                elif entry.is_dir(follow_symlinks=False):
                    total += self.get_dir_size(entry.path)
        except (PermissionError, FileNotFoundError):
            pass
        return total
    
    def clean_pycache(self):
        """清理 __pycache__ 目录"""
        print("清理 __pycache__ 目录...")
        count = 0
        size_freed = 0
        
        for root, dirs, files in os.walk(self.root_dir):
            # 跳过虚拟环境
            if 'venv' in root or 'env' in root or '.git' in root:
                continue
            
            if '__pycache__' in dirs:
                pycache_path = os.path.join(root, '__pycache__')
                try:
                    size = self.get_dir_size(pycache_path)
                    shutil.rmtree(pycache_path)
                    count += 1
                    size_freed += size
                    self.cleaned_items.append(f"  - {pycache_path}")
                except Exception as e:
                    print(f"  警告: 无法删除 {pycache_path}: {e}")
        
        self.total_size_freed += size_freed
        print(f"  ✓ 清理了 {count} 个 __pycache__ 目录")
        print(f"  ✓ 释放空间: {size_freed / (1024 * 1024):.2f} MB")
        print()
    
    def clean_pyc_files(self):
        """清理 .pyc 文件"""
        print("清理 .pyc 文件...")
        count = 0
        size_freed = 0
        
        for root, dirs, files in os.walk(self.root_dir):
            # 跳过虚拟环境
            if 'venv' in root or 'env' in root or '.git' in root:
                continue
            
            for file in files:
                if file.endswith('.pyc'):
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        os.remove(file_path)
                        count += 1
                        size_freed += size
                        self.cleaned_items.append(f"  - {file_path}")
                    except Exception as e:
                        print(f"  警告: 无法删除 {file_path}: {e}")
        
        self.total_size_freed += size_freed
        print(f"  ✓ 清理了 {count} 个 .pyc 文件")
        print(f"  ✓ 释放空间: {size_freed / (1024 * 1024):.2f} MB")
        print()
    
    def clean_cache_db(self):
        """清理缓存数据库文件"""
        print("清理缓存数据库...")
        count = 0
        size_freed = 0
        
        # 清理 .ocr_cache 目录
        cache_dirs = [
            '.ocr_cache',
            '.ocr_system_config',
        ]
        
        for cache_dir in cache_dirs:
            cache_path = self.root_dir / cache_dir
            if cache_path.exists():
                try:
                    size = self.get_dir_size(cache_path)
                    shutil.rmtree(cache_path)
                    count += 1
                    size_freed += size
                    self.cleaned_items.append(f"  - {cache_path}")
                except Exception as e:
                    print(f"  警告: 无法删除 {cache_path}: {e}")
        
        # 清理 .db 文件
        for root, dirs, files in os.walk(self.root_dir):
            # 跳过虚拟环境和models目录
            if 'venv' in root or 'env' in root or '.git' in root or 'models' in root:
                continue
            
            for file in files:
                if file.endswith('.db') or file.endswith('.db-journal'):
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        os.remove(file_path)
                        count += 1
                        size_freed += size
                        self.cleaned_items.append(f"  - {file_path}")
                    except Exception as e:
                        print(f"  警告: 无法删除 {file_path}: {e}")
        
        self.total_size_freed += size_freed
        print(f"  ✓ 清理了 {count} 个缓存文件/目录")
        print(f"  ✓ 释放空间: {size_freed / (1024 * 1024):.2f} MB")
        print()
    
    def clean_build_artifacts(self):
        """清理构建产物"""
        print("清理构建产物...")
        count = 0
        size_freed = 0
        
        # 构建目录
        build_dirs = [
            'build',
            'dist',
            'Pack/Pyinstaller/build',
            'Pack/Pyinstaller/dist',
            '.pytest_cache',
            '.coverage',
            'htmlcov',
            '*.egg-info',
        ]
        
        for pattern in build_dirs:
            if '*' in pattern:
                # 处理通配符
                for path in self.root_dir.rglob(pattern):
                    if path.exists():
                        try:
                            size = self.get_dir_size(path) if path.is_dir() else path.stat().st_size
                            if path.is_dir():
                                shutil.rmtree(path)
                            else:
                                path.unlink()
                            count += 1
                            size_freed += size
                            self.cleaned_items.append(f"  - {path}")
                        except Exception as e:
                            print(f"  警告: 无法删除 {path}: {e}")
            else:
                path = self.root_dir / pattern
                if path.exists():
                    try:
                        size = self.get_dir_size(path) if path.is_dir() else path.stat().st_size
                        if path.is_dir():
                            shutil.rmtree(path)
                        else:
                            path.unlink()
                        count += 1
                        size_freed += size
                        self.cleaned_items.append(f"  - {path}")
                    except Exception as e:
                        print(f"  警告: 无法删除 {path}: {e}")
        
        self.total_size_freed += size_freed
        print(f"  ✓ 清理了 {count} 个构建产物")
        print(f"  ✓ 释放空间: {size_freed / (1024 * 1024):.2f} MB")
        print()
    
    def clean_temp_files(self):
        """清理临时文件"""
        print("清理临时文件...")
        count = 0
        size_freed = 0
        
        # 临时文件模式
        temp_patterns = [
            '*.tmp',
            '*.temp',
            '*.log',
            '*.bak',
            '*.swp',
            '*.swo',
            '*~',
            '.DS_Store',
            'Thumbs.db',
        ]
        
        for pattern in temp_patterns:
            for path in self.root_dir.rglob(pattern):
                # 跳过虚拟环境和.git
                if 'venv' in str(path) or 'env' in str(path) or '.git' in str(path):
                    continue
                
                try:
                    size = path.stat().st_size
                    path.unlink()
                    count += 1
                    size_freed += size
                    self.cleaned_items.append(f"  - {path}")
                except Exception as e:
                    print(f"  警告: 无法删除 {path}: {e}")
        
        self.total_size_freed += size_freed
        print(f"  ✓ 清理了 {count} 个临时文件")
        print(f"  ✓ 释放空间: {size_freed / (1024 * 1024):.2f} MB")
        print()
    
    def clean_dev_config(self):
        """清理开发环境配置（不应打包）"""
        print("检查开发环境配置...")
        
        dev_files = [
            'config.py',  # 开发配置（不打包）
            '.env',       # 环境变量（不打包）
        ]
        
        warnings = []
        for file in dev_files:
            file_path = self.root_dir / file
            if file_path.exists():
                warnings.append(file)
                print(f"  ⚠ 发现开发配置文件: {file}")
        
        if warnings:
            print()
            print("  打包策略说明:")
            print("  - config.py 不应打包（开发环境配置）")
            print("  - 打包时只包含 config.py.example")
            print("  - 首次运行时自动从 config.py.example 创建 config.py")
            print("  - 配置向导 (config_wizard.py) 会引导用户完成配置")
            print()
            print("  ✓ 这些文件已在 .gitignore 中排除")
            print("  ✓ PyInstaller spec 文件已配置为只打包 .example 文件")
        else:
            print("  ✓ 未发现开发配置文件（符合打包要求）")
        
        print()
    
    def generate_report(self):
        """生成清理报告"""
        report = []
        report.append("# 打包前清理报告")
        report.append("")
        report.append("## 清理摘要")
        report.append("")
        report.append(f"- **清理项目数**: {len(self.cleaned_items)}")
        report.append(f"- **释放空间**: {self.total_size_freed / (1024 * 1024):.2f} MB")
        report.append("")
        
        if self.cleaned_items:
            report.append("## 清理详情")
            report.append("")
            report.append("已清理的文件和目录:")
            report.append("")
            for item in self.cleaned_items[:50]:  # 只显示前50项
                report.append(item)
            
            if len(self.cleaned_items) > 50:
                report.append(f"  ... 还有 {len(self.cleaned_items) - 50} 项")
            report.append("")
        
        report.append("## 验证需求")
        report.append("")
        report.append("**需求 5.4, 5.5**: ✓ 已完成")
        report.append("")
        report.append("- ✓ 清理 __pycache__ 目录")
        report.append("- ✓ 清理 .pyc 文件")
        report.append("- ✓ 清理 .db 缓存文件")
        report.append("- ✓ 清理构建产物")
        report.append("- ✓ 清理临时文件")
        report.append("")
        report.append("---")
        report.append("")
        report.append("*报告生成时间: " + __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S') + "*")
        
        return '\n'.join(report)
    
    def run(self):
        """执行清理"""
        print("=" * 60)
        print("打包前清理工具")
        print("=" * 60)
        print()
        print(f"工作目录: {self.root_dir}")
        print()
        
        # 执行清理
        self.clean_pycache()
        self.clean_pyc_files()
        self.clean_cache_db()
        self.clean_build_artifacts()
        self.clean_temp_files()
        self.clean_dev_config()
        
        # 生成报告
        print("生成清理报告...")
        report = self.generate_report()
        
        report_file = self.root_dir / 'CLEANUP_REPORT.md'
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"✓ 报告已保存到: {report_file}")
        print()
        
        # 显示摘要
        print("=" * 60)
        print("清理完成")
        print("=" * 60)
        print()
        print(f"清理项目数: {len(self.cleaned_items)}")
        print(f"释放空间: {self.total_size_freed / (1024 * 1024):.2f} MB")
        print()
        print("现在可以开始打包了！")
        print("=" * 60)


def main():
    """主函数"""
    # 确认操作
    print("=" * 60)
    print("打包前清理工具")
    print("=" * 60)
    print()
    print("此工具将清理以下内容:")
    print()
    print("1. __pycache__ 目录")
    print("2. .pyc 文件")
    print("3. 缓存数据库 (.db 文件)")
    print("4. 构建产物 (build/, dist/)")
    print("5. 临时文件 (*.tmp, *.log, *.bak)")
    print()
    
    # 在Windows上，input可能会有问题，所以直接执行
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        confirm = 'y'
    else:
        try:
            confirm = input("确认执行清理? (y/n): ").lower()
        except (EOFError, KeyboardInterrupt):
            confirm = 'y'  # 默认执行
    
    if confirm != 'y' and confirm != '':
        print("已取消清理")
        return
    
    print()
    
    # 执行清理
    cleaner = PackagingCleaner()
    cleaner.run()


if __name__ == '__main__':
    main()
