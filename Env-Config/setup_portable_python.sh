#!/bin/bash
# 便携式 Python 环境创建工具 (Git Bash 版本)

set -e  # 遇到错误立即退出

echo "============================================================"
echo "便携式 Python 环境创建工具 (Bash 版本)"
echo "============================================================"
echo ""

# 配置参数
PYTHON_VERSION="3.11.7"
PYTHON_URL="https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-embed-amd64.zip"
# 便携式 Python 将安装到 OCR-System 根目录
PORTABLE_DIR="../portable_python"
# 临时文件目录
TMP_DIR="tmp"

# 0. 创建临时文件目录
mkdir -p "$TMP_DIR"

# 1. 下载嵌入式Python
echo "[1/6] 下载嵌入式 Python ${PYTHON_VERSION}..."
# 下载文件保存到 Env-Config/tmp 目录
if [ -f "$TMP_DIR/python-embed.zip" ]; then
    echo "  检测到已下载的文件，跳过下载"
else
    echo "  正在下载... 请稍候"
    curl -L -o "$TMP_DIR/python-embed.zip" "$PYTHON_URL" || {
        echo "  ❌ 下载失败，请检查网络连接"
        exit 1
    }
fi

# 2. 解压
echo ""
echo "[2/6] 解压 Python 文件..."
if [ -d "$PORTABLE_DIR" ]; then
    echo "  删除旧的便携环境..."
    rm -rf "$PORTABLE_DIR"
fi
mkdir -p "$PORTABLE_DIR"
unzip -q "$TMP_DIR/python-embed.zip" -d "$PORTABLE_DIR" || {
    echo "  ❌ 解压失败"
    exit 1
}
echo "  ✓ 解压完成"

# 3. 配置 Python 路径
echo ""
echo "[3/6] 配置 Python 环境..."
cd "$PORTABLE_DIR"

# 修改 python311._pth 以支持 pip 和 site-packages
cat > python311._pth << EOF
python311.zip
.
import site
EOF
echo "  ✓ 路径配置完成"

# 4. 下载并安装 pip
echo ""
echo "[4/6] 安装 pip..."
if [ -f get-pip.py ]; then
    rm get-pip.py
fi
curl -o get-pip.py https://bootstrap.pypa.io/get-pip.py || {
    echo "  ❌ 下载 pip 安装脚本失败"
    cd ..
    exit 1
}

./python.exe get-pip.py --no-warn-script-location || {
    echo "  ❌ pip 安装失败"
    cd ..
    exit 1
}
echo "  ✓ pip 安装完成"

# 5. 升级 pip
echo ""
echo "[5/6] 升级 pip..."
./python.exe -m pip install --upgrade pip -i https://pypi.tuna.tsinghua.edu.cn/simple
echo "  ✓ pip 升级完成"

# 6. 安装项目依赖
echo ""
echo "[6/6] 安装项目依赖（使用清华镜像源）..."
echo "  这可能需要几分钟，请耐心等待..."
./python.exe -m pip install -r ../requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple || {
    echo "  ❌ 依赖安装失败"
    cd ..
    exit 1
}

cd ..

echo ""
echo "============================================================"
echo "✅ 便携式 Python 环境创建完成！"
echo "============================================================"
echo ""
echo "环境位置: OCR-System/portable_python"
echo "Python 版本: ${PYTHON_VERSION}"
echo ""
echo "使用方式:"
echo "  1. 直接运行: portable_python/python.exe qt_run.py"
echo "  2. 使用启动脚本: ./run_portable.sh"
echo ""
