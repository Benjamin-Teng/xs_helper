# 內建函數（builtin functions / bif）

> **來源**：⚠️ bif 為 XS **引擎原語**，`XScript_Preset` **無**原始碼 → 簽名**唯一權威是 xshelp**
> （`xshelp.xq.com.tw/XSHelp/lists?a=<分類碼>`，build-time 抓取的快照）。grammar 的
> `keyword.bif` 只佐證名字、且為 2023 快照已落後，以本檔（xshelp）清單為準。
> 此處未收錄、或冷門無把握者 → 走 SKILL.md 的 **F3 線上查證**，**不杜撰**（G1）。
> 收錄 9 分類，xshelp 分類碼：`GENERALFUNC` / `TIMEFUNC` / `DATEFUNC` / `STRINGFUNC` /
> `NUMBERFUNC` / `FIELDFUNC` / `ARRAYFUNC` / `TRANSACTIONFUNC` / `SDTFUNC`。

---

## 共通慣例（讀本檔前先看）

1. **bif vs sysfnc 的差異**：bif 是**引擎內建原語**（編譯器直接認得），sysfnc 是 Preset 用 XS
   寫的函數庫。bif **大小寫不敏感**（`AbsValue` = `absvalue`），多數**直接回傳值**
   （`x = AbsValue(y);`），少數為**指令式**無回傳（如 `Buy(1);`、`Print(...);`、`Plot(...);`）。
2. **簽名標記**：本檔簽名沿用 xshelp 原始參數中文名（如 `AddSpread(基礎價格, 檔位)`）。
   `[...]` 表選填參數；`a | b` 表多載（同名不同參數組）。回傳型別在「說明」內描述。
   - **版本分水嶺以 `vX.XX` 標注**：凡某特性自特定 XQ 版本起才支援者（如 `CallFunction` 中文函數名自
     `v6.20` 起），在該條目標 `⚠️ 版本相關` 與版本號；生成/回答涉及此類特性時，提醒使用者確認 XQ 版本，
     舊版可能不支援。
3. **欄位 / 報價 / 交易函數的腳本邊界**（關鍵，違反會編譯/執行錯）：
   - `GetField` 系列 → 任何腳本皆可（含選股），讀**資料欄位**（見 [fields.md](fields.md)）。
   - `GetQuote` / `GetSymbolInfo` → **僅警示 / 自動交易**等即時腳本可用，讀**報價欄位**。
   - 交易函數（`Buy/Sell/Short/Cover/SetPosition/Market/Filled*`…）→ **僅自動交易**
     （`{@type:autotrade}`）可用；選股 / 指標 / 函數腳本用了會出錯（見 [script-types.md](script-types.md)）。
4. **`Plot` 系列**：繪圖輸出用，主要在**指標**（`{@type:indicator}`）腳本；`OutputField` 才是
   **選股**腳本的輸出欄位設定。兩者別混。
5. 日期一律 `YYYYMMDD` 8 位整數、時間一律 `HHMMSS`（含毫秒版 `HHMMSS.fff`）；非字串。

---

## 1. 一般函數（`GENERALFUNC`）

> 執行環境 / 繪圖輸出 / 商品資訊 / Bar 控制。多數只在特定腳本類型有意義（見每條說明）。

