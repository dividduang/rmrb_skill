# 人民日报PDF自动下载器 (rmrb-pdf-fetcher)

> 自动下载并合并当天人民日报各版面PDF，支持命令行和 Claude Code Skill 调用。
>
> 仅限个人学习使用，若有侵权请联系删除。

基于 [Kings-en/rmrb-pdf-fetcher](https://github.com/Kings-en/rmrb-pdf-fetcher) 开发，使用 Playwright 重构，比 Selenium 版本更快更稳定。

## 样板展示

### PDF版报纸

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
| Playwright | >= 1.40.0 |
| 网络访问 | 需能访问 `paper.people.com.cn` |

### 一键安装（推荐）

**Windows:**
```bash
# 克隆项目后，双击运行或在终端执行
install.bat
```

**Linux / macOS:**
```bash
git clone https://github.com/your-username/rmrb-pdf-fetcher.git
cd rmrb-pdf-fetcher
bash install.sh
```

安装脚本会自动完成：
1. 检测 Python 环境
2. 安装 Python 依赖（优先使用 uv，回退到 pip + venv）
3. 安装 Playwright Chromium 浏览器
4. 注册 Claude Code Skill

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

pip install -r requirements.txt
playwright install chromium
```

---

## 使用方法

### 命令行

**一次性下载（最常用）：**
```bash
# uv 方式
uv run python rmrb_download_playwright.py --once

# pip 方式（虚拟环境已激活）
python rmrb_download_playwright.py --once
```

**JSON 输出（用于集成）：**
```bash
python rmrb_download_playwright.py --once --output-json
```

输出示例：
```json
{
  "success": true,
  "date": "2026-04-02",
  "file_path": "/path/to/人民日报下载/人民日报-2026-04-02-完整版.pdf",
  "pages_count": 20,
  "message": "下载完成"
}
```

**定时任务模式（默认早8点）：**
```bash
python rmrb_download_playwright.py
```

按 `Ctrl+C` 停止定时任务。

### 命令行参数

| 参数 | 说明 |
|------|------|
| `--once` | 执行一次下载后退出 |
| `--output-json` | JSON 格式输出，禁用控制台日志 |

---

## Claude Code Skill 集成

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

如果自动安装未注册 Skill，可以手动操作：

```bash
# Windows
mkdir %USERPROFILE%\.claude\skills\rmrb-pdf-fetcher
copy SKILL.md %USERPROFILE%\.claude\skills\rmrb-pdf-fetcher\

# Linux/macOS
mkdir -p ~/.claude/skills/rmrb-pdf-fetcher
cp SKILL.md ~/.claude/skills/rmrb-pdf-fetcher/
```

---

## 项目结构

```
rmrb-pdf-fetcher/
├── rmrb_download_playwright.py   # 主程序（Playwright版本，推荐）
├── rmrb_download_once.py         # 简化版（仅一次性下载）
├── upload_mineru.py              # MinerU 上传工具（可选）
├── SKILL.md                      # Claude Code Skill 定义
├── install.sh                    # Linux/macOS 一键安装
├── install.bat                   # Windows 一键安装
├── pyproject.toml                # 项目配置
├── requirements.txt              # Python 依赖
├── README.md                     # 本文档
└── 人民日报下载/                  # 下载输出目录（自动创建）
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

**症状：** `playwright install chromium` 报错或超时

**解决方案：**
```bash
# 设置国内镜像
set PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright  # Windows
export PLAYWRIGHT_DOWNLOAD_HOST=https://npmmirror.com/mirrors/playwright  # Linux/macOS

playwright install chromium
```

### 2. 下载失败或无版面

**可能原因：**
- 网络无法访问 `paper.people.com.cn`
- 当天报纸尚未上线（通常早6点后可用）
- 版面结构变化

**排查步骤：**
```bash
# 检查网络连通性
curl -I https://paper.people.com.cn/rmrb/

# 查看详细日志
cat rmrb_download.log
```

### 3. Python 版本不兼容

确保 Python >= 3.11：
```bash
python --version
# 如版本过低，从 https://www.python.org/downloads/ 下载安装
```

### 4. uv sync 失败

回退到 pip 方式：
```bash
python -m venv .venv
# 激活虚拟环境后
pip install -r requirements.txt
playwright install chromium
```

---

## 致谢

- 原项目: [Kings-en/rmrb-pdf-fetcher](https://github.com/Kings-en/rmrb-pdf-fetcher)

## 贡献

欢迎提交 Pull Request 或 Issue。

## 许可证

MIT License
