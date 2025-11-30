#!/bin/bash

# OCR Cache Engine - Windows DLL 编译脚本
# 使用 MinGW/MSYS2 的 g++ 编译器

set -e

echo "========================================"
echo "OCR Cache Engine - Windows DLL 编译器"
echo "========================================"
echo ""

# 检查编译器
if ! command -v g++ &> /dev/null; then
    echo "❌ 错误: 找不到 g++ 编译器"
    echo "   请确保在 Git Bash 或 MSYS2 环境中运行此脚本"
    exit 1
fi

echo "✓ 编译器: $(g++ --version | head -n 1)"
echo ""

# 检查源文件
if [ ! -f "ocr_cache_engine.cpp" ]; then
    echo "❌ 错误: 找不到 ocr_cache_engine.cpp"
    echo "   请确保在 cpp_engine 目录下运行此脚本"
    exit 1
fi

if [ ! -f "sqlite3.c" ]; then
    echo "❌ 错误: 找不到 sqlite3.c"
    echo "   SQLite源码不存在，请先运行 download_sqlite.sh"
    exit 1
fi

echo "✓ 源文件检查通过"
echo ""

# 编译参数说明
echo "编译配置:"
echo "  - 输出: ../ocr_cache.dll"
echo "  - C++标准: C++17"
echo "  - 优化级别: O3 (最高优化)"
echo "  - 体积优化: 启用strip和section gc"
echo "  - 线程支持: pthread"
echo "  - SQLite: 嵌入式编译（精简版）"
echo ""

# 开始编译
echo "开始编译..."
echo ""

# 编译步骤说明：
# 1. 使用 gcc 编译 SQLite (C 代码)
# 2. 使用 g++ 编译 OCR 引擎 (C++ 代码)
# 3. 链接生成 DLL

echo "步骤 1/3: 编译 SQLite (C 代码)..."
gcc -c sqlite3.c \
    -o sqlite3.o \
    -O3 \
    -ffunction-sections \
    -fdata-sections \
    -DSQLITE_THREADSAFE=1 \
    -DSQLITE_OMIT_DEPRECATED \
    -DSQLITE_OMIT_LOAD_EXTENSION \
    -DSQLITE_OMIT_PROGRESS_CALLBACK \
    -DSQLITE_OMIT_SHARED_CACHE \
    -DSQLITE_DEFAULT_MEMSTATUS=0 \
    -DSQLITE_DEFAULT_WAL_SYNCHRONOUS=1 \
    -DSQLITE_LIKE_DOESNT_MATCH_BLOBS \
    -DSQLITE_MAX_EXPR_DEPTH=0 \
    -DSQLITE_OMIT_DECLTYPE \
    -DSQLITE_OMIT_AUTOINIT

if [ $? -ne 0 ]; then
    echo "❌ SQLite 编译失败"
    exit 1
fi
echo "  ✓ SQLite 编译完成"

echo ""
echo "步骤 2/3: 编译 OCR Cache Engine (C++ 代码)..."
g++ -c ocr_cache_engine.cpp \
    -o ocr_cache_engine.o \
    -I. \
    -std=c++17 \
    -O3 \
    -ffunction-sections \
    -fdata-sections \
    -fno-exceptions \
    -fno-rtti \
    -fvisibility=hidden

if [ $? -ne 0 ]; then
    echo "❌ OCR Cache Engine 编译失败"
    exit 1
fi
echo "  ✓ OCR Cache Engine 编译完成"

echo ""
echo "步骤 3/3: 链接生成 DLL..."
# 完全静态链接所有依赖，避免运行时依赖问题
# 使用 -s 移除调试符号，使用 --gc-sections 移除未使用代码
g++ -shared \
    ocr_cache_engine.o \
    sqlite3.o \
    -o ../ocr_cache.dll \
    -static-libgcc \
    -static-libstdc++ \
    -static \
    -lpthread \
    -lwinpthread \
    -s \
    -Wl,--gc-sections \
    -Wl,--strip-all

if [ $? -ne 0 ]; then
    echo "❌ 链接失败"
    exit 1
fi

# 清理中间文件
rm -f sqlite3.o ocr_cache_engine.o

echo "  ✓ DLL 生成完成"

# 检查编译结果
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✓ 编译成功！"
    echo "========================================"
    echo ""
    
    # 显示生成的文件信息
    if [ -f "../ocr_cache.dll" ]; then
        DLL_SIZE=$(ls -lh ../ocr_cache.dll | awk '{print $5}')
        echo "生成的文件:"
        echo "  位置: models/ocr_cache.dll"
        echo "  大小: $DLL_SIZE"
        echo ""
        echo "✓ 缓存引擎 DLL 已准备就绪！"
        echo ""
        echo "下一步:"
        echo "  1. 重启 OCR 系统"
        echo "  2. 验证启动日志中缓存初始化成功"
    else
        echo "⚠ 警告: DLL文件未找到"
    fi
else
    echo ""
    echo "========================================"
    echo "✗ 编译失败"
    echo "========================================"
    exit 1
fi

echo "========================================"
