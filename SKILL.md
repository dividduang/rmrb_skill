---
name: rmrb-pdf-fetcher
description: Use when user wants to download today's People's Daily (人民日报) PDF newspaper, or mentions 人民日报/人民報/rmrb. Triggers on Chinese newspaper download requests.
---

# 人民日报 PDF 下载器 (rmrb-pdf-fetcher)

下载当天人民日报完整版 PDF 报纸，自动抓取所有版面并合并为单个文件。

## 前置条件

首次使用需安装依赖：
```bash
bash scripts/install.sh      # Linux/macOS
scripts\install.bat          # Windows
```

## 工具

### rmrb_download - 下载当天人民日报

**执行命令（已安装包）：**
```bash
rmrb-download --once --output-json
```

**执行命令（开发模式）：**
```bash
python -m rmrb_fetcher.cli --once --output-json
```

**参数：**
- `--once`: 执行一次下载后退出
- `--output-json`: 返回 JSON 格式结果
- `--output-dir DIR`: 指定下载目录

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

## 使用示例

用户输入：
- "下载今天的人民日报"
- "/rmrb"
- "帮我下载人民日报PDF"

## 输出文件

下载的文件保存在 `人民日报下载/` 目录（相对于当前工作目录）。

## 注意事项

- 下载耗时约 2-5 分钟
- 仅支持下载当天的人民日报
- 需要能访问 `paper.people.com.cn`
