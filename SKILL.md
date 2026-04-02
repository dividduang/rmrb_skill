---
name: rmrb-pdf-fetcher
description: Use when user wants to download today's People's Daily (人民日报) PDF newspaper, or mentions 人民日报/人民報/rmrb. Triggers on Chinese newspaper download requests.
---

# 人民日报 PDF 下载器 (rmrb-pdf-fetcher)

下载当天人民日报完整版 PDF 报纸，自动抓取所有版面并合并为单个文件。

## 前置条件

运行前必须确保环境已安装：
- Python >= 3.11
- Playwright + Chromium 浏览器

首次使用需执行安装：
```bash
# 项目目录下运行
pip install -r requirements.txt
playwright install chromium
```

## 工具

### rmrb_download - 下载当天人民日报

**执行命令：**
```bash
cd {{项目目录}} && python rmrb_download_playwright.py --once --output-json
```

- `--once`: 执行一次下载后退出
- `--output-json`: 返回 JSON 格式结果（禁用控制台日志）

**成功返回：**
```json
{
  "success": true,
  "date": "2026-04-02",
  "file_path": "/path/to/人民日报下载/人民日报-2026-04-02-完整版.pdf",
  "pages_count": 20,
  "message": "下载完成"
}
```

**失败返回：**
```json
{
  "success": false,
  "error": "未找到PDF链接"
}
```

## 使用示例

用户输入：
- "下载今天的人民日报"
- "/rmrb"
- "帮我下载人民日报PDF"
- "获取今天的报纸"

## 输出文件

下载的文件保存在 `人民日报下载/` 目录（相对于项目根目录）。

## 注意事项

- 下载耗时约 2-5 分钟，取决于网络速度和版面数量
- 仅支持下载当天的人民日报
- 需要能访问 `paper.people.com.cn`
