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
    echo "  1. 完整版 - 文件夹模式 (包含所有OCR引擎)"
    echo "  2. 核心版 - 文件夹模式 (仅RapidOCR，不含在线OCR)"
    echo "  3. 单文件模式 (生成单个可执行文件)"
    echo "  4. 清理构建文件"
    echo "  5. 清理缓存和临时文件 (推荐打包前执行)"
    echo "  6. 退出"
    echo ""
    
    read -p "请输入选项 (1-6): " choice
    
    case $choice in
        1)
            build_full_version
            ;;
        2)
            build_core_version
            ;;
        3)
            build_onefile
            ;;
        4)
            clean_build
            ;;
        5)
            clean_cache
            ;;
        6)
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
# 清理缓存和临时文件函数
# ============================================================================

function clean_cache() {
    echo ""
    echo -e "${YELLOW}[清理] 准备清理缓存和临时文件...${RESET}"
    echo ""
    echo "此操作将清理:"
    echo "  - __pycache__ 目录"
    echo "  - .pyc 文件"
    echo "  - 缓存数据库 (.db 文件)"
    echo "  - 临时文件 (*.tmp, *.log, *.bak)"
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
    echo -e "${YELLOW}正在执行清理脚本...${RESET}"
    echo ""
    
    # 切换到项目根目录
    cd "$PROJECT_ROOT"
    
    # 执行清理脚本
    $PYTHON_CMD cleanup_before_packaging.py --auto
    
    if [ $? -ne 0 ]; then
        echo ""
        echo -e "${RED}清理脚本执行失败${RESET}"
        echo ""
    else
        echo ""
        echo -e "${GREEN}清理完成!${RESET}"
        echo ""
        echo "详细报告请查看: CLEANUP_REPORT.md"
        echo ""
    fi
    
    cd "$SCRIPT_DIR"
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
# 完整版构建函数
# ============================================================================

function build_full_version() {
    echo ""
    echo -e "${BLUE}========================================${RESET}"
    echo -e "${BLUE}   开始完整版构建${RESET}"
    echo -e "${BLUE}========================================${RESET}"
    echo ""
    
    echo -e "${YELLOW}[2/3] 准备构建...${RESET}"
    echo "  版本: 完整版 (包含所有OCR引擎和在线OCR支持)"
    echo "  输出: dist/OCR-System/"
    echo ""
    
    # 切换到项目根目录执行构建
    cd "$PROJECT_ROOT"
    
    echo -e "${YELLOW}[3/3] 执行 PyInstaller...${RESET}"
    echo ""
    
    # 使用完整版 spec 文件构建
    if [ -f "$SCRIPT_DIR/ocr_system.spec" ]; then
        echo "使用完整版 spec 文件..."
        if $PYINSTALLER_CMD --clean "$SCRIPT_DIR/ocr_system.spec"; then
            BUILD_SUCCESS=1
        else
            BUILD_SUCCESS=0
        fi
    else
        echo -e "${RED}错误: 找不到 ocr_system.spec 文件${RESET}"
        BUILD_SUCCESS=0
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
# 核心版构建函数
# ============================================================================

function build_core_version() {
    echo ""
    echo -e "${BLUE}========================================${RESET}"
    echo -e "${BLUE}   开始核心版构建${RESET}"
    echo -e "${BLUE}========================================${RESET}"
    echo ""
    
    echo -e "${YELLOW}[2/3] 准备构建...${RESET}"
    echo "  版本: 核心版 (仅RapidOCR，不含在线OCR依赖)"
    echo "  输出: dist/OCR-System-Core/"
    echo "  体积: 约250MB (相比完整版减少60%)"
    echo ""
    
    # 切换到项目根目录执行构建
    cd "$PROJECT_ROOT"
    
    echo -e "${YELLOW}[3/3] 执行 PyInstaller...${RESET}"
    echo ""
    
    # 使用核心版 spec 文件构建
    if [ -f "$SCRIPT_DIR/ocr_system_core.spec" ]; then
        echo "使用核心版 spec 文件..."
        if $PYINSTALLER_CMD --clean "$SCRIPT_DIR/ocr_system_core.spec"; then
            BUILD_SUCCESS=1
        else
            BUILD_SUCCESS=0
        fi
    else
        echo -e "${RED}错误: 找不到 ocr_system_core.spec 文件${RESET}"
        BUILD_SUCCESS=0
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
    echo -e "${BLUE}核心版说明:${RESET}"
    echo "  - 仅包含RapidOCR本地引擎"
    echo "  - 不包含在线OCR依赖（阿里云、DeepSeek）"
    echo "  - 用户可通过pip单独安装在线OCR插件"
    echo "  - PaddleOCR引擎可通过程序内下载"
    echo ""
    
    display_results
}

# ============================================================================
# 文件夹模式构建函数（保留用于向后兼容）
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
