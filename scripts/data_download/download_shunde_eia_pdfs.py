"""
顺德区生态环境局环评报告PDF下载 (2023-2026)
反爬保护：随机UA、递增延迟、自动重试、断点续传
"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import requests
import json
import re
import os
import time
import random
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path(r"E:\软件\2023-2026年顺德受理公告")
API_BASE = "https://www.shunde.gov.cn/fssdsthjj/gkmlpt/api/all/4094"
MANIFEST_FILE = Path(r"E:\软件\shunde_eia_manifest.json")
PROGRESS_FILE = Path(r"E:\软件\download_progress.json")

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:126.0) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Edg/125.0.0.0",
]

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def safe_filename(name):
    """清理文件名中的非法字符"""
    illegal = r'[<>:"/\\|?*]'
    name = re.sub(illegal, '_', name)
    name = re.sub(r'\s+', ' ', name)
    if len(name) > 220:
        name = name[:220]
    return name.strip()

def load_progress():
    if PROGRESS_FILE.exists():
        with open(PROGRESS_FILE, encoding='utf-8') as f:
            return set(json.load(f))
    return set()

def save_progress(completed_ids):
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(sorted(completed_ids), f)

def get_session():
    session = requests.Session()
    session.headers.update({
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Cache-Control": "no-cache",
    })
    return session

def fetch_detail(session, url, retries=3):
    """获取详情页，带重试和指数退避"""
    for attempt in range(retries):
        try:
            resp = session.get(url, timeout=45)
            resp.encoding = 'utf-8'
            if resp.status_code == 200:
                return resp.text
            elif resp.status_code == 429:
                wait = (2 ** attempt) * 5 + random.uniform(1, 5)
                print(f"        429限流, 等待{wait:.0f}秒...")
                time.sleep(wait)
            else:
                time.sleep(2 ** attempt)
        except Exception as e:
            time.sleep(2 ** attempt)
    return None

def extract_pdfs(html):
    """从详情页提取PDF链接"""
    pdfs = set()
    for m in re.finditer(r'href=["\']([^"\']*\.pdf[^"\']*)["\']', html, re.IGNORECASE):
        url = m.group(1)
        if url.startswith('/'):
            url = f"http://www.shunde.gov.cn{url}"
        elif not url.startswith('http'):
            url = f"http://www.shunde.gov.cn/{url}"
        pdfs.add(url)
    return list(pdfs)

def get_title(html):
    m = re.search(r'<title>([^<]*)</title>', html)
    return m.group(1).strip() if m else None

def download_pdf(session, url, filepath, retries=3):
    """下载PDF，带重试"""
    for attempt in range(retries):
        try:
            resp = session.get(url, timeout=180, stream=True)
            resp.raise_for_status()
            ct = resp.headers.get('Content-Type', '')
            if 'html' in ct:
                print(f"        PDF链接返回HTML(可能失效), 跳过")
                return False
            with open(filepath, 'wb') as f:
                for chunk in resp.iter_content(chunk_size=65536):
                    f.write(chunk)
            # 验证文件大小
            if os.path.getsize(filepath) < 1024:
                os.remove(filepath)
                print(f"        PDF过小(<1KB), 删除")
                return False
            return True
        except Exception as e:
            if attempt < retries - 1:
                wait = (2 ** attempt) * 3 + random.uniform(1, 3)
                time.sleep(wait)
            else:
                print(f"        PDF下载失败: {e}")
    return False

def download_all():
    # 加载manifest
    with open(MANIFEST_FILE, encoding='utf-8') as f:
        all_articles = json.load(f)

    # 筛选2023-2026
    articles = [a for a in all_articles if a['date'][:4] in ('2023','2024','2025','2026')]
    print(f"目标: {len(articles)} 篇 (2023-2026)")
    print(f"输出: {OUTPUT_DIR}\n")

    completed = load_progress()
    print(f"已完成: {len(completed)} 篇\n")

    session = get_session()
    stats = {'ok': 0, 'no_pdf': 0, 'fail': 0, 'skip': 0}

    for idx, article in enumerate(articles):
        aid = str(article['id'])
        if aid in completed:
            stats['skip'] += 1
            continue

        date_str = article['date']
        year = date_str[:4]

        # 随机延迟(反爬)
        delay = random.uniform(1.0, 3.0)
        time.sleep(delay)

        # 获取详情页
        html = fetch_detail(session, article['url'])
        if not html:
            print(f"[{idx+1}/{len(articles)}] {date_str} 详情页获取失败")
            stats['fail'] += 1
            continue

        page_title = get_title(html) or article['title']

        # 提取PDF
        pdf_urls = extract_pdfs(html)

        if not pdf_urls:
            print(f"[{idx+1}/{len(articles)}] {year} | {date_str} | 无PDF: {page_title[:60]}")
            stats['no_pdf'] += 1
            completed.add(aid)
            continue

        print(f"[{idx+1}/{len(articles)}] {year} | {date_str} | {page_title[:60]}... ({len(pdf_urls)}PDF)")

        # 下载每个PDF
        all_ok = True
        for i, pdf_url in enumerate(pdf_urls):
            # 文件名: 年份_页面标题[_序号].pdf
            if len(pdf_urls) > 1:
                fname = f"{year}_{page_title}_{i+1}.pdf"
            else:
                fname = f"{year}_{page_title}.pdf"
            fname = safe_filename(fname)
            fpath = OUTPUT_DIR / fname

            if fpath.exists():
                print(f"    [{i+1}/{len(pdf_urls)}] 已存在: {fname}")
                continue

            print(f"    [{i+1}/{len(pdf_urls)}] {fname[:80]}...")

            # PDF之间也加延迟
            time.sleep(random.uniform(1.0, 2.5))

            if download_pdf(session, pdf_url, fpath):
                stats['ok'] += 1
            else:
                all_ok = False

        if all_ok:
            completed.add(aid)

        # 每20篇保存进度
        if (idx + 1) % 20 == 0:
            save_progress(completed)
            print(f"  --- 进度: {len(completed)}/{len(articles)}, "
                  f"PDF已下载:{stats['ok']}, 失败:{stats['fail']} ---")

    save_progress(completed)

    print("\n" + "=" * 50)
    print("下载完成!")
    print(f"  总文章: {len(articles)}")
    print(f"  已处理: {len(completed)}")
    print(f"  PDF下载成功: {stats['ok']}")
    print(f"  无PDF附件: {stats['no_pdf']}")
    print(f"  失败: {stats['fail']}")
    print(f"  跳过(已完成): {stats['skip']}")
    print(f"  文件目录: {OUTPUT_DIR}")
    # Count files
    pdf_count = len(list(OUTPUT_DIR.glob("*.pdf")))
    print(f"  目录中PDF总数: {pdf_count}")

if __name__ == '__main__':
    download_all()
