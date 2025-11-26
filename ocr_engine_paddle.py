"""
PaddleOCR-json 引擎封装
基于高性能 C++ 版本的 PaddleOCR-json
项目地址: https://github.com/hiroi-sora/PaddleOCR-json
"""

import os
import tempfile
from PIL import Image
from PPOCR_api import GetOcrApi


class PaddleOCREngine:
    """PaddleOCR-json 引擎类（高性能C++版本）"""
    
    def __init__(self):
        """初始化 PaddleOCR-json 引擎"""
        import sys
        import subprocess
        
        # 确定 PaddleOCR-json.exe 路径
        current_dir = os.path.dirname(os.path.abspath(__file__))
        exe_path = os.path.join(current_dir, "models", "PaddleOCR-json", "PaddleOCR-json_v1.4.1", "PaddleOCR-json.exe")
        
        if not os.path.exists(exe_path):
            raise Exception(f"PaddleOCR-json.exe 不存在: {exe_path}")
        
        print(f"正在初始化 PaddleOCR-json 引擎...")
        print(f"  - 可执行文件: {exe_path}")
        
        # 检测系统平台，如果是 Linux 则使用 wine
        if sys.platform.startswith('linux'):
            # 检查 wine 是否安装
            try:
                wine_check = subprocess.run(['which', 'wine'], capture_output=True, text=True)
                if wine_check.returncode != 0:
                    raise Exception("在 Linux 系统上运行 Windows exe 需要安装 wine")
                print(f"  - 运行环境: Linux + Wine")
                # 创建 wine 包装脚本
                self._create_wine_wrapper(exe_path)
                exe_path = exe_path + ".sh"  # 使用包装脚本
            except FileNotFoundError:
                raise Exception("在 Linux 系统上运行 Windows exe 需要安装 wine")
        
        # 初始化 OCR API（管道模式，最快）
        try:
            self.ocr = GetOcrApi(exe_path, ipcMode="pipe")
            print(f"✓ PaddleOCR-json 引擎初始化成功")
            print(f"  - 模式: 高性能 C++ 引擎（管道模式）")
            print(f"  - 特性: 极速识别、低内存占用")
        except Exception as e:
            raise Exception(f"PaddleOCR-json 引擎初始化失败: {e}")
    
    def _create_wine_wrapper(self, exe_path):
        """创建 wine 包装脚本"""
        wrapper_path = exe_path + ".sh"
        exe_dir = os.path.dirname(exe_path)
        exe_name = os.path.basename(exe_path)
        
        wrapper_content = f"""#!/bin/bash
cd "{exe_dir}"
wine "{exe_name}" "$@"
"""
        
        with open(wrapper_path, 'w') as f:
            f.write(wrapper_content)
        
        # 添加执行权限
        os.chmod(wrapper_path, 0o755)
        print(f"  - 创建 Wine 包装脚本: {wrapper_path}")
    
    def ocr_image(self, image, rect=None):
        """
        对图片进行OCR识别
        :param image: PIL Image对象
        :param rect: 识别区域 (x1, y1, x2, y2)，None表示识别全图
        :return: 识别文本
        """
        try:
            # 如果指定了区域，先裁剪图片
            if rect:
                x1, y1, x2, y2 = rect
                image = image.crop((x1, y1, x2, y2))
            
            # 保存临时图片文件（PaddleOCR-json 需要文件路径）
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                temp_path = tmp_file.name
                image.save(temp_path)
            
            try:
                # 调用 OCR 识别
                result = self.ocr.run(temp_path)
                
                # 解析结果
                if result["code"] == 100:  # 识别成功
                    texts = []
                    for line in result["data"]:
                        text = line.get("text", "").strip()
                        if text:
                            texts.append(text)
                    return "\n".join(texts) if texts else ""
                elif result["code"] == 101:  # 无文字
                    return ""
                else:  # 识别失败
                    print(f"OCR识别失败: code={result['code']}, data={result['data']}")
                    return ""
            finally:
                # 清理临时文件
                if os.path.exists(temp_path):
                    os.remove(temp_path)
        
        except Exception as e:
            print(f"OCR识别异常: {e}")
            return ""
    
    def is_ready(self):
        """检查引擎是否就绪"""
        return hasattr(self, 'ocr') and self.ocr is not None
    
    def recognize_region(self, image, rect, **kwargs):
        """
        识别图片中的指定区域
        :param image: PIL Image对象
        :param rect: OCRRect对象或坐标元组 (x1, y1, x2, y2)
        :return: 识别的文本字符串
        """
        if not self.is_ready():
            return ""
        
        # 获取坐标
        if hasattr(rect, 'get_coords'):
            coords = rect.get_coords()
        else:
            coords = rect
        
        # 使用 ocr_image 方法识别
        return self.ocr_image(image, rect=coords)
    
    def recognize_regions(self, image, rects, **kwargs):
        """
        批量识别多个区域
        :param image: PIL Image对象
        :param rects: OCRRect对象列表
        :return: 识别结果字典 {rect: text}
        """
        if not self.is_ready():
            return {}
        
        results = {}
        for rect in rects:
            text = self.recognize_region(image, rect, **kwargs)
            results[rect] = text
            
            # 更新rect的text属性
            if hasattr(rect, 'text'):
                rect.text = text
        
        return results
    
    def __del__(self):
        """析构函数，关闭OCR引擎"""
        if hasattr(self, 'ocr') and self.ocr:
            try:
                self.ocr.exit()
            except:
                pass


# 测试代码
if __name__ == "__main__":
    print("="*60)
    print("PaddleOCR-json 引擎测试")
    print("="*60)
    
    try:
        # 初始化引擎
        engine = PaddleOCREngine()
        
        # 测试识别（需要有测试图片）
        test_image_path = "测试图/576DG.jpg"
        if os.path.exists(test_image_path):
            print(f"\n正在识别测试图片: {test_image_path}")
            img = Image.open(test_image_path)
            text = engine.ocr_image(img)
            print(f"\n识别结果：\n{text}")
        else:
            print(f"\n测试图片不存在: {test_image_path}")
        
        print("\n✓ 测试完成")
    
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()
