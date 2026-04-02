"""
人民日报PDF下载器 - 核心下载逻辑
"""

import re
import time
import random
import logging
import os
import traceback
from datetime import datetime

import requests
from playwright.sync_api import sync_playwright
from PyPDF2 import PdfMerger, PdfReader

# 默认输出目录（相对于当前工作目录）
DEFAULT_OUTPUT_DIR = "人民日报下载"

# 人民日报官网地址
RMRB_URL = "https://paper.people.com.cn/rmrb/"

# 用户代理列表，用于随机切换，降低被反爬机制拦截的概率
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


def get_current_date():
    """获取当前日期字符串"""
    return datetime.now().strftime("%Y-%m-%d")


def _launch_browser(playwright):
    """启动 Playwright 浏览器并返回 (browser, context, page)"""
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
    return browser, context, page


def _close_browser(browser, page):
    """安全关闭浏览器资源"""
    if page:
        try:
            page.close()
        except Exception:
            pass
    if browser:
        try:
            browser.close()
        except Exception:
            pass


def get_pdf_urls(page, main_url=None):
    """
    使用 Playwright 获取所有版面 PDF 链接

    返回: (date_str, pdf_urls)
    """
    if main_url is None:
        main_url = RMRB_URL

    pdf_urls = []
    date_str = get_current_date()

    try:
        logging.info(f"正在访问人民日报网站: {main_url}")
        page.goto(main_url, wait_until="load", timeout=30000)
        page.wait_for_load_state("networkidle", timeout=10000)
        page.wait_for_timeout(1000)
        logging.info("页面加载完成")

        # 获取日期
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

        # 获取版面链接
        try:
            page_links = page.evaluate("""
                () => {
                    const links = Array.from(document.querySelectorAll('a[href*="node_"]'));
                    return links
                        .map(a => ({ text: a.textContent.trim(), href: a.href }))
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

            # 遍历每个版面获取 PDF 链接
            for i, page_data in enumerate(unique_pages):
                try:
                    logging.info(f"处理版面 {i+1}/{len(unique_pages)}: {page_data['text']}")
                    page.goto(page_data['href'], wait_until="load", timeout=30000)
                    page.wait_for_load_state("networkidle", timeout=10000)
                    page.wait_for_timeout(500)

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


def download_and_merge_pdfs(date_str, pdf_urls, output_dir=None):
    """
    下载并合并 PDF 文件

    Args:
        date_str: 日期字符串
        pdf_urls: PDF URL 列表
        output_dir: 输出目录，默认为 DEFAULT_OUTPUT_DIR

    Returns:
        合并后的文件路径，失败返回 None
    """
    if not pdf_urls:
        logging.warning("没有可下载的PDF链接")
        return None

    if output_dir is None:
        output_dir = DEFAULT_OUTPUT_DIR

    os.makedirs(output_dir, exist_ok=True)

    merger = PdfMerger()
    downloaded_files = []
    success_count = 0

    for i, url in enumerate(pdf_urls):
        try:
            logging.info(f"下载PDF {i+1}/{len(pdf_urls)}: {url}")

            headers = {
                'User-Agent': random.choice(USER_AGENTS),
                'Referer': 'https://paper.people.com.cn/',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
                'Connection': 'keep-alive',
            }

            time.sleep(random.uniform(1.0, 3.0))

            response = requests.get(url, headers=headers, stream=True, timeout=60)
            response.raise_for_status()

            filename = os.path.join(output_dir, f"人民日报-{date_str}-第{i+1:02d}版.pdf")
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            # 验证 PDF 有效性
            try:
                with open(filename, 'rb') as f:
                    PdfReader(f)
                downloaded_files.append(filename)
                success_count += 1

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

    if success_count > 0:
        merged_filename = os.path.join(output_dir, f"人民日报-{date_str}-完整版.pdf")
        with open(merged_filename, 'wb') as f:
            merger.write(f)

        logging.info(f"已合并并保存完整版: {merged_filename}")

        # 清理单个版面文件
        for file in downloaded_files:
            try:
                os.remove(file)
            except Exception as e:
                logging.error(f"删除文件失败: {file}, 错误: {e}")

        return merged_filename
    else:
        logging.warning("没有成功下载任何PDF文件")
        return None


def download(output_dir=None):
    """
    下载当天人民日报 PDF - 主入口

    Args:
        output_dir: 输出目录

    Returns:
        合并后的文件路径，失败返回 None
    """
    with sync_playwright() as playwright:
        browser = None
        page = None
        try:
            logging.info("开始人民日报PDF下载任务")
            browser, context, page = _launch_browser(playwright)
            date_str, pdf_urls = get_pdf_urls(page)
            result = download_and_merge_pdfs(date_str, pdf_urls, output_dir)

            if result:
                logging.info("人民日报PDF下载任务完成")
            else:
                logging.warning("人民日报PDF下载任务未完成")

            return result
        except Exception as e:
            logging.error(f"任务执行失败: {e}")
            logging.error(traceback.format_exc())
            return None
        finally:
            _close_browser(browser, page)
            logging.info("浏览器已关闭")


def download_with_result(output_dir=None):
    """
    下载当天人民日报，返回结构化结果字典
    用于 Skill 调用

    Returns:
        dict: {"success": bool, "date": str, "file_path": str, "pages_count": int, "message": str}
    """
    with sync_playwright() as playwright:
        browser = None
        page = None
        try:
            browser, context, page = _launch_browser(playwright)
            date_str, pdf_urls = get_pdf_urls(page)

            if not pdf_urls:
                return {"success": False, "error": "未找到PDF链接"}

            merged_path = download_and_merge_pdfs(date_str, pdf_urls, output_dir)

            if merged_path:
                return {
                    "success": True,
                    "date": date_str,
                    "file_path": os.path.abspath(merged_path),
                    "pages_count": len(pdf_urls),
                    "message": "下载完成"
                }
            else:
                return {"success": False, "error": "下载或合并PDF失败"}

        except Exception as e:
            return {"success": False, "error": str(e)}
        finally:
            _close_browser(browser, page)
