# 欄位（fields）— 報價 / 資料 / 選股 三類

> **來源**：xshelp 三組清單為主幹（`/XSHelp/lists?a=<分類碼>`，build-time 快照）。
> 報價欄位另以 grammar `variable.field`（`q_*` 與 OHLCV）名單錨定；
> 選股欄位以 `XQStrategy` 的 `GetField("中文")` 實際用例**交叉驗證**（掃出實用名單，
> 高頻者於下表標 ✅）。未收錄之冷門欄位 → 走 SKILL.md **F3 線上查證**，**不杜撰**（G1）。

---

## 共通慣例（讀本檔前先看）

1. **三類欄位的取用入口與腳本邊界**（搞錯會編譯/執行錯，最重要）：

   | 類別 | 取用方式 | 可用腳本 | xshelp 分類碼前綴 |
   |------|----------|----------|------------------|
   | **報價欄位** | `GetQuote("中文")` 或內建 `q_*` / OHLCV 變數 | **僅即時**（警示 / 自動交易） | `Q*`（`QOFTEN`…） |
   | **資料欄位** | `GetField("中文" [, "頻率"])` | **各類通用**（指標 / 函數 / 自動交易 / 警示） | `T*`（`TOFTEN`…） |
   | **選股欄位** | `GetField("中文")`（選股引擎內） | **僅選股**（`{@type:filter}`） | `F*`（`FOFTEN`…） |

   ⚠️ **選股欄位 ≠ 報價欄位**：選股欄位限選股腳本；報價欄位限即時腳本。中文名常**重疊**
   （如「收盤價」三類都有），但語意與可用情境不同——選股的「收盤價」是選股日 K 棒收盤、
   報價的「成交」才是即時最新價。依腳本類型選對入口（見 [script-types.md](script-types.md)）。

2. **OHLCV 內建變數**（最常用，grammar `variable.field`，大小寫不敏感）：
   `open`/`o`、`high`/`h`、`low`/`l`、`close`/`c`、`volume`/`v`、`OpenInterest`/`OI`、`date`、`time`。
   可 `[n]` 取前 n 根（`close[1]` = 前一根收盤）。即時腳本的逐筆細節才用 `q_*`。

3. **頻率代碼**（`GetField` 第二參數）：`D`=日、`W`=週、`M`=月、`Q`=季、`H`=半年、`Y`=年；
   分鐘以數字字串 `"1"/"5"/"60"`。省略=腳本當前頻率。

4. **欄位名是字串**：`GetField("收盤價")` 的中文要逐字相符（含括號單位，如 `每股稅後淨利(元)`、
   `成交金額(億)`、`股本(元)` vs `股本(億)`）。括號 / 單位差一字就查不到 → 對不準時走 F3。
   - **中文或英文皆可（欄位/資訊函數全家族通則）**：官方說明明載 `GetField` / `GetSymbolField` /
     `GetSymbolInfo` 等的欄位名「**中文或是英文名稱**」都接受（例：`GetSymbolInfo("交易所")` ＝
     `GetSymbolInfo("exchange")`）；`GetQuote` 英文用 `q_*`、中文用報價欄位名。詳見
     [builtin-functions.md](builtin-functions.md) FIELDFUNC 區段。本檔欄位表以中文名為主（最穩、
     官方範例慣用），英文代碼字串不確定時走 F3 查證，勿臆造。

---

## A. 報價欄位（即時，`Q*` / `q_*`）

> ⚠️ 僅警示 / 自動交易等**即時**腳本。`GetQuote("中文")` 取中文欄位；`q_*` 為 grammar 內建變數可直接寫。

### A1. 常用（`QOFTEN`，`GetQuote` 中文名）

| 欄位 | 說明 |
|------|------|
| `成交` | 最新成交價（等同 Close） |
| `成交時間` | 最新成交時間（亦可 `GetField("Time","Tick")`） |
| `單量` | 最新一筆成交量 |
| `總量(日)` | 當日累計成交量 |
| `昨量` | 昨日成交量 |
| `估計量` | 當日預估收盤量 |
| `開盤(日)` / `最高(日)` / `最低(日)` | 當日開 / 高 / 低 |
| `參考價` | 當日參考價（昨收） |
| `買進` / `賣出` | 委買最高價 / 委賣最低價 |

### A2. `q_*` 內建變數（grammar `variable.field` 全名單，即時逐筆 / 五檔 / 期權 / 財務快照）

> 直接當變數用，不需 `GetQuote`。**此名單為 2023 grammar 快照**，與 xshelp 現況若有出入以 xshelp 為準。

