import os
import re

# 指定原始檔案路徑和目標檔案路徑
source_dir = r'D:\Python\抓取結果\章節抓取' # 資料路徑如有修改，建議改 \抓取結果 前墜即可
target_dir = r'D:\Python\抓取結果' # 同上，可更改路徑，但不建議改掉 \抓取結果

# 合併後的檔案名稱
merged_filename = "" # 自行設定合併後的檔案名稱是什麼，會根據輸入的內容變成《檔案名稱》

# 替換清單
replacement_dict = {
    ',': '，',
    ':': '：',
    '!': '！',
    '?': '？',
    '...': '…',
    '。。。': '…',
    '(': '（',
    ')': '）',
    '~': '～'
}

# 匹配特定隱藏空格（1-5）
hidden_spaces_pattern = re.compile(r'[\u00A0\u1680\u2000-\u200A\u202F\u205F]')

# 處理標點符號前後的空格（**只要有就刪除，不是「前後都有才刪」**）
punctuation_pattern = re.compile(r'\s*([,:!?\.\(\)~])\s*')

# 清理文本內容
def replace_chars(text):
    # 先替換標點符號
    for original, replacement in replacement_dict.items():
        text = text.replace(original, replacement)
    
    # **刪除標點符號前或後的空格**
    text = punctuation_pattern.sub(lambda m: m.group(1), text)

    # **刪除特定隱藏空格**
    text = hidden_spaces_pattern.sub('', text)

    return text.strip()  # 去除開頭與結尾的空白

# 自定義排序方法，根據檔案名稱中的數字部分進行排序
def custom_sort(file_name):
    match = re.search(r'\d+', file_name)
    return int(match.group()) if match else float('inf')

# 確保目標資料夾存在
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

# 獲取原始檔案列表並排序
file_list = sorted(os.listdir(source_dir), key=custom_sort)

# 開啟目標檔案
target_filename = f'《{merged_filename}》.txt'
with open(os.path.join(target_dir, target_filename), 'w', encoding='utf-8') as target_file:
    for i, filename in enumerate(file_list):
        with open(os.path.join(source_dir, filename), 'r', encoding='utf-8') as source_file:
            content = source_file.read()
            content = replace_chars(content)
            target_file.write(content)
            if i < len(file_list) - 1:
                target_file.write('\n' * 2)
                target_file.write('---')
                target_file.write('\n' * 2)

print(f"檔案已合併為：{target_filename}")
