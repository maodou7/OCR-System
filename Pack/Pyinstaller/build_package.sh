#!/bin/bash
# ============================================================================
# OCR System - PyInstaller 打包脚本 (Unix/Linux/macOS/Git Bash)
# ============================================================================
# 此脚本用于自动化 PyInstaller 打包流程
# 支持单文件模式和文件夹模式
# ============================================================================

set -e  # 遇到错误立即退出

# 颜色代码（用于美化输出）
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RESET='\033[0m'

# 获取项目根目录（脚本所在目录的上两级）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 全局变量
BUILD_SUCCESS=0

# ============================================================================
# 信号处理 - 捕获 Ctrl+C
# ============================================================================

trap ctrl_c INT

function ctrl_c() {
    echo ""
    echo -e "${YELLOW}构建被用户中断${RESET}"
    echo ""
    exit 130
}

# ============================================================================
# 环境验证函数
# ============================================================================

function check_environment() {
    echo -e "${YELLOW}[1/3] 检查环境...${RESET}"
    
    # 检查 PyInstaller 是否安装（优先使用项目中的 portable_python）
    PYINSTALLER_CMD="pyinstaller"
    PYTHON_CMD="python"
    
    if [ -f "$PROJECT_ROOT/portable_python/Scripts/pyinstaller.exe" ]; then
        PYINSTALLER_CMD="$PROJECT_ROOT/portable_python/Scripts/pyinstaller.exe"
        PYTHON_CMD="$PROJECT_ROOT/portable_python/python.exe"
    elif [ -f "$PROJECT_ROOT/portable_python/bin/pyinstaller" ]; then
        PYINSTALLER_CMD="$PROJECT_ROOT/portable_python/bin/pyinstaller"
        PYTHON_CMD="$PROJECT_ROOT/portable_python/bin/python"
    fi
    
    if ! command -v $PYINSTALLER_CMD &> /dev/null && ! [ -f "$PYINSTALLER_CMD" ]; then
        echo -e "${RED}错误: PyInstaller 未安装${RESET}"
        echo ""
        echo "请使用以下命令安装 PyInstaller:"
        echo "    pip install pyinstaller"
        echo ""
        echo "或者使用项目中的 portable_python:"
        echo "    ./portable_python/python.exe -m pip install pyinstaller"
        echo ""
        exit 1
    fi
    
    echo -e "${GREEN}  ✓ PyInstaller 已安装${RESET}"
    
    # 检查必需的源文件
    local required_files=("qt_run.py" "qt_main.py" "config.py")
    local missing_files=()
    
    for file in "${required_files[@]}"; do
        if [ ! -f "$PROJECT_ROOT/$file" ]; then
            missing_files+=("$file")
        fi
    done
    
    if [ ${#missing_files[@]} -gt 0 ]; then
        echo -e "${RED}错误: 缺少必需的源文件:${RESET}"
        for file in "${missing_files[@]}"; do
            echo "  - $file"
        done
        echo ""
        exit 1
    fi
    
    echo -e "${GREEN}  ✓ 所有必需源文件存在${RESET}"
    
    # 检查 spec 文件
    if [ ! -f "$SCRIPT_DIR/ocr_system.spec" ]; then
        echo -e "${YELLOW}  ! 警告: ocr_system.spec 不存在${RESET}"
        echo -e "${YELLOW}    PyInstaller 将自动生成 spec 文件${RESET}"
    fi
    
    echo ""
}

# ============================================================================
# 显示主菜单函数
# ============================================================================

function show_menu() {
    echo -e "${BLUE}========================================${RESET}"
    echo -e "${BLUE}   请选择打包模式:${RESET}"
    echo -e "${BLUE}========================================${RESET}"
    echo ""
    echo "  1. 单文件模式 (生成单个可执行文件)"
    echo "  2. 文件夹模式 (生成包含依赖的文件夹)"
    echo "  3. 清理构建文件"
    echo "  4. 退出"
    echo ""
    
    read -p "请输入选项 (1-4): " choice
    
    case $choice in
        1)
            build_onefile
            ;;
        2)
            build_onefolder
            ;;
        3)
            clean_build
            ;;
        4)
            exit_script
            ;;
        *)
            echo -e "${RED}无效选项，请重新选择${RESET}"
            echo ""
            show_menu
            ;;
    esac
}

# ============================================================================
# 清理构建文件函数
# ============================================================================

