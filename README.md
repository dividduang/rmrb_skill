# 人民日报PDF自动下载器 (rmrb-pdf-fetcher)

> 自动下载并合并当天人民日报各版面PDF，支持命令行和 Claude Code Skill 调用。
>
> 仅限个人学习使用，若有侵权请联系删除。

基于 [Kings-en/rmrb-pdf-fetcher](https://github.com/Kings-en/rmrb-pdf-fetcher) 开发，使用 Playwright 重构。

## 样板展示

[人民日报-2025-10-19-完整版.pdf](https://github.com/user-attachments/files/22998360/-2025-10-19-.pdf)

## 功能

- 自动获取人民日报当天所有版面
- 下载并合并为单个完整PDF
- 支持每天定时自动执行（默认早8点）
- 支持 Claude Code Skill 一键调用
- JSON 输出模式，便于集成
- 随机 User-Agent + 延迟，降低被拦截风险

---

## 快速开始

### 环境要求

| 依赖 | 版本要求 |
|------|----------|
| Python | >= 3.11 |
| 网络访问 | 需能访问 `paper.people.com.cn` |

### 一键安装（推荐）

**Windows:**
```bash
scripts\install.bat
```

**Linux / macOS:**
```bash
bash scripts/install.sh
```

安装脚本自动完成：
1. 检测 Python 环境（优先使用 uv，回退到 pip + venv）
2. 安装 Python 依赖
3. 安装 Playwright Chromium 浏览器
4. 注册 Claude Code Skill 到 `~/.claude/skills/`

### 手动安装

**方式一：使用 uv**
```bash
git clone https://github.com/your-username/rmrb-pdf-fetcher.git
cd rmrb-pdf-fetcher
uv sync
uv run playwright install chromium
```

**方式二：使用 pip**
```bash
git clone https://github.com/your-username/rmrb-pdf-fetcher.git
cd rmrb-pdf-fetcher
python -m venv .venv

# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -e .
playwright install chromium
```

---

## 使用方法

### CLI 命令行

安装后提供 `rmrb-download` 命令：

```bash
# 一次性下载（最常用）
rmrb-download --once

# JSON 输出（用于集成）
rmrb-download --once --output-json

# 指定输出目录
rmrb-download --once --output-dir ~/Downloads

# 定时任务模式（默认早8点）
rmrb-download
```

**JSON 输出示例：**
```json
{
  "success": true,
  "date": "2026-04-02",
  "file_path": "/path/to/人民日报下载/人民日报-2026-04-02-完整版.pdf",
  "pages_count": 20,
  "message": "下载完成"
}
```

### Python API

```python
from rmrb_fetcher.downloader import download, download_with_result

# 简单下载，返回文件路径
file_path = download()

# 获取结构化结果
result = download_with_result()
print(result["success"], result["file_path"])
```

### 命令行参数

| 参数 | 说明 |
|------|------|
| `--once` | 执行一次下载后退出 |
| `--output-json` | JSON 格式输出，禁用控制台日志 |
| `--output-dir DIR` | 指定下载输出目录 |

---

## Claude Code Skill

安装后，在 Claude Code 中可以直接使用：

```
/rmrb
```

或自然语言：
```
下载今天的人民日报
帮我下载人民日报PDF
获取今天的报纸
```

### 手动注册 Skill

```bash
# Windows
mkdir %USERPROFILE%\.claude\skills\rmrb-pdf-fetcher
copy SKILL.md %USERPROFILE%\.claude\skills\rmrb-pdf-fetcher\

# Linux/macOS
mkdir -p ~/.claude/skills/rmrb-pdf-fetcher
cp SKILL.md ~/.claude/skills/rmrb-pdf-fetcher/
```

### Claude Code Hooks

项目包含 `.claude/settings.json`，配置了 SessionStart hook 自动检查依赖是否安装。

---

## 项目结构

```
rmrb-pdf-fetcher/
├── src/
│   └── rmrb_fetcher/            # Python 包
│       ├── __init__.py          # 包初始化
│       ├── cli.py               # CLI 入口 (rmrb-download)
│       └── downloader.py        # 核心下载逻辑
├── scripts/
│   ├── install.sh               # Linux/macOS 一键安装
│   └── install.bat              # Windows 一键安装
├── .claude/
│   └── settings.json            # Claude Code hooks 配置
├── SKILL.md                     # Claude Code Skill 定义
├── pyproject.toml               # 项目配置 & 依赖
├── requirements.txt             # pip 依赖（向后兼容）
├── README.md                    # 本文档
├── rmrb_download_playwright.py  # 独立脚本（向后兼容）
└── rmrb_download_once.py        # 简化版脚本（向后兼容）
```

## 输出文件

下载的文件保存在 `人民日报下载/` 目录：

```
人民日报下载/
└── 人民日报-2026-04-02-完整版.pdf
```

运行日志保存在 `rmrb_download.log`。

---

## 常见问题

### 1. Playwright 安装失败

```bash
# 设置国内镜像加速
set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright    # Windows
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright  # Linux/macOS

playwright install chromium
```

### 2. 下载失败或无版面

- 检查网络能否访问 `paper.people.com.cn`
- 当天报纸通常早6点后上线
- 查看日志：`cat rmrb_download.log`

### 3. Python 版本不兼容

```bash
python --version  # 确保 >= 3.11
```

### 4. uv sync 失败

回退到 pip：
```bash
python -m venv .venv && source .venv/bin/activate  # Linux/macOS
python -m venv .venv && .venv\Scripts\activate      # Windows
pip install -e .
playwright install chromium
```

---

## 致谢

- 原项目: [Kings-en/rmrb-pdf-fetcher](https://github.com/Kings-en/rmrb-pdf-fetcher)

## 贡献

欢迎提交 Pull Request 或 Issue。

## 许可证

MIT License
