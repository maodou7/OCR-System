# 集成测试快速指南

## 概述

本指南提供了运行所有集成测试的快速参考。

## 前置要求

### 必需
```bash
pip install PySide6 Pillow openpyxl PyMuPDF
```

### 强烈推荐
```bash
pip install psutil  # 用于内存测试
```

## 快速测试（推荐用于日常开发）

运行所有快速测试（约5分钟）:

```bash
# 1. 功能测试
python test_integration_functionality.py

# 2. 性能测试
python test_integration_performance.py

# 3. 快速工作流测试
python test_integration_comprehensive.py --quick
```

## 完整测试（推荐用于发布前）

### 1. 打包测试

```bash
python test_integration_packaging.py
```

**耗时**: 5-10分钟  
**输出**: `INTEGRATION_TEST_PACKAGING_REPORT.md`

### 2. 功能完整性测试

```bash
python test_integration_functionality.py
```

**耗时**: 1-2分钟  
**输出**: `INTEGRATION_TEST_FUNCTIONALITY_REPORT.md`

### 3. 性能指标测试

```bash
python test_integration_performance.py
```

**耗时**: 2-3分钟  
**输出**: `INTEGRATION_TEST_PERFORMANCE_REPORT.md`, `performance_current.json`

### 4. 完整工作流测试

```bash
python test_integration_comprehensive.py
```

**耗时**: 10-15分钟  
**输出**: `INTEGRATION_TEST_COMPREHENSIVE_REPORT.md`

### 5. 干净环境测试

```bash
# 生成测试工具
python test_integration_clean_environment.py

# 然后在虚拟机中:
# 1. 复制打包后的程序到虚拟机
# 2. 复制 clean_env_auto_check.bat 到程序目录
# 3. 运行 clean_env_auto_check.bat
# 4. 按照 CLEAN_ENVIRONMENT_TEST_CHECKLIST.md 进行测试
```

**耗时**: 30-60分钟（手动）  
**输出**: `CLEAN_ENVIRONMENT_TEST_CHECKLIST.md`, `clean_env_auto_check.bat`

## 一键运行所有测试

创建批处理脚本 `run_all_tests.bat`:

```batch
@echo off
echo ========================================
echo 运行所有集成测试
echo ========================================
echo.

echo [1/4] 功能完整性测试...
python test_integration_functionality.py
if errorlevel 1 goto :error

echo.
echo [2/4] 性能指标测试...
python test_integration_performance.py
if errorlevel 1 goto :error

echo.
echo [3/4] 快速工作流测试...
python test_integration_comprehensive.py --quick
if errorlevel 1 goto :error

echo.
echo [4/4] 生成干净环境测试工具...
python test_integration_clean_environment.py
if errorlevel 1 goto :error

echo.
echo ========================================
echo 所有测试完成!
echo ========================================
echo.
echo 查看生成的报告:
echo - INTEGRATION_TEST_FUNCTIONALITY_REPORT.md
echo - INTEGRATION_TEST_PERFORMANCE_REPORT.md
echo - INTEGRATION_TEST_COMPREHENSIVE_REPORT.md
echo - CLEAN_ENVIRONMENT_TEST_CHECKLIST.md
echo.
pause
exit /b 0

:error
echo.
echo ========================================
echo 测试失败!
echo ========================================
echo.
pause
exit /b 1
```

然后运行:
```bash
run_all_tests.bat
```

## 测试结果检查

### 查看报告

所有测试都会生成Markdown格式的报告:

```bash
# Windows
start INTEGRATION_TEST_FUNCTIONALITY_REPORT.md
start INTEGRATION_TEST_PERFORMANCE_REPORT.md
start INTEGRATION_TEST_COMPREHENSIVE_REPORT.md

# Linux/Mac
open INTEGRATION_TEST_FUNCTIONALITY_REPORT.md
open INTEGRATION_TEST_PERFORMANCE_REPORT.md
open INTEGRATION_TEST_COMPREHENSIVE_REPORT.md
```

### 检查测试状态

查看报告中的状态标记:
- ✅ 通过
- ❌ 失败
- ⚠️  警告

### 关键指标

**体积**:
- 核心程序 < 100MB ✅
- 含RapidOCR < 250MB ✅

**性能**:
- 启动时间 < 1秒 ✅
- 完全就绪 < 3秒 ✅
- 空闲内存 < 200MB ✅

**稳定性**:
- 无内存泄漏 ✅
- 长时间运行稳定 ✅

## 故障排除

### 问题: psutil未安装

```bash
pip install psutil
```

### 问题: 打包失败

检查:
1. PyInstaller是否安装: `pip install pyinstaller`
2. spec文件是否存在: `Pack/Pyinstaller/ocr_system_core.spec`
3. 磁盘空间是否充足

### 问题: 测试超时

使用快速模式:
```bash
python test_integration_comprehensive.py --quick
```

### 问题: 内存测试失败

确保:
1. psutil已安装
2. 关闭其他程序
3. 系统有足够内存

## 持续集成

### GitHub Actions 示例

```yaml
name: Integration Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install psutil
    
    - name: Run functionality tests
      run: python test_integration_functionality.py
    
    - name: Run performance tests
      run: python test_integration_performance.py
    
    - name: Run quick workflow tests
      run: python test_integration_comprehensive.py --quick
    
    - name: Upload reports
      uses: actions/upload-artifact@v2
      with:
        name: test-reports
        path: |
          INTEGRATION_TEST_*.md
          performance_current.json
```

## 测试频率建议

### 每次提交
- 功能完整性测试
- 快速工作流测试

### 每日构建
- 功能完整性测试
- 性能指标测试
- 快速工作流测试

### 发布前
- 所有测试（包括完整工作流）
- 打包测试
- 干净环境测试

## 报告解读

### 功能测试报告

查看:
- 通过的测试数量
- 失败的测试项
- 模块加载情况

### 性能测试报告

关注:
- 启动时间是否达标
- 内存占用是否合理
- 与基线的对比

### 工作流测试报告

检查:
- 工作流是否完整
- 内存增长是否正常
- 稳定性是否良好

## 总结

- ✅ 快速测试: 5分钟
- ✅ 完整测试: 20-30分钟
- ✅ 含虚拟机测试: 1-2小时

**建议**: 日常开发使用快速测试，发布前执行完整测试。
