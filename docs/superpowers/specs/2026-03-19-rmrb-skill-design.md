# rmrb-pdf-fetcher Skill 设计文档

## 背景

将 rmrb-pdf-fetcher（人民日报PDF下载器）封装成 Claude Code skill，让用户可以通过自然语言或命令调用下载当天的人民日报。

## 目标

- 创建 `/rmrb` 命令，一键下载当天人民日报
- 提供单一工具：下载当天人民日报
- 最小化代码改动，复用现有 Python 脚本

## 技术方案

### 架构

```
用户输入 "/rmrb" 或 "下载今天的人民日报"
    ↓
Claude Code 加载 skill.md
    ↓
Skill 指示 Claude 调用 rmrb_download 工具
    ↓
Claude 执行：python rmrb_download_playwright.py --once --output-json
    ↓
返回结果给用户
```

### 文件结构

```
~/.claude/skills/rmrb-pdf-fetcher/
├── skill.md          # Skill 定义文件

项目目录：
D:\a_gitlab_new\A_2026\rmrb-pdf-fetcher\
├── rmrb_download_playwright.py  # 现有脚本（需修改）
└── requirements.txt             # 依赖（无需修改）
```

### 工具定义

#### rmrb_download

下载当天的人民日报 PDF。

**调用方式：**
```bash
python rmrb_download_playwright.py --once --output-json
```

**返回格式（成功）：**
```json
{
  "success": true,
  "date": "2026-03-19",
  "file_path": "D:\\a_gitlab_new\\A_2026\\rmrb-pdf-fetcher\\人民日报下载\\人民日报-2026-03-19-完整版.pdf",
  "pages_count": 20,
  "message": "下载完成"
}
```

**返回格式（失败）：**
```json
{
  "success": false,
  "error": "网络连接失败"
}
```

---

## 代码修改

### 1. Import 部分（文件顶部）

**原代码（第7-17行）：**
```python
import schedule
import time
import re
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from PyPDF2 import PdfMerger, PdfReader
import os
import logging
from datetime import datetime
import traceback
import random
```

**修改为：**
```python
import schedule
import time
import re
import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from PyPDF2 import PdfMerger, PdfReader
import os
import logging
from datetime import datetime
import traceback
import random
import argparse
import json
import sys
```

### 2. 日志配置后添加 JSON 模式处理函数（第28行后）

在 `logging.basicConfig()` 之后添加：

```python
def disable_console_logging():
    """禁用控制台日志输出（用于 JSON 模式）"""
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
            root_logger.removeHandler(handler)
```

### 3. 添加新函数 download_rmrb_pdf_with_result()（在 download_rmrb_pdf() 函数之后）

```python
def download_rmrb_pdf_with_result():
    """
    下载当天人民日报，返回结果字典
    用于 skill 调用，返回结构化 JSON 结果
    """
    with sync_playwright() as playwright:
        browser = None
        page = None
        try:
            browser = playwright.chromium.launch(
                headless=True,
                args=[
                    '--disable-gpu',
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-extensions',
                    '--disable-infobars',
                    '--disable-notifications',
                ]
            )
            context = browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={'width': 1920, 'height': 1080},
                locale='zh-CN'
            )
            page = context.new_page()
            page.set_default_timeout(30000)
            main_url = 'https://paper.people.com.cn/rmrb/'
            date_str, pdf_urls = get_pdf_urls(page, main_url)

            if not pdf_urls:
                return {
                    "success": False,
                    "error": "未找到PDF链接"
                }

            # 下载并合并
            success = download_and_merge_pdfs(date_str, pdf_urls)

            if success:
                # 返回绝对路径
                script_dir = os.path.dirname(os.path.abspath(__file__))
                file_path = os.path.join(script_dir, "人民日报下载", f"人民日报-{date_str}-完整版.pdf")
                return {
                    "success": True,
                    "date": date_str,
                    "file_path": os.path.abspath(file_path),
                    "pages_count": len(pdf_urls),
                    "message": "下载完成"
                }
            else:
                return {
                    "success": False,
                    "error": "下载或合并PDF失败"
                }

        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
        finally:
            if page:
                try:
                    page.close()
                except:
                    pass
            if browser:
                try:
                    browser.close()
                except:
                    pass
```

### 4. 添加 main() 函数并重构底部代码

