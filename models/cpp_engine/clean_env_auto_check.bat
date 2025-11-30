
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
