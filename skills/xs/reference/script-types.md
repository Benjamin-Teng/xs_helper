# 五種腳本類型（script types）

> 蒸餾自 `XScript_Preset`（5 類 `{@type:}` 真實範例）＋ `XQStrategy`（filter 交叉驗證）。
> 觸發 / 洗價模型見 memory `xs-execution-trigger-model`；變數不回捲見 memory
> `xs-intrabarpersist-semantics` 與 `language.md §7`。

## 0. 類型由檔首 `{@type:}` 確定性決定

每支 `.xs` 第一行（或 BOM 後第一行）的 `{@type:xxx}` **唯一決定**腳本類型，XQ 編輯器據此切換可用函數、執行模型、輸出介面。蒸餾期實測 Preset 的型別分佈：

| 類型 | `{@type:}` 標記 | Preset 出現數 | 一句話 |
|------|----------------|--------------|--------|
| 自動交易 | `autotrade` | 64 | 依條件 `SetPosition` 進出場下單 |
| 選股 | `filter` | 324 | 對全市場逐檔判斷，`ret=1` 表「選中」 |
| 指標 | `indicator` | 395 | `plotN(...)` 在圖上畫線 |
| 警示 | `sensor` | 359 | 監控單檔，`ret=1` 表「觸發警示」 |
| 函數 | `function` / `function_bool` / `function_string` | 207 / 16 / 1 | 被其他腳本呼叫，回傳值 |

> ⚠️ **`function` 是一個家族，不是單一標記**。子型別決定回傳型別：
> `function`＝數值（numeric）、`function_bool`＝布林、`function_string`＝字串。
> 生成函數時必須依「要回傳什麼」選對子標記，否則引用端型別不符。

---

## 跨類型共通：回傳機制（最容易錯）

| 機制 | 用在哪類 | 寫法 | 語意 |
|------|---------|------|------|
| `ret = 1` | **filter** | `if 條件 then ret = 1;` | 這檔股票**入選** |
| `ret = 1` | **sensor** | `if 條件 then ret = 1;` | **觸發警示**（推播 / 監控視窗） |
| `plotN(值, "名")` | **indicator** | `plot1(ma, "MA");` | 畫第 N 條線 |
| `SetPosition(口數[, MARKET])` | **autotrade** | `SetPosition(1);` | 設定目標部位（驅動下單） |
| 對「函數同名變數」賦值 | **function 家族** | `MyFunc = 結果;`（函數名＝檔名） | 函數回傳值 |

> ⚠️ `ret = 1` 在 **filter** 與 **sensor** 意義不同（入選 vs 觸發），但寫法相同；
> 由 `{@type:}` 區分用途。**indicator / autotrade / function 不用 `ret`**。

> ⚠️ **`Alert()` 不是警示腳本的觸發方式**。實證：Preset 警示資料夾 359 檔有 333 檔用
> `ret=1`、**0 檔用 `Alert()`**。`Alert(訊息...)` 是**自動交易**的「通知」函數
> （訊息送到自動交易中心 / 推播），與 sensor 的觸發判定無關。

---

## 1. 自動交易 `{@type:autotrade}`

**執行模型**：即時。歷史回放→即時銜接，**換棒必觸發**、盤中逐筆洗價疊加。下單由
`SetPosition`（設定目標部位）驅動，引擎比對目標 vs 現有 `Position` 後送單。

**核心函數 / 變數**：

| 名稱 | 作用 |
|------|------|
| `SetPosition(n[, MARKET])` | 設定目標部位（n>0 多、n<0 空、0 平倉）；`MARKET` 市價 |
| `Position` | 目前部位（口數，多正空負） |
| `Filled` | 是否已成交（1=已成交） |
| `FilledAvgPrice` | 成交均價（停損停利基準） |
| `FilledRecord(...)` | 成交記錄查詢 |
| `CancelAllOrders` | 刪單 |
| `Alert(訊息...)` | 送通知（非下單） |
| `settotalbar(n)` / `setbarback(n)` | 設定回看資料筆數（指標暖機） |