- **逐筆 / 日**：`q_Last` `q_Bid` `q_Ask` `q_BidAskFlag` `q_TickVolume` `q_PreTotalVolume`
  `q_PriceChangeRatio` `q_InSize` `q_OutSize` `q_RefPrice` `q_DailyOpen` `q_DailyHigh`
  `q_DailyLow` `q_DailyVolume` `q_DailyUplimit` `q_DailyDownlimit` `q_DayAmplitude`
  `q_AvgPrice` `q_AvgDealedShare` `q_MatchUnit` `q_TotalAmount` `q_VolumeRatio`
- **五檔**：`q_BestBid1..5` `q_BestAsk1..5` `q_BestBidSize1..5` `q_BestAskSize1..5`
  `q_BestBidSize` `q_BestAskSize` `q_SumBidSize` `q_SumAskSize` `q_BidAskDiff`
  `q_BidAskDiffRatio` `q_OrderRatio` `q_BidUnits` `q_AskUnits`
- **委買賣 / 漲跌家數**：`q_CulBidTicks` `q_CulAskTicks` `q_CulBuyTicks` `q_CulSellTicks`
  `q_CulMatchTicks` `q_TotalTicks` `q_UpSecurities` `q_DownSecurities` `q_UpLimitSecs`
  `q_DownLimitSecs` `q_BoughtLotsAtOpen` `q_SoldLotsAtOpen` `q_BoughtTickAtOpen` `q_SoldTickAtOpen`
- **期權 / 期貨**：`q_Basis` `q_Spread` `q_RemainDays` `q_RemainTradingDays` `q_ExpiredDate`
  `q_LastTradingDate` `q_StrikePrice` `q_IntrinsicValue` `q_TimeValue` `q_TheoreticalPrice`
  `q_Delta` `q_Gamma` `q_Theta` `q_Vega` `q_RHO` `q_Volatility` `q_VolatilityDiff`
  `q_ImpliedVolatilityonBuy` `q_ImpliedVolatilityonSell` `q_Leverage` `q_IOofMoney`
  `q_CPTradeRatio` `q_CPOIRatio` `q_ContractRatio` `q_PremiumRatio` `q_BreakEvenPoint`
  `q_Profitability` `q_TargetPrice` `q_TargetChange` `q_TargetChangeRatio`
- **財務快照**：`q_CurrentShareCapital` `q_NetValuePerShare` `q_GrossMarginRate`
  `q_OpeProfitMarginRate` `q_OpeRevenuePerShare` `q_CurrentEPS` `q_CurrentROE`
  `q_CurrentCapitalin100Million` `q_MarketCapin100Million` `q_RevenueMonth` `q_RevenueYoY`
  `q_RevenueGrowth` `q_FinancialStatementsTime` `q_MinTradingShares` `q_CashDirect`
  `q_AvgLongUnits` `q_AvgShortUnits`
- **歷史收盤**：`q_Close1Wago` `q_Close1Mago` `q_Close3Mago` `q_Close1Yago` `q_CloseOfLastYear`
- **五檔前值**：`q_PreMatch1..4`

> 其餘分類（`QPRICE`/`QVOLUME`/`QFINANCE`/`QMARKET`/`QOPTION`/`QFIVE`）的完整中文清單走 F3。

---

## B. 資料欄位（`GetField`，`T*` 代碼，各腳本通用）

> 分類：常用`TOFTEN` / 價格`TPRICE` / 量能`TVOLUME` / 籌碼`TCHIP` / 基本`TBASIC` /
> 事件 / 市場統計`TMARKET` / 期權。中文名與「選股欄位」大量重疊，但**資料欄位可帶頻率、各腳本通用**。

### B1. 常用（`TOFTEN`）

| 欄位 | 說明 |
|------|------|
| `收盤價` / `開盤價` / `最高價` / `最低價` | 該棒 OHLC（等同 OHLCV 變數，但可指定頻率） |
| `成交量` | 該棒成交量 |
| `成交金額(元)` | 成交值（元） |
| `均價` | 當日均價 |
| `參考價` | 當日參考價 |
| `漲停價` / `跌停價` | 當日漲 / 跌停價 |
| `內盤量` / `外盤量` | 內 / 外盤量 |
| `估計量` | 預估收盤量 |
| `日期` / `時間` | `YYYYMMDD` / `HHMMSS` |
| `買入價` / `賣出價` | 成交明細的買 / 賣價 |

