# 人民日报自动下载器

> 这是一个用于自动获取每日人民日报完整PDF的项目，仅限自己学习使用，若有侵权联系删除。

这是一个用于自动下载并合并人民日报版面 PDF 的 Python 程序。该程序每天定时从人民日报的官方网站下载最新的 PDF 文件，并将它们合并为一个完整的 PDF 文件。

**本项目现已使用 Playwright 重构，比之前的 Selenium 版本更快、更稳定！**

## 致谢

本项目基于 [Kings-en/rmrb-pdf-fetcher](https://github.com/Kings-en/rmrb-pdf-fetcher) 开发，感谢原作者的工作。

## 样板展示

### `main` 分支 - PDF版报纸

[人民日报-2025-10-19-完整版.pdf](https://github.com/user-attachments/files/22998360/-2025-10-19-.pdf)

### `article-crawler` 分支 - 文章汇总

[rmrb_20251020.pdf](https://github.com/user-attachments/files/22998375/rmrb_20251020.pdf)

## 功能

- 自动获取人民日报最新页面
- 下载并合并该页面中的所有 PDF 文件
- 每天早上8点定时执行任务
- 支持日志记录和错误处理
- 使用 Playwright 浏览器自动化，比 Selenium 更快更稳定
- 支持 Claude Code Skill 调用

---

## 安装部署

### 方式一：使用 uv（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/your-username/rmrb-pdf-fetcher.git
cd rmrb-pdf-fetcher

# 2. 同步依赖
uv sync

# 3. 安装 Playwright 浏览器
uv run playwright install chromium
```

### 方式二：使用 pip

```bash
# 1. 克隆项目
git clone https://github.com/your-username/rmrb-pdf-fetcher.git
cd rmrb-pdf-fetcher

# 2. 安装依赖
pip install -r requirements.txt

# 3. 安装 Playwright 浏览器
playwright install chromium
```

---

## 使用方法

### 命令行运行

**定时任务模式（默认）**：

```bash
uv run python rmrb_download_playwright.py
```

**执行一次**：

```bash
uv run python rmrb_download_playwright.py --once
```

**JSON 输出模式（用于 skill 调用）**：

```bash
uv run python rmrb_download_playwright.py --once --output-json
```

### 命令行参数

| 参数 | 说明 |
|------|------|
| `--once` | 执行一次下载后退出（不启动定时任务） |
| `--output-json` | JSON 格式输出（禁用控制台日志） |

---

## Claude Code Skill 集成

### 安装 Skill

将 `skill.md` 复制到 Claude Code skills 目录：

```bash
# Windows
mkdir %USERPROFILE%\.claude\skills\rmrb-pdf-fetcher
copy skill.md %USERPROFILE%\.claude\skills\rmrb-pdf-fetcher\

# Linux/macOS
mkdir -p ~/.claude/skills/rmrb-pdf-fetcher
cp skill.md ~/.claude/skills/rmrb-pdf-fetcher/
```

### 使用方式

在 Claude Code 中输入：

```
/rmrb
```

或自然语言：

```
下载今天的人民日报
```

---

## 输出文件

下载的文件保存在 `人民日报下载/` 目录：

```
人民日报下载/
└── 人民日报-2026-03-19-完整版.pdf
```

## 日志

运行日志保存在项目根目录的 `rmrb_download.log` 文件中。

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Kings-en/rmrb-pdf-fetcher&type=date&legend=top-left)](https://www.star-history.com/#Kings-en/rmrb-pdf-fetcher&type=date&legend=top-left)

## 贡献

如果你希望为该项目贡献代码，可以创建一个 pull request，提交新的功能或修复 bug。

## 许可证

MIT License
