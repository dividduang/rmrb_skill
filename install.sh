#!/usr/bin/env bash
# ============================================================
# rmrb-pdf-fetcher 一键安装脚本 (Linux / macOS)
# 用法: bash install.sh
# ============================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
echo_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
echo_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 项目根目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo ""
echo "=========================================="
echo "  人民日报PDF下载器 - 安装向导"
echo "=========================================="
echo ""

# ---- 1. 检测 Python ----
echo_info "检测 Python 环境..."

if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo_error "未找到 Python，请先安装 Python >= 3.11"
    echo "  下载地址: https://www.python.org/downloads/"
    exit 1
fi

PY_VERSION=$($PYTHON -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo_info "Python 版本: $PY_VERSION"

# 检查版本 >= 3.11
$PYTHON -c "
import sys
if sys.version_info < (3, 11):
    print('ERROR: 需要 Python >= 3.11, 当前版本: ' + sys.version)
    sys.exit(1)
" || { echo_error "Python 版本过低，请升级到 3.11+"; exit 1; }

# ---- 2. 选择安装方式 (uv / pip) ----
VENV_DIR="$SCRIPT_DIR/.venv"

if command -v uv &>/dev/null; then
    echo_info "检测到 uv，使用 uv 安装..."
    uv sync
    UV_CMD="uv run"
    RUN_PREFIX="$UV_CMD"
else
    echo_info "使用 pip + venv 安装..."

    # 创建虚拟环境
    if [ ! -d "$VENV_DIR" ]; then
        echo_info "创建虚拟环境..."
        $PYTHON -m venv "$VENV_DIR"
    fi

    # 激活虚拟环境
    source "$VENV_DIR/bin/activate"

    # 安装依赖
    echo_info "安装 Python 依赖..."
    pip install --upgrade pip -q
    pip install -r requirements.txt

    RUN_PREFIX=""
fi

# ---- 3. 安装 Playwright Chromium ----
echo_info "安装 Playwright Chromium 浏览器（首次安装可能需要几分钟）..."
$RUN_PREFIX playwright install chromium

# ---- 4. 注册 Claude Code Skill ----
SKILL_DIR="$HOME/.claude/skills/rmrb-pdf-fetcher"

echo_info "注册 Claude Code Skill..."
mkdir -p "$SKILL_DIR"
cp "$SCRIPT_DIR/SKILL.md" "$SKILL_DIR/SKILL.md"

echo_info "Skill 已安装到: $SKILL_DIR/SKILL.md"

# ---- 5. 验证安装 ----
echo ""
echo_info "验证安装..."
if $RUN_PREFIX python -c "import playwright; import requests; import PyPDF2; print('OK')" 2>/dev/null; then
    echo_info "Python 依赖: 正常"
else
    echo_warn "部分依赖可能未正确安装，请检查上方日志"
fi

if [ -f "$SKILL_DIR/SKILL.md" ]; then
    echo_info "Skill 注册: 正常"
else
    echo_warn "Skill 注册可能失败，请手动复制 SKILL.md"
fi

# ---- 完成 ----
echo ""
echo "=========================================="
echo -e "  ${GREEN}安装完成！${NC}"
echo "=========================================="
echo ""
echo "使用方法："
echo "  命令行:  $RUN_PREFIX python rmrb_download_playwright.py --once"
echo "  JSON:    $RUN_PREFIX python rmrb_download_playwright.py --once --output-json"
echo "  定时:    $RUN_PREFIX python rmrb_download_playwright.py"
echo "  Skill:   在 Claude Code 中输入 /rmrb"
echo ""
echo "下载目录: $SCRIPT_DIR/人民日报下载/"
echo ""
