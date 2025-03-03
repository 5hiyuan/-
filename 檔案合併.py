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
    ', ': '，',
    '， ': '，',
    ':': '：',
    '!': '！',
    '?': '？',
    '...': '…',
    '。。。': '…',
    '(': '（',
    ' (': '（',
    '( ': '（',
    ')': '）',
    ' )': '）',
    ') ': '）',
    '~': '～'
}

# 函數用於替換內容中的特定字符
def replace_chars(text):
    for original, replacement in replacement_dict.items():
        text = text.replace(original, replacement)
    return text

# 自定義排序方法，根據檔案名稱中的數字部分進行排序
def custom_sort(file_name):
    match = re.search(r'\d+', file_name)
    if match:
        return int(match.group())
    else:
        return float('inf')

# 確保目標資料夾存在，如果不存在就建立它
if not os.path.exists(target_dir):
    os.makedirs(target_dir)

# 獲取原始檔案列表並按照自定義排序方法進行排序
file_list = sorted(os.listdir(source_dir), key=custom_sort)

# 開啟目標檔案
target_filename = f'《{merged_filename}》.txt'
with open(os.path.join(target_dir, target_filename), 'w', encoding='utf-8') as target_file:
    # 遍歷每個原始檔案
    for i, filename in enumerate(file_list):
        # 讀取原始檔案內容
        with open(os.path.join(source_dir, filename), 'r', encoding='utf-8') as source_file:
            content = source_file.read()
            # 檢查並替換內容中的特定字符
            content = replace_chars(content)
            # 寫入檔案內容
            target_file.write(content)
            # 在每個檔案內容之間插入三行空行
            if i < len(file_list) - 1:  # 如果不是最後一個檔案，插入分隔行
                target_file.write('\n' * 2)
                target_file.write('---')
                target_file.write('\n' * 2)

print(f"檔案已合併為：{target_filename}")
