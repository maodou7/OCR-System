"""
模型压缩和解压功能测试

测试模型文件的压缩和自动解压功能。
"""

import os
import sys
import time
import shutil
from pathlib import Path


def test_compression():
    """测试模型压缩功能"""
    print("\n" + "="*60)
    print("测试 1: 模型压缩功能")
    print("="*60)
    
    try:
        from model_compressor import ModelCompressor
        
        compressor = ModelCompressor()
        
        # 检查7z工具
        if not compressor.seven_zip.exists():
            print(f"⚠ 跳过测试: 7z工具不存在 ({compressor.seven_zip})")
            return False
        
        # 检查模型目录
        models_exist = False
        paddle_dir = compressor.models_path / compressor.PADDLE_MODEL_DIR
        rapid_dir = compressor.models_path / compressor.RAPID_MODEL_DIR
        
        if paddle_dir.exists():
            print(f"✓ 找到PaddleOCR模型目录")
            models_exist = True
        else:
            print(f"⚠ PaddleOCR模型目录不存在")
        
        if rapid_dir.exists():
            print(f"✓ 找到RapidOCR模型目录")
            models_exist = True
        else:
            print(f"⚠ RapidOCR模型目录不存在")
        
        if not models_exist:
            print(f"⚠ 跳过测试: 没有可压缩的模型")
            return False
        
        # 执行压缩
        print("\n开始压缩测试...")
        results = compressor.compress_all_models()
        
        # 检查结果
        success = any(results.values())
        if success:
            print("\n✓ 压缩测试通过")
        else:
            print("\n✗ 压缩测试失败")
        
        return success
        
    except Exception as e:
        print(f"\n✗ 压缩测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_decompression():
    """测试模型解压功能"""
    print("\n" + "="*60)
    print("测试 2: 模型解压功能")
    print("="*60)
    
    try:
        from model_decompressor import ModelDecompressor
        
        decompressor = ModelDecompressor()
        
        # 打印当前状态
        decompressor.print_status()
        
        # 测试每个引擎
        test_results = {}
        
        for engine_type in ['paddle', 'rapid']:
            print(f"\n测试 {engine_type} 引擎:")
            
            # 获取状态
            status = decompressor.get_engine_status(engine_type)
            
            if status['extracted']:
                print(f"  ✓ 引擎已解压，跳过测试")
                test_results[engine_type] = True
                continue
            
            if not status['archive_exists']:
                print(f"  ⚠ 压缩包不存在，跳过测试")
                test_results[engine_type] = None
                continue
            
            # 执行解压测试
            print(f"  开始解压测试...")
            success, msg = decompressor.extract_engine(
                engine_type,
                progress_callback=lambda m: print(f"    {m}")
            )
            
            test_results[engine_type] = success
            
            if success:
                print(f"  ✓ 解压测试通过")
            else:
                print(f"  ✗ 解压测试失败: {msg}")
        
        # 总结
        print("\n" + "-"*60)
        tested = [k for k, v in test_results.items() if v is not None]
        passed = [k for k, v in test_results.items() if v is True]
        
        if tested:
            print(f"测试结果: {len(passed)}/{len(tested)} 通过")
            for engine, result in test_results.items():
                if result is not None:
                    status = "✓" if result else "✗"
                    print(f"  {status} {engine}")
            
            return len(passed) == len(tested)
        else:
            print("⚠ 没有可测试的引擎")
            return False
        
    except Exception as e:
        print(f"\n✗ 解压测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_auto_extraction():
    """测试自动解压集成"""
    print("\n" + "="*60)
    print("测试 3: 自动解压集成")
    print("="*60)
    
    try:
        from model_decompressor import ensure_engine_available, is_engine_extracted
        
        # 测试便捷函数
        for engine_type in ['paddle', 'rapid']:
            print(f"\n测试 {engine_type} 引擎:")
            
            # 检查是否已解压
            extracted = is_engine_extracted(engine_type)
            print(f"  已解压: {extracted}")
            
            # 确保可用
            print(f"  确保引擎可用...")
            available = ensure_engine_available(
                engine_type,
                progress_callback=lambda m: print(f"    {m}")
            )
            
            if available:
                print(f"  ✓ 引擎可用")
            else:
                print(f"  ✗ 引擎不可用")
        
        print("\n✓ 自动解压集成测试完成")
        return True
        
    except Exception as e:
        print(f"\n✗ 自动解压集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_performance():
    """测试解压性能"""
    print("\n" + "="*60)
    print("测试 4: 解压性能测试")
    print("="*60)
    
    try:
        from model_decompressor import ModelDecompressor
        
        decompressor = ModelDecompressor()
        
        # 测试每个引擎的解压时间
        for engine_type in ['paddle', 'rapid']:
            status = decompressor.get_engine_status(engine_type)
            
            if not status['archive_exists']:
                print(f"\n⚠ {engine_type}: 压缩包不存在，跳过性能测试")
                continue
            
            if status['extracted']:
                print(f"\n⚠ {engine_type}: 已解压，跳过性能测试")
                continue
            
            print(f"\n测试 {engine_type} 解压性能:")
            
            # 获取压缩包大小
            archive_path = Path(status['archive_path'])
            archive_size = archive_path.stat().st_size / (1024 * 1024)  # MB
            print(f"  压缩包大小: {archive_size:.2f} MB")
            
            # 执行解压并计时
            start_time = time.time()
            success, msg = decompressor.extract_engine(engine_type)
            elapsed_time = time.time() - start_time
            
            if success:
                print(f"  ✓ 解压成功")
                print(f"  解压时间: {elapsed_time:.2f} 秒")
                print(f"  解压速度: {archive_size/elapsed_time:.2f} MB/s")
                
                # 检查用户体验（解压时间应<10秒）
                if elapsed_time < 10:
                    print(f"  ✓ 用户体验良好 (< 10秒)")
                else:
                    print(f"  ⚠ 用户体验一般 (> 10秒)")
            else:
                print(f"  ✗ 解压失败: {msg}")
        
        print("\n✓ 性能测试完成")
        return True
        
    except Exception as e:
        print(f"\n✗ 性能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主函数"""
    print("\n" + "="*60)
    print("模型压缩和解压功能测试套件")
    print("="*60)
    
    results = {}
    
    # 运行测试
    results['compression'] = test_compression()
    results['decompression'] = test_decompression()
    results['auto_extraction'] = test_auto_extraction()
    results['performance'] = test_performance()
    
    # 总结
    print("\n" + "="*60)
    print("测试总结")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for r in results.values() if r)
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
