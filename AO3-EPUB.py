import os
import re
import json
import math
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

# 設定
cookie_txt_file = os.path.join(os.path.dirname(__file__), "") # cookie 檔案名稱根據實際情況填寫
input_file = os.path.join(os.path.dirname(__file__), "抓取清單.xlsx")
output_dir = os.path.join(os.path.dirname(__file__), "抓取結果")
os.makedirs(output_dir, exist_ok=True)

# Cookie 讀取
def load_cookies_from_txt(txt_path):
    cookies = {}
    with open(txt_path, "r", encoding="utf-8") as f:
        for line in f:
            if "=" in line:
                parts = line.strip().split("=", 1)
                if len(parts) == 2:
                    name, value = parts
                    cookies[name] = value
                else:
                    print(f"⚠️ 無效的 cookie 格式：{line}")
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

def exponential_backoff(attempt):
    delay = min(30 * math.exp(attempt - 1), 300)
    print(f"🔄 等待 {int(delay)} 秒後重試...")
    time.sleep(delay)

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

# Header
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Referer": "https://archiveofourown.org/"
}

success_count = 0
fail_urls = []

# 下載函式
def attempt_download(work_url):
    try:
        time.sleep(random.uniform(1.0, 3.0))
        r = requests.get(work_url + "?view_adult=true&view_full_work=true", headers=headers, cookies=cookies, timeout=180)
        r.raise_for_status()

        soup = BeautifulSoup(r.text, "html.parser")
        title_tag = soup.select_one("h2.title")
        author_tag = soup.select_one("h3.byline a")
        title = clean_title(title_tag.text if title_tag else "untitled")
        author = author_tag.text.strip() if author_tag else "作者不明"

        epub_link = soup.find("a", string="EPUB")
        if not epub_link:
            log_error(work_url, "找不到 EPUB 連結")
            return (work_url, "FAIL")

        download_url = "https://archiveofourown.org" + epub_link["href"]
        time.sleep(random.uniform(1.0, 2.0))
        res = requests.get(download_url, headers=headers, cookies=cookies, timeout=180)
        res.raise_for_status()

        filename = f"{title}.epub" # 可依習慣變更下載檔案名稱格式
        filepath = os.path.join(output_dir, filename)
        with open(filepath, "wb") as f:
            f.write(res.content)
        print(f"✅ 已儲存：{filename}\n📁 儲存路徑：{filepath}")
        return (work_url, "SUCCESS")

    except requests.exceptions.Timeout as e:
        print(f"⏳ 請求超時：{e}")
        return (work_url, "RETRY")
    except requests.exceptions.RequestException as e:
        print(f"❌ 請求失敗：{e}")
        return (work_url, "RETRY")
    except Exception as e:
        print(f"⚠️ 其他錯誤：{e}")
        return (work_url, "RETRY")

# 同步進行最多兩篇
retry_queue = []
with ThreadPoolExecutor(max_workers=2) as executor:
    future_to_url = {executor.submit(attempt_download, url): url for url in urls}
    for future in as_completed(future_to_url):
        work_url, status = future.result()
        if status == "SUCCESS":
            success_count += 1
        elif status == "RETRY":
            retry_queue.append(work_url)
        else:
            fail_urls.append(work_url)

# 重試最多 10 次
for work_url in retry_queue:
    for attempt in range(1, 11):
        print(f"🔁 重試 ({attempt}/10)：{work_url}")
        _, result = attempt_download(work_url)
        if result == "SUCCESS":
            success_count += 1
            break
        elif attempt == 10:
            log_error(work_url, "重試 10 次失敗")
            fail_urls.append(work_url)
        else:
            exponential_backoff(attempt)

# 統計報告
print("\n📊 抓取完成報告")
print(f"✅ 成功：{success_count} 篇 / {len(urls)} 篇")
if fail_urls:
    print("❌ 失敗清單：")
    for fail in fail_urls:
        print(f" - {fail}")