> `GetField` 取財務 / 籌碼類資料欄位時，欄位名與「選股欄位」對應表（下節 C）相同；
> 差別只在呼叫情境（資料欄位可在指標 / 函數 / 自動交易腳本用、可帶頻率）。其餘 `T*` 子類走 F3。

---

## C. 選股欄位（選股腳本專用，`F*` 代碼，`GetField("中文")`）

> ⚠️ **僅選股腳本**（`{@type:filter}`）。分類：常用`FOFTEN` / 價格`FPRICE` / 量能`FVOLUME` /
> 籌碼`FCHIP` / 基本`FBASIC` / 財務`FFINANCE` / 事件`FEVENT`。
> **✅ = 經 `XQStrategy/<市場>的選股條件/*.xs` 的 `GetField` 實際用例交叉驗證**（高頻、可信度最高）。

### C1. 常用（`FOFTEN`）

| 欄位 | 驗證 | 說明 |
|------|:----:|------|
| `收盤價` | ✅ | K 棒收盤價（最高頻，786 例） |
| `成交量` | ✅ | K 棒成交量（564 例） |
| `開盤價` | ✅ | K 棒開盤價 |
| `最高價` / `最低價` | ✅ | K 棒高 / 低 |
| `漲跌幅` | ✅ | 期間漲跌幅 % |
| `均價` | | 當日均價 |
| `每股稅後淨利(元)` | ✅ | EPS（稅後）（244 例） |
| `股東權益報酬率` | ✅ | ROE |
| `營業毛利率` | ✅ | 毛利率 |
| `本益比` | | P/E |
| `股價淨值比` | | P/B |
| `殖利率` | | 殖利率 |
| `主力買賣超張數` | | 主力淨買賣張數 |
| `法人買賣超張數` | | 三大法人淨買賣張數 |
| `月營收` | ✅ | 當月營收 |
| `成交金額(億)` | ✅ | 成交值（億） |
| `總市值(億)` | ✅ | 市值（億） |

### C2. 價格（`FPRICE`）

`參考價`、`漲停價`、`跌停價`、`振幅`、`高低差`、`真實範圍`、`真實範圍波幅`、`波動率`、
`標準差`、`貝他值`、`月平均收益率`、`週平均收益率`、
風險指標 `Jensen`/`SHARPE`/`Treynor`（英文名，✅ 見 GetField 用例）、
產業鏈 `上游股價指標`/`下游股價指標`/`同業股價指標`、`投資建議目標價`（美股）。

### C3. 量能（`FVOLUME`）

- 基本：`成交金額(元)`/`成交金額(億)`、`成交均量`、`開盤量`/`收盤量`/`盤後量`/`零股量`/`鉅額交易量`、
  `上漲量`/`下跌量`、`內盤量`/`外盤量`/`內盤均量`/`外盤均量`/`內外盤比`、`佔大盤成交量比`/`佔全市場成交量比`。
- 大單分級（買 / 賣 × 特大 / 大 / 中 / 小，各有「量 / 金額 / 成交次數」三式）：
  `買進大單量`/`買進大單金額`/`買進大單成交次數`…、`賣出特大單量`… 以此類推。
- 委託 / 次數：`開盤委買`/`開盤委賣`、`漲停委買數量`/`跌停委賣筆數`…、`總成交次數`/`總成交筆數`。
- 新聞情緒：`新聞正向分數`/`新聞負向分數`/`新聞聲量分數`。

### C4. 籌碼（`FCHIP`）

- 法人 / 主力（持股 / 成本 / 買賣超 / 買張 / 賣張）：`外資買賣超`/`外資持股`/`外資成本`/`外資買張`/`外資賣張`、
  `投信買賣超`/`投信持股`…、`自營商買賣超`（含 `自營商自行買賣*`/`自營商避險*`）、
  `法人買賣超張數`/`法人持股`、`主力買賣超張數`/`主力成本`/`主力持股`、
  `控盤者買賣超張數`、`散戶買賣超張數`、`實戶買賣超張數`。
- 信用 / 借券：`融資餘額張數`/`融券餘額張數`/`融資使用率`/`融券使用率`/`券資比`/`資券互抵張數`、
  `借券張數`/`借券賣出張數`/`借券賣出餘額張數`/`借券餘額張數`/`還券張數`。
- 持股結構：`內部人持股`/`董監持股`/`大戶持股比例`/`散戶持股比例`/`總持股人數`/`集保張數`/`週轉率`/`籌碼鎖定率`。
- 當沖 / 庫藏：`現股當沖張數`/`當日沖銷張數`、`庫藏股預計買回張數`/`庫藏股實際買回張數`。

