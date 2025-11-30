@echo off
chcp 65001 >nul
REM ============================================================================
REM OCR System - PyInstaller 打包脚本 (Windows)
REM ============================================================================
REM 此脚本用于自动化 PyInstaller 打包流程
REM 支持单文件模式和文件夹模式
REM ============================================================================

setlocal enabledelayedexpansion

REM 设置颜色代码（用于美化输出）
set "GREEN=[92m"
set "RED=[91m"
set "YELLOW=[93m"
set "BLUE=[94m"
set "RESET=[0m"

REM 获取项目根目录（脚本所在目录的上两级）
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"
cd ..\..
set "PROJECT_ROOT=%CD%"
cd /d "%SCRIPT_DIR%"

echo.
echo %BLUE%========================================%RESET%
echo %BLUE%   OCR System - PyInstaller 打包工具   %RESET%
echo %BLUE%========================================%RESET%
echo.

REM ============================================================================
REM 环境验证
REM ============================================================================

:check_environment
echo %YELLOW%[1/3] 检查环境...%RESET%

REM 检查 PyInstaller 是否安装（优先使用项目中的 portable_python）
set "PYINSTALLER_CMD=pyinstaller"
if exist "%PROJECT_ROOT%\portable_python\Scripts\pyinstaller.exe" (
    set "PYINSTALLER_CMD=%PROJECT_ROOT%\portable_python\Scripts\pyinstaller.exe"
    set "PYTHON_CMD=%PROJECT_ROOT%\portable_python\python.exe"
) else (
    set "PYTHON_CMD=python"
)

%PYINSTALLER_CMD% --version >nul 2>&1
if errorlevel 1 (
    echo %RED%错误: PyInstaller 未安装%RESET%
    echo.
    echo 请使用以下命令安装 PyInstaller:
    echo     pip install pyinstaller
    echo.
    echo 或者使用项目中的 portable_python:
    echo     .\portable_python\python.exe -m pip install pyinstaller
    echo.
    exit /b 1
)

echo %GREEN%  ✓ PyInstaller 已安装%RESET%

REM 检查必需的源文件
set "MISSING_FILES="
set "REQUIRED_FILES=qt_run.py qt_main.py config.py"

for %%F in (%REQUIRED_FILES%) do (
    if not exist "%PROJECT_ROOT%\%%F" (
        set "MISSING_FILES=!MISSING_FILES! %%F"
    )
)

if not "!MISSING_FILES!"=="" (
    echo %RED%错误: 缺少必需的源文件:%RESET%
    for %%F in (!MISSING_FILES!) do (
        echo   - %%F
    )
    echo.
    exit /b 1
)

echo %GREEN%  ✓ 所有必需源文件存在%RESET%

REM 检查 spec 文件
if not exist "%SCRIPT_DIR%ocr_system.spec" (
    echo %YELLOW%  ! 警告: ocr_system.spec 不存在%RESET%
    echo %YELLOW%    PyInstaller 将自动生成 spec 文件%RESET%
)

echo.

REM ============================================================================
REM 主菜单
REM ============================================================================

:main_menu
echo %BLUE%========================================%RESET%
echo %BLUE%   请选择打包模式:%RESET%
echo %BLUE%========================================%RESET%
echo.
echo   1. 单文件模式 (生成单个 .exe 文件)
echo   2. 文件夹模式 (生成包含依赖的文件夹)
echo   3. 清理构建文件
echo   4. 清理缓存和临时文件 (推荐打包前执行)
echo   5. 退出
echo.

choice /C 12345 /N /M "请输入选项 (1-5): "
set "MENU_CHOICE=%errorlevel%"

if "%MENU_CHOICE%"=="1" goto build_onefile
if "%MENU_CHOICE%"=="2" goto build_onefolder
if "%MENU_CHOICE%"=="3" goto clean_build
if "%MENU_CHOICE%"=="4" goto clean_cache
if "%MENU_CHOICE%"=="5" goto exit_script

REM 如果到达这里，说明出现了意外情况
goto main_menu

REM ============================================================================
REM 清理功能
REM ============================================================================

:clean_build
echo.
echo %YELLOW%[清理] 准备清理构建文件...%RESET%
echo.

set "CLEAN_TARGETS="
if exist "%SCRIPT_DIR%build" set "CLEAN_TARGETS=!CLEAN_TARGETS! build"
if exist "%SCRIPT_DIR%dist" set "CLEAN_TARGETS=!CLEAN_TARGETS! dist"
if exist "%PROJECT_ROOT%\build" set "CLEAN_TARGETS=!CLEAN_TARGETS! 项目根目录的build"
if exist "%PROJECT_ROOT%\dist" set "CLEAN_TARGETS=!CLEAN_TARGETS! 项目根目录的dist"

