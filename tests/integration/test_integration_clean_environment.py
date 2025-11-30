#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成测试 - 干净环境测试指南

在干净的系统环境中测试程序，验证无依赖问题，测试首次运行体验。
验证需求: 6.1, 6.2, 6.3, 6.4, 6.5

注意: 此测试需要在虚拟机或干净的Windows环境中手动执行

测试内容:
- 在Windows虚拟机中测试
- 验证无依赖问题
- 测试引擎下载功能
- 测试首次运行体验

使用方法:
    python test_integration_clean_environment.py --generate-checklist
"""

import os
import sys
import argparse
from pathlib import Path


def generate_test_checklist():
    """生成测试检查清单"""
    checklist = """
# 干净环境测试检查清单

## 测试环境准备

### 1. 虚拟机设置
- [ ] 创建Windows 10/11虚拟机
- [ ] 安装最新Windows更新
- [ ] 不安装Python或其他开发工具
- [ ] 不安装Visual C++ Redistributable（测试是否需要）

### 2. 获取测试包
- [ ] 从dist目录复制OCR-System-Core文件夹到虚拟机
- [ ] 或使用7z自解压包安装

## 测试步骤

### 测试1: 首次启动

**目标**: 验证程序可以在干净环境中启动

- [ ] 双击OCR-System-Core.exe启动程序
- [ ] 记录是否出现缺少DLL的错误
- [ ] 记录启动时间（应<3秒）
- [ ] 验证主窗口正常显示

**预期结果**:
- 程序正常启动，无依赖错误
- 主窗口显示正常
- 启动时间在可接受范围内

**实际结果**:
```
[在此记录实际结果]
```

---

### 测试2: 配置向导

**目标**: 验证首次运行配置向导

- [ ] 首次启动时是否显示配置向导
- [ ] 配置向导界面是否友好
- [ ] 可以完成基本配置
- [ ] 配置保存成功

**预期结果**:
- 配置向导自动启动
- 可以轻松完成配置
- 配置文件正确生成

**实际结果**:
```
[在此记录实际结果]
```

---

### 测试3: OCR引擎检测

**目标**: 验证OCR引擎检测和提示

- [ ] 程序检测到没有OCR引擎
- [ ] 显示友好的提示信息
- [ ] 提供下载选项
- [ ] 可以选择"稍后下载"

**预期结果**:
- 清晰提示缺少OCR引擎
- 提供下载和跳过选项
- 不影响程序其他功能

**实际结果**:
```
[在此记录实际结果]
```

---

### 测试4: 引擎下载功能

**目标**: 验证OCR引擎在线下载功能

#### 4.1 RapidOCR下载
- [ ] 选择下载RapidOCR引擎
- [ ] 下载进度显示正常
- [ ] 下载速度合理
- [ ] 自动解压和安装
- [ ] 下载完成后自动配置

**下载信息**:
- 文件大小: ~45MB
- 下载时间: ___秒
- 是否成功: [ ] 是 [ ] 否

#### 4.2 PaddleOCR下载
- [ ] 选择下载PaddleOCR引擎
- [ ] 下载进度显示正常
- [ ] 下载速度合理
- [ ] 自动解压和安装
- [ ] 下载完成后自动配置

**下载信息**:
- 文件大小: ~200MB (优化后)
- 下载时间: ___秒
- 是否成功: [ ] 是 [ ] 否

**预期结果**:
- 下载流程顺畅
- 进度显示准确
- 自动安装配置
- 下载失败有友好提示

**实际结果**:
```
[在此记录实际结果]
```

---

### 测试5: 引擎切换

**目标**: 验证引擎切换功能

- [ ] 在设置中可以看到已安装的引擎
- [ ] 可以切换引擎
- [ ] 切换后OCR功能正常
- [ ] 可以下载未安装的引擎

**预期结果**:
- 引擎列表显示正确
- 切换功能正常
- 下载功能可用

**实际结果**:
```
[在此记录实际结果]
```

---

### 测试6: 基本功能测试

**目标**: 验证核心功能在干净环境中正常工作

#### 6.1 图像加载
- [ ] 可以打开图片文件
- [ ] 图片显示正常
- [ ] 支持常见格式（PNG, JPG, BMP）

#### 6.2 OCR识别
- [ ] OCR识别功能正常
- [ ] 识别结果准确
- [ ] 识别速度合理

#### 6.3 结果导出
- [ ] 可以复制文本
- [ ] 可以导出Excel
- [ ] Excel文件正常打开

#### 6.4 PDF处理
- [ ] 可以打开PDF文件
- [ ] PDF页面显示正常
- [ ] 可以对PDF进行OCR

**预期结果**:
- 所有核心功能正常
- 无崩溃或错误
- 性能符合预期

**实际结果**:
```
[在此记录实际结果]
```

---

### 测试7: 错误处理

**目标**: 验证错误处理和用户提示

#### 7.1 网络错误
- [ ] 断开网络后尝试下载引擎
- [ ] 显示友好的错误提示
- [ ] 提供重试选项
- [ ] 提供手动下载链接

#### 7.2 文件错误
- [ ] 尝试打开损坏的图片
- [ ] 显示友好的错误提示
- [ ] 程序不崩溃

#### 7.3 权限错误
- [ ] 在只读目录运行程序
- [ ] 显示友好的错误提示
- [ ] 提供解决方案

**预期结果**:
- 所有错误都有友好提示
- 程序不崩溃
- 提供解决方案

**实际结果**:
```
[在此记录实际结果]
```

---

### 测试8: 性能测试

**目标**: 验证在干净环境中的性能

- [ ] 启动时间: ___秒
- [ ] 空闲内存占用: ___MB
- [ ] OCR识别速度: ___秒/页
- [ ] 长时间运行稳定性

