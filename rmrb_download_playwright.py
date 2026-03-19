"""
人民日报PDF自动下载器 - Playwright版本
这个SB代码用Playwright替代了那个破Selenium，速度更快还更稳定
作者：隔壁老王
"""

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

# 配置日志 - 别tm乱改格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rmrb_download.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)


def disable_console_logging():
    """禁用控制台日志输出（用于 JSON 模式）"""
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        if isinstance(handler, logging.StreamHandler) and not isinstance(handler, logging.FileHandler):
            root_logger.removeHandler(handler)

# 用户代理列表，用于随机切换 - 防止被憨批反爬虫系统ban了
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
]


def get_current_date():
    """获取当前日期字符串，这特喵的还需要注释？"""
    return datetime.now().strftime("%Y-%m-%d")


def get_pdf_urls(page, main_url):
    """
    使用Playwright获取所有PDF链接
    比那个破Selenium快多了，还更稳定
    """
    pdf_urls = []
    date_str = get_current_date()

    try:
        # 访问人民日报网站
        logging.info(f"正在访问人民日报网站: {main_url}")
        page.goto(main_url, wait_until="load", timeout=30000)

        # 等待页面完全稳定，避免执行上下文被销毁
        page.wait_for_load_state("networkidle", timeout=10000)
        page.wait_for_timeout(1000)  # 额外等待1秒确保页面稳定
        logging.info("页面加载完成")

        # 尝试获取日期元素
        try:
            date_text = page.evaluate("""
                () => {
                    const text = document.body.innerText;
                    const match = text.match(/(\\d{4})年(\\d{2})月(\\d{2})日/);
                    return match ? `${match[1]}-${match[2]}-${match[3]}` : null;
                }
            """)
            if date_text:
                date_str = date_text
                logging.info(f"从页面获取到日期: {date_str}")
            else:
                logging.warning("未获取到页面日期，使用当前日期")
        except Exception as e:
            logging.warning(f"获取日期失败: {e}，使用当前日期")

        # 获取所有版面链接
        try:
            page_links = page.evaluate("""
                () => {
                    const links = Array.from(document.querySelectorAll('a[href*="node_"]'));
                    return links
                        .map(a => ({
                            text: a.textContent.trim(),
                            href: a.href
                        }))
                        .filter(link => link.href.match(/node_\\d+\\.html$/) && link.text.includes('版'));
                }
            """)

            if not page_links:
                logging.warning("未找到任何版面链接")
                return date_str, []

            # 去重并排序
            unique_pages = []
            seen = set()
            for link in page_links:
                match = re.search(r'node_(\d+)\.html', link['href'])
                if match:
                    page_num = match.group(1)
                    if page_num not in seen:
                        seen.add(page_num)
                        unique_pages.append({
                            'page_num': page_num,
                            'href': link['href'],
                            'text': link['text']
                        })

            unique_pages.sort(key=lambda x: int(x['page_num']))
            logging.info(f"找到 {len(unique_pages)} 个版面")

            # 遍历每个版面，获取PDF链接
            for i, page_data in enumerate(unique_pages):
                try:
                    logging.info(f"处理版面 {i+1}/{len(unique_pages)}: {page_data['text']}")

                    # 导航到版面页面
                    page.goto(page_data['href'], wait_until="load", timeout=30000)

                    # 等待页面完全稳定，避免执行上下文被销毁
                    page.wait_for_load_state("networkidle", timeout=10000)
                    page.wait_for_timeout(500)

                    # 提取PDF链接
                    pdf_url = page.evaluate("""
                        () => {
                            const pdfLink = document.querySelector('.paper-bot a');
                            return pdfLink ? pdfLink.href : null;
                        }
                    """)

                    if pdf_url and pdf_url.endswith('.pdf'):
                        pdf_urls.append(pdf_url)
                        logging.info(f"找到PDF链接: {pdf_url}")
                    else:
                        logging.warning(f"版面 {page_data['text']} 未找到有效的PDF链接")

                except Exception as e:
                    logging.error(f"处理版面 {page_data['text']} 时出错: {e}")
                    logging.error(traceback.format_exc())

            return date_str, pdf_urls

        except Exception as e:
            logging.error(f"获取版面链接失败: {e}")
            logging.error(traceback.format_exc())
            return date_str, []

    except Exception as e:
        logging.error(f"访问人民日报网站失败: {e}")
        logging.error(traceback.format_exc())
        return date_str, []