if "!CLEAN_TARGETS!"=="" (
    echo %GREEN%没有需要清理的文件%RESET%
    echo.
    pause
    goto main_menu
)

echo 将要删除以下目录:
echo !CLEAN_TARGETS!
echo.

choice /C YN /M "确认清理? (Y/N): "
if errorlevel 2 (
    echo %YELLOW%已取消清理%RESET%
    echo.
    pause
    goto main_menu
)

echo.
echo %YELLOW%正在清理...%RESET%

if exist "%SCRIPT_DIR%build" (
    rmdir /s /q "%SCRIPT_DIR%build" 2>nul
    if errorlevel 1 (
        echo %RED%  ✗ 无法删除 build 目录%RESET%
    ) else (
        echo %GREEN%  ✓ 已删除 build 目录%RESET%
    )
)

if exist "%SCRIPT_DIR%dist" (
    rmdir /s /q "%SCRIPT_DIR%dist" 2>nul
    if errorlevel 1 (
        echo %RED%  ✗ 无法删除 dist 目录%RESET%
    ) else (
        echo %GREEN%  ✓ 已删除 dist 目录%RESET%
    )
)

if exist "%PROJECT_ROOT%\build" (
    rmdir /s /q "%PROJECT_ROOT%\build" 2>nul
    if errorlevel 1 (
        echo %RED%  ✗ 无法删除项目根目录的 build 目录%RESET%
    ) else (
        echo %GREEN%  ✓ 已删除项目根目录的 build 目录%RESET%
    )
)

if exist "%PROJECT_ROOT%\dist" (
    rmdir /s /q "%PROJECT_ROOT%\dist" 2>nul
    if errorlevel 1 (
        echo %RED%  ✗ 无法删除项目根目录的 dist 目录%RESET%
    ) else (
        echo %GREEN%  ✓ 已删除项目根目录的 dist 目录%RESET%
    )
)

echo.
echo %GREEN%清理完成!%RESET%
echo.
pause
goto main_menu

REM ============================================================================
REM 清理缓存和临时文件
REM ============================================================================

:clean_cache
echo.
echo %YELLOW%[清理] 准备清理缓存和临时文件...%RESET%
echo.
echo 此操作将清理:
echo   - __pycache__ 目录
echo   - .pyc 文件
echo   - 缓存数据库 (.db 文件)
echo   - 临时文件 (*.tmp, *.log, *.bak)
echo.

choice /C YN /M "确认清理? (Y/N): "
if errorlevel 2 (
    echo %YELLOW%已取消清理%RESET%
    echo.
    pause
    goto main_menu
)

echo.
echo %YELLOW%正在执行清理脚本...%RESET%
echo.

REM 切换到项目根目录
cd /d "%PROJECT_ROOT%"

REM 执行清理脚本
%PYTHON_CMD% cleanup_before_packaging.py --auto

if errorlevel 1 (
    echo.
    echo %RED%清理脚本执行失败%RESET%
    echo.
) else (
    echo.
    echo %GREEN%清理完成!%RESET%
    echo.
    echo 详细报告请查看: CLEANUP_REPORT.md
    echo.
)

cd /d "%SCRIPT_DIR%"
pause
goto main_menu

REM ============================================================================
REM 单文件模式构建
REM ============================================================================

:build_onefile
echo.
echo %BLUE%========================================%RESET%
echo %BLUE%   开始单文件模式构建%RESET%
echo %BLUE%========================================%RESET%
echo.

echo %YELLOW%[2/3] 准备构建...%RESET%
echo   模式: 单文件 (--onefile)
echo   输出: dist/OCR-System.exe
echo.

REM 切换到项目根目录执行构建
cd /d "%PROJECT_ROOT%"

echo %YELLOW%[3/3] 执行 PyInstaller...%RESET%
echo.

REM 使用 spec 文件构建（如果存在）
if exist "%SCRIPT_DIR%ocr_system.spec" (
    echo 使用现有的 spec 文件...
    REM 修改 spec 文件为单文件模式
    %PYINSTALLER_CMD% --clean --onefile "%SCRIPT_DIR%ocr_system.spec"
) else (
    echo 生成新的构建配置...
    %PYINSTALLER_CMD% --clean --onefile ^
        --name "OCR-System" ^
        --noconsole ^
        --hidden-import "PySide6.QtCore" ^
        --hidden-import "PySide6.QtGui" ^
        --hidden-import "PySide6.QtWidgets" ^
        --hidden-import "PIL" ^
        --hidden-import "openpyxl" ^
        --hidden-import "fitz" ^
        --hidden-import "openai" ^
        --add-data "models;models" ^
        --add-data "portable_python;portable_python" ^
        --add-data "config.py.example;." ^
        --add-data ".env.example;." ^
        --exclude-module "tkinter" ^
        --exclude-module "matplotlib" ^
        --exclude-module "scipy" ^
        --exclude-module "pandas" ^
        "qt_run.py"
)

