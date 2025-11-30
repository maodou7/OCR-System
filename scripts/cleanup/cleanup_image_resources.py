"""
清理未使用的图像资源
根据分析结果清理未使用的图像文件
"""

import os
import shutil
from pathlib import Path
from typing import List

class ImageResourceCleaner:
    """图像资源清理器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        
    def cleanup_test_images(self, dry_run: bool = True) -> List[str]:
        """清理test_images目录中未使用的图像"""
        test_images_dir = self.project_root / "test_images"
        
        if not test_images_dir.exists():
            print("test_images 目录不存在")
            return []
        
        removed_files = []
        
        # 这些图像是由evaluate_mobile_vs_server_models.py动态生成的
        # 不是项目必需的资源文件
        print("\n" + "="*70)
        print("清理 test_images 目录")
        print("="*70)
        
        for image_file in test_images_dir.glob("*.png"):
            if dry_run:
                print(f"[模拟] 将删除: {image_file.relative_to(self.project_root)}")
                removed_files.append(str(image_file.relative_to(self.project_root)))
            else:
                try:
                    image_file.unlink()
                    print(f"✓ 已删除: {image_file.relative_to(self.project_root)}")
                    removed_files.append(str(image_file.relative_to(self.project_root)))
                except Exception as e:
                    print(f"✗ 删除失败: {image_file.relative_to(self.project_root)} - {e}")
        
        # 如果目录为空，删除目录
        if not dry_run and test_images_dir.exists():
            try:
                if not any(test_images_dir.iterdir()):
                    test_images_dir.rmdir()
                    print(f"✓ 已删除空目录: test_images")
            except Exception as e:
                print(f"✗ 删除目录失败: {e}")
        
        return removed_files
    
    def update_gitignore(self, dry_run: bool = True):
        """更新.gitignore以排除test_images"""
        gitignore_path = self.project_root / ".gitignore"
        
        print("\n" + "="*70)
        print("更新 .gitignore")
        print("="*70)
        
        # 读取现有内容
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                content = f.read()
        else:
            content = ""
        
        # 检查是否已经包含test_images
        if 'test_images/' in content:
            print("✓ .gitignore 已包含 test_images/ 规则")
            return
        
        # 添加test_images规则
        new_rule = "\n# 测试图片目录（由脚本动态生成）\ntest_images/\n"
        
        if dry_run:
            print("[模拟] 将添加规则到 .gitignore:")
            print(new_rule)
        else:
            with open(gitignore_path, 'a', encoding='utf-8') as f:
                f.write(new_rule)
            print("✓ 已更新 .gitignore")
    
    def verify_spec_files(self):
        """验证spec文件是否排除了test_images"""
        print("\n" + "="*70)
        print("验证 PyInstaller spec 文件")
        print("="*70)
        
        spec_files = [
            self.project_root / "Pack" / "Pyinstaller" / "ocr_system.spec",
            self.project_root / "Pack" / "Pyinstaller" / "ocr_system_core.spec"
        ]
        
        for spec_file in spec_files:
            if spec_file.exists():
                with open(spec_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # 检查是否排除了test相关文件
                if 'test_' in content or 'excludes' in content:
                    print(f"✓ {spec_file.name} 包含排除规则")
                else:
                    print(f"⚠ {spec_file.name} 可能需要添加test文件排除规则")
            else:
                print(f"✗ {spec_file.name} 不存在")
    
    def create_readme_note(self, dry_run: bool = True):
        """在test_images目录创建README说明"""
        test_images_dir = self.project_root / "test_images"
        readme_path = test_images_dir / "README.md"
        
        print("\n" + "="*70)
        print("创建 test_images/README.md")
        print("="*70)
        
        readme_content = """# 测试图片目录

此目录用于存放测试图片，由以下脚本动态生成：

- `evaluate_mobile_vs_server_models.py` - 模型评估测试图片

## 说明

- 此目录中的图片**不应**提交到版本控制
- 图片会在运行相关测试脚本时自动生成
- 打包时会自动排除此目录

## 清理

如需清理测试图片，运行：

```bash
python cleanup_image_resources.py --execute
```
"""
        
        if dry_run:
            print("[模拟] 将创建 test_images/README.md")
        else:
            test_images_dir.mkdir(exist_ok=True)
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(readme_content)
            print("✓ 已创建 test_images/README.md")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='清理未使用的图像资源')
    parser.add_argument('--execute', action='store_true', 
                       help='实际执行清理（默认为模拟运行）')
    args = parser.parse_args()
    
    dry_run = not args.execute
    
    if dry_run:
        print("="*70)
        print("模拟运行模式（使用 --execute 参数实际执行）")
        print("="*70)
    else:
        print("="*70)
        print("执行清理操作")
        print("="*70)
    
    cleaner = ImageResourceCleaner()
    
    # 1. 清理test_images
    removed = cleaner.cleanup_test_images(dry_run=dry_run)
    
    # 2. 更新.gitignore
    cleaner.update_gitignore(dry_run=dry_run)
    
    # 3. 验证spec文件
    cleaner.verify_spec_files()
    
    # 4. 创建README说明
    cleaner.create_readme_note(dry_run=dry_run)
    
    # 总结
    print("\n" + "="*70)
    print("清理总结")
    print("="*70)
    
    if removed:
        total_size = sum([
            (Path(f).stat().st_size / 1024) if Path(f).exists() else 0 
            for f in removed
        ])
        print(f"\n{'将' if dry_run else '已'}删除 {len(removed)} 个文件")
        if dry_run:
            print(f"可节省空间: {total_size:.2f} KB")
        else:
            print(f"节省空间: {total_size:.2f} KB")
    else:
        print("\n没有需要清理的文件")
    
    if dry_run:
        print("\n提示: 使用 --execute 参数实际执行清理")


if __name__ == "__main__":
    main()