**原代码（第315-339行）：**
```python
# 设置定时任务 - 每天8点执行，别tm迟到
schedule.every().day.at("08:00").do(download_rmrb_pdf)

# 立即执行一次（测试用） - 看看这憨批代码能不能跑
logging.info("开始测试运行...")
if download_rmrb_pdf():
    logging.info("测试运行成功！")
else:
    logging.warning("测试运行失败")

logging.info("人民日报自动下载程序已启动，每天8点自动执行")

# 保持程序运行 - 按Ctrl+C可以中断，别tm强行关进程
while True:
    try:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次
    except KeyboardInterrupt:
        logging.info("程序被用户中断")
        break
    except Exception as e:
        logging.error(f"主循环出错: {e}")
        logging.error(traceback.format_exc())
        time.sleep(300)  # 出错后等待5分钟再重试
```

**替换为：**
```python
def main():
    """主函数 - 处理命令行参数并执行相应操作"""
    parser = argparse.ArgumentParser(description='人民日报PDF下载器')
    parser.add_argument('--once', action='store_true',
                        help='执行一次下载后退出（不启动定时任务）')
    parser.add_argument('--output-json', action='store_true',
                        help='JSON格式输出（禁用控制台日志）')
    args = parser.parse_args()

    # JSON模式下禁用控制台日志
    if args.output_json:
        disable_console_logging()

    if args.once:
        # 执行一次下载并返回 JSON 结果
        result = download_rmrb_pdf_with_result()
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(0 if result['success'] else 1)

    # 默认行为：启动定时任务（保持向后兼容）
    schedule.every().day.at("08:00").do(download_rmrb_pdf)

    logging.info("开始测试运行...")
    if download_rmrb_pdf():
        logging.info("测试运行成功！")
    else:
        logging.warning("测试运行失败")

    logging.info("人民日报自动下载程序已启动，每天8点自动执行")

    while True:
        try:
            schedule.run_pending()
            time.sleep(60)
        except KeyboardInterrupt:
            logging.info("程序被用户中断")
            break
        except Exception as e:
            logging.error(f"主循环出错: {e}")
            logging.error(traceback.format_exc())
            time.sleep(300)


if __name__ == "__main__":
    main()
```

---

## Skill 文件内容

### skill.md

```markdown
---
name: rmrb-pdf-fetcher
description: 下载当天人民日报PDF报纸。使用场景：用户要求下载人民日报、获取今天的报纸。
---

# 人民日报 PDF 下载器

下载当天的人民日报 PDF 报纸。

## 可用工具

### rmrb_download

下载当天的人民日报 PDF。

**使用场景：** 用户要下载今天的人民日报。

**执行方式：**
```bash
cd /d D:\a_gitlab_new\A_2026\rmrb-pdf-fetcher && python rmrb_download_playwright.py --once --output-json
```

**返回：** JSON 格式的下载结果

## 使用示例

用户输入：
- "下载今天的人民日报"
- "/rmrb"
- "帮我下载人民日报"
```

> **注意：** 此 skill 使用硬编码的 Windows 路径，仅适用于当前开发环境。如需在其他环境使用，请修改 skill.md 中的路径。

---

## 配置

- **运行模式：** 同步（等待下载完成，约2-5分钟）
- **错误处理：** 简单返回（成功/失败状态和错误消息）
- **下载目录：** 固定为 `人民日报下载/`（相对于项目目录）

## 验证方式

1. 安装依赖：
   ```bash
   pip install -r requirements.txt
   playwright install chromium
   ```

2. 测试命令行：
   ```bash
   python rmrb_download_playwright.py --once --output-json
   ```

3. 安装 skill：
   将 skill.md 复制到 `~/.claude/skills/rmrb-pdf-fetcher/skill.md`

4. 在 Claude Code 中测试：
   ```
   /rmrb
   ```

## 限制

- 仅支持下载当天的人民日报
- 需要本地安装 Playwright 和 Chromium
- 下载目录固定，无法自定义
- 同步模式，下载期间会阻塞
- Skill 路径为 Windows 特定，需手动调整才能用于其他环境

## 文件清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `rmrb_download_playwright.py` | 修改 | 添加命令行参数、JSON输出、main函数 |
| `~/.claude/skills/rmrb-pdf-fetcher/skill.md` | 新建 | Skill 定义文件 |