| 名稱 | 簽名 | 說明 |
|------|------|------|
| `CurrentBar` | `(): Num` | 目前運算到第幾根 K 棒（從 1 起算） |
| `GetTotalBar` | `(): Num` | 已處理的資料總棒數 |
| `MaxBarsBack` | `(): Num` | 目前設定的最大回看棒數 |
| `SetBackBar` / `SetBarBack` | `(count [, freq])` | 設定最大回看（參考）棒數；可指定頻率 |
| `GetBackBar` / `GetBarBack` | `(): Num` | 取得目前總參考棒數 |
| `SetTotalBar` | `(count)` | 設定讀取的資料範圍棒數 |
| `GetBarOffset` | `(YYYYMMDD [, HHMMSS]): Num` | 由日期(時間)取相對棒位移 |
| `ExecOffset` | `(): Num` | 本次執行的位移棒數 |
| `GetFirstBarDate` | `(): Num` | 第一根資料棒的日期 |
| `SetFirstBarDate` | `(date)` | 設定起始資料日期 |
| `GetFieldStartOffset` | `(): Num` | 欄位起始位移；無則回 -1 |
| `GetSymbolFieldStartOffset` | `("ID", "欄位名稱" [, "頻率"]): Num` | `GetFieldStartOffset` 的延伸，可指定商品；回傳該商品該欄位最新一筆與第一筆資料間的筆數，無此欄位或超出範圍回 -1；僅支援選股腳本（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=GetSymbolFieldStartOffset&group=GENERALFUNC)） |
| `IsFirstCall` | `(): Bool` | 是否為事件首次計算 |
| `IsLastBar` | `(): Bool` | 目前是否為最新一根棒 |
| `IsSessionFirstBar` | `(): Bool` | 是否為交易盤節的第一根棒 |
| `IsSessionLastBar` | `(): Bool` | 是否為交易盤節的最後一根棒 |
| `BarAdjusted` | `(): Bool` | 目前棒是否使用還原頻率 |
| `BarFreq` | `(): Str` | 傳回執行腳本的資料頻率單位 |
| `BarInterval` | `(): Num` | 分鐘頻率下的分鐘間隔 |
| `SetBarFreq` | `(freq1, freq2, ...)` | 宣告腳本支援的頻率 |
| `SetBarMode` | `(n)` | 設定函數計算（洗價）方式 |
| `DataAlign` | `(0 \| 1)` | 設定資料對齊方式 |
| `SetAlign` | `(category, method)` | 設定指定類別的資料對齊 |
| `SetRemoveOutlier` | `("zscore" \| "IQR", value:=range)` | 排除離群值 |
| `CurrentBar`／`GetTotalBar`… | — | （上列已含；Bar 控制族整組） |
| `Symbol` 相關 → 見「欄位函數」 | — | `Symbol`/`SymbolName` 歸 FIELDFUNC |
| `SymbolExchange` | `(): Str` | 目前商品的交易所代碼 |
| `SymbolType` | `(): Num` | 目前商品的型態 |
| `GetSymbolGroup` | `([商品,] "清單類型")` | 取相關商品清單；清單類型用**中文名**（如 `"成分股"`/`"權證"`），未載英文 |
| `GroupSize` | `(group): Num` | 指定族群的商品數 |
| `GetInfo` | `(infoName)` | 取執行環境資訊；`infoName` 為**固定英文關鍵字**（`"Instance"`/`"IsRealTime"`/`"IsTimerMode"`/`"FilterMode"`/`"TradeMode"`/`"AT_EnableTrade"`/`"AT_BID"`/`"AT_AccType"`/`"AT_AID"`）——非中英雙語、不可用中文 |
| `GetTBMode` / `SetTBMode` | `(...)` | 取得 / 設定自訂指標繪圖模式 |
| `CallFunction` | `("函數名", param1, param2, ...)` | 以名稱動態呼叫函數；`callfunction("average",c,5)` ≡ `average(c,5)`。⚠️ **版本相關**：自 **v6.20** 起函數可用**中文名**，而中文名函數被其他腳本呼叫時**必須**透過 `CallFunction`（直接寫中文函數名呼叫不行） |
| `Print` | `(values...) \| (File(path), values...)` | 輸出值（除錯 / log） |
| `File` | `(path)` | 指定 `Print` 輸出目的地：`Print(File(path), ...)` |
| `RaiseRunTimeError` | `(errorMessage)` | 中斷執行並拋出錯誤訊息 |
| `Playsound` | `(file)` | 播放指定音效檔（警示用） |
| **繪圖（指標腳本）** | | |
| `Plot` | `Plot(輸出序號，指標數值)` \| `Plot(輸出序號，指標數值，繪圖序列名稱)` \| `Plot(輸出序號，指標數值，繪圖序列名稱，checkbox:=1)` \| 序號版 `Plot1(指標數值)` \| `Plot1(指標數值，繪圖序列名稱)` \| `Plot1(指標數值，繪圖序列名稱，checkbox:=1)` | 建立繪圖序列（逐字依 [xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=Plot&group=GENERALFUNC) 列出的重載）；`checkbox:=` 是**命名參數**，放在名稱之後，1＝預設繪出、0＝預設不繪（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=checkbox&group=DECLARATION)）。官方範例庫另見 `axis:=`、`ScaleLabel:=`、`ScaleDecimal:=` 等命名參數，語意見 language.md §9.4 |
| `PlotFill` | `(order, vFrom, vTo [, name])` | 區間填色 |
| `PlotK` | `(order, open, high, low, close [, name])` | 畫 K 棒 |
| `PlotLine` | `(order, x1, y1, x2, y2 [, name])` | 畫趨勢線 |
| `NoPlot` | `(seriesNumber)` | 清除該序列繪圖值 |
| `SetPlotLabel` | `(order, name)` | 設定繪圖序列名稱 |
| **選股輸出 / 輸入命名** | | |
| `OutputField` | `OutputField(輸出序號, 數值)` \| `OutputField(輸出序號, 數值, 小數位數)` \| `OutputField(輸出序號, 數值, 小數位數, 輸出欄位名稱)` \| 序號版 `OutputField1(數值)` \| `OutputField1(數值, 小數位數)` \| `OutputField1(數值, 小數位數, 輸出欄位名稱)` | 設定**選股**腳本輸出欄位（逐字依 [xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=outputfield&group=GENERALFUNC) 列出的重載）；還可另外加命名參數 `order:=`（`-1` 由小到大、`1` 由大到小，排序該欄輸出數值），見下方說明與 [order 條目](https://xshelp.xq.com.tw/XSHelp/?HelpName=order&group=DECLARATION) |
| `SetInputName` | `(order, name)` | 設定 input 參數顯示名 |
| `SetOutputName` | `(order, title)` | 設定輸出欄位標題 |

**`Plot` 的兩個關鍵事實（逐字依 xshelp `Plot` 條目 fulldesc）**：

- 每個指標腳本**最多可以產生 999 個繪圖數列**，用時在 `Plot` 之後加上序號，例如 `Plot1`、`Plot2`，
  一路到 `Plot999`。
- **`Plot1` 到 `Plot99` 除了可以是一個函數之外，也可以在腳本內被當成數列來引用**（xshelp 原文：
  「Plot1到Plot99除了可以是一個函數之外，也可以在腳本內被當成數列來引用」）。xshelp 的 `Plot`
  條目把 `Plot(輸出序號, …)` 形式與序號版 `Plot1(…)`／`Plot2(…)`／… 列為同一個 `Plot` 條目下的
  重載，寫法等價；但**當數列讀的能力明確只到 `Plot1`～`Plot99`**——呼叫 `PlotN(值)`（N 在
  1 到 99 之間）建立第 N 條繪圖數列後，才可以直接把 `PlotN` 當成一個變數/數列讀，不必再查一次值。
  `Plot100` 到 `Plot999` 只在「最多可以產生 999 個繪圖數列」這句話裡被列為合法的繪圖呼叫，
  xshelp 並未提到它們也能像 `Plot1`～`Plot99` 那樣被當成數列讀，此處不作延伸。

xshelp `範例#2`（逐字）：

```xs
Plot1(Average(Close, 5));
Plot2(Close, "收盤價");
Value1 = Plot2 - Plot1;
Plot3(Value1, "差值");
```

xshelp 原文對這段的說明：「在範例#2 內Value1的數值是繪圖數列2(Plot2)與繪圖數列1(Plot1)的相減值，
然後把這個差值畫在Plot3上面。」

**`OutputField` 的 `order:=` 範例與上面簽名的位置定義有落差（照抄兩個來源，不調和）**：
xshelp `order` 條目給的範例是 `outputfield1(value1,"5日均量",order:=-1);`。按上面
`OutputField1(數值, 小數位數, 輸出欄位名稱)` 的簽名，第 2 個位置參數應該是「小數位數」（數字），
但這個範例把字串 `"5日均量"`（欄位名稱）放在第 2 個位置、後面才接命名參數 `order:=-1`——
也就是說這個範例把「小數位數」整個省略、直接讓字串補進原本該是小數位數的位置。xshelp
兩個條目（`outputfield` 與 `order`）都沒有解釋這個重載是怎麼決議的（例如是否按型別而非位置比對）。
這裡**只逐字記錄兩段來源的原文**，不自行推測 XS 引擎的參數比對規則。

---

## 2. 時間函數（`TIMEFUNC`）

> 時間值為 `HHMMSS` 整數（毫秒版 `HHMMSS.fff`）。

| 名稱 | 簽名 | 說明 |
|------|------|------|
| `CurrentTime` | `(): Num` | 腳本執行時間（歷史=當時 / 即時=當下），`HHMMSS` |
| `CurrentTimeMS` | `(): Num` | 同上，含毫秒 `HHMMSS.fff` |
| `Hour` | `(time): Num` | 取時 (0–23) |
| `Minute` | `(time): Num` | 取分 (0–59) |
| `Second` | `(time): Num` | 取秒 (0–59) |
| `MilliSecond` | `(time): Num` | 取毫秒 (0–999) |
| `TimeValue` | `(time, field)` | 取時間某欄位（`H`/`M`/`S`/`MS`） |
| `EncodeTime` | `(hour, minute, second [, ms])` | 由時分秒(毫秒)組成時間值 |
| `TimeAdd` | `(time, unit, increment)` | 時間加減（`unit` = `H`/`M`/`S`/`MS`） |
| `TimeDiff` | `(time1, time2, unit)` | 兩時間差（指定單位） |
| `TimeToString` | `(time): Str` | 轉 `"HH:MM:SS"`（或含毫秒）字串 |
| `StringToTime` | `(str): Num` | `"HH:MM:SS[.fff]"` 字串轉時間值 |
| `FormatTime` | `(format, time): Str` | 依格式字串格式化時間 |

---

## 3. 日期函數（`DATEFUNC`）

> 日期值為 `YYYYMMDD` 8 位整數。

| 名稱 | 簽名 | 說明 |
|------|------|------|
| `CurrentDate` | `(): Num` | 腳本執行日期（歷史=當時 / 即時=當日），`YYYYMMDD` |
| `Year` | `(date): Num` | 取年 |
| `Month` | `(date): Num` | 取月 (1–12) |
| `DayOfMonth` | `(date): Num` | 取日 (1–31) |
| `DayOfWeek` | `(date): Num` | 星期幾（0=日 … 6=六） |
| `WeekOfMonth` | `(date): Num` | 當月第幾週 (1–6) |
| `WeekOfYear` | `(date): Num` | 當年第幾週 (1–53) |
| `DateValue` | `(date, field)` | 取日期某欄位（年/月/日/週幾/月內週/年內週） |
| `EncodeDate` | `(year, month, day): Num` | 由年月日組成日期值 |
| `DateAdd` | `(date, unit, value): Num` | 日期加減（`unit` = `Y`/`M`/`D`） |
| `DateDiff` | `(date1, date2): Num` | 兩日期相差天數（前減後） |
| `DateToString` | `(date): Str` | 轉 `"YYYY/MM/DD"` 字串 |
| `StringToDate` | `(str): Num` | `"YYYY/MM/DD"` 字串轉 `YYYYMMDD` |
| `FormatDate` | `(format, date): Str` | 依格式字串格式化日期 |
| `DateToJulian` | `(date): Num` | `YYYYMMDD` 轉 Julian |
| `JulianToDate` | `(julian): Num` | Julian 轉 `YYYYMMDD` |

---

## 4. 字串函數（`STRINGFUNC`）

| 名稱 | 簽名 | 說明 |
|------|------|------|
| `StrLen` | `(str): Num` | 字串字元數 |
| `LeftStr` | `(str, len): Str` | 取最左 `len` 字元 |
| `RightStr` | `(str, len): Str` | 取最右 `len` 字元 |
| `MidStr` | `(str, pos, len): Str` | 由 `pos` 取 `len` 長子字串 |
| `InStr` | `(src, find) \| (s1, s2, startPos): Num` | 子字串位置（找不到回 0） |
| `StrStartWith` | `(s1, s2, mode): Bool` | s1 是否以 s2 開頭 |
| `StrEndWith` | `(s1, s2, mode): Bool` | s1 是否以 s2 結尾 |
| `StrCompare` | `(s1, s2, ignoreCase): Num` | 比較兩字串是否相等（可不分大小寫） |
| `StrSplit` | `(str, delim, outArray): Num` | 依分隔字元切割到輸出陣列 |
| `StrTrim` | `(str, option): Str` | 去頭尾空白 |
| `UpperStr` | `(str): Str` | 英文字母轉大寫 |
| `LowerStr` | `(str): Str` | 英文字母轉小寫 |
| `Text` | `(p1, p2, ...): Str` | 串接多個參數成字串 |
| `NumToStr` | `(num, decimals): Str` | 數值轉字串（指定小數位） |
| `StrToNum` | `(str): Num` | 字串轉數值 |

---

## 5. 數學函數（`NUMBERFUNC`）

| 名稱 | 簽名 | 說明 |
|------|------|------|
| `AbsValue` | `(x): Num` | 絕對值 |
| `Sign` | `(x): Num` | 取正負號（1 / -1 / 0） |
| `Neg` | `(x): Num` | 轉為負的絕對值 |
| `Pos` | `(x): Num` | 轉為正值 |
| `Round` | `(x, decimals): Num` | 四捨五入到指定小數位 |
| `Ceiling` | `(x): Num` | 無條件進位 |
| `Floor` | `(x): Num` | 無條件捨去 |
| `IntPortion` | `(x): Num` | 取整數部分 |
| `FracPortion` | `(x): Num` | 取小數部分 |
| `Mod` | `(dividend, divisor): Num` | 取餘數 |
| `Power` | `(base, exp): Num` | 次方 |
| `Square` | `(x): Num` | 平方 |
| `SquareRoot` | `(x): Num` | 平方根（x > 0） |
| `ExpValue` | `(x): Num` | e^x |
| `Log` | `(x): Num` | 自然對數（x > 0） |
| `Factorial` | `(n): Num` | 階乘 |
| `Combination` | `(M, N): Num` | 組合 C(M,N) |
| `Permutation` | `(M, N): Num` | 排列 P(M,N) |
| `Random` | `(max): Num` | 0 ~ max 間亂數 |
| `SumList` | `(v1, v2, ...): Num` | 多值加總 |
| `AvgList` | `(v1, v2, ...): Num` | 多值平均 |
| `MaxList` | `(v1, v2, ...): Num` | 多值最大 |
| `MinList` | `(v1, v2, ...): Num` | 多值最小 |
| `MaxList2` | `(v1, v2, ...): Num` | 多值第二大 |
| `MinList2` | `(v1, v2, ...): Num` | 多值第二小 |
| `NthMaxList` | `(rank, v1, ...): Num` | 多值第 N 大 |
| `NthMinList` | `(rank, v1, ...): Num` | 多值第 N 小 |
| `Sin`/`Sine` | `(angle): Num` | 正弦 |
| `Cos`/`Cosine` | `(angle): Num` | 餘弦 |
| `Tan`/`Tangent` | `(angle): Num` | 正切 |
| `CoTangent` | `(angle): Num` | 餘切 |
| `ArcSine` | `(x): Num` | 反正弦（\|x\| < 1） |
| `ArcCosine` | `(x): Num` | 反餘弦（\|x\| < 1） |
| `ArcTangent` | `(x): Num` | 反正切 |

> ⚠️ 三角函數有 `Sin/Sine`、`Cos/Cosine`、`Tan/Tangent` 兩種拼法皆可（同義）。

---

## 6. 欄位函數（`FIELDFUNC`）

> 讀「資料欄位 / 報價欄位 / 商品資訊」的入口。⚠️ `GetQuote` / `GetSymbolInfo` 限即時腳本
> （警示 / 自動交易），`GetField` 系列各腳本通用。欄位中文名清單見 [fields.md](fields.md)。
>
> **欄位名中英文皆可（全家族通則）**：官方說明明載 `GetField`、`GetSymbolField`、`GetSymbolInfo`
> 的欄位/資訊名「**中文或是英文名稱**」都接受（例：`GetSymbolInfo("交易所")` ＝ `GetSymbolInfo("exchange")`；
> `GetQuote` 英文用 `q_*` 名、中文用報價欄位名）。`*Date` / `Check*` / `IsSupport*` 變體官方註明
> 「參數與 `GetField` 相同」，故一併適用。本檔欄位表以中文名為主（最穩、官方範例慣用）；
> 英文代碼字串不確定時走 F3 查證，勿臆造。

| 名稱 | 簽名 | 說明 |
|------|------|------|
| `GetField` | `("欄位" [, "頻率" [, 還原]])` | 讀**資料欄位**；可指定頻率（`D`/`W`/`M`/`Q`/`H`/`Y`/分鐘字串）與還原 |
| `GetFieldDate` | `("欄位" [, "頻率"]): Num` | 取該欄位最新一期的日期 |
| `GetFieldPublishDate` | `("欄位" [, "頻率"]): Num` | 取該欄位在 XQ 系統的資料更新日 |
| `GetSymbolField` | `(symbolID, "欄位" [, "頻率"])` | 讀**指定商品**的資料欄位 |
| `GetSymbolFieldDate` | `(symbolID, "欄位" [, "頻率"]): Num` | 指定商品欄位最新資料日 |
| `GetSymbolFieldTime` | `(symbolID, "欄位" [, "頻率"]): Num` | 讀系統內指定商品欄位的資料時間，格式 `HHmmss`（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=GetSymbolFieldTime&group=FIELDFUNC)） |
| `GetfieldFiscalQ` | `("欄位名稱" [, "頻率"]): Num` | 讀取系統內欄位的財務季別（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=GetfieldFiscalQ&group=FIELDFUNC)） |
| `GetfieldFiscalY` | `("欄位名稱" [, "頻率"]): Num` | 讀取系統內欄位的財務年度（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=GetfieldFiscalY&group=FIELDFUNC)） |
| `GetQuote` | `("報價欄位")` | 讀系統內**報價欄位**（限警示 / 交易腳本） |
| `GetSymbolInfo` | `("資訊欄位")` | 讀系統內商品資訊欄位 |
| `CheckField` | `("欄位", "頻率"): Bool` | 該欄位資料是否存在 |
| `CheckSymbolField` | `("商品", "欄位", "頻率"): Bool` | 指定商品該欄位資料是否存在 |
| `IsSupportField` | `("欄位", "頻率"): Bool` | 是否支援該欄位×頻率組合 |
| `IsSupportSymbolField` | `(symbol, "欄位", "頻率"): Bool` | 指定商品是否支援該組合 |
| `Symbol` | `(): Str` | 目前執行商品代碼 |
| `SymbolName` | `(): Str` | 目前執行商品名稱 |
| `UserID` | `(): Str` | 目前登入的 XQ 帳號 |

