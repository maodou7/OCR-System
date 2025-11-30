"""
分析和清理图像资源
审查所有图像资源文件，识别未使用的图像，并提供压缩建议
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Tuple

class ImageResourceAnalyzer:
    """图像资源分析器"""
    
    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self.image_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg', '.tiff', '.tif'}
        self.exclude_dirs = {
            'portable_python', 'dist', 'build', '.git', '__pycache__', 
            '.pytest_cache', 'models', 'Env-Config', '.ocr_cache', 'Pack'
        }
        
    def find_all_images(self) -> List[Tuple[Path, int]]:
        """查找所有图像文件"""
        images = []
        
        for root, dirs, files in os.walk(self.project_root):
            # 排除不需要检查的目录
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in self.image_extensions:
                    size = file_path.stat().st_size
                    images.append((file_path, size))
        
        return images
    
    def check_image_usage(self, image_path: Path) -> Dict[str, any]:
        """检查图像是否被使用"""
        image_name = image_path.name
        image_stem = image_path.stem
        relative_path = image_path.relative_to(self.project_root)
        
        # 搜索所有Python文件和Markdown文件
        references = []
        search_extensions = {'.py', '.md', '.txt', '.spec', '.bat', '.sh'}
        
        for root, dirs, files in os.walk(self.project_root):
            # 排除不需要检查的目录
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                file_path = Path(root) / file
                if file_path.suffix.lower() in search_extensions:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            # 检查文件名或路径是否出现
                            if image_name in content or str(relative_path).replace('\\', '/') in content:
                                references.append(str(file_path.relative_to(self.project_root)))
                    except Exception:
                        pass
        
        return {
            'path': relative_path,
            'size_kb': round(image_path.stat().st_size / 1024, 2),
            'references': references,
            'is_used': len(references) > 0
        }
    
    def analyze(self) -> Dict[str, any]:
        """执行完整分析"""
        print("="*70)
        print("图像资源分析报告")
        print("="*70)
        
        images = self.find_all_images()
        print(f"\n找到 {len(images)} 个图像文件\n")
        
        results = {
            'total_images': len(images),
            'total_size_kb': 0,
            'used_images': [],
            'unused_images': [],
            'by_directory': {}
        }
        
        for image_path, size in images:
            usage_info = self.check_image_usage(image_path)
            results['total_size_kb'] += usage_info['size_kb']
            
            # 按目录分类
            dir_name = str(image_path.parent.relative_to(self.project_root))
            if dir_name not in results['by_directory']:
                results['by_directory'][dir_name] = {
                    'images': [],
                    'total_size_kb': 0
                }
            results['by_directory'][dir_name]['images'].append(usage_info)
            results['by_directory'][dir_name]['total_size_kb'] += usage_info['size_kb']
            
            if usage_info['is_used']:
                results['used_images'].append(usage_info)
            else:
                results['unused_images'].append(usage_info)
        
        return results
    
    def print_report(self, results: Dict[str, any]):
        """打印分析报告"""
        print(f"总图像数量: {results['total_images']}")
        print(f"总大小: {results['total_size_kb']:.2f} KB ({results['total_size_kb']/1024:.2f} MB)")
        print(f"已使用: {len(results['used_images'])}")
        print(f"未使用: {len(results['unused_images'])}")
        
        print("\n" + "="*70)
        print("按目录分类")
        print("="*70)
        
        for dir_name, dir_info in sorted(results['by_directory'].items()):
            print(f"\n目录: {dir_name}")
            print(f"  图像数量: {len(dir_info['images'])}")
            print(f"  总大小: {dir_info['total_size_kb']:.2f} KB")
            
            for img in dir_info['images']:
                status = "✓ 使用中" if img['is_used'] else "✗ 未使用"
                print(f"    {status} - {img['path'].name} ({img['size_kb']:.2f} KB)")
                if img['references']:
                    for ref in img['references'][:3]:  # 只显示前3个引用
                        print(f"        引用于: {ref}")
                    if len(img['references']) > 3:
                        print(f"        ... 还有 {len(img['references']) - 3} 个引用")
        
        if results['unused_images']:
            print("\n" + "="*70)
            print("未使用的图像（可以考虑删除）")
            print("="*70)
            
            total_unused_size = sum(img['size_kb'] for img in results['unused_images'])
            print(f"\n可节省空间: {total_unused_size:.2f} KB ({total_unused_size/1024:.2f} MB)\n")
            
            for img in results['unused_images']:
                print(f"  - {img['path']} ({img['size_kb']:.2f} KB)")
        
        print("\n" + "="*70)
        print("压缩建议")
        print("="*70)
        
        large_images = [img for img in results['used_images'] if img['size_kb'] > 50]
        if large_images:
            print("\n以下图像较大，建议压缩:")
            for img in sorted(large_images, key=lambda x: x['size_kb'], reverse=True):
                print(f"  - {img['path']} ({img['size_kb']:.2f} KB)")
                print(f"    可使用 tinypng.com 或 Pillow 进行压缩")
        else:
            print("\n所有使用中的图像大小都在合理范围内。")
        
        print("\n" + "="*70)
        print("建议操作")
        print("="*70)
        print("\n1. 删除未使用的图像文件")
        print("2. 压缩大于50KB的图像")
        print("3. 考虑使用WebP格式替代PNG/JPG（更小的文件大小）")
        print("4. 确保打包配置排除test_images目录")
        print("5. 检查README中引用的不存在的图像路径")


def main():
    """主函数"""
    analyzer = ImageResourceAnalyzer()
    results = analyzer.analyze()
    analyzer.print_report(results)
    
    # 保存详细报告
    import json
    report_path = "image_resource_analysis.json"
    
    # 转换Path对象为字符串以便JSON序列化
    json_results = {
        'total_images': results['total_images'],
        'total_size_kb': results['total_size_kb'],
        'used_count': len(results['used_images']),
        'unused_count': len(results['unused_images']),
        'used_images': [
            {
                'path': str(img['path']),
                'size_kb': img['size_kb'],
                'references': img['references']
            }
            for img in results['used_images']
        ],
        'unused_images': [
            {
                'path': str(img['path']),
                'size_kb': img['size_kb']
            }
            for img in results['unused_images']
        ]
    }
    
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(json_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n详细报告已保存到: {report_path}")


if __name__ == "__main__":
    main()