**結構慣例**：用 `Position` 守門避免重複下單——`Position=0` 才判進場、`Position=1` 才判出場。

```xs
{@type:autotrade}
input: Shortlength(5,"短期均線期數"), Longlength(20,"長期均線期數");
settotalbar(8);
setbarback(maxlist(Shortlength, Longlength, 6));   // 指標暖機筆數

if Position = 0 and Average(Close,Shortlength) Cross Above Average(Close,Longlength)
    then SetPosition(1);                            // 黃金交叉進場
if Position = 1 and Average(Close,Shortlength) Cross Below Average(Close,Longlength)
    then SetPosition(0);                            // 死亡交叉出場
```

**⭐ 第一次洗價控管**：盤中同一根 Bar 會被逐筆重算多次。若直接用「即時值」判斷，
未收盤的條件可能瞬間成立又消失，造成誤觸下單。慣例是**以收盤確認的值（`Close[1]` /
換棒）判進出**，或對「盤中只想做一次」的動作用 `intraBarPersist` 旗標 + 換 Bar 重設：

```xs
var: intraBarPersist _done_this_bar(false);
if Date <> Date[1] then _done_this_bar = false;     // 換 Bar 重設旗標
if not _done_this_bar and 進場條件 then begin
    SetPosition(1);
    _done_this_bar = true;                          // 本根 Bar 不再重複
end;
```

**邊界**：禁用選股欄位（`GetField` 屬 filter 範疇）；即時報價 `GetQuote`/`q_` 僅即時段有效，回測段無盤中 tick。

---

## 2. 選股 `{@type:filter}`

**執行模型**：**非即時 tick**。排程 / 手動單次掃全市場，逐檔跑一遍腳本，`ret=1` 的入選。
頻率（D/W/M/Q/Y）由執行設定或 `GetField` 第二參數決定。

**核心函數**：

| 名稱 | 作用 |
|------|------|
| `GetField("欄位"[, "期別"])` | 取選股 / 資料欄位（中文欄位名）；期別 `D/W/M/Q/Y` |
| `ret = 1` | 標記此檔入選 |
| `SetTotalBar(n)` | 設定每檔回看資料筆數（取歷史值需 ≥ 用到的回看深度） |
| `input: X(預設)` + `SetInputName(i,"中文")` | 對外可調參數 |
| `OutputField1(值)` + `SetOutputName1("欄名")` | 在選股結果表額外輸出一欄（`OutputField1..N`） |

```xs
{@type:filter}
input: N(5); SetInputName(1, "期別");
SetTotalBar(3);

Value1 = Average(GetField("Close"), N);
if GetField("Close") > Value1 then ret = 1;     // 股價站上 N 期均價

SetOutputName1("均價");
OutputField1(Value1);                            // 結果表多顯示一欄
```

**跨市場**：`XQStrategy` 分台 / 陸 / 港 / 美四庫，差異在**可用欄位與欄位中文名**，語法結構一致。
冷門欄位走 SKILL.md F3 線上查 `fields.md` 未涵蓋者。

**邊界**：限選股 / 資料欄位；**禁下單函數**（`SetPosition` 等）；無盤中即時 tick，`GetQuote` 不適用。

---

## 3. 指標 `{@type:indicator}`

**執行模型**：每根 Bar 運算，盤中逐 tick 重畫。輸出是「線」不是「訊號」。

**核心函數**：

| 名稱 | 作用 |
|------|------|
| `plotN(值, "名稱")` | 畫第 N 條線（`plot1`、`plot2`…） |
| `input: X(預設, "中文")` / `setinputname(i,"中文")` | 對外參數 |
| `SetPlotColor` / `SetPlotWidth` 等 | 線條樣式（樣式函數，可選） |

```xs
{@type:indicator}
input: Length(20, "MA的天數"), UpperBand(2, "上通道倍數"), LowerBand(2, "下通道倍數");
variable: mid(0), up(0), down(0);

up   = BollingerBand(Close, Length,  UpperBand);
mid  = Average(Close, Length);
down = BollingerBand(Close, Length, -1 * LowerBand);

plot1(up,  "UB");
plot2(mid, "BBandMA");
plot3(down, "LB");
```

