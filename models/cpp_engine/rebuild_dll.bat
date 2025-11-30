@echo off
echo ========================================
echo 重新编译OCR缓存引擎DLL
echo ========================================

cd /d "%~dp0"

REM 清理旧的构建文件
if exist build rmdir /s /q build
mkdir build
cd build

REM 使用CMake生成构建文件
echo.
echo [1/3] 生成构建文件...
cmake -G "MinGW Makefiles" -DCMAKE_BUILD_TYPE=Release ..
if errorlevel 1 (
    echo 错误: CMake配置失败
    pause
    exit /b 1
)

REM 编译
echo.
echo [2/3] 编译中...
cmake --build . --config Release
if errorlevel 1 (
    echo 错误: 编译失败
    pause
    exit /b 1
)

REM 复制DLL到models目录
echo.
echo [3/3] 复制DLL文件...
if exist ocr_cache.dll (
    copy /y ocr_cache.dll ..\..\ocr_cache.dll
    echo 成功: DLL已复制到 models\ocr_cache.dll
) else (
    echo 错误: 找不到编译后的DLL文件
    pause
    exit /b 1
)

echo.
echo ========================================
echo 编译完成！
echo ========================================
pause
