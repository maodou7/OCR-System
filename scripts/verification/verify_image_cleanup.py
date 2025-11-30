"""
验证图像资源清理
确认所有清理操作已正确完成
"""

import os
from pathlib import Path

class ImageCleanupVerifier:
    """图像清理验证器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.passed = []
        self.failed = []
        
    def verify_test_images_cleaned(self):
        """验证test_images目录已清理"""
        test_images_dir = self.project_root / "test_images"
        
        if not test_images_dir.exists():
            self.passed.append("✓ test_images目录不存在（已完全清理）")
            return True
        
        # 检查是否只有README.md
        files = list(test_images_dir.glob("*"))
        image_files = [f for f in files if f.suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif', '.bmp'}]
        
        if len(image_files) == 0:
            self.passed.append("✓ test_images目录中没有图像文件")
            
            # 检查是否有README.md
            readme = test_images_dir / "README.md"
            if readme.exists():
                self.passed.append("✓ test_images/README.md 存在")
            else:
                self.failed.append("✗ test_images/README.md 不存在")
            
            return len(image_files) == 0
        else:
            self.failed.append(f"✗ test_images目录中仍有 {len(image_files)} 个图像文件")
            for img in image_files:
                self.failed.append(f"  - {img.name}")
            return False
    
    def verify_gitignore_updated(self):
        """验证.gitignore已更新"""
        gitignore_path = self.project_root / ".gitignore"
        
        if not gitignore_path.exists():
            self.failed.append("✗ .gitignore 文件不存在")
            return False
        
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        if 'test_images/' in content:
            self.passed.append("✓ .gitignore 包含 test_images/ 规则")
            return True
        else:
            self.failed.append("✗ .gitignore 不包含 test_images/ 规则")
            return False
    
    def verify_spec_files(self):
        """验证spec文件配置"""
        spec_files = [
            self.project_root / "Pack" / "Pyinstaller" / "ocr_system.spec",
            self.project_root / "Pack" / "Pyinstaller" / "ocr_system_core.spec"
        ]
        
        for spec_file in spec_files:
            if not spec_file.exists():
                self.failed.append(f"✗ {spec_file.name} 不存在")
                continue
            
            with open(spec_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查是否排除了测试相关模块
            if 'pytest' in content and 'unittest' in content:
                self.passed.append(f"✓ {spec_file.name} 排除了测试模块")
            else:
                self.failed.append(f"✗ {spec_file.name} 未排除测试模块")
    
    def verify_readme_fixed(self):
        """验证README.md中的图像引用已修复"""
        readme_path = self.project_root / "README.md"
        
        if not readme_path.exists():
            self.failed.append("✗ README.md 不存在")
            return False
        
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否还有不存在的图像引用
        if 'docs/images/engine-selection.png' in content:
            self.failed.append("✗ README.md 仍包含不存在的图像引用")
            return False
        else:
            self.passed.append("✓ README.md 已修复图像引用")
            return True
    
    def verify_tools_created(self):
        """验证清理工具已创建"""
        tools = [
            'analyze_image_resources.py',
            'cleanup_image_resources.py',
            'IMAGE_RESOURCE_CLEANUP_REPORT.md'
        ]
        
        for tool in tools:
            tool_path = self.project_root / tool
            if tool_path.exists():
                self.passed.append(f"✓ {tool} 已创建")
            else:
                self.failed.append(f"✗ {tool} 不存在")
    
    def run_verification(self):
        """运行所有验证"""
        print("="*70)
        print("图像资源清理验证")
        print("="*70)
        
        print("\n1. 验证test_images目录清理...")
        self.verify_test_images_cleaned()
        
        print("\n2. 验证.gitignore更新...")
        self.verify_gitignore_updated()
        
        print("\n3. 验证spec文件配置...")
        self.verify_spec_files()
        
        print("\n4. 验证README.md修复...")
        self.verify_readme_fixed()
        
        print("\n5. 验证清理工具创建...")
        self.verify_tools_created()
        
        # 打印结果
        print("\n" + "="*70)
        print("验证结果")
        print("="*70)
        
        if self.passed:
            print(f"\n通过的检查 ({len(self.passed)}):")
            for item in self.passed:
                print(f"  {item}")
        
        if self.failed:
            print(f"\n失败的检查 ({len(self.failed)}):")
            for item in self.failed:
                print(f"  {item}")
        
        print("\n" + "="*70)
        
        if not self.failed:
            print("✓ 所有验证通过！图像资源清理任务完成。")
            return True
        else:
            print(f"✗ 有 {len(self.failed)} 项验证失败，请检查。")
            return False


def main():
    """主函数"""
    verifier = ImageCleanupVerifier()
    success = verifier.run_verification()
    
    if success:
        print("\n任务 7.1 已完成:")
        print("  - 列出所有图像资源文件 ✓")
        print("  - 识别未使用的图像 ✓")
        print("  - 清理未使用的图像 ✓")
        print("  - 验证打包配置 ✓")
        print("  - 创建管理工具 ✓")
        
        return 0
    else:
        return 1


if __name__ == "__main__":
    exit(main())