**性能目标**:
- 启动时间 < 3秒
- 空闲内存 < 200MB
- OCR速度合理
- 无内存泄漏

**实际性能**:
```
[在此记录实际性能数据]
```

---

### 测试9: 用户体验

**目标**: 评估首次使用体验

- [ ] 界面是否直观
- [ ] 功能是否易于发现
- [ ] 提示信息是否清晰
- [ ] 是否需要查看文档

**用户体验评分** (1-5分):
- 易用性: ___/5
- 界面美观: ___/5
- 功能完整性: ___/5
- 性能: ___/5
- 总体满意度: ___/5

**改进建议**:
```
[在此记录改进建议]
```

---

## 测试总结

### 通过的测试
```
[列出通过的测试项]
```

### 失败的测试
```
[列出失败的测试项及原因]
```

### 发现的问题
```
[列出发现的所有问题]
```

### 优化建议
```
[列出优化建议]
```

### 结论
```
[总体评价和结论]
```

---

## 附录: 测试环境信息

- **操作系统**: Windows ___
- **系统版本**: ___
- **CPU**: ___
- **内存**: ___GB
- **测试日期**: ___
- **测试人员**: ___
- **程序版本**: ___

"""
    
    return checklist


def generate_automated_checks():
    """生成自动化检查脚本"""
    script = """
@echo off
REM 干净环境自动化检查脚本
REM 在虚拟机中运行此脚本进行基本检查

echo ========================================
echo 干净环境自动化检查
echo ========================================
echo.

REM 检查1: 程序文件存在
echo [1/6] 检查程序文件...
if exist "OCR-System-Core.exe" (
    echo   [OK] 主程序存在
) else (
    echo   [FAIL] 主程序不存在
    goto :error
)

REM 检查2: 依赖DLL
echo.
echo [2/6] 检查依赖DLL...
if exist "python311.dll" (
    echo   [OK] Python DLL存在
) else (
    echo   [FAIL] Python DLL不存在
    goto :error
)

REM 检查3: 模型目录
echo.
echo [3/6] 检查模型目录...
if exist "models" (
    echo   [OK] 模型目录存在
) else (
    echo   [WARN] 模型目录不存在
)

REM 检查4: 配置文件
echo.
echo [4/6] 检查配置文件...
if exist "config.py.example" (
    echo   [OK] 配置示例存在
) else (
    echo   [WARN] 配置示例不存在
)

REM 检查5: 尝试启动（5秒后自动关闭）
echo.
echo [5/6] 测试启动...
echo   启动程序（5秒后自动关闭）...
start "" "OCR-System-Core.exe"
timeout /t 5 /nobreak >nul
taskkill /f /im "OCR-System-Core.exe" >nul 2>&1

REM 检查6: 生成报告
echo.
echo [6/6] 生成报告...
echo 测试时间: %date% %time% > clean_env_test_result.txt
echo 程序文件: OK >> clean_env_test_result.txt
echo 依赖检查: OK >> clean_env_test_result.txt
echo   [OK] 报告已生成: clean_env_test_result.txt

echo.
echo ========================================
echo 自动化检查完成
echo ========================================
echo.
echo 请查看 clean_env_test_result.txt 获取详细结果
echo 请继续手动测试其他功能
echo.
pause
exit /b 0

:error
echo.
echo ========================================
echo 检查失败
echo ========================================
echo.
pause
exit /b 1
"""
    
    return script


def main():
    parser = argparse.ArgumentParser(description='干净环境测试工具')
    parser.add_argument('--generate-checklist', action='store_true',
                       help='生成测试检查清单')
    parser.add_argument('--generate-script', action='store_true',
                       help='生成自动化检查脚本')
    
    args = parser.parse_args()
    
    if args.generate_checklist:
        checklist = generate_test_checklist()
        output_file = 'CLEAN_ENVIRONMENT_TEST_CHECKLIST.md'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(checklist)
        
        print(f"✅ 测试检查清单已生成: {output_file}")
        print()
        print("请按照检查清单在干净的Windows虚拟机中进行测试")
        print()
        return 0
    
    if args.generate_script:
        script = generate_automated_checks()
        output_file = 'clean_env_auto_check.bat'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(script)
        
        print(f"✅ 自动化检查脚本已生成: {output_file}")
        print()
        print("将此脚本复制到打包后的dist目录中运行")
        print()
        return 0
    
    # 默认: 生成两个文件
    print()
    print("=" * 80)
    print("干净环境测试工具")
    print("=" * 80)
    print()
    
    # 生成检查清单
    checklist = generate_test_checklist()
    checklist_file = 'CLEAN_ENVIRONMENT_TEST_CHECKLIST.md'
    with open(checklist_file, 'w', encoding='utf-8') as f:
        f.write(checklist)
    print(f"✅ 测试检查清单: {checklist_file}")
    
    # 生成自动化脚本
    script = generate_automated_checks()
    script_file = 'clean_env_auto_check.bat'
    with open(script_file, 'w', encoding='utf-8') as f:
        f.write(script)
    print(f"✅ 自动化检查脚本: {script_file}")
    
    print()
    print("=" * 80)
    print("使用说明")
    print("=" * 80)
    print()
    print("1. 准备Windows虚拟机（干净的Windows 10/11）")
    print("2. 将打包后的程序复制到虚拟机")
    print("3. 将 clean_env_auto_check.bat 复制到程序目录")
    print("4. 运行 clean_env_auto_check.bat 进行基本检查")
    print("5. 按照 CLEAN_ENVIRONMENT_TEST_CHECKLIST.md 进行完整测试")
    print("6. 记录测试结果")
    print()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
