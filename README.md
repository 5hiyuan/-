## 不定時更新，更新內容見 commit

### 初次使用請先閱讀
- [檔案開啟教學](https://rainbow-argon-393.notion.site/VSC-Python-py-5204886a37dd483fb71130161ba479d3?pvs=4)
- [cookies 儲存方式](https://rainbow-argon-393.notion.site/LOFTER-cookies-1326c803ace38073b66ed19a192985d8?pvs=4)
- 資料夾名稱、檔案名稱、工作表名稱等皆可變更，但變更後須修改程式碼

### Lofter 抓取與合併

**抓取文章**
1. 登入後儲存 cookie 為 txt
2. 檔案抓取會根據 PYTHON 所在位置自動建立【抓取結果】資料夾
3. 可變更抓取資料夾名稱，但如果後續要執行合併檔案，記得要連檔案合併中的路徑也要修改
4. 執行 LOF 抓取.py

**合併檔案**
1. 因為設定是單篇各自抓取，所以會有多個檔案，如果需要合併，請在【抓取結果】中另外新建【章節抓取】
2. 把需要合併的文章放到【章節抓取】中，注意檔案命名要有規律
3. 執行 檔案合併.py

### AO3 批次下載
1. 登入後儲存 cookie 為 txt
2. 建立【抓取清單】表單，將工作表命名為 EPUB，並建立欄位 URL（為方便辨識可額外新增 TITLE）
3. URL 只需貼上：https://archiveofourown.org/works/文章ID
4. 執行 AO3-EPUB.py
