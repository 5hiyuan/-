## 不定時更新，更新內容見 commit

### 初次使用請先閱讀
- [檔案開啟教學](https://rainbow-argon-393.notion.site/VSC-Python-py-5204886a37dd483fb71130161ba479d3?pvs=4)
- 資料夾名稱、檔案名稱、工作表名稱等皆可變更，但變更後須修改程式碼

### Lofter 抓取與合併

**抓取文章**
1. 登入 Lofter 後[儲存 cookie 為 txt](https://rainbow-argon-393.notion.site/LOFTER-cookies-1326c803ace38073b66ed19a192985d8?pvs=4)
2. 檔案抓取會根據 PYTHON 所在位置自動建立【抓取結果】資料夾
3. 可變更抓取資料夾名稱，但如果後續要執行合併檔案，記得要連檔案合併中的路徑也要修改

**合併檔案**
1. 因為設定是單篇各自抓取，所以會有多個檔案，如果需要合併，請在【抓取結果】中另外新建【章節抓取】
2. 把需要合併的文章放到【章節抓取】中，注意檔案命名要有規律
3. 執行 檔案合併.py

### AO3 批次下載
1. 安裝瀏覽器外掛 [Cookie-Editor](https://chrome.google.com/webstore/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)
2. 進入 AO3 網站（不用登入）後，點選擴充，Export As JSON
3. 在 VSC 另開新檔案儲存瀏覽器匯出的 JSON，名稱預設為【AO3cookie】
4. 建立【抓取清單】表單，將工作表命名為 EPUB，並分別設置欄位 ID、URL（為方便辨識可額外新增 TITLE）
5. 執行 AO3-EPUB.py
