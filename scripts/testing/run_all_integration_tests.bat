@echo off
REM ============================================================================
REM 集成测试 - 一键运行所有测试
REM ============================================================================
REM 此脚本自动运行所有集成测试并生成报告
REM ============================================================================

setlocal enabledelayedexpansion

REM 颜色代码（Windows 10+）
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "RESET=[0m"

echo.
echo ================================================================================
echo                        集成测试 - 一键运行所有测试
echo ================================================================================
echo.

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo %RED%错误: Python未安装或不在PATH中%RESET%
    echo.
    pause
    exit /b 1
)

echo %GREEN%Python已安装%RESET%
python --version
echo.

REM 询问测试模式
echo 请选择测试模式:
echo   1. 快速测试 (约5分钟)
echo   2. 完整测试 (约20-30分钟)
echo   3. 仅打包测试
echo   4. 仅功能测试
echo   5. 仅性能测试
echo.
set /p choice="请输入选项 (1-5): "

if "%choice%"=="1" goto :quick_test
if "%choice%"=="2" goto :full_test
if "%choice%"=="3" goto :packaging_test
if "%choice%"=="4" goto :functionality_test
if "%choice%"=="5" goto :performance_test

echo %RED%无效选项%RESET%
pause
exit /b 1

REM ============================================================================
REM 快速测试
REM ============================================================================
:quick_test
echo.
echo ================================================================================
echo                              快速测试模式
echo ================================================================================
echo.

set test_count=0
set passed_count=0

REM 测试1: 功能测试
echo %BLUE%[1/3] 功能完整性测试...%RESET%
echo.
python test_integration_functionality.py
if errorlevel 1 (
    echo %RED%  功能测试失败%RESET%
) else (
    echo %GREEN%  功能测试通过%RESET%
    set /a passed_count+=1
)
set /a test_count+=1
echo.

REM 测试2: 性能测试
echo %BLUE%[2/3] 性能指标测试...%RESET%
echo.
python test_integration_performance.py
if errorlevel 1 (
    echo %RED%  性能测试失败%RESET%
) else (
    echo %GREEN%  性能测试通过%RESET%
    set /a passed_count+=1
)
set /a test_count+=1
echo.

REM 测试3: 快速工作流
echo %BLUE%[3/3] 快速工作流测试...%RESET%
echo.
python test_integration_comprehensive.py --quick
if errorlevel 1 (
    echo %RED%  工作流测试失败%RESET%
) else (
    echo %GREEN%  工作流测试通过%RESET%
    set /a passed_count+=1
)
set /a test_count+=1
echo.

goto :summary

REM ============================================================================
REM 完整测试
REM ============================================================================
:full_test
echo.
echo ================================================================================
echo                              完整测试模式
echo ================================================================================
echo.
echo %YELLOW%警告: 完整测试可能需要20-30分钟%RESET%
echo.
set /p confirm="确认继续? (Y/N): "
if /i not "%confirm%"=="Y" (
    echo 已取消
    pause
    exit /b 0
)
echo.

set test_count=0
set passed_count=0

REM 测试1: 打包测试
echo %BLUE%[1/5] 打包流程测试...%RESET%
echo.
python test_integration_packaging.py
if errorlevel 1 (
    echo %RED%  打包测试失败%RESET%
) else (
    echo %GREEN%  打包测试通过%RESET%
    set /a passed_count+=1
)
set /a test_count+=1
echo.

REM 测试2: 功能测试
echo %BLUE%[2/5] 功能完整性测试...%RESET%
echo.
python test_integration_functionality.py
if errorlevel 1 (
    echo %RED%  功能测试失败%RESET%
) else (
    echo %GREEN%  功能测试通过%RESET%
    set /a passed_count+=1
)
set /a test_count+=1
echo.

REM 测试3: 性能测试
echo %BLUE%[3/5] 性能指标测试...%RESET%
echo.
python test_integration_performance.py
if errorlevel 1 (
    echo %RED%  性能测试失败%RESET%
) else (
    echo %GREEN%  性能测试通过%RESET%
    set /a passed_count+=1
)
set /a test_count+=1
echo.

REM 测试4: 完整工作流
echo %BLUE%[4/5] 完整工作流测试...%RESET%
echo.
python test_integration_comprehensive.py
if errorlevel 1 (
    echo %RED%  工作流测试失败%RESET%
) else (
    echo %GREEN%  工作流测试通过%RESET%
    set /a passed_count+=1
)
set /a test_count+=1
echo.

REM 测试5: 生成干净环境测试工具
echo %BLUE%[5/5] 生成干净环境测试工具...%RESET%
echo.
python test_integration_clean_environment.py
if errorlevel 1 (
    echo %RED%  工具生成失败%RESET%
) else (
    echo %GREEN%  工具生成成功%RESET%
    set /a passed_count+=1
)
set /a test_count+=1
echo.

goto :summary

REM ============================================================================
REM 单项测试
REM ============================================================================
:packaging_test
echo.
echo %BLUE%打包流程测试...%RESET%
echo.
python test_integration_packaging.py
goto :end

:functionality_test
echo.
echo %BLUE%功能完整性测试...%RESET%
echo.
python test_integration_functionality.py
goto :end

:performance_test
echo.
echo %BLUE%性能指标测试...%RESET%
echo.
python test_integration_performance.py
goto :end

REM ============================================================================
REM 测试总结
REM ============================================================================
:summary
echo ================================================================================
echo                              测试总结
echo ================================================================================
echo.
echo 总测试数: %test_count%
echo 通过: %passed_count%
echo 失败: %test_count% - %passed_count% = !test_count! - !passed_count!
echo.

if %passed_count%==%test_count% (
    echo %GREEN%所有测试通过!%RESET%
) else (
    echo %YELLOW%部分测试失败，请查看报告%RESET%
)

echo.
echo 生成的报告:
if exist "INTEGRATION_TEST_PACKAGING_REPORT.md" (
    echo   - INTEGRATION_TEST_PACKAGING_REPORT.md
)
if exist "INTEGRATION_TEST_FUNCTIONALITY_REPORT.md" (
    echo   - INTEGRATION_TEST_FUNCTIONALITY_REPORT.md
)
if exist "INTEGRATION_TEST_PERFORMANCE_REPORT.md" (
    echo   - INTEGRATION_TEST_PERFORMANCE_REPORT.md
)
if exist "INTEGRATION_TEST_COMPREHENSIVE_REPORT.md" (
    echo   - INTEGRATION_TEST_COMPREHENSIVE_REPORT.md
)
if exist "CLEAN_ENVIRONMENT_TEST_CHECKLIST.md" (
    echo   - CLEAN_ENVIRONMENT_TEST_CHECKLIST.md
)
echo.

REM 询问是否打开报告
set /p open_reports="是否打开测试报告? (Y/N): "
if /i "%open_reports%"=="Y" (
    if exist "INTEGRATION_TEST_FUNCTIONALITY_REPORT.md" (
        start "" "INTEGRATION_TEST_FUNCTIONALITY_REPORT.md"
    )
    if exist "INTEGRATION_TEST_PERFORMANCE_REPORT.md" (
        start "" "INTEGRATION_TEST_PERFORMANCE_REPORT.md"
    )
    if exist "INTEGRATION_TEST_COMPREHENSIVE_REPORT.md" (
        start "" "INTEGRATION_TEST_COMPREHENSIVE_REPORT.md"
    )
)

:end
echo.
echo ================================================================================
echo                              测试完成
echo ================================================================================
echo.
pause
exit /b 0
