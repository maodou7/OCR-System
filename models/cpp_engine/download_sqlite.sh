#!/bin/bash

# SQLite Amalgamation 下载脚本
# 自动下载并解压SQLite源码

set -e

SQLITE_VERSION="3440200"  # SQLite 3.44.2
SQLITE_YEAR="2023"
SQLITE_URL="https://www.sqlite.org/${SQLITE_YEAR}/sqlite-amalgamation-${SQLITE_VERSION}.zip"
SQLITE_FILE="sqlite-amalgamation-${SQLITE_VERSION}.zip"

echo "========================================"
echo "SQLite Amalgamation 下载器"
echo "========================================"

# 检查是否已存在
if [ -f "sqlite3.c" ] && [ -f "sqlite3.h" ]; then
    echo "✓ SQLite源码已存在，跳过下载"
    exit 0
fi

# 检查wget或curl
if command -v wget &> /dev/null; then
    DOWNLOAD_CMD="wget"
elif command -v curl &> /dev/null; then
    DOWNLOAD_CMD="curl -O"
else
    echo "✗ 错误: 需要wget或curl来下载文件"
    echo "  Ubuntu/Debian: sudo apt-get install wget"
    echo "  macOS: brew install wget"
    exit 1
fi

# 下载SQLite
echo "下载SQLite Amalgamation ${SQLITE_VERSION}..."
if [ "$DOWNLOAD_CMD" = "wget" ]; then
    wget "$SQLITE_URL" -O "$SQLITE_FILE"
else
    curl -L "$SQLITE_URL" -o "$SQLITE_FILE"
fi

# 检查unzip
if ! command -v unzip &> /dev/null; then
    echo "✗ 错误: 需要unzip来解压文件"
    echo "  Ubuntu/Debian: sudo apt-get install unzip"
    echo "  macOS: brew install unzip"
    exit 1
fi

# 解压
echo "解压SQLite源码..."
unzip -q "$SQLITE_FILE"

# 移动文件到当前目录
mv sqlite-amalgamation-${SQLITE_VERSION}/sqlite3.c .
mv sqlite-amalgamation-${SQLITE_VERSION}/sqlite3.h .
mv sqlite-amalgamation-${SQLITE_VERSION}/sqlite3ext.h .

# 清理
rm -rf sqlite-amalgamation-${SQLITE_VERSION}
rm "$SQLITE_FILE"

echo "✓ SQLite源码下载完成"
echo "  - sqlite3.c (约6.5MB)"
echo "  - sqlite3.h"
echo "  - sqlite3ext.h"
echo "========================================"
