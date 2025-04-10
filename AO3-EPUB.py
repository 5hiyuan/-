import os
import re
import json
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random

# 設定 
# cookie 檔案名稱根據實際情況填寫
cookie_txt_file = os.path.join(os.path.dirname(__file__), "")
input_file = os.path.join(os.path.dirname(__file__), "抓取清單.xlsx")
output_dir = os.path.join(os.path.dirname(__file__), "抓取結果")
os.makedirs(output_dir, exist_ok=True)

# Cookie 讀取（從 txt 檔） 
def load_cookies_from_txt(txt_path):
    cookies = {}
    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line:
                name, value = line.strip().split("=", 1)
                cookies[name] = value
    return cookies

cookies = load_cookies_from_txt(cookie_txt_file)

# 工具函式 
def clean_title(title):
    replacements = {
        ":": "：", "?": "？", "/": "／", "\\": "＼",
        "*": "＊", "<": "＜", ">": "＞", "|": "｜",
        "(": "（", ")": "）", "~": "～"
    }
    for k, v in replacements.items():
        title = title.replace(k, v)
    title = re.sub(r'[\n\r\t]+', '', title).strip()
    return title[:100] or "untitled"

def log_error(url, reason):
    with open("錯誤清單.txt", "a", encoding="utf-8") as f:
        f.write(f"{url}  # {reason}\n")
    print(f"❌ 錯誤：{url}  # {reason}")

# 抓取網址 
df = pd.read_excel(input_file, sheet_name="EPUB")
urls = []
for _, row in df.iterrows():
    url = str(row.get("URL", "")).strip()
    ao3_id = str(row.get("ID", "")).strip()
    if url and url.lower() != "nan":
        urls.append(url)
    elif ao3_id and ao3_id.lower() != "nan":
        urls.append(f"https://archiveofourown.org/works/{ao3_id}")

# 強化 Header 
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
    "Referer": "https://archiveofourown.org/",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Upgrade-Insecure-Requests": "1"
}

retry_later = []

def attempt_download(work_url):
    try:
        time.sleep(random.randint(3, 7))  # 模擬人類行為延遲
        r = requests.get(work_url + "?view_adult=true&view_full_work=true", headers=headers, cookies=cookies, timeout=180)
        if r.status_code == 525:
            return "RETRY"
        elif r.status_code != 200:
            log_error(work_url, f"作品頁錯誤 HTTP {r.status_code}")
            return "FAIL"

        soup = BeautifulSoup(r.text, "html.parser")
        title_tag = soup.select_one("h2.title")
        author_tag = soup.select_one("h3.byline a")
        title = clean_title(title_tag.text if title_tag else "untitled")
        author = author_tag.text.strip() if author_tag else "作者不明"

        epub_link = soup.find("a", string="EPUB")
        if not epub_link:
            log_error(work_url, "找不到 EPUB 連結")
            return "FAIL"

        download_url = "https://archiveofourown.org" + epub_link["href"]
        time.sleep(random.randint(2, 6))  # 再加一層點擊延遲
        res = requests.get(download_url, headers={**headers, "Referer": work_url}, cookies=cookies, timeout=180)
        if res.status_code == 525:
            return "RETRY"
        elif res.status_code != 200:
            log_error(work_url, f"EPUB 下載錯誤 HTTP {res.status_code}")
            return "FAIL"

        filename = f"{title}.epub"
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "wb") as f:
            f.write(res.content)
        print(f"✅ 已儲存：{filename}\n📁 儲存路徑：{filepath}")
        return "SUCCESS"

    except Exception as e:
        print(f"⚠️ 抓取失敗（{str(e)}）將稍後重試：{work_url}")
        return "RETRY"

# 第一輪嘗試：成功的立即處理，525 與例外延後重試
for idx, work_url in enumerate(urls, 1):
    print(f"[{idx}/{len(urls)}] 讀取：{work_url}")
    result = attempt_download(work_url)
    if result == "RETRY":
        retry_later.append(work_url)

# 第二輪重試：每個最多 5 次
for work_url in retry_later:
    for attempt in range(1, 6):
        print(f"🔁 重試 ({attempt}/5)：{work_url}")
        result = attempt_download(work_url)
        if result == "SUCCESS":
            break
        elif attempt == 5:
            log_error(work_url, "重試 5 次失敗")
        else:
            time.sleep(attempt * 30)