### C5. 基本（`FBASIC`）

`月營收`、`月營收月增率`/`月營收年增率`、`累計營收`/`累計營收年增率`、
`股本(元)`/`股本(億)`/`財報股本(億)`、`總市值(元)`/`總市值(億)`、`員工人數`、
`公司成立日期`/`公司掛牌日期`、`公司風格`/`公司類別`、`董事長`/`總經理`、
股利：`股利合計`/`現金股利`/`股票股利`/`盈餘配股`/`公積配股`、
`現金股利殖利率`/`股票股利殖利率`/`殖利率`、`現金股利佔股利比重`/`股票股利佔股利比重`、
`填息天數`/`填權天數`、`發行張數(張)`/`發行張數(萬張)`、`投資建議評級`、`新產能預計量產日期`。

### C6. 財務（`FFINANCE`，約 200+ 欄位，僅列高頻；完整清單走 F3）

- **獲利能力（高頻 ✅）**：`每股稅後淨利(元)`、`股東權益報酬率`、`營業毛利率`/`營業毛利`、
  `營業利益`/`營業利益率`、`稅前淨利`/`稅前淨利率`、`稅後淨利率`、`資產報酬率`、`每股淨值(元)`、
  `本期稅後淨利`、`稀釋後每股淨利`、`每股營業額(元)`/`每股稅前淨利(元)`/`每股營業利益(元)`。
- **現金流量（✅）**：`來自營運之現金流量`、`投資活動之現金流量`、`理財活動之現金流量`、
  `自由現金流量`/`每股自由現金流量`/`自由現金流量營收比`。
- **安全性 / 償債**：`負債比率`、`流動比率`/`速動比率`、`負債總額`/`資產總額`/`股東權益總額`、
  `流動資產`/`流動負債`/`固定資產`/`長期投資`/`無形資產`、`利息保障倍數`、`借款依存度`。
- **成長 / 週轉**：`營收成長率`、`稅後淨利成長率`/`稅前淨利成長率`、`總資產成長率`/`淨值成長率`、
  `存貨週轉率(次)`/`應收帳款週轉率(次)`/`總資產週轉率(次)`/`固定資產週轉率(次)`。
- **杜邦 / 估值**：`杜邦型ROE`/`杜邦型ROA`、`盈餘殖利率`、`市值營收比`/`企業價值`/`企業價值營收比`、
  `誠信指標`、`盈餘成長係數`。
- **因子（量化選股）**：`因子_*` 與 `因子分數_*` 系列（動能 / 流動性 / QMJ獲利 / 帳面市值比 /
  貝他值 / 特質波動度…），完整名單走 F3。

### C7. 事件（`FEVENT`）

`日期`/`最後交易日`、除權息：`除息日期`/`除權日期`/`除權息日期`/`除息值`/`除權值`/`除權息值`（含 `*年度`）、
股東會 / 法說：`股東會日期`/`法說會日期`/`下一次董監改選年`/`董監事就任日期`、
庫藏股：`庫藏股開始日期`/`庫藏股結束日期`、處置：`處置開始日期`/`處置結束日期`、
增減資：`現增繳款日期`/`現增新股上市日`/`現增比率`/`現增金額`/`現增價格`、
`減資日期`/`減資比例`/`減資新股上市日`、`新股上市日`、`最後過戶日期`、`融券最後回補日`、
可轉債：`停止轉換起始日`/`停止轉換結束日`、`股利年度`。

> ⚠️ **市場差異**：`XQStrategy` 的選股條件依市場分 `01台股 / 02陸股 / 03港股 / 04美股`。
> 部分欄位**僅特定市場有**（如 `機構持股比重`/`總流通在外股數`/`EPS預估值` 為美股；
> `因子_*` 多為台股）。生成跨市場選股時，欄位可用性對不準就走 F3 查證該市場是否支援。

---

> **待補 / 邊界（build-time，非 F3 回寫）：**
>
> - 報價 `QPRICE/QVOLUME/QFINANCE/QMARKET/QOPTION/QFIVE`、資料 `TPRICE/TVOLUME/TCHIP/TBASIC/…`
>   各子類的完整中文清單未逐一收錄（量大、與選股欄位高度重疊）；需要時 build-time 抓對應 `a=` 頁。
> - 選股 `FFINANCE` 200+ 欄位本檔僅收高頻子集；冷門財務 / 因子欄位走 SKILL.md F3（不杜撰，G1）。
