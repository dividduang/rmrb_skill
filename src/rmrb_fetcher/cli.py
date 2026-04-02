"""
人民日报PDF下载器 - 命令行入口
"""

import argparse
import json
import logging
import sys
import time

import schedule

from .downloader import download, download_with_result


def _disable_console_logging():
    """禁用控制台日志输出（用于 JSON 模式）"""
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
            root_logger.removeHandler(handler)


def main():
    """CLI 主函数"""
    parser = argparse.ArgumentParser(
        prog='rmrb-download',
        description='人民日报PDF自动下载器'
    )
    parser.add_argument(
        '--once', action='store_true',
        help='执行一次下载后退出（不启动定时任务）'
    )
    parser.add_argument(
        '--output-json', action='store_true',
        help='JSON格式输出（禁用控制台日志）'
    )
    parser.add_argument(
        '--output-dir', type=str, default=None,
        help='指定下载输出目录'
    )
    args = parser.parse_args()

    if args.output_json:
        _disable_console_logging()

    if args.once:
        result = download_with_result(output_dir=args.output_dir)
        print(json.dumps(result, ensure_ascii=False))
        sys.exit(0 if result['success'] else 1)

    # 默认：定时任务模式
    schedule.every().day.at("08:00").do(download, output_dir=args.output_dir)

    logging.info("开始测试运行...")
    if download(output_dir=args.output_dir):
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
            time.sleep(300)


if __name__ == "__main__":
    main()
