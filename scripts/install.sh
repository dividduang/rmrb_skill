#!/usr/bin/env bash
# ============================================================
# rmrb-pdf-fetcher 一键安装脚本 (Linux / macOS)
# 用法: bash scripts/install.sh
# ============================================================

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo_info()  { echo -e "${GREEN}[INFO]${NC} $1"; }
echo_warn()  { echo -e "${YELLOW}[WARN]${NC} $1"; }
echo_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# 项目根目录（scripts 的上级目录）
PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$PROJECT_ROOT"

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

$PYTHON -c "
import sys
if sys.version_info < (3, 11):
    print('ERROR: 需要 Python >= 3.11')
    sys.exit(1)
" || { echo_error "Python 版本过低，请升级到 3.11+"; exit 1; }

# ---- 2. 安装依赖 ----
VENV_DIR="$PROJECT_ROOT/.venv"

if command -v uv &>/dev/null; then
    echo_info "检测到 uv，使用 uv 安装..."
    uv sync
    RUN_PREFIX="uv run"
else
    echo_info "使用 pip + venv 安装..."

    if [ ! -d "$VENV_DIR" ]; then
        echo_info "创建虚拟环境..."
        $PYTHON -m venv "$VENV_DIR"
    fi

    source "$VENV_DIR/bin/activate"
    pip install --upgrade pip -q
    pip install -e "$PROJECT_ROOT"

    RUN_PREFIX=""
fi

# ---- 3. 安装 Playwright Chromium ----
echo_info "安装 Playwright Chromium 浏览器（首次安装可能需要几分钟）..."
$RUN_PREFIX playwright install chromium

# ---- 4. 注册 Claude Code Skill ----
SKILL_DIR="$HOME/.claude/skills/rmrb-pdf-fetcher"

echo_info "注册 Claude Code Skill..."
mkdir -p "$SKILL_DIR"
cp "$PROJECT_ROOT/SKILL.md" "$SKILL_DIR/SKILL.md"
echo_info "Skill 已安装到: $SKILL_DIR/SKILL.md"

# ---- 5. 验证安装 ----
echo ""
echo_info "验证安装..."
if $RUN_PREFIX python -c "from rmrb_fetcher.downloader import download; print('OK')" 2>/dev/null; then
    echo_info "Python 包: 正常"
else
    echo_warn "rmrb_fetcher 包可能未正确安装"
fi

if command -v playwright &>/dev/null || $RUN_PREFIX python -c "import playwright; print('OK')" 2>/dev/null; then
    echo_info "Playwright: 正常"
else
    echo_warn "Playwright 可能未正确安装"
fi

if [ -f "$SKILL_DIR/SKILL.md" ]; then
    echo_info "Skill 注册: 正常"
else
    echo_warn "Skill 注册可能失败"
fi

# ---- 完成 ----
echo ""
echo "=========================================="
echo -e "  ${GREEN}安装完成！${NC}"
echo "=========================================="
echo ""
echo "使用方法："
echo "  CLI:    $RUN_PREFIX rmrb-download --once"
echo "  JSON:   $RUN_PREFIX rmrb-download --once --output-json"
echo "  定时:   $RUN_PREFIX rmrb-download"
echo "  Skill:  在 Claude Code 中输入 /rmrb"
echo ""
echo "下载目录: $PROJECT_ROOT/人民日报下载/"
echo ""
