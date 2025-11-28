@echo off
REM ============================================================================
REM OCR System - 7-Zip 自解压程序制作脚本 (Windows)
REM ============================================================================
REM 此脚本用于将打包好的应用程序制作成自解压安装包
REM ============================================================================

setlocal enabledelayedexpansion

REM 设置代码页为 UTF-8
chcp 65001 >nul

REM 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
set "PROJECT_ROOT=%SCRIPT_DIR%..\.."

REM 配置变量
set "APP_NAME=OCR-System"
set "APP_VERSION=v1.4.1"
set "SFX_MODULE=%SCRIPT_DIR%7z.sfx"
set "SEVEN_ZIP=%SCRIPT_DIR%7zr.exe"

REM ============================================================================
REM 检查环境
REM ============================================================================

echo.
echo ========================================
echo    OCR System - 自解压程序制作工具
echo ========================================
echo.

echo [1/5] 检查环境...

REM 检查 7zr.exe
if not exist "%SEVEN_ZIP%" (
    echo [错误] 找不到 7zr.exe
    echo 请确保 7zr.exe 位于: %SEVEN_ZIP%
    pause
    exit /b 1
)
echo   [√] 7zr.exe 已找到

REM 检查 7z.sfx
if not exist "%SFX_MODULE%" (
    echo [错误] 找不到 7z.sfx 模块
    echo 请确保 7z.sfx 位于: %SFX_MODULE%
    pause
    exit /b 1
)
echo   [√] 7z.sfx 模块已找到

REM 检查 dist 目录
if not exist "%PROJECT_ROOT%\dist" (
    echo [错误] 找不到 dist 目录
    echo 请先使用 PyInstaller 打包应用程序
    echo 运行: cd Pack\Pyinstaller ^&^& build_package.bat
    pause
    exit /b 1
)
echo   [√] dist 目录已找到

echo.

REM ============================================================================
REM 选择源目录
REM ============================================================================

echo [2/5] 选择要打包的目录...
echo.
echo 可用的打包目录:
echo.

set "option_count=0"

REM 检查文件夹模式
if exist "%PROJECT_ROOT%\dist\%APP_NAME%" (
    set /a option_count+=1
    echo   !option_count!. dist\%APP_NAME%\ ^(文件夹模式^)
    set "option_!option_count!=%PROJECT_ROOT%\dist\%APP_NAME%"
    set "is_folder_!option_count!=1"
)

REM 检查单文件模式
if exist "%PROJECT_ROOT%\dist\%APP_NAME%.exe" (
    set /a option_count+=1
    echo   !option_count!. dist\%APP_NAME%.exe ^(单文件模式^)
    set "option_!option_count!=%PROJECT_ROOT%\dist\%APP_NAME%.exe"
    set "is_folder_!option_count!=0"
)

if %option_count%==0 (
    echo [错误] 在 dist 目录中找不到打包输出
    echo 请先运行 PyInstaller 打包脚本
    pause
    exit /b 1
)

echo.
set /p "choice=请选择 (1-%option_count%): "

if not defined option_%choice% (
    echo [错误] 无效选择
    pause
    exit /b 1
)

set "SOURCE_PATH=!option_%choice%!"
set "IS_FOLDER=!is_folder_%choice%!"
echo   [√] 已选择: !SOURCE_PATH!
echo.

REM ============================================================================
REM 创建临时目录并准备文件
REM ============================================================================

echo [3/5] 准备文件...

set "TEMP_DIR=%SCRIPT_DIR%temp_sfx"
if exist "%TEMP_DIR%" rmdir /s /q "%TEMP_DIR%"
mkdir "%TEMP_DIR%"

REM 复制文件
if "%IS_FOLDER%"=="1" (
    echo   复制文件夹...
    xcopy /E /I /Q /Y "!SOURCE_PATH!\*" "%TEMP_DIR%\" >nul
) else (
    echo   复制单文件...
    copy /Y "!SOURCE_PATH!" "%TEMP_DIR%\" >nul
)

