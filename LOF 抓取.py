import os
import re
import requests
from bs4 import BeautifulSoup
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter
from urllib.parse import unquote

# 使用 cookies.txt 中的 Cookie 進行已登入的 Session
def load_cookies_from_file(filepath):
    session = requests.Session()
    with open(filepath, 'r') as file:
        for line in file:
            name, value = line.strip().split('=', 1)
            session.cookies.set(name, value)
    return session

# 建立已登入的 Session，使用 cookies.txt 中的 Cookie
session = load_cookies_from_file(r'') # 路徑根據實際情況填寫，資料夾路徑+檔案名稱.txt，例如 'd:\cookies.txt'

# 起始URL和抓取模式設定
start_url = "" # 要抓的網址放這裡
direction = 'prev'  # 抓較新的文章
# direction = 'next'  # 抓較早的文章
fetch_single_article = False  # True 只抓取單篇文章；False 抓取多篇

def fetch_article_content(soup, url):
    title_tag = soup.find('h2')
    title = title_tag.text.strip() if title_tag and title_tag.text.strip() else url.split('/')[-1]  # 沒標題則用 URL 作為標題

    content = ""
    h2_tag = soup.find('h2')
    if not h2_tag:
        print("找不到標題 <h2>，無法確定文章內容區域")
        return title, content

    paragraphs = []
    for elem in h2_tag.find_all_next(['p', 'br']):  # 抓取 <h2> 之後的所有 <p> 和 <br>
        if elem.name == 'p':  # 處理 <p> 段落
            paragraph_text = elem.get_text(separator="")  # **確保 <strong> 不會產生額外換行**
            paragraph_text = paragraph_text.replace("\n", " ")  # 避免過多換行
            if paragraph_text.strip():  # 過濾空白行
                paragraphs.append(paragraph_text)
        elif elem.name == 'br':  # 處理 <br>
            if paragraphs and paragraphs[-1].strip():  # 確保 <br> 讓上一個段落結束
                paragraphs[-1] += "\n\n"

    content = "\n\n".join(paragraphs).rstrip("\n")  # 確保結尾沒有多餘換行

    return title, content

# 清理標題中的特殊字符和括號
def clean_title(title):
    # 使用字典簡化特殊字符替換邏輯
    char_map = {
        ':': '：', '?': '？', '!': '！', '/': '／', '|': '｜', '\\': '＼', '*': '＊',
        '<': '＜', '>': '＞', '(': '（', ')': '）', '~': '～'
    }
    for key, value in char_map.items():
        title = title.replace(key, value)
    return title

# 清理和替換內文中的HTML空白字符實體、Unicode形式及標點符號
def clean_content(content):
    content = content.replace('&nbsp;', ' ').replace('&emsp;', ' ').replace('&ensp;', ' ')
    content = content.replace('\xa0', ' ').replace('\u2003', ' ').replace('\u2002', ' ')
    # 保留原本的分行模式
    content = content.replace('<br>', '\n').replace('<br/>', '\n').replace('<br />', '\n')
    content = '\n'.join([line for line in content.split('\n') if line.strip() != ''])
    
    punctuations = {',': '，', ', ': '，', '， ': '，', ':': '：', '!': '！', '?': '？', '...': '…', '。。。': '…', '(': '（', ' (': '（', '( ': '（', ')': '）', ' )': '）', ') ': '）', '~': '～'}
    for key, value in punctuations.items():
        content = content.replace(key, value)
    return content

# 儲存文章和圖片
def save_article(title, url, content, image_links):
    folder = "抓取結果"
    base_path = os.path.dirname(__file__)
    save_path = os.path.join(base_path, folder)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    file_path = os.path.join(save_path, f"{clean_title(title)}.txt")
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(f"{url}\n{title}\n\n\n{content}")  # 確保標題和內文之間有兩行空行，如果不想抓原始文章網址就把最前面的 {url}\ 刪掉
    print(f"已儲存為：{file_path}")

    for index, image_url in enumerate(image_links):
        image_name = f"{clean_title(title)}__{index + 1}.jpg"
        image_path = os.path.join(save_path, image_name)
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(image_path, 'wb') as f:
                f.write(response.content)
            print(f"圖片已保存為：{image_path}")

# 獲取文章中的圖片連結
def fetch_images(soup):
    images = set()  # 用 set() 避免重複抓取相同圖片
    
    image_containers = soup.find_all(['div'], class_=['content', 'text', 'pic'])  # 確保包含 <div class="pic">
    
    for container in image_containers:
        img_tags = container.find_all('img')  # 找所有 <img>
        a_tags = container.find_all('a', class_='imgclasstag')  # 找 <a> 標籤的 bigimgsrc

        for a_tag in a_tags:  # 優先抓取 <a> 內的 bigimgsrc（高清圖）
            img_url = a_tag.get('bigimgsrc')
            if img_url:
                clean_img_url = unquote(img_url.split('?')[0])
                images.add(clean_img_url)

        for img in img_tags:  # 如果 <a> 沒有 bigimgsrc，才抓 <img> 的 src
            img_url = img.get('src')
            if img_url:
                clean_img_url = unquote(img_url.split('?')[0])
                images.add(clean_img_url)

    images = list(images)  # 轉回列表，確保順序不亂

    print(f"✅ 抓取到 {len(images)} 張圖片:")
    for img in images:
        print(img)

    return images

# 獲取文章內容和圖片
def fetch_article(url, fetched_urls, session):
    if url in fetched_urls:
        print(f"跳過重複文章：{url}")
        return None, fetched_urls

    try:
        response = session.get(url, timeout=60)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 獲取標題與內容
            title, content = fetch_article_content(soup, url)

            image_links = fetch_images(soup)
            save_article(title, url, content, image_links)
            fetched_urls.add(url)

            if fetch_single_article:
                return None, fetched_urls

            link_element = soup.find('a', id='__next_permalink__') if direction == 'next' else soup.find('a', id='__prev_permalink__')
            new_url = link_element['href'] if link_element else None
            return new_url, fetched_urls
    except requests.exceptions.Timeout as e:
        print(f"獲取 {url} 時出錯：連線逾時。 {e}")
        return None, fetched_urls
    except requests.exceptions.RequestException as e:
        print(f"獲取 {url} 時出錯： {e}")
        return None, fetched_urls
    except Exception as e:
        print(f"發生意外錯誤： {e}")
        return None, fetched_urls

    return None, fetched_urls

# 設置HTTP請求的重試會話
def requests_retry_session(retries=3, backoff_factor=0.3, status_forcelist=(500, 502, 504), session=None):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor,
        status_forcelist=status_forcelist,
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

# 主函數
def main():
    fetched_urls = set()
    url = start_url

    while url:
        new_url, fetched_urls = fetch_article(url, fetched_urls, session)
        if not new_url:
            if fetch_single_article:
                print("【提醒】已抓取指定文章。")
            elif direction == 'next':
                print("【提醒】抓取完畢，沒有更早的文章了。")
            else:
                print("【提醒】抓取完畢，沒有更新的文章了。")
            break
        url = new_url

if __name__ == "__main__":
    main()