---

## 7. 陣列函數（`ARRAYFUNC`）

> 多回傳「狀態碼」（成功通常 0），結果回填到傳入的陣列參數。陣列宣告見 [language.md](language.md)。

| 名稱 | 簽名 | 說明 |
|------|------|------|
| `Array_GetMaxIndex` | `(array): Num` | 取陣列元素個數 |
| `Array_SetMaxIndex` | `(array, count): Num` | 重設一維陣列大小 |
| `Array_GetType` | `(array): Num` | 取陣列資料型別（2/3/7） |
| `Array_SetValRange` | `(array, from, to, value)` | 將一段範圍元素設為指定值 |
| `Array_Copy` | `(src, dest): Num` | 複製元素（成功回 0） |
| `Array_Compare` | `(A, B): Num` | 比較兩陣列元素（1/-1/0/-2） |
| `Array_Sum` | `(array, from, to): Num` | 範圍內元素加總 |
| `Array_Sort` | `(array, order)` | 一維陣列排序（升 / 降） |
| `Array_Sort2d` | `(array, col, order)` | 二維陣列依指定欄排序 |

---

## 8. 交易函數（`TRANSACTIONFUNC`）

> ⚠️ **僅自動交易腳本**（`{@type:autotrade}`）可用。下單前的「第一次洗價控管」、盤中累計用
> `intraBarPersist` 等慣例見 [script-types.md](script-types.md) 與 memory `xs-intrabarpersist-semantics`。