REM 复制配置文件示例
if exist "%PROJECT_ROOT%\config.py.example" (
    copy /Y "%PROJECT_ROOT%\config.py.example" "%TEMP_DIR%\" >nul
    echo   [√] 已添加 config.py.example
)

REM 复制 .env 示例
if exist "%PROJECT_ROOT%\.env.example" (
    copy /Y "%PROJECT_ROOT%\.env.example" "%TEMP_DIR%\" >nul
    echo   [√] 已添加 .env.example
)

REM 创建 README.txt
(
echo OCR System - 批量OCR识别系统
echo.
echo 版本: v1.4.1
echo 发布日期: 2025-11-28
echo.
echo ===========================================
echo 安装说明
echo ===========================================
echo.
echo 1. 本程序为绿色版，无需安装
echo 2. 解压后直接运行 OCR-System.exe 即可
echo 3. 首次运行会自动创建配置文件
echo.
echo ===========================================
echo 使用说明
echo ===========================================
echo.
echo 1. 启动程序
echo    - Windows: 双击 OCR-System.exe
echo    - 或运行: 启动程序点这.bat
echo.
echo 2. 选择 OCR 引擎
echo    - 工具栏选择引擎（推荐 PaddleOCR-json）
echo.
echo 3. 打开文件
echo    - 单个文件: 点击"打开文件"
echo    - 批量处理: 点击"打开文件夹"
echo.
echo 4. 框选识别区域
echo    - 鼠标拖拽框选文字区域
echo    - 可框选多个区域
echo    - 右键删除区域
echo.
echo 5. 开始识别
echo    - 点击"开始识别"按钮
echo    - 等待识别完成
echo.
echo 6. 导出结果
echo    - 点击"导出Excel"保存结果
echo.
echo ===========================================
echo 配置说明
echo ===========================================
echo.
echo 如需使用在线 OCR 引擎（阿里云/DeepSeek）:
echo.
echo 1. 复制 config.py.example 为 config.py
echo 2. 编辑 config.py，填入 API 密钥
echo 3. 重启程序
echo.
echo ===========================================
echo 系统要求
echo ===========================================
echo.
echo - 操作系统: Windows 7/8/10/11 ^(64位^)
echo - 内存: 至少 2GB RAM
echo - 磁盘空间: 至少 1GB 可用空间
echo.
echo ===========================================
echo 常见问题
echo ===========================================
echo.
echo Q: 提示"OCR引擎未就绪"？
echo A: 确保 models 文件夹完整，包含 OCR 引擎文件
echo.
echo Q: 识别速度慢？
echo A: 首次加载需要初始化模型，后续会快
echo.
echo Q: 如何提高准确率？
echo A: 使用高分辨率图片，框选区域贴合文字边缘
echo.
echo ===========================================
echo 技术支持
echo ===========================================
echo.
echo GitHub: https://github.com/maodou7/OCR-System
echo 问题反馈: https://github.com/maodou7/OCR-System/issues
echo.
echo ===========================================
echo 许可证
echo ===========================================
echo.
echo 本软件采用 MIT 许可证
echo 详见: LICENSE 文件
echo.
echo 感谢使用 OCR System！
) > "%TEMP_DIR%\README.txt"

echo   [√] 已创建 README.txt
echo.

REM ============================================================================
REM 创建 7z 压缩包
REM ============================================================================

echo [4/5] 创建 7z 压缩包...

set "OUTPUT_NAME=%APP_NAME%-%APP_VERSION%-Setup"
set "ARCHIVE_FILE=%SCRIPT_DIR%%OUTPUT_NAME%.7z"

REM 删除旧的压缩包
if exist "%ARCHIVE_FILE%" del /f /q "%ARCHIVE_FILE%"

REM 创建压缩包
echo   正在压缩文件（这可能需要几分钟，请耐心等待）...
echo   提示: 文件越大，压缩时间越长
echo.

pushd "%TEMP_DIR%"
REM 使用 -mx7 而不是 -mx9，速度更快，压缩率仍然很好
"%SEVEN_ZIP%" a -mx7 "%ARCHIVE_FILE%" *
popd

