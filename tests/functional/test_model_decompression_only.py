"""
简单的模型解压功能测试

只测试解压功能，不执行压缩（压缩耗时较长）。
"""

import sys


def test_decompressor_import():
    """测试解压器模块导入"""
    print("\n测试 1: 导入解压器模块")
    try:
        from model_decompressor import ModelDecompressor, ensure_engine_available, is_engine_extracted
        print("✓ 解压器模块导入成功")
        return True
    except Exception as e:
        print(f"✗ 解压器模块导入失败: {e}")
        return False


def test_decompressor_status():
    """测试解压器状态检查"""
    print("\n测试 2: 检查引擎状态")
    try:
        from model_decompressor import ModelDecompressor
        
        decompressor = ModelDecompressor()
        decompressor.print_status()
        
        print("\n✓ 状态检查成功")
        return True
    except Exception as e:
        print(f"✗ 状态检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_engine_detection():
    """测试引擎检测"""
    print("\n测试 3: 引擎检测")
    try:
        from model_decompressor import is_engine_extracted
        
        for engine_type in ['paddle', 'rapid']:
            extracted = is_engine_extracted(engine_type)
            print(f"  {engine_type}: {'已解压' if extracted else '未解压'}")
        
        print("\n✓ 引擎检测成功")
        return True
    except Exception as e:
        print(f"✗ 引擎检测失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ocr_manager_integration():
    """测试OCR管理器集成"""
    print("\n测试 4: OCR管理器集成")
    try:
        # 测试OCR管理器是否能正确导入解压器
        import ocr_engine_manager
        
        print("  检查OCR引擎可用性...")
        ocr_engine_manager.OCREngineManager._check_engine_availability()
        
        print("\n✓ OCR管理器集成成功")
        return True
    except Exception as e:
        print(f"✗ OCR管理器集成失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("="*60)
    print("模型解压功能测试")
    print("="*60)
    
    results = []
    
    # 运行测试
    results.append(("导入测试", test_decompressor_import()))
    results.append(("状态检查", test_decompressor_status()))
    results.append(("引擎检测", test_engine_detection()))
    results.append(("OCR集成", test_ocr_manager_integration()))
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    for test_name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n✓ 所有测试通过")
        return 0
    else:
        print("\n⚠ 部分测试失败")
        return 1


if __name__ == '__main__':
    sys.exit(main())
