# xshelp 本機鏡像（A）＋ references 名稱索引（B）設計

> 狀態：規格，供 [`../plans/2026-09-24-xshelp-mirror-and-index.md`](../plans/2026-09-24-xshelp-mirror-and-index.md) 引用。
> 起因：使用者提議「把 xshelp 整個網頁下載放進 references」。評估後不採全文散佈（版權、安裝器、過期三個理由），改做 A＋B。

## 已查證的事實（2026-09-24）

- **一個請求拿到整站**：`GET https://xshelp.xq.com.tw/XSHelp/rest?a=`（空字串）回傳 JSON 陣列 1621 筆，`id` 全部不重複。先前以 a–z 各查一次的窮舉只得 1593 筆，漏 28 筆；空字串仍是唯一可靠的全量查法（列舉法漏筆，且無法窮舉中文字首）。中文名稱查詢本身可行，但 `a=<中文名>` 必須先 URL-encode，未編碼直接送出中文字會回傳 0 筆——這是編碼問題，不是該名稱不存在；同一名稱編碼後可能命中多筆（分屬不同分組），須依分組代碼比對再取用。
- **每筆欄位**：`id`、`name`、`ename`、`abbrev`、`Description`（分組代碼，如 `GENERALFUNC`、`QPRICE`）、`CategoryName`（分組中文名）、`father`（大類中文名）、`categoryid`、`desc`（官方語法／多載）、`fulldesc`（完整說明＋範例）。
- **規模**：10 個大類（選股欄位 492、資料欄位 363、系統函數 267、內建函數 220、報價欄位 131、宣告 51、屬性欄位 38、流程控制 37、忽略字 14、常數 8），54 個分組；全文約 700 KB；111 筆 `desc`／`fulldesc` 皆空。
- **條目頁內文由 JS 渲染**：`?HelpName=<名稱>&group=<代碼>` 的原始 HTML 只剩 `<meta property="og:description">` 有文字。`desc`／`fulldesc` 為空的條目，只能從 og:description 取得摘要。
- **欄位清單有來源**：`fields.md` 待補的 `QPRICE`／`QVOLUME`／`TPRICE`／`FFINANCE` 等完整清單，就是索引裡對應分組的條目名稱（v0.6.0 判定「來源待定位」為誤判）。

## 目標

- **A：本機全站鏡像，不進 repo。** 一支 stdlib 腳本把 `rest?a=` 的全量 JSON 存到 `sources/xshelp/`（已被 `.gitignore` 的 `sources/` 涵蓋），並為全文為空的條目補抓 og:description。用途：蒸餾、驗證、lint 名單重生時離線全文搜尋。
- **B：references 名稱索引。** 由鏡像產生 `skills/xs/references/xshelp-index.md`：依大類→分組列出全部條目名稱，只含名稱、分組代碼與中文名，不含任何說明內容；網址用一個樣板描述。用途：agent 離線確認名稱**存在與否**（強化 G1）、精準組出 F3 查詢網址。

## 設計決定

- **不散佈官方說明內容**：索引只放名稱、分組代碼、分組中文名與網址樣板。名稱是事實性指標，與 SPEC Open Q5 不散佈官方原始檔的原則一致。
- **索引大小**：名稱依分組以 `·` 串接，約 35 KB。檔首寫明「用搜尋找名稱，不要整份讀入」。
- **產生可重現**：`python -B scripts/xshelp_mirror.py fetch` 抓鏡像；`python -B scripts/xshelp_mirror.py index` 由鏡像產生索引檔（決定性排序，相同鏡像產生逐位元相同的檔案）。維持 SPEC「不建立自動全量同步」：手動重生、隨版本更新。
- **F3 改走索引 API**：SKILL.md 的 F3 改成先查 `xshelp-index.md` 確認名稱與分組，再用 `rest?a=<名稱>` 取 `desc`／`fulldesc`；條目頁只作為給使用者的連結。
- **lint 名單同步**：索引中大類為「內建函數」「系統函數」且名稱為 ASCII 識別字者，必須都在 `xs_lint.KNOWN_TOKENS`（中文名函數無法以 `識別字(` 比對，排除）。以測試守住。
- **reference 份數**：由 10 份變 11 份，頁面與文件中的「10 份參考文件」同步。

## 不做

- 不把鏡像全文放進 repo 或 references。
- 不做排程自動同步。
- 不改 `fields.md` 既有的欄位解說，只把「完整清單走 F3」改成指向索引對應分組。