if exist "%ARCHIVE_FILE%" (
    echo   [√] 压缩包创建成功
    
    REM 显示文件大小
    for %%F in ("%ARCHIVE_FILE%") do (
        set "size=%%~zF"
        set /a "size_mb=!size! / 1048576"
        echo   压缩包大小: !size_mb! MB
    )
) else (
    echo   [×] 压缩包创建失败
    pause
    exit /b 1
)

echo.

REM ============================================================================
REM 创建自解压程序
REM ============================================================================

echo [5/5] 创建自解压程序...

REM 创建配置文件
set "CONFIG_FILE=%SCRIPT_DIR%config.txt"

(
echo ;!@Install@!UTF-8!
echo Title="OCR System %APP_VERSION% 安装程序"
echo BeginPrompt="欢迎安装 OCR System %APP_VERSION%\n\n这是一个批量OCR识别工具\n\n点击"安装"开始解压文件"
echo ExtractDialogText="正在解压文件，请稍候..."
echo ExtractPathText="解压路径:"
echo ExtractTitle="OCR System %APP_VERSION% - 解压中"
echo GUIFlags="8+32+64+256+4096"
echo GUIMode="1"
echo OverwriteMode="0"
echo InstallPath="C:\\Program Files\\OCR-System"
echo ;!@InstallEnd@!
) > "%CONFIG_FILE%"

echo   [√] 配置文件已创建

REM 合并文件创建自解压程序
set "SFX_OUTPUT=%SCRIPT_DIR%%OUTPUT_NAME%.exe"
if exist "%SFX_OUTPUT%" del /f /q "%SFX_OUTPUT%"

echo   合并文件...

REM 合并: sfx模块 + 配置 + 压缩包
copy /b "%SFX_MODULE%" + "%CONFIG_FILE%" + "%ARCHIVE_FILE%" "%SFX_OUTPUT%" >nul

if exist "%SFX_OUTPUT%" (
    echo   [√] 自解压程序创建成功
    
    REM 显示文件大小
    for %%F in ("%SFX_OUTPUT%") do (
        set "size=%%~zF"
        set /a "size_mb=!size! / 1048576"
        echo   文件大小: !size_mb! MB
    )
    echo   输出位置: %SFX_OUTPUT%
) else (
    echo   [×] 自解压程序创建失败
    pause
    exit /b 1
)

echo.

REM ============================================================================
REM 清理临时文件
REM ============================================================================

echo 清理临时文件...

REM 删除临时目录
if exist "%TEMP_DIR%" (
    rmdir /s /q "%TEMP_DIR%"
    echo   [√] 已删除临时目录
)

REM 删除配置文件
if exist "%CONFIG_FILE%" (
    del /f /q "%CONFIG_FILE%"
    echo   [√] 已删除配置文件
)

REM 删除 7z 压缩包
if exist "%ARCHIVE_FILE%" (
    del /f /q "%ARCHIVE_FILE%"
    echo   [√] 已删除压缩包
)

echo.

REM ============================================================================
REM 显示完成信息
REM ============================================================================

echo ========================================
echo    自解压程序创建完成!
echo ========================================
echo.
echo 输出文件:
echo   %SFX_OUTPUT%
echo.
echo 使用说明:
echo   1. 将 .exe 文件分发给用户
echo   2. 用户双击运行即可自动解压安装
echo   3. 默认安装路径: C:\Program Files\OCR-System
echo.
echo 提示:
echo   - 首次运行可能触发 Windows SmartScreen 警告
echo   - 点击"更多信息" -^> "仍要运行"即可
echo   - 建议使用代码签名证书签名以避免警告
echo.

REM 询问是否测试
set /p "test_choice=是否测试自解压程序? (y/N): "

if /i "%test_choice%"=="y" (
    echo.
    echo 启动测试...
    start "" "%SFX_OUTPUT%"
)

echo.
echo 感谢使用!
echo.
pause
