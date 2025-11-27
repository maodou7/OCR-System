#!/bin/bash

# OCR Cache Engine 编译脚本
# 自动检测系统并编译共享库

set -e

echo "========================================"
echo "OCR Cache Engine 编译器"
echo "========================================"

# 检查SQLite源码
if [ ! -f "sqlite3.c" ]; then
    echo "SQLite源码不存在，开始下载..."
    chmod +x download_sqlite.sh
    ./download_sqlite.sh
fi

# 检测操作系统
OS_TYPE=$(uname -s)
echo "检测到操作系统: $OS_TYPE"

# 创建构建目录
BUILD_DIR="build"
if [ -d "$BUILD_DIR" ]; then
    echo "清理旧的构建目录..."
    rm -rf "$BUILD_DIR"
fi

mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# 运行CMake配置
echo "配置CMake..."
cmake .. -DCMAKE_BUILD_TYPE=Release

# 编译
echo "开始编译..."
cmake --build . --config Release

# 检查编译结果
echo ""
echo "========================================"
if [ $? -eq 0 ]; then
    echo "✓ 编译成功！"
    
    # 显示生成的库文件
    cd ..
    if [ "$OS_TYPE" == "Linux" ]; then
        LIB_FILE="libocr_cache.so"
    elif [ "$OS_TYPE" == "Darwin" ]; then
        LIB_FILE="libocr_cache.dylib"
    else
        LIB_FILE="ocr_cache.dll"
    fi
    
    if [ -f "../$LIB_FILE" ]; then
        echo "生成的库文件: $LIB_FILE"
        ls -lh "../$LIB_FILE"
    else
        echo "警告: 未找到库文件 $LIB_FILE"
    fi
else
    echo "✗ 编译失败"
    exit 1
fi

echo "========================================"
