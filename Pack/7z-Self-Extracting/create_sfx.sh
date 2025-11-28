#!/bin/bash
# ============================================================================
# OCR System - 7-Zip 自解压程序制作脚本
# ============================================================================
# 此脚本用于将打包好的应用程序制作成自解压安装包
# 支持 Windows 和 Linux 平台
# ============================================================================

set -e  # 遇到错误立即退出

# 颜色代码
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RESET='\033[0m'

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# 配置变量
APP_NAME="OCR-System"
APP_VERSION="v1.4.1"
SFX_MODULE="$SCRIPT_DIR/7z.sfx"
SEVEN_ZIP="$SCRIPT_DIR/7zr.exe"

# ============================================================================
# 信号处理 - 捕获 Ctrl+C
# ============================================================================

trap ctrl_c INT

function ctrl_c() {
    echo ""
    echo -e "${YELLOW}操作被用户中断${RESET}"
    echo ""
    exit 130
}

# ============================================================================
# 检查环境
# ============================================================================

function check_environment() {
    echo -e "${YELLOW}[1/5] 检查环境...${RESET}"
    
    # 检查 7zr.exe 是否存在
    if [ ! -f "$SEVEN_ZIP" ]; then
        echo -e "${RED}错误: 找不到 7zr.exe${RESET}"
        echo "请确保 7zr.exe 位于: $SEVEN_ZIP"
        exit 1
    fi
    echo -e "${GREEN}  ✓ 7zr.exe 已找到${RESET}"
    
    # 检查 7z.sfx 是否存在
    if [ ! -f "$SFX_MODULE" ]; then
        echo -e "${RED}错误: 找不到 7z.sfx 模块${RESET}"
        echo "请确保 7z.sfx 位于: $SFX_MODULE"
        exit 1
    fi
    echo -e "${GREEN}  ✓ 7z.sfx 模块已找到${RESET}"
    
    # 检查 dist 目录
    if [ ! -d "$PROJECT_ROOT/dist" ]; then
        echo -e "${RED}错误: 找不到 dist 目录${RESET}"
        echo "请先使用 PyInstaller 打包应用程序"
        echo "运行: cd Pack/Pyinstaller && ./build_package.sh"
        exit 1
    fi
    echo -e "${GREEN}  ✓ dist 目录已找到${RESET}"
    
    echo ""
}

# ============================================================================
# 选择源目录
# ============================================================================

