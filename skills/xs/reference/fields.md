# 欄位（fields）— 報價 / 資料 / 選股 三類

> 🚧 骨架佔位 — 待蒸餾。
> **來源**：xshelp 三組清單為主幹；報價欄位另有 grammar `variable.field`（q_*）名單；
> 選股欄位以 Strategy `GetField("中文")` 實際用例交叉驗證（掃出 498+ 種）。

## 待蒸餾內容

### 報價欄位（即時，`q_*` 與 OHLCV）
- [ ] 常用/價格/量能/財務/市場統計/期權/五檔統計
- [ ] grammar 已列：`open/high/low/close/volume`、`q_Last/q_Bid/q_Ask`、`q_BestBid1..5`、`q_Delta/q_Gamma`…

### 資料欄位（`GetField`，xshelp `T*` 代碼）
- [ ] 常用`TOFTEN` / 價格`TPRICE` / 量能`TVOLUME` / 籌碼`TCHIP` / 基本`TBASIC` / 事件 / 市場統計`TMARKET` / 期權
- [ ] 基本(`TBASIC`)實證：月營收、本益比、股本(元/億)、殖利率、總市值(元)…

### 選股欄位（選股腳本專用，xshelp `F*` 代碼）
- [ ] 常用`FOFTEN` / 價格`FPRICE` / 量能`FVOLUME` / 籌碼`FCHIP` / 基本`FBASIC` / 財務`FFINANCE` / 事件`FEVENT`
- [ ] Strategy 高頻用例：收盤價、成交量、每股稅後淨利(元)、漲跌幅、股東權益報酬率、營業毛利率…

> ⚠️ 三類欄位不可混用：選股欄位限選股腳本，報價欄位限即時腳本（見 script-types.md 邊界）。