### 下單 / 部位

| 名稱 | 簽名 | 說明 |
|------|------|------|
| `Buy` | `(qty [, price [, label]])` | 多單加碼（增加多頭部位） |
| `Sell` | `(qty [, price [, label]])` | 多單減碼（減少多頭部位） |
| `Short` | `(qty [, price [, label]])` | 空單加碼（增加空頭部位） |
| `Cover` | `(qty [, price [, label]])` | 空單回補（減少空頭部位） |
| `SetPosition` | `(target [, price [, label]])` | 直接調整到目標部位 |
| `Market` | `()` | 以當前市價下單（價格參數位置使用） |
| `IsMarketPrice` | `(value): Bool` | 判斷某價格是否為市價 |
| `AddSpread` | `(基礎價格, 檔位): Num` | 依跳動點(檔位)調整後的價格 |
| `CancelAllOrders` | `() \| (label)` | 取消委託單 |
| `DefaultBuyPrice` | `(): Num` | 自動交易預設買價 |
| `DefaultSellPrice` | `(): Num` | 自動交易預設賣價 |
| `IsListedSymbol` | `(): Bool` | 是否為上市(掛牌)商品 |

### 部位 / 成交查詢

| 名稱 | 簽名 | 說明 |
|------|------|------|
| `Position` | `(): Num` | 目前部位（`Value1 = Position;`） |
| `Filled` | `(): Num` | 目前成交部位量（`Value1 = Filled;`） |
| `FilledAtBroker` | `(): Num` | 券商端實際庫存量 |
| `FilledAvgPrice` | `(): Num` | 目前部位的未實現成本（均價） |
| `FilledEntryDate` | `(): Num` | 部位進場日期 `YYYYMMDD` |
| `FilledEntryTime` | `(): Num` | 部位進場時間 `HHMMSS` |
| `FilledEntryTimeMS` | `(): Num` | 部位進場時間（含毫秒） |
| `FilledRecordCount` | `(): Num` | 成交紀錄總筆數 |
| `FilledRecordBS` | `(idx): Num` | 第 idx 筆成交方向（1=買 / -1=賣） |
| `FilledRecordDate` | `(idx): Num` | 第 idx 筆成交日期 |
| `FilledRecordTime` | `(idx): Num` | 第 idx 筆成交時間 `HHMMSS` |
| `FilledRecordTimeMS` | `(idx): Num` | 第 idx 筆成交時間（含毫秒） |
| `FilledRecordPrice` | `(idx): Num` | 第 idx 筆成交價 |
| `FilledRecordQty` | `(idx): Num` | 第 idx 筆成交量 |
| `FilledRecordIsRealtime` | `(idx): Bool` | 第 idx 筆是即時或回測期間成交 |