**邊界**：不下單、不 `ret`；輸出全靠 `plotN`。

---

## 4. 警示 `{@type:sensor}`

**執行模型**：即時監控單一商品，**換棒必觸發**、盤中逐筆洗價疊加。`ret=1` → 觸發警示
（推播 / 監控視窗）。觸發設定（每根 Bar 一次 / 持續）由 XQ 警示設定去重，腳本只管「成立否」。

**核心函數**：

| 名稱 | 作用 |
|------|------|
| `ret = 1` | 觸發警示 |
| `GetQuote("欄位")` / `q_欄位` | 取盤中即時報價（委買賣、內外盤、漲停價…），**僅即時段** |
| `input` / `variable` / 各 sysfnc | 同一般腳本 |

```xs
{@type:sensor}
input: shortlength(5), longlength(20);
SetInputName(1, "短天期");

value1 = Close - Close[1];
value2 = AbsValue(value1) / Close;               // 當根漲跌幅
value3 = Average(value2, longlength);            // 長期平均
value4 = Average(value2, shortlength);           // 短期平均
if value4 Crosses Over value3 then ret = 1;      // 短均上穿長均→觸發
```

盤中即時數據範例（外盤漲停）：

```xs
{@type:sensor}
value1 = GetQuote("Ask");           // 賣出價（可寫 q_Ask）
value2 = GetQuote("DailyUplimit");  // 漲停價
if value1 = value2 then ret = 1;
```

**邊界**：不下單（要下單請用 autotrade）；`GetQuote` 僅即時有效；`Alert()` 屬 autotrade，sensor 不用它觸發。

---

## 5. 函數 `{@type:function}` / `_bool` / `_string`

**執行模型**：不獨立執行，被其他腳本當函數呼叫。回傳值＝對「**與檔名同名的變數**」賦值。

**慣例**：

- 多數函數開頭寫 `SetBarMode(1);`（Preset 函數 207 檔中 202 檔有），確保以「時間序列模式」計算（取 `[n]` 回看正確）。
- `input` 用**型別關鍵字**宣告（非預設值）：`numericsimple`（單一數值）、`numericseries`
  （時間序列，可取 `[n]`）、`truefalseseries`（布林序列）、`numericref`（回填參數）。
- 回傳：對函數名賦值（如函數叫 `CountIF` → `CountIF = variableA;`）。

```xs
{@type:function}
SetBarMode(1);
input: TrueAndFalse(truefalseseries), Length(numericsimple);
variable: variableA(0);

variableA = 0;
for Value1 = 0 to Length - 1 begin
    if TrueAndFalse[Value1] then variableA = variableA + 1;
end;
CountIF = variableA;                  // 回傳：對函數名賦值
```

布林函數（`function_bool`，回傳 true/false，常用於 `if MyFunc(...) then ...`）：

```xs
{@type:function_bool}
SetBarMode(1);
input: SeriesA(numericseries), SeriesB(numericseries);
CrossOver = SeriesA[0] > SeriesB[0] and SeriesA[1] <= SeriesB[1];
```

字串函數（`function_string`，回傳字串）：

```xs
{@type:function_string}
SetBarMode(1);
input: Date1(numericsimple);
FormatMQY = FormatDate("yyyyMM", Date1);   // 回傳字串
```

**邊界**：函數不下單、不 `plot`、不 `ret`；純運算回值。子型別回傳型別必須與標記一致。

---

## 速查：選哪個 `{@type:}`？

| 你想做… | 用 |
|---------|----|
| 自動下單進出場 | `autotrade`（`SetPosition`） |
| 全市場挑符合條件的股票 | `filter`（`GetField` + `ret=1`） |
| 在 K 線圖上畫線 | `indicator`（`plotN`） |
| 盯盤、條件成立發通知 | `sensor`（`ret=1`） |
| 寫可被重用的計算邏輯（回數值） | `function` |
| …回 true/false | `function_bool` |
| …回字串 | `function_string` |