function clean_build() {
    echo ""
    echo -e "${YELLOW}[清理] 准备清理构建文件...${RESET}"
    echo ""
    
    local clean_targets=()
    
    [ -d "$SCRIPT_DIR/build" ] && clean_targets+=("$SCRIPT_DIR/build")
    [ -d "$SCRIPT_DIR/dist" ] && clean_targets+=("$SCRIPT_DIR/dist")
    [ -d "$PROJECT_ROOT/build" ] && clean_targets+=("$PROJECT_ROOT/build")
    [ -d "$PROJECT_ROOT/dist" ] && clean_targets+=("$PROJECT_ROOT/dist")
    
    if [ ${#clean_targets[@]} -eq 0 ]; then
        echo -e "${GREEN}没有需要清理的文件${RESET}"
        echo ""
        read -p "按 Enter 键继续..."
        show_menu
        return
    fi
    
    echo "将要删除以下目录:"
    for target in "${clean_targets[@]}"; do
        echo "  - $target"
    done
    echo ""
    
    read -p "确认清理? (y/N): " confirm
    
    if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}已取消清理${RESET}"
        echo ""
        read -p "按 Enter 键继续..."
        show_menu
        return
    fi
    
    echo ""
    echo -e "${YELLOW}正在清理...${RESET}"
    
    for target in "${clean_targets[@]}"; do
        if rm -rf "$target" 2>/dev/null; then
            echo -e "${GREEN}  ✓ 已删除 $target${RESET}"
        else
            echo -e "${RED}  ✗ 无法删除 $target${RESET}"
        fi
    done
    
    echo ""
    echo -e "${GREEN}清理完成!${RESET}"
    echo ""
    read -p "按 Enter 键继续..."
    show_menu
}

# ============================================================================
# 单文件模式构建函数
# ============================================================================

function build_onefile() {
    echo ""
    echo -e "${BLUE}========================================${RESET}"
    echo -e "${BLUE}   开始单文件模式构建${RESET}"
    echo -e "${BLUE}========================================${RESET}"
    echo ""
    
    echo -e "${YELLOW}[2/3] 准备构建...${RESET}"
    echo "  模式: 单文件 (--onefile)"
    echo "  输出: dist/OCR-System"
    echo ""
    
    # 切换到项目根目录执行构建
    cd "$PROJECT_ROOT"
    
    echo -e "${YELLOW}[3/3] 执行 PyInstaller...${RESET}"
    echo ""
    
    # 使用 spec 文件构建（如果存在）
    if [ -f "$SCRIPT_DIR/ocr_system.spec" ]; then
        echo "使用现有的 spec 文件..."
        if $PYINSTALLER_CMD --clean --onefile "$SCRIPT_DIR/ocr_system.spec"; then
            BUILD_SUCCESS=1
        else
            BUILD_SUCCESS=0
        fi
    else
        echo "生成新的构建配置..."
        if $PYINSTALLER_CMD --clean --onefile \
            --name "OCR-System" \
            --noconsole \
            --hidden-import "PySide6.QtCore" \
            --hidden-import "PySide6.QtGui" \
            --hidden-import "PySide6.QtWidgets" \
            --hidden-import "PIL" \
            --hidden-import "openpyxl" \
            --hidden-import "fitz" \
            --hidden-import "openai" \
            --add-data "models:models" \
            --add-data "portable_python:portable_python" \
            --add-data "config.py.example:." \
            --add-data ".env.example:." \
            --exclude-module "tkinter" \
            --exclude-module "matplotlib" \
            --exclude-module "scipy" \
            --exclude-module "pandas" \
            "qt_run.py"; then
            BUILD_SUCCESS=1
        else
            BUILD_SUCCESS=0
        fi
    fi
    
    if [ $BUILD_SUCCESS -eq 0 ]; then
        echo ""
        echo -e "${RED}========================================${RESET}"
        echo -e "${RED}   构建失败!${RESET}"
        echo -e "${RED}========================================${RESET}"
        echo ""
        echo "请检查上面的错误信息"
        echo ""
        cd "$SCRIPT_DIR"
        read -p "按 Enter 键继续..."
        show_menu
        return
    fi
    
    echo ""
    echo -e "${GREEN}========================================${RESET}"
    echo -e "${GREEN}   构建成功!${RESET}"
    echo -e "${GREEN}========================================${RESET}"
    echo ""
    
    display_results
}

# ============================================================================
# 文件夹模式构建函数
# ============================================================================

function build_onefolder() {
    echo ""
    echo -e "${BLUE}========================================${RESET}"
    echo -e "${BLUE}   开始文件夹模式构建${RESET}"
    echo -e "${BLUE}========================================${RESET}"
    echo ""
    
    echo -e "${YELLOW}[2/3] 准备构建...${RESET}"
    echo "  模式: 文件夹 (--onedir)"
    echo "  输出: dist/OCR-System/"
    echo ""
    
    # 切换到项目根目录执行构建
    cd "$PROJECT_ROOT"
    
    echo -e "${YELLOW}[3/3] 执行 PyInstaller...${RESET}"
    echo ""
    
    # 使用 spec 文件构建（如果存在）
    if [ -f "$SCRIPT_DIR/ocr_system.spec" ]; then
        echo "使用现有的 spec 文件..."
        if $PYINSTALLER_CMD --clean "$SCRIPT_DIR/ocr_system.spec"; then
            BUILD_SUCCESS=1
        else
            BUILD_SUCCESS=0
        fi
    else
        echo "生成新的构建配置..."
        if $PYINSTALLER_CMD --clean --onedir \
            --name "OCR-System" \
            --noconsole \
            --hidden-import "PySide6.QtCore" \
            --hidden-import "PySide6.QtGui" \
            --hidden-import "PySide6.QtWidgets" \
            --hidden-import "PIL" \
            --hidden-import "openpyxl" \
            --hidden-import "fitz" \
            --hidden-import "openai" \
            --add-data "models:models" \
            --add-data "portable_python:portable_python" \
            --add-data "config.py.example:." \
            --add-data ".env.example:." \
            --exclude-module "tkinter" \
            --exclude-module "matplotlib" \
            --exclude-module "scipy" \
            --exclude-module "pandas" \
            "qt_run.py"; then
            BUILD_SUCCESS=1
        else
            BUILD_SUCCESS=0
        fi
    fi
    
    if [ $BUILD_SUCCESS -eq 0 ]; then
        echo ""
        echo -e "${RED}========================================${RESET}"
        echo -e "${RED}   构建失败!${RESET}"
        echo -e "${RED}========================================${RESET}"
        echo ""
        echo "请检查上面的错误信息"
        echo ""
        cd "$SCRIPT_DIR"
        read -p "按 Enter 键继续..."
        show_menu
        return
    fi
    
    echo ""
    echo -e "${GREEN}========================================${RESET}"
    echo -e "${GREEN}   构建成功!${RESET}"
    echo -e "${GREEN}========================================${RESET}"
    echo ""
    
    display_results
}

# ============================================================================
# 显示构建结果函数
# ============================================================================

function display_results() {
    echo -e "${BLUE}构建信息:${RESET}"
    echo ""
    
    # 检查输出文件
    if [ -f "$PROJECT_ROOT/dist/OCR-System" ]; then
        echo "  输出位置: $PROJECT_ROOT/dist/OCR-System"
        
        # 获取文件大小
        local file_size=$(stat -f%z "$PROJECT_ROOT/dist/OCR-System" 2>/dev/null || stat -c%s "$PROJECT_ROOT/dist/OCR-System" 2>/dev/null || echo "0")
        local size_mb=$((file_size / 1048576))
        echo "  文件大小: ${size_mb} MB"
    elif [ -d "$PROJECT_ROOT/dist/OCR-System" ]; then
        echo "  输出位置: $PROJECT_ROOT/dist/OCR-System/"
        
        # 计算文件夹大小
        local folder_size=$(du -sm "$PROJECT_ROOT/dist/OCR-System" 2>/dev/null | cut -f1 || echo "未知")
        echo "  文件夹大小: ${folder_size} MB"
        echo ""
        echo "  主程序: $PROJECT_ROOT/dist/OCR-System/OCR-System"
    fi
    
    echo ""
    echo -e "${GREEN}提示:${RESET}"
    echo "  - 可执行文件位于 dist 目录"
    echo "  - 首次运行时会自动创建 config.py"
    echo "  - 可以编辑 config.py 修改配置"
    echo ""
    
    cd "$SCRIPT_DIR"
    read -p "按 Enter 键继续..."
    show_menu
}

# ============================================================================
# 退出脚本函数
# ============================================================================

function exit_script() {
    echo ""
    echo -e "${GREEN}感谢使用 OCR System 打包工具!${RESET}"
    echo ""
    exit 0
}

# ============================================================================
# 主程序入口
# ============================================================================

# 显示欢迎信息
echo ""
echo -e "${BLUE}========================================${RESET}"
echo -e "${BLUE}   OCR System - PyInstaller 打包工具   ${RESET}"
echo -e "${BLUE}========================================${RESET}"
echo ""

# 执行环境检查
check_environment

# 显示主菜单
show_menu