if errorlevel 1 (
    echo.
    echo %RED%========================================%RESET%
    echo %RED%   构建失败!%RESET%
    echo %RED%========================================%RESET%
    echo.
    echo 请检查上面的错误信息
    echo.
    cd /d "%SCRIPT_DIR%"
    pause
    goto main_menu
)

echo.
echo %GREEN%========================================%RESET%
echo %GREEN%   构建成功!%RESET%
echo %GREEN%========================================%RESET%
echo.

goto display_results

REM ============================================================================
REM 文件夹模式构建
REM ============================================================================

:build_onefolder
echo.
echo %BLUE%========================================%RESET%
echo %BLUE%   开始文件夹模式构建%RESET%
echo %BLUE%========================================%RESET%
echo.

echo %YELLOW%[2/3] 准备构建...%RESET%
echo   模式: 文件夹 (--onedir)
echo   输出: dist/OCR-System/
echo.

REM 切换到项目根目录执行构建
cd /d "%PROJECT_ROOT%"

echo %YELLOW%[3/3] 执行 PyInstaller...%RESET%
echo.

REM 使用 spec 文件构建（如果存在）
if exist "%SCRIPT_DIR%ocr_system.spec" (
    echo 使用现有的 spec 文件...
    %PYINSTALLER_CMD% --clean "%SCRIPT_DIR%ocr_system.spec"
) else (
    echo 生成新的构建配置...
    %PYINSTALLER_CMD% --clean --onedir ^
        --name "OCR-System" ^
        --noconsole ^
        --hidden-import "PySide6.QtCore" ^
        --hidden-import "PySide6.QtGui" ^
        --hidden-import "PySide6.QtWidgets" ^
        --hidden-import "PIL" ^
        --hidden-import "openpyxl" ^
        --hidden-import "fitz" ^
        --hidden-import "openai" ^
        --add-data "models;models" ^
        --add-data "portable_python;portable_python" ^
        --add-data "config.py.example;." ^
        --add-data ".env.example;." ^
        --exclude-module "tkinter" ^
        --exclude-module "matplotlib" ^
        --exclude-module "scipy" ^
        --exclude-module "pandas" ^
        "qt_run.py"
)

if errorlevel 1 (
    echo.
    echo %RED%========================================%RESET%
    echo %RED%   构建失败!%RESET%
    echo %RED%========================================%RESET%
    echo.
    echo 请检查上面的错误信息
    echo.
    cd /d "%SCRIPT_DIR%"
    pause
    goto main_menu
)

echo.
echo %GREEN%========================================%RESET%
echo %GREEN%   构建成功!%RESET%
echo %GREEN%========================================%RESET%
echo.

goto display_results

REM ============================================================================
REM 显示构建结果
REM ============================================================================

:display_results
echo %BLUE%构建信息:%RESET%
echo.

REM 检查输出文件
if exist "%PROJECT_ROOT%\dist\OCR-System.exe" (
    echo   输出位置: %PROJECT_ROOT%\dist\OCR-System.exe
    
    REM 获取文件大小
    for %%A in ("%PROJECT_ROOT%\dist\OCR-System.exe") do (
        set "FILE_SIZE=%%~zA"
        set /a "SIZE_MB=!FILE_SIZE! / 1048576"
        echo   文件大小: !SIZE_MB! MB
    )
) else if exist "%PROJECT_ROOT%\dist\OCR-System" (
    echo   输出位置: %PROJECT_ROOT%\dist\OCR-System\
    
    REM 计算文件夹大小（简化版本）
    echo   文件夹大小: 请手动检查
    echo.
    echo   主程序: %PROJECT_ROOT%\dist\OCR-System\OCR-System.exe
)

echo.
echo %GREEN%提示:%RESET%
echo   - 可执行文件位于 dist 目录
echo   - 首次运行时会自动创建 config.py
echo   - 可以编辑 config.py 修改配置
echo.

cd /d "%SCRIPT_DIR%"
pause
goto main_menu

REM ============================================================================
REM 退出脚本
REM ============================================================================

:exit_script
echo.
echo %GREEN%感谢使用 OCR System 打包工具!%RESET%
echo.
exit /b 0