function select_source() {
    echo -e "${YELLOW}[2/5] 选择要打包的目录...${RESET}"
    echo ""
    
    # 列出 dist 目录下的内容
    echo "可用的打包目录:"
    echo ""
    
    local options=()
    local index=1
    
    # 检查文件夹模式的输出
    if [ -d "$PROJECT_ROOT/dist/$APP_NAME" ]; then
        echo "  $index. dist/$APP_NAME/ (文件夹模式)"
        options+=("$PROJECT_ROOT/dist/$APP_NAME")
        ((index++))
    fi
    
    # 检查单文件模式的输出
    if [ -f "$PROJECT_ROOT/dist/$APP_NAME.exe" ]; then
        echo "  $index. dist/$APP_NAME.exe (单文件模式)"
        options+=("$PROJECT_ROOT/dist/$APP_NAME.exe")
        ((index++))
    fi
    
    if [ ${#options[@]} -eq 0 ]; then
        echo -e "${RED}错误: 在 dist 目录中找不到打包输出${RESET}"
        echo "请先运行 PyInstaller 打包脚本"
        exit 1
    fi
    
    echo ""
    read -p "请选择 (1-${#options[@]}): " choice
    
    if ! [[ "$choice" =~ ^[0-9]+$ ]] || [ "$choice" -lt 1 ] || [ "$choice" -gt ${#options[@]} ]; then
        echo -e "${RED}无效选择${RESET}"
        exit 1
    fi
    
    SOURCE_PATH="${options[$((choice-1))]}"
    echo -e "${GREEN}  ✓ 已选择: $SOURCE_PATH${RESET}"
    echo ""
}

# ============================================================================
# 创建临时目录并准备文件
# ============================================================================

function prepare_files() {
    echo -e "${YELLOW}[3/5] 准备文件...${RESET}"
    echo ""
    
    # 询问是否排除 portable_python（可以大幅减少体积和压缩时间）
    echo -e "${BLUE}优化选项:${RESET}"
    echo "portable_python 文件夹约 870MB，会显著增加压缩时间"
    echo "PyInstaller 已包含必需的 Python 运行时，可以安全排除"
    echo ""
    read -p "是否排除 portable_python 文件夹? (Y/n): " exclude_portable
    
    EXCLUDE_PORTABLE=true
    if [[ "$exclude_portable" =~ ^[Nn]$ ]]; then
        EXCLUDE_PORTABLE=false
    fi
    
    echo ""
    
    # 创建临时目录
    TEMP_DIR="$SCRIPT_DIR/temp_sfx"
    rm -rf "$TEMP_DIR"
    mkdir -p "$TEMP_DIR"
    
    # 复制文件到临时目录
    if [ -d "$SOURCE_PATH" ]; then
        echo "  复制文件夹..."
        
        if [ "$EXCLUDE_PORTABLE" = true ]; then
            echo "  (排除 portable_python 文件夹)"
            # 复制除了 portable_python 之外的所有文件
            rsync -a --exclude='portable_python' "$SOURCE_PATH/" "$TEMP_DIR/" 2>/dev/null || \
            (cd "$SOURCE_PATH" && find . -type f ! -path "*/portable_python/*" -exec cp --parents {} "$TEMP_DIR/" \; 2>/dev/null) || \
            cp -r "$SOURCE_PATH"/* "$TEMP_DIR/" 2>/dev/null
        else
            cp -r "$SOURCE_PATH"/* "$TEMP_DIR/"
        fi
    else
        echo "  复制单文件..."
        cp "$SOURCE_PATH" "$TEMP_DIR/"
    fi
    
    # 复制配置文件示例
    if [ -f "$PROJECT_ROOT/config.py.example" ]; then
        cp "$PROJECT_ROOT/config.py.example" "$TEMP_DIR/"
        echo -e "${GREEN}  ✓ 已添加 config.py.example${RESET}"
    fi
    
    # 复制 .env 示例
    if [ -f "$PROJECT_ROOT/.env.example" ]; then
        cp "$PROJECT_ROOT/.env.example" "$TEMP_DIR/"
        echo -e "${GREEN}  ✓ 已添加 .env.example${RESET}"
    fi
    
    # 创建 README.txt
    cat > "$TEMP_DIR/README.txt" << 'EOF'
OCR System - 批量OCR识别系统

版本: v1.4.1
发布日期: 2025-11-28

===========================================
安装说明
===========================================

1. 本程序为绿色版，无需安装
2. 解压后直接运行 OCR-System.exe 即可
3. 首次运行会自动创建配置文件

===========================================
使用说明
===========================================

1. 启动程序
   - Windows: 双击 OCR-System.exe
   - 或运行: 启动程序点这.bat

2. 选择 OCR 引擎
   - 工具栏选择引擎（推荐 PaddleOCR-json）

3. 打开文件
   - 单个文件: 点击"打开文件"
   - 批量处理: 点击"打开文件夹"

4. 框选识别区域
   - 鼠标拖拽框选文字区域
   - 可框选多个区域
   - 右键删除区域

5. 开始识别
   - 点击"开始识别"按钮
   - 等待识别完成

6. 导出结果
   - 点击"导出Excel"保存结果

===========================================
配置说明
===========================================

如需使用在线 OCR 引擎（阿里云/DeepSeek）:

1. 复制 config.py.example 为 config.py
2. 编辑 config.py，填入 API 密钥
3. 重启程序

===========================================
系统要求
===========================================

- 操作系统: Windows 7/8/10/11 (64位)
- 内存: 至少 2GB RAM
- 磁盘空间: 至少 1GB 可用空间

===========================================
常见问题
===========================================

Q: 提示"OCR引擎未就绪"？
A: 确保 models 文件夹完整，包含 OCR 引擎文件

Q: 识别速度慢？
A: 首次加载需要初始化模型，后续会快

Q: 如何提高准确率？
A: 使用高分辨率图片，框选区域贴合文字边缘

===========================================
技术支持
===========================================

GitHub: https://github.com/maodou7/OCR-System
问题反馈: https://github.com/maodou7/OCR-System/issues

===========================================
许可证
===========================================

本软件采用 MIT 许可证
详见: LICENSE 文件

感谢使用 OCR System！
EOF
    
    echo -e "${GREEN}  ✓ 已创建 README.txt${RESET}"
    echo ""
}

# ============================================================================
# 创建 7z 压缩包
# ============================================================================

function create_archive() {
    echo -e "${YELLOW}[4/5] 创建 7z 压缩包...${RESET}"
    echo ""
    
    # 计算临时目录大小
    echo "  正在计算文件大小..."
    TEMP_SIZE_KB=$(du -sk "$TEMP_DIR" 2>/dev/null | cut -f1 || echo "0")
    TEMP_SIZE_MB=$((TEMP_SIZE_KB / 1024))
    
    echo -e "${GREEN}  ✓ 待压缩文件大小: ${TEMP_SIZE_MB} MB${RESET}"
    echo ""
    
    # 检测 CPU 核心数
    CPU_CORES=$(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo "4")
    
    # 让用户选择压缩级别
    echo -e "${BLUE}请选择压缩级别:${RESET}"
    echo ""
    echo "  1. 快速 (-mx3)   - 速度最快，压缩率约 45%"
    echo "  2. 标准 (-mx5)   - 速度快，压缩率约 50%"
    echo "  3. 高级 (-mx7)   - 平衡，压缩率约 55% (推荐)"
    echo "  4. 最高 (-mx9)   - 最慢，压缩率约 60%"
    echo ""
    
    # 计算预估时间（基于经验值）
    # 基准: 100MB 在 4 核 CPU 上的压缩时间
    local base_time_mx3=10   # 秒
    local base_time_mx5=20   # 秒
    local base_time_mx7=40   # 秒
    local base_time_mx9=120  # 秒
    
    # 根据文件大小和 CPU 核心数调整
    local size_factor=$((TEMP_SIZE_MB / 100))
    if [ $size_factor -lt 1 ]; then
        size_factor=1
    fi
    local cpu_factor=$((4 / CPU_CORES))
    if [ $cpu_factor -lt 1 ]; then
        cpu_factor=1
    fi
    
    local est_time_mx3=$((base_time_mx3 * size_factor * cpu_factor))
    local est_time_mx5=$((base_time_mx5 * size_factor * cpu_factor))
    local est_time_mx7=$((base_time_mx7 * size_factor * cpu_factor))
    local est_time_mx9=$((base_time_mx9 * size_factor * cpu_factor))
    
    # 格式化时间显示
    function format_time() {
        local seconds=$1
        if [ $seconds -lt 60 ]; then
            echo "${seconds} 秒"
        elif [ $seconds -lt 3600 ]; then
            local minutes=$((seconds / 60))
            local secs=$((seconds % 60))
            echo "${minutes} 分 ${secs} 秒"
        else
            local hours=$((seconds / 3600))
            local minutes=$(((seconds % 3600) / 60))
            echo "${hours} 小时 ${minutes} 分"
        fi
    }
    
    echo -e "${YELLOW}预计压缩时间 (${CPU_CORES} 核 CPU):${RESET}"
    echo "  1. 快速: $(format_time $est_time_mx3)"
    echo "  2. 标准: $(format_time $est_time_mx5)"
    echo "  3. 高级: $(format_time $est_time_mx7)"
    echo "  4. 最高: $(format_time $est_time_mx9)"
    echo ""
    
    read -p "请选择 (1-4) [默认: 3]: " compress_choice
    
    # 设置压缩级别
    case $compress_choice in
        1)
            COMPRESS_LEVEL="-mx3"
            COMPRESS_NAME="快速"
            ;;
        2)
            COMPRESS_LEVEL="-mx5"
            COMPRESS_NAME="标准"
            ;;
        4)
            COMPRESS_LEVEL="-mx9"
            COMPRESS_NAME="最高"
            ;;
        *)
            COMPRESS_LEVEL="-mx7"
            COMPRESS_NAME="高级"
            ;;
    esac
    
    echo ""
    echo -e "${GREEN}  ✓ 已选择: ${COMPRESS_NAME} 压缩${RESET}"
    echo ""
    
    # 输出文件名
    OUTPUT_NAME="${APP_NAME}-${APP_VERSION}-Setup"
    ARCHIVE_FILE="$SCRIPT_DIR/${OUTPUT_NAME}.7z"
    
    # 删除旧的压缩包
    rm -f "$ARCHIVE_FILE"
    
    # 创建压缩包
    cd "$TEMP_DIR"
    
    echo "  开始压缩..."
    echo "  文件大小: ${TEMP_SIZE_MB} MB"
    echo "  压缩级别: ${COMPRESS_NAME} (${COMPRESS_LEVEL})"
    echo "  CPU 核心: ${CPU_CORES} 个"
    echo ""
    echo "  压缩进度:"
    echo "  ----------------------------------------"
    
    # 记录开始时间
    START_TIME=$(date +%s)
    
    # 显示完整输出，不过滤
    if command -v wine &> /dev/null; then
        # 尝试使用 wine
        if wine "$SEVEN_ZIP" a $COMPRESS_LEVEL "$ARCHIVE_FILE" * 2>&1; then
            echo ""
            echo "  ----------------------------------------"
            echo -e "${GREEN}  ✓ 压缩包创建成功${RESET}"
        else
            echo -e "${RED}  ✗ Wine 运行失败，尝试直接运行...${RESET}"
            # 如果 wine 失败，尝试直接运行（Windows 环境）
            if "$SEVEN_ZIP" a $COMPRESS_LEVEL "$ARCHIVE_FILE" *; then
                echo ""
                echo "  ----------------------------------------"
                echo -e "${GREEN}  ✓ 压缩包创建成功${RESET}"
            else
                echo -e "${RED}  ✗ 压缩包创建失败${RESET}"
                exit 1
            fi
        fi
    else
        # 没有 wine，直接运行（Windows/Git Bash）
        if "$SEVEN_ZIP" a $COMPRESS_LEVEL "$ARCHIVE_FILE" *; then
            echo ""
            echo "  ----------------------------------------"
            echo -e "${GREEN}  ✓ 压缩包创建成功${RESET}"
        else
            echo -e "${RED}  ✗ 压缩包创建失败${RESET}"
            exit 1
        fi
    fi
    
    # 计算实际用时
    END_TIME=$(date +%s)
    ACTUAL_TIME=$((END_TIME - START_TIME))
    
    cd "$SCRIPT_DIR"
    
    # 显示压缩统计
    if [ -f "$ARCHIVE_FILE" ]; then
        local size=$(stat -f%z "$ARCHIVE_FILE" 2>/dev/null || stat -c%s "$ARCHIVE_FILE" 2>/dev/null || echo "0")
        local size_mb=$((size / 1048576))
        local compress_ratio=$((100 - (size_mb * 100 / TEMP_SIZE_MB)))
        
        echo ""
        echo -e "${BLUE}压缩统计:${RESET}"
        echo "  原始大小: ${TEMP_SIZE_MB} MB"
        echo "  压缩后: ${size_mb} MB"
        echo "  压缩率: ${compress_ratio}%"
        echo "  实际用时: $(format_time $ACTUAL_TIME)"
        echo "  压缩级别: ${COMPRESS_NAME}"
    fi
    
    echo ""
}

# ============================================================================
# 创建自解压配置文件
# ============================================================================

function create_sfx_config() {
    echo -e "${YELLOW}[5/5] 创建自解压程序...${RESET}"
    
    # 创建配置文件
    CONFIG_FILE="$SCRIPT_DIR/config.txt"
    
    cat > "$CONFIG_FILE" << EOF
;!@Install@!UTF-8!
Title="OCR System ${APP_VERSION} 安装程序"
BeginPrompt="欢迎安装 OCR System ${APP_VERSION}\n\n这是一个批量OCR识别工具\n\n点击"安装"开始解压文件"
ExtractDialogText="正在解压文件，请稍候..."
ExtractPathText="解压路径:"
ExtractTitle="OCR System ${APP_VERSION} - 解压中"
GUIFlags="8+32+64+256+4096"
GUIMode="1"
OverwriteMode="0"
InstallPath="C:\\Program Files\\OCR-System"
;!@InstallEnd@!
EOF
    
    echo -e "${GREEN}  ✓ 配置文件已创建${RESET}"
    
    # 合并文件创建自解压程序
    SFX_OUTPUT="$SCRIPT_DIR/${OUTPUT_NAME}.exe"
    rm -f "$SFX_OUTPUT"
    
    echo "  合并文件..."
    
    # 合并: sfx模块 + 配置 + 压缩包
    cat "$SFX_MODULE" "$CONFIG_FILE" "$ARCHIVE_FILE" > "$SFX_OUTPUT"
    
    if [ -f "$SFX_OUTPUT" ]; then
        echo -e "${GREEN}  ✓ 自解压程序创建成功${RESET}"
        
        # 显示文件大小
        local size=$(stat -f%z "$SFX_OUTPUT" 2>/dev/null || stat -c%s "$SFX_OUTPUT" 2>/dev/null || echo "0")
        local size_mb=$((size / 1048576))
        echo "  文件大小: ${size_mb} MB"
        echo "  输出位置: $SFX_OUTPUT"
    else
        echo -e "${RED}  ✗ 自解压程序创建失败${RESET}"
        exit 1
    fi
    
    echo ""
}

# ============================================================================
# 清理临时文件
# ============================================================================

function cleanup() {
    echo -e "${YELLOW}清理临时文件...${RESET}"
    
    # 删除临时目录
    if [ -d "$TEMP_DIR" ]; then
        rm -rf "$TEMP_DIR"
        echo -e "${GREEN}  ✓ 已删除临时目录${RESET}"
    fi
    
    # 删除配置文件
    if [ -f "$CONFIG_FILE" ]; then
        rm -f "$CONFIG_FILE"
        echo -e "${GREEN}  ✓ 已删除配置文件${RESET}"
    fi
    
    # 删除 7z 压缩包
    if [ -f "$ARCHIVE_FILE" ]; then
        rm -f "$ARCHIVE_FILE"
        echo -e "${GREEN}  ✓ 已删除压缩包${RESET}"
    fi
    
    echo ""
}

# ============================================================================
# 显示完成信息
# ============================================================================

function show_completion() {
    echo -e "${GREEN}========================================${RESET}"
    echo -e "${GREEN}   自解压程序创建完成!${RESET}"
    echo -e "${GREEN}========================================${RESET}"
    echo ""
    echo -e "${BLUE}输出文件:${RESET}"
    echo "  $SFX_OUTPUT"
    echo ""
    echo -e "${BLUE}使用说明:${RESET}"
    echo "  1. 将 .exe 文件分发给用户"
    echo "  2. 用户双击运行即可自动解压安装"
    echo "  3. 默认安装路径: C:\\Program Files\\OCR-System"
    echo ""
    echo -e "${YELLOW}提示:${RESET}"
    echo "  - 首次运行可能触发 Windows SmartScreen 警告"
    echo "  - 点击"更多信息" -> "仍要运行"即可"
    echo "  - 建议使用代码签名证书签名以避免警告"
    echo ""
}

# ============================================================================
# 主程序入口
# ============================================================================

# 显示欢迎信息
echo ""
echo -e "${BLUE}========================================${RESET}"
echo -e "${BLUE}   OCR System - 自解压程序制作工具   ${RESET}"
echo -e "${BLUE}========================================${RESET}"
echo ""

# 执行步骤
check_environment
select_source
prepare_files
create_archive
create_sfx_config
cleanup
show_completion

# 询问是否测试
echo ""
read -p "是否在 Wine 中测试自解压程序? (y/N): " test_choice

if [[ "$test_choice" =~ ^[Yy]$ ]]; then
    echo ""
    echo -e "${YELLOW}启动测试...${RESET}"
    wine "$SFX_OUTPUT"
fi

echo ""
echo -e "${GREEN}感谢使用!${RESET}"
echo ""
