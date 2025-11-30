"""
评估 Mobile vs Server OCR 模型
对比移动版和服务器版模型的识别精度和文件大小
"""

import os
import sys
import json
import time
import tempfile
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PPOCR_api import GetOcrApi
from config import get_resource_path


class ModelEvaluator:
    """模型评估器"""
    
    def __init__(self):
        self.paddle_exe = get_resource_path(
            os.path.join("models", "PaddleOCR-json", "PaddleOCR-json_v1.4.1", "PaddleOCR-json.exe")
        )
        self.models_dir = get_resource_path(
            os.path.join("models", "PaddleOCR-json", "PaddleOCR-json_v1.4.1", "models")
        )
        
        if not os.path.exists(self.paddle_exe):
            raise Exception(f"PaddleOCR-json.exe 不存在: {self.paddle_exe}")
    
    def get_model_size(self, model_path):
        """获取模型文件大小（MB）"""
        total_size = 0
        if os.path.isdir(model_path):
            for root, dirs, files in os.walk(model_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    total_size += os.path.getsize(file_path)
        elif os.path.isfile(model_path):
            total_size = os.path.getsize(model_path)
        return round(total_size / (1024 * 1024), 2)
    
    def analyze_current_models(self):
        """分析当前模型大小"""
        print("="*60)
        print("当前模型分析")
        print("="*60)
        
        models_info = {}
        
        # 检测模型
        det_model = os.path.join(self.models_dir, "ch_PP-OCRv3_det_infer")
        if os.path.exists(det_model):
            size = self.get_model_size(det_model)
            models_info['detection'] = {
                'name': 'ch_PP-OCRv3_det_infer',
                'type': 'server',
                'size_mb': size
            }
            print(f"检测模型 (Detection): {size} MB - PP-OCRv3 (Server)")
        
        # 识别模型 - 中文
        rec_model_ch = os.path.join(self.models_dir, "ch_PP-OCRv3_rec_infer")
        if os.path.exists(rec_model_ch):
            size = self.get_model_size(rec_model_ch)
            models_info['recognition_ch'] = {
                'name': 'ch_PP-OCRv3_rec_infer',
                'type': 'server',
                'size_mb': size
            }
            print(f"识别模型-中文 (Recognition-CN): {size} MB - PP-OCRv3 (Server)")
        
        # 识别模型 - 英文
        rec_model_en = os.path.join(self.models_dir, "en_PP-OCRv3_rec_infer")
        if os.path.exists(rec_model_en):
            size = self.get_model_size(rec_model_en)
            models_info['recognition_en'] = {
                'name': 'en_PP-OCRv3_rec_infer',
                'type': 'server',
                'size_mb': size
            }
            print(f"识别模型-英文 (Recognition-EN): {size} MB - PP-OCRv3 (Server)")
        
        # 分类模型
        cls_model = os.path.join(self.models_dir, "ch_ppocr_mobile_v2.0_cls_infer")
        if os.path.exists(cls_model):
            size = self.get_model_size(cls_model)
            models_info['classification'] = {
                'name': 'ch_ppocr_mobile_v2.0_cls_infer',
                'type': 'mobile',
                'size_mb': size
            }
            print(f"分类模型 (Classification): {size} MB - Mobile v2.0")
        
        total_size = sum(m['size_mb'] for m in models_info.values())
        print(f"\n总计: {total_size} MB")
        
        return models_info
    
    def create_test_images(self, output_dir="test_images"):
        """创建测试图片集"""
        print("\n" + "="*60)
        print("创建测试图片集")
        print("="*60)
        
        os.makedirs(output_dir, exist_ok=True)
        
        test_cases = [
            {
                'name': 'simple_chinese',
                'text': '你好世界',
                'expected': '你好世界',
                'lang': 'chinese'
            },
            {
                'name': 'simple_english',
                'text': 'Hello World',
                'expected': 'Hello World',
                'lang': 'english'
            },
            {
                'name': 'mixed_text',
                'text': 'OCR识别测试Test123',
                'expected': 'OCR识别测试Test123',
                'lang': 'mixed'
            },
            {
                'name': 'numbers',
                'text': '1234567890',
                'expected': '1234567890',
                'lang': 'numbers'
            },
            {
                'name': 'long_chinese',
                'text': '这是一段较长的中文文本用于测试OCR识别准确率',
                'expected': '这是一段较长的中文文本用于测试OCR识别准确率',
                'lang': 'chinese'
            },
            {
                'name': 'long_english',
                'text': 'This is a longer English text for testing OCR accuracy',
                'expected': 'This is a longer English text for testing OCR accuracy',
                'lang': 'english'
            },
            {
                'name': 'punctuation',
                'text': '你好这是测试',
                'expected': '你好这是测试',
                'lang': 'chinese'
            },
            {
                'name': 'special_chars',
                'text': '价格99元',
                'expected': '价格99元',
                'lang': 'mixed'
            }
        ]
        
        created_images = []
        
        for case in test_cases:
            # 创建更大的白色背景图片，确保文字清晰
            img = Image.new('RGB', (1200, 300), color='white')
            draw = ImageDraw.Draw(img)
            
            # 尝试使用系统字体，使用更大的字号
            font = None
            try:
                # Windows 系统字体
                if os.name == 'nt':
                    # 尝试多个字体
                    for font_name in ["msyh.ttc", "simhei.ttf", "simsun.ttc", "arial.ttf"]:
                        try:
                            font = ImageFont.truetype(font_name, 60)
                            break
                        except:
                            continue
                else:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 60)
            except:
                pass
            
            if font is None:
                # 如果找不到字体，使用默认字体
                print(f"  警告: 无法加载TrueType字体，使用默认字体")
                font = ImageFont.load_default()
            
            # 绘制文本 - 居中显示
            draw.text((100, 120), case['text'], fill='black', font=font)
            
            # 保存图片
            image_path = os.path.join(output_dir, f"{case['name']}.png")
            img.save(image_path)
            
            case['image_path'] = image_path
            created_images.append(case)
            print(f"✓ 创建测试图片: {case['name']}.png - {case['text']}")
        
        return created_images
    
    def test_ocr_accuracy(self, test_images, config_name="config_chinese.txt"):
        """测试OCR识别准确率"""
        print(f"\n使用配置: {config_name}")
        
        # 初始化OCR引擎
        try:
            # 使用完整的配置文件路径
            config_path = os.path.join(self.models_dir, config_name)
            ocr = GetOcrApi(self.paddle_exe, argument={"config_path": config_path}, ipcMode="pipe")
        except Exception as e:
            print(f"✗ OCR引擎初始化失败: {e}")
            return None
        
        results = []
        total_chars = 0
        correct_chars = 0
        
        for case in test_images:
            try:
                # 识别图片 - 使用绝对路径
                abs_image_path = os.path.abspath(case['image_path'])
                result = ocr.run(abs_image_path)
                
                if result["code"] == 100:  # 识别成功
                    # 提取识别文本
                    recognized_text = ""
                    for line in result["data"]:
                        text = line.get("text", "").strip()
                        if text:
                            recognized_text += text
                    
                    # 计算准确率
                    expected = case['expected'].replace(" ", "")  # 移除空格进行比较
                    recognized = recognized_text.replace(" ", "")
                    
                    # 字符级别的准确率
                    match_count = sum(1 for e, r in zip(expected, recognized) if e == r)
                    max_len = max(len(expected), len(recognized))
                    
                    if max_len > 0:
                        accuracy = (match_count / max_len) * 100
                    else:
                        accuracy = 100.0 if expected == recognized else 0.0
                    
                    total_chars += len(expected)
                    correct_chars += match_count
                    
                    results.append({
                        'name': case['name'],
                        'expected': case['expected'],
                        'recognized': recognized_text,
                        'accuracy': accuracy,
                        'match': expected == recognized
                    })
                    
                    status = "✓" if expected == recognized else "✗"
                    print(f"{status} {case['name']}: {accuracy:.1f}% - 期望: '{case['expected']}' | 识别: '{recognized_text}'")
                
                elif result["code"] == 101:  # 无文字
                    results.append({
                        'name': case['name'],
                        'expected': case['expected'],
                        'recognized': "",
                        'accuracy': 0.0,
                        'match': False
                    })
                    print(f"✗ {case['name']}: 未识别到文字")
                
                else:
                    error_msg = result.get('data', 'Unknown error')
                    print(f"✗ {case['name']}: 识别失败 (code={result['code']}, error={error_msg})")
            
            except Exception as e:
                print(f"✗ {case['name']}: 异常 - {e}")
        
        # 计算总体准确率
        overall_accuracy = (correct_chars / total_chars * 100) if total_chars > 0 else 0.0
        
        # 关闭OCR引擎
        try:
            ocr.exit()
        except:
            pass
        
        return {
            'results': results,
            'overall_accuracy': overall_accuracy,
            'total_chars': total_chars,
            'correct_chars': correct_chars
        }
    
    def compare_models(self):
        """对比模型性能"""
        print("\n" + "="*60)
        print("模型对比评估")
        print("="*60)
        
        # 1. 分析当前模型大小
        current_models = self.analyze_current_models()
        
        # 2. 创建测试图片
        test_images = self.create_test_images()
        
        # 3. 测试当前模型（Server版本）
        print("\n" + "="*60)
        print("测试当前模型 (PP-OCRv3 Server)")
        print("="*60)
        server_results = self.test_ocr_accuracy(test_images, "config_chinese.txt")
        
        # 4. 生成报告
        report = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'current_models': current_models,
            'server_model_results': server_results,
            'comparison': self.generate_comparison(current_models, server_results)
        }
        
        return report
    
    def generate_comparison(self, models_info, server_results):
        """生成对比分析"""
        comparison = {
            'current_total_size_mb': sum(m['size_mb'] for m in models_info.values()),
            'server_accuracy': server_results['overall_accuracy'] if server_results else 0.0,
            'recommendation': ''
        }
        
        # 分析建议
        print("\n" + "="*60)
        print("分析与建议")
        print("="*60)
        
        print(f"\n当前模型配置:")
        print(f"  - 总大小: {comparison['current_total_size_mb']} MB")
        print(f"  - 识别准确率: {comparison['server_accuracy']:.2f}%")
        
        print(f"\nMobile vs Server 模型对比:")
        print(f"  当前使用: PP-OCRv3 (Server版本)")
        print(f"  - 检测模型: ch_PP-OCRv3_det_infer (~3.6 MB)")
        print(f"  - 识别模型: ch_PP-OCRv3_rec_infer (~11.3 MB)")
        print(f"  - 分类模型: ch_ppocr_mobile_v2.0_cls_infer (~1.4 MB) [已是Mobile版]")
        
        print(f"\n  如果切换到 Mobile 版本:")
        print(f"  - 检测模型: ch_ppocr_mobile_v2.0_det_infer (~2.6 MB) [节省 ~1 MB]")
        print(f"  - 识别模型: ch_ppocr_mobile_v2.0_rec_infer (~4.4 MB) [节省 ~7 MB]")
        print(f"  - 预计总节省: ~8 MB")
        
        # 根据准确率给出建议
        if comparison['server_accuracy'] >= 95.0:
            comparison['recommendation'] = (
                "当前Server模型准确率很高 (≥95%)。\n"
                "建议: 可以尝试切换到Mobile模型以减小体积，但需要先测试Mobile模型的准确率。\n"
                "如果Mobile模型准确率下降<5%，则可以接受切换。"
            )
        elif comparison['server_accuracy'] >= 90.0:
            comparison['recommendation'] = (
                "当前Server模型准确率良好 (90-95%)。\n"
                "建议: 谨慎考虑切换到Mobile模型，需要确保准确率不会显著下降。"
            )
        else:
            comparison['recommendation'] = (
                "当前Server模型准确率较低 (<90%)。\n"
                "建议: 保持使用Server模型，或检查测试数据和配置。"
            )
        
        print(f"\n建议:")
        print(comparison['recommendation'])
        
        # 注意事项
        print(f"\n注意事项:")
        print(f"  1. 本评估使用合成测试图片，实际场景可能有差异")
        print(f"  2. Mobile模型体积更小但精度可能略低")
        print(f"  3. 建议使用实际业务图片进行更全面的测试")
        print(f"  4. 如需下载Mobile模型，请访问PaddleOCR官方仓库")
        
        return comparison
    
    def save_report(self, report, output_file="model_evaluation_report.json"):
        """保存评估报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(f"\n✓ 评估报告已保存: {output_file}")
        
        # 同时生成Markdown报告
        md_file = output_file.replace('.json', '.md')
        self.save_markdown_report(report, md_file)
    
    def save_markdown_report(self, report, output_file):
        """保存Markdown格式报告"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# OCR模型评估报告 - Mobile vs Server\n\n")
            f.write(f"**评估时间**: {report['timestamp']}\n\n")
            
            f.write("## 1. 当前模型配置\n\n")
            f.write("| 模型类型 | 模型名称 | 版本 | 大小(MB) |\n")
            f.write("|---------|---------|------|----------|\n")
            for key, model in report['current_models'].items():
                f.write(f"| {key} | {model['name']} | {model['type']} | {model['size_mb']} |\n")
            
            total_size = report['comparison']['current_total_size_mb']
            f.write(f"\n**总计**: {total_size} MB\n\n")
            
            f.write("## 2. 识别准确率测试\n\n")
            if report['server_model_results']:
                results = report['server_model_results']
                f.write(f"**总体准确率**: {results['overall_accuracy']:.2f}%\n\n")
                f.write(f"**统计**: {results['correct_chars']}/{results['total_chars']} 字符正确\n\n")
                
                f.write("### 详细测试结果\n\n")
                f.write("| 测试用例 | 期望文本 | 识别文本 | 准确率 | 状态 |\n")
                f.write("|---------|---------|---------|--------|------|\n")
                for r in results['results']:
                    status = "✓" if r['match'] else "✗"
                    f.write(f"| {r['name']} | {r['expected']} | {r['recognized']} | {r['accuracy']:.1f}% | {status} |\n")
            
            f.write("\n## 3. Mobile vs Server 对比分析\n\n")
            f.write("### 当前配置 (Server版本)\n\n")
            f.write("- **检测模型**: ch_PP-OCRv3_det_infer (~3.6 MB)\n")
            f.write("- **识别模型**: ch_PP-OCRv3_rec_infer (~11.3 MB)\n")
            f.write("- **分类模型**: ch_ppocr_mobile_v2.0_cls_infer (~1.4 MB) [已是Mobile版]\n\n")
            
            f.write("### 如果切换到 Mobile 版本\n\n")
            f.write("- **检测模型**: ch_ppocr_mobile_v2.0_det_infer (~2.6 MB) [节省 ~1 MB]\n")
            f.write("- **识别模型**: ch_ppocr_mobile_v2.0_rec_infer (~4.4 MB) [节省 ~7 MB]\n")
            f.write("- **预计总节省**: ~8 MB\n\n")
            
            f.write("## 4. 建议\n\n")
            f.write(report['comparison']['recommendation'] + "\n\n")
            
            f.write("## 5. 注意事项\n\n")
            f.write("1. 本评估使用合成测试图片，实际场景可能有差异\n")
            f.write("2. Mobile模型体积更小但精度可能略低\n")
            f.write("3. 建议使用实际业务图片进行更全面的测试\n")
            f.write("4. 如需下载Mobile模型，请访问PaddleOCR官方仓库\n")
        
        print(f"✓ Markdown报告已保存: {output_file}")


def main():
    """主函数"""
    print("="*60)
    print("OCR模型评估工具 - Mobile vs Server")
    print("="*60)
    
    try:
        evaluator = ModelEvaluator()
        report = evaluator.compare_models()
        evaluator.save_report(report)
        
        print("\n" + "="*60)
        print("评估完成！")
        print("="*60)
        print("\n查看详细报告:")
        print("  - JSON格式: model_evaluation_report.json")
        print("  - Markdown格式: model_evaluation_report.md")
        
    except Exception as e:
        print(f"\n✗ 评估失败: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