### 警示輸出

| 名稱 | 簽名 | 說明 |
|------|------|------|
| `Alert` | `(str1) \| (str1, num1, ...)` | 策略執行中產生**警示**紀錄（警示腳本核心） |

> `Playsound`（音效）歸一般函數；`Alert` 才是文字警示輸出。

---

## 9. SDT 函數（`SDTFUNC`）

> 2026-09-24 以 xshelp rest 索引窮舉 `*FUNC` 分類時新發現的第 9 個分類（原 8 分類清單未涵蓋）。
> SDT（Symbol Data Table，依 xshelp 分類名稱推測）是一張以 **key（列）× column（1~100 直行）**
> 定址的鍵值表，供腳本暫存/共用資料；每個函數均有 `_L` 尾碼版本，xshelp 對兩者的說明文字逐字相同，
> `_L` 確切語意差異待查證（不臆造）。

| 名稱 | 簽名 | 說明 |
|------|------|------|
| `SDT_GetValue` / `SDT_GetValue_L` | `(key, column [, default:=0]): Num` | 取得 SDT 指定 key 列、column 行的數值；找不到回 default，字串會嘗試轉數值失敗則回 0（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=SDT_GetValue&group=SDTFUNC)） |
| `SDT_GetString` / `SDT_GetString_L` | `(key, column [, default:=""]): Str` | 取得 SDT 指定 key 列、column 行的字串；找不到回 default（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=SDT_GetString&group=SDTFUNC)） |
| `SDT_SetValue` / `SDT_SetValue_L` | `(key, column, value)` | 寫入 SDT 指定 key 列、column 行的數值；column 為新字串會新增該行，column 數字大於現有行數會補齊中間空白欄，欄號或直行總數超過 100 回傳錯誤（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=SDT_SetValue&group=SDTFUNC)） |
| `SDT_SetString` / `SDT_SetString_L` | `(key, column, value)` | 寫入 SDT 指定 key 列、column 行的字串；規則同 `SDT_SetValue`（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=SDT_SetString&group=SDTFUNC)） |
| `SDT_SetValueIf` / `SDT_SetValueIf_L` | `(key, column, newvalue, oldvalue): Bool` | 僅當指定欄位目前數值等於 `oldvalue` 才覆寫為 `newvalue` 並回 True，可用於避免多商品/策略同時寫入互相覆蓋（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=SDT_SetValueIf&group=SDTFUNC)） |
| `SDT_SetStringIf` / `SDT_SetStringIf_L` | `(key, column, newvalue, oldvalue): Bool` | 字串版 `SDT_SetValueIf`：僅當目前字串等於 `oldvalue` 才覆寫並回 True（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=SDT_SetStringIf&group=SDTFUNC)） |
| `SDT_HasKey` / `SDT_HasKey_L` | `(key): Bool` | 判斷傳入字串是否包含在 SDT 的 key 中（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=SDT_HasKey&group=SDTFUNC)） |
| `SDT_GetKeys` / `SDT_GetKeys_L` | `(output_key_array)` | 取得 SDT 所有 key，寫入傳入的一維字串陣列（輸出用）；取回順序不保證，需依序處理改用 `SDT_SortKey` / `SDT_Sort`（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=SDT_GetKeys&group=SDTFUNC)） |
| `SDT_RemoveKey` / `SDT_RemoveKey_L` | `(key)` | 移除 SDT 指定 key 所對應的整列資料（含 key）（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=SDT_RemoveKey&group=SDTFUNC)） |
| `SDT_RemoveAll` / `SDT_RemoveAll_L` | `()` | 一次移除此 SDT 內所有資料（清空整張表）（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=SDT_RemoveAll&group=SDTFUNC)） |
| `SDT_SetColumnName` / `SDT_SetColumnName_L` | `(column_num, column_name)` | 命名或修改 SDT 指定直行的名稱（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=SDT_SetColumnName&group=SDTFUNC)） |
| `SDT_Average` / `SDT_Average_L` | `(column): Num` | 取得 SDT 指定直行的數值平均；無法轉數值的列以 0 計入（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=SDT_Average&group=SDTFUNC)） |
| `SDT_Max` / `SDT_Max_L` | `(column [, output_key]): Num` | 取得 SDT 指定直行的最大值，可另傳字串變數 `output_key` 取回最大值所在列的 key（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=SDT_Max&group=SDTFUNC)） |
| `SDT_Min` / `SDT_Min_L` | `(column [, output_key]): Num` | 取得 SDT 指定直行的最小值，用法同 `SDT_Max`（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=SDT_Min&group=SDTFUNC)） |
| `SDT_Median` / `SDT_Median_L` | `(column [, output_key]): Num` | 取得 SDT 指定直行的中位數，可另傳 `output_key` 取回該列 key（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=SDT_Median&group=SDTFUNC)） |
| `SDT_Sort` / `SDT_Sort_L` | `(column, sorted_key_array [, order:=-1])` | 依指定直行的**數值**排序，將排序後的 key 寫入傳入的字串陣列；`order` -1 由小到大（預設）、1 由大到小（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=SDT_Sort&group=SDTFUNC)） |
| `SDT_SortString` / `SDT_SortString_L` | `(column, sorted_key_array [, order:=-1])` | 依指定直行的**字串**排序，用法同 `SDT_Sort`（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=SDT_SortString&group=SDTFUNC)） |
| `SDT_SortKey` / `SDT_SortKey_L` | `(sorted_key_array [, order:=-1])` | 依 SDT 的 key 排序，將排序後的 key 寫入傳入的字串陣列（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=SDT_SortKey&group=SDTFUNC)） |
| `SDT_Sum` / `SDT_Sum_L` | `(column): Num` | 取得 SDT 指定直行所有列的數值加總；無法轉數值的列以 0 計入（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=SDT_Sum&group=SDTFUNC)） |

---

> **待補 / 邊界（build-time，非 F3 回寫）：**
>
> - 各 bif 的多載細節（如 `Buy` 的 `price`/`label` 完整位置語意）以 xshelp 個別函數頁
>   （`/XSHelp/?HelpName=<名稱>&group=<分類碼>`）為準，本檔只收一行語意；需要精確語意時 build-time 補。
> - `keyword.bif`（grammar 2023 快照）與本檔若有名單差異，以本檔（xshelp 現況）為準。