def download_and_merge_pdfs(date_str, pdf_urls):
    """
    下载并合并PDF文件
    这个憨批函数写得特喵的规范
    """
    if not pdf_urls:
        logging.warning("没有可下载的PDF链接")
        return False

    # 创建下载目录
    download_dir = "人民日报下载"
    os.makedirs(download_dir, exist_ok=True)

    # 下载并合并PDF
    merger = PdfMerger()
    downloaded_files = []
    success_count = 0

    for i, url in enumerate(pdf_urls):
        try:
            logging.info(f"下载PDF {i+1}/{len(pdf_urls)}: {url}")

            # 设置请求头，模拟浏览器访问 - 不然那憨批服务器不给你下
            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                'Referer': 'https://paper.people.com.cn/',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Connection': 'keep-alive',
            }

            # 增加随机延迟，避免请求过快被ban
            time.sleep(random.uniform(1.0, 3.0))

            response = requests.get(url, headers=headers, stream=True, timeout=60)
            response.raise_for_status()

            # 保存单个PDF
            filename = os.path.join(download_dir, f"人民日报-{date_str}-第{i+1:02d}版.pdf")
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # 验证PDF文件是否有效 - 万一下载的是个憨批错误页面呢
            try:
                with open(filename, 'rb') as f:
                    PdfReader(f)
                downloaded_files.append(filename)
                success_count += 1

                # 添加到合并器
                with open(filename, 'rb') as f:
                    merger.append(f)

                logging.info(f"已保存: {filename}")
            except Exception as e:
                logging.error(f"PDF文件无效: {filename}, 错误: {e}")
                os.remove(filename)
                logging.info(f"已删除无效文件: {filename}")

        except Exception as e:
            logging.error(f"下载PDF失败: {url}, 错误: {e}")
            logging.error(traceback.format_exc())

    # 保存合并的PDF
    if success_count > 0:
        merged_filename = os.path.join(download_dir, f"人民日报-{date_str}-完整版.pdf")
        with open(merged_filename, 'wb') as f:
            merger.write(f)

        logging.info(f"已合并并保存完整版: {merged_filename}")

        # 删除单个版面的PDF文件 - 别tm占硬盘空间
        for file in downloaded_files:
            try:
                os.remove(file)
                logging.info(f"已删除单个文件: {file}")
            except Exception as e:
                logging.error(f"删除文件失败: {file}, 错误: {e}")

        return True
    else:
        logging.warning("没有成功下载任何PDF文件")
        return False


def download_rmrb_pdf():
    """
    下载并合并人民日报PDF - 主流程控制函数
    这个函数协调一切，像个憨批管家
    """
    with sync_playwright() as playwright:
        browser = None
        page = None
        try:
            logging.info("开始人民日报PDF下载任务")

            # 启动浏览器 - Chromium比Chrome快，别tm废话
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

            # 创建浏览器上下文 - 模拟真实浏览器环境
            context = browser.new_context(
                user_agent=random.choice(USER_AGENTS),
                viewport={'width': 1920, 'height': 1080},
                locale='zh-CN'
            )

            # 创建页面
            page = context.new_page()

            # 设置默认超时时间
            page.set_default_timeout(30000)

            # 人民日报网址
            main_url = 'https://paper.people.com.cn/rmrb/'

            # 获取日期和PDF链接
            date_str, pdf_urls = get_pdf_urls(page, main_url)

            # 下载并合并PDF
            result = download_and_merge_pdfs(date_str, pdf_urls)

            if result:
                logging.info("人民日报PDF下载任务完成")
            else:
                logging.warning("人民日报PDF下载任务未完成")

            return result

        except Exception as e:
            logging.error(f"任务执行失败: {e}")
            logging.error(traceback.format_exc())
            return False
        finally:
            # 清理资源 - 别tm占用内存
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
            logging.info("浏览器已关闭")


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
