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
    
    # 输出文件名
    OUTPUT_NAME="${APP_NAME}-${APP_VERSION}-Setup"
    ARCHIVE_FILE="$SCRIPT_DIR/${OUTPUT_NAME}.7z"
    
    # 删除旧的压缩包
    rm -f "$ARCHIVE_FILE"
    
    # 创建压缩包
    cd "$TEMP_DIR"
    
    echo "  正在压缩文件（这可能需要几分钟，请耐心等待）..."
    echo "  提示: 文件越大，压缩时间越长"
    echo "  使用中等压缩率 (-mx7)，比最高压缩率快 3-5 倍"
    echo ""
    echo "  压缩进度:"
    echo "  ----------------------------------------"
    
    # 使用 -mx7 而不是 -mx9，速度更快，压缩率仍然很好
    # 显示完整输出，不过滤
    if command -v wine &> /dev/null; then
        # 尝试使用 wine
        if wine "$SEVEN_ZIP" a -mx7 "$ARCHIVE_FILE" * 2>&1; then
            echo ""
            echo "  ----------------------------------------"
            echo -e "${GREEN}  ✓ 压缩包创建成功${RESET}"
        else
            echo -e "${RED}  ✗ Wine 运行失败，尝试直接运行...${RESET}"
            # 如果 wine 失败，尝试直接运行（Windows 环境）
            if "$SEVEN_ZIP" a -mx7 "$ARCHIVE_FILE" *; then
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
        if "$SEVEN_ZIP" a -mx7 "$ARCHIVE_FILE" *; then
            echo ""
            echo "  ----------------------------------------"
            echo -e "${GREEN}  ✓ 压缩包创建成功${RESET}"
        else
            echo -e "${RED}  ✗ 压缩包创建失败${RESET}"
            exit 1
        fi
    fi
    
    cd "$SCRIPT_DIR"
    
    # 显示压缩包大小
    if [ -f "$ARCHIVE_FILE" ]; then
        local size=$(stat -f%z "$ARCHIVE_FILE" 2>/dev/null || stat -c%s "$ARCHIVE_FILE" 2>/dev/null || echo "0")
        local size_mb=$((size / 1048576))
        echo "  压缩包大小: ${size_mb} MB"
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
