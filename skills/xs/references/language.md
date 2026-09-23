# XS 語言基礎（language）

> **來源**：token 名單蒸餾自 vscode-xs grammar（`xs.tmLanguage.json`，2023 快照）的
> `keyword.control` / `keyword.skipword` / `keyword.operator` / `variable.*` 分類；
> 語法範式（宣告、流程控制寫法）以 `XScript_Preset` 真實 `.xs` 原始碼校對。
> grammar 為 2023 快照，名單可能落後最新 xshelp；冷門關鍵字以 xshelp「關鍵字」分類為準，
> 查無把握者走 SKILL.md 的 F3 線上查證，不臆測。
> **§9 的關鍵字／保留字總表**則直接窮舉自 xshelp「關鍵字」大分類（2026-09-23 擷取），
> 與前文 grammar 名單衝突時以 §9 為準。

XS 語法family近似 TradeStation EasyLanguage：大小寫不敏感（`Close` = `close`）、敘述以分號 `;` 結尾、區塊用 `begin … end`。

---

## 1. 註解

| 形式 | 寫法 | 備註 |
|------|------|------|
| 行註解 | `// 到行尾` | |
| 區塊註解 | `{ 多行 }` | XS 慣例：檔首用 `{ … }` 寫說明，**同時也是 `{@type:}` 標記的容器** |

> ⚠️ `{ … }` 既是註解也是型別標記載體：原始碼第一行 `{@type:autotrade}` 不是普通註解，
> 是腳本類型宣告（見 [script-types.md](script-types.md)）。

---

## 2. 變數宣告

冒號式宣告，可附初始值與中文標籤。大小寫不敏感（`var` = `Var` = `Vars` = `Variable` = `Variables`）。

**命名限制**：不要拿 §9 總表裡的任何名稱（關鍵字、忽略字、常數、保留字）當變數或參數名稱。XS 大小寫不敏感，所以 `if`、`If`、`IF` 都算同一個字，都不要用。
xshelp 沒有明文列出命名規則（全站搜尋「保留字」「命名規則」「變數名稱」皆 0 筆）；用了之後編譯器是否一定報錯**待查證**（需在 XQ 編輯器實測），因此這裡採保守寫法：一律避開。

```xs
var: acc(0), idx(0);                 // 多變數一行，括號內為初始值
var: intraBarPersist _last_date(0);  // 帶 intraBarPersist 修飾子（見 §7）
Array: MAArray[](0);                 // 陣列，[] 表動態長度，括號內初始值
```

**輸入參數**（`function` / `indicator` 類用來收呼叫端傳入值），`input:` / `inputs:`：

```xs
input: pv(numericsimple, "成交金額");      // 型別 + 中文標籤
input: TheSeries(numericseries, "序列");
Input: TargetArray[X](NumericArrayRef);   // 陣列參考（回填用）
```

### 型別關鍵字（grammar `keyword.control`）

| 群組 | token |
|------|-------|
| 數值 | `Numeric` `NumericSimple` `NumericSeries` `NumericRef` `NumericArray` `NumericArrayRef` |
| 字串 | `String` `StringSimple` `StringSeries` `StringRef` `StringArray` `StringArrayRef` |
| 布林 | `TrueFalse` `TrueFalseSimple` `TrueFalseSeries` `TrueFalseRef` `TrueFalseArray` `TrueFalseArrayRef` |
| 陣列 | `Array` `Arrays` |

- ⚠️ `Bool` `Int` `Float` `Double` **不是可用的型別**：xshelp 標為保留字，原文「此文字為系統預先保留的文字，目前並沒有任何作用。」（見 §9.5）。宣告型別一律用上表。
- 布林簡單型別 xshelp 寫作 `TrueFalseSimple`；vscode-xs grammar 另收 `TrueFalseSimpleVar`，xshelp 查無此名，不要用。
- `*Simple`：純量；`*Series`：時間序列（可用 `x[n]` 取前 n 根值）；`*Ref` / `*ArrayRef`：傳參考（函數回填）。
- 回傳：`RetVal` / `Ret` / `RetMsg`（`function` 類以 `retval = …` 回傳，見 [script-types.md](script-types.md)）。

### 序列位移（offset）

`Series` 型別變數與報價欄位可用 `[n]` 取「往前第 n 根 K 棒」的值（`[0]` = 當根）：

```xs
Close[1]        // 前一根收盤
TheSeries[idx]  // 第 idx 根前的值
```

---

## 3. 流程控制

寫法以 Preset 原始碼校對。`begin … end` 包多行；單行敘述可省略 `begin/end`。

```xs
// if / then / else（單行）
if pv > _threshold then retval = true else retval = false;

// if / then begin … end;（多行區塊）
if _last_date <> Date then begin
    _last_date = Date;
    _open_price = GetField("Open", "D");
end;

// else if 串接
if _open_price < 30 then _threshold = 800000
else if _open_price < 50 then _threshold = 1000000
else _threshold = 4000000;

// for … to / downto（注意：迴圈體直接接 begin，無 then）
for idx = 0 to MALength-1 begin
    acc = acc + TheSeries[idx];
end;
```

| 關鍵字 | 用途 |
|--------|------|
| `if` / `then` / `else` | 條件；**`if` 必有 `then`**（務必配對） |
| `begin` / `end` | 區塊；**務必成對** |
| `for` / `to` / `downto` | 計數迴圈；`to` 遞增、`downto` 遞減 |
| `while` | 條件迴圈 |
| `repeat` / `until` | 後測迴圈 |
| `switch` / `case` / `default` | 多分支 |
| `once` | 只執行一次的區塊 |
| `break` / `return` | 跳出 / 提前返回 |

### 3.1 迴圈與分支的官方寫法

以下四段各取自官方 Preset / xshelp 原文，未涵蓋在上面 §3 範例裡的完整語法範式。

**`while 條件 begin … end;`**：迴圈體多行時用 `begin/end` 包住（與 §3 已示範的 `if`/`for` 同慣例）。

```xs
idx = 1;
while GetFieldDate("Date", "1")[idx] = lastdate begin
    idx = idx + 1;
end;
```

摘錄自 `XScript_Preset/函數/交易相關/CalcVWAPDistribution.xs`。同一支腳本另有 `while` 巢狀寫法：

```xs
while success = 1 and tmpnow-now <= LeftStrength
begin
    if Price[now] < Price[tmpnow] then
        success = 0
    else tmpnow = tmpnow+1;
end;
```

摘錄自 `XScript_Preset/函數/趨勢分析/SwingHigh.xs`。

**`repeat … until 條件;`**：先執行迴圈體、再判斷 `until` 後的條件（後測迴圈），迴圈體可用 `begin/end`：

```xs
repeat
 begin
    value1 = simplehighest(high[1], period);
    value2 = simplelowest(low[1], period);
    period = period + 1;
 end;
until period >= rangemax or (value1 > value2 * (1 + limit1/100));
```

逐字取自 `XScript_Preset/選股/05.型態選股/突破整理格局.xs`。

**`Once(條件) begin … end;`**：**只有這一種語法**——xshelp 條目
（[HelpName=Once&group=CONTROLFLOW](https://xshelp.xq.com.tw/XSHelp/?HelpName=Once&group=CONTROLFLOW)）提到的「只做一次」另一種做法，是用
`var: FirstTime(false);` 搭配 `if … and not FirstTime then begin … FirstTime = True; end;`，那是 `if` 加旗標的等效寫法，**不是 `Once` 本身的第二種語法**。

```xs
Once(Position = 0 and Filled = 0 and GetInfo("TradeMode") = 1) begin
    SetPosition(1, GetField("跌停價", "D"), label:="跌停價買進委託");
    _time = TimeAdd(CurrentTime, "M", _n);
end;
```

逐字取自 `XScript_Preset/自動交易/0-基本語法/09-CancelAllOrders.xs`。

**`switch (變數) begin case 值: … ; case N to M: … ; default: … ; end;`**：`case`
支援 `N to M` 數值範圍，且 `switch` 可以巢狀。xshelp 條目
（[HelpName=switch&group=CONTROLFLOW](https://xshelp.xq.com.tw/XSHelp/?HelpName=switch&group=CONTROLFLOW)）範例（摘錄，原文含 `Case 1` 到 `Case 5` 五段，此處只留頭尾示範 `Case N to M` 用法）：

```xs
Value1 = DayOfMonth(date);
Switch (value1) Begin
Case 1:
    print(Text("今天的日期是", NumToStr(date,0)), "value1=1時執行這段程式碼");
Case 6 to 20:
    print(Text("今天的日期是", NumToStr(date,0)), "value1=6~20時執行這段程式碼");
Default:
    print(Text("今天的日期是", NumToStr(date,0)), "其他情形都執行這段程式碼");
End;
```

巢狀寫法（摘錄，原文外層還包一層 `if x <= 10 then … else`，此處只留 `else` 分支裡的巢狀 `switch`）：

```xs
switch(value1) begin
    case 1: condition1 = TrueAll(Getfield("大戶持股人數",param:=50) > Getfield("大戶持股人數",param:=50)[1],N);
    value2 = Getfield("大戶持股人數",param:=50);
    default : value1 = round(x/200,0);
    switch (value1) begin
        case 1: condition1 = TrueAll(Getfield("大戶持股人數",param:=200) > Getfield("大戶持股人數",param:=200)[1],N);
        default: condition1 = TrueAll(Getfield("大戶持股人數",param:=1000) > Getfield("大戶持股人數",param:=1000)[1],N);
    end;
end;
```

摘錄自 `XQStrategy/01台股的選股條件/04籌碼/大戶持股人數/連續N期大戶持股人數增加.xs`。

---

## 4. 運算子

| 類別 | token |
|------|-------|
| 算術 | `+` `-` `*` `/` |
| 指派 | `=`（同時是相等比較，依語境）、`+=` `-=` |
| 比較 | `=` `<=` `>=` `<>`（不等於）、`<` `>` |
| 邏輯 | `And` `Or` `Not` `Xor` |
| 關係（穿越/突破） | `Cross Above` / `Cross Below`（= `Crosses Above/Below`）、`Cross Over` / `Cross Under`、`Above` `Below` `Over` `Under` |

> `Cross Above` / `Cross Below` 是 XS 慣用的「向上/向下穿越」語法糖（亦有對應函數
> `CrossOver` / `CrossUnder`，見 [system-functions.md](system-functions.md)）。

---

## 5. 內建變數（grammar `variable.builtin`）

| 變數 | 說明 |
|------|------|
| `Value1` … `Value999` | 暫存數值槽 |
| `Condition1` … `Condition999` | 暫存布林槽 |
| `Position` | 目前部位（自動交易語境） |
| `Filled` | 目前實際成交部位量（自動交易語境，數量非布林） |

---

## 6. 常數（grammar `variable.constant`）

`PI`、星期常數 `Monday` `Tuesday` `Wednesday` `Thursday` `Friday` `Saturday` `Sunday`（數值見 §9.2）。

---

## 7. ⭐ `intraBarPersist` —— 逐筆洗價變數修飾子（一級概念）

`intraBarPersist` 是**變數宣告修飾子**（不是函數），寫法 `var: intraBarPersist _name(0);`。
只在**逐筆洗價**（盤中即時、K 棒未收盤、每筆 tick 重算）情境有意義——主要是
**自動交易、警示**類腳本（觸發/洗價模型見 [script-types.md](script-types.md)）。

**核心語意（回捲陷阱）**：盤中每進一筆 tick，整支腳本重算一次。

| | 同一根 Bar 內，tick 與 tick 之間 | 跨 Bar |
|---|---|---|
| **一般變數** | ❌ 每筆 tick 都被「回捲」到前一根 Bar 收盤時的值，當根中間累計被丟掉 | ✅ 延續 |
| **`intraBarPersist` 變數** | ✅ 延續、不回捲，可跨 tick 累加 | ✅ 延續 |

差別**只在「同一根 Bar 內 tick 與 tick 之間」**。

**典型用途**：一根 Bar 內跨多筆成交累計（官方點名「累計大單」：當根累加每筆大單，
超過 N 筆觸發訊號）。用一般變數會每筆 tick 歸零、**不報錯只默默算錯**——這是 Claude 最易生錯之處。

**配套慣例**：`intraBarPersist` 不會自動重設，**跨 Bar 歸零要自己寫**。Preset
`函數/邏輯判斷/IsXLOrder.xs` 的真實作法：

```xs
var: intraBarPersist _last_date(0);
var: intraBarPersist _threshold(0);

if _last_date <> Date then begin   // 換 Bar（日期變了）→ 手動重設
    _last_date = Date;
    _threshold = ...;
end;
```

---

## 8. 忽略字（skipword，grammar `keyword.skipword`）

純粹提升可讀性的語法糖，**對語意無影響**，可寫可不寫：
`A` `An` `At` `Based` `By` `Does` `From` `Is` `Of` `On` `Place` `Than` `The` `Was`。

例：`Buy 1 share` 中的 `share` 之類修飾字（依語境）。寫了不影響執行。

---

## 9. 關鍵字與保留字總表（xshelp 窮舉）

> **來源**：xshelp「關鍵字」大分類只有 4 個 group——忽略字 `SKIPWORD`、常數 `CONSTANT`、
> 流程控制 `CONTROLFLOW`、宣告 `DECLARATION`。以站內搜尋索引 `/XSHelp/rest?a=<字母>` 對 a–z
> 各查一次取聯集，共 **110 個名稱**（含別名），逐一開頁核對內容，2026-09-23 擷取。
> 條目網址格式：`https://xshelp.xq.com.tw/XSHelp/?HelpName=<名稱>&group=<GROUP>`。
> 下列全部名稱都**不要拿來當變數或參數名稱**（見 §2 命名限制）。

### 9.1 忽略字 `SKIPWORD`（14 個）

`A` `An` `At` `Based` `By` `Does` `From` `Is` `Of` `On` `Place` `Than` `The` `Was`

語意見 §8；xshelp 只有一張群組總表（[條目](https://xshelp.xq.com.tw/XSHelp/?HelpName=A&group=SKIPWORD)）。

### 9.2 常數 `CONSTANT`（8 個）

| 名稱 | 值 |
|------|----|
| `PI` | 3.14159 |
| `Sunday` `Monday` `Tuesday` `Wednesday` `Thursday` `Friday` `Saturday` | 依序 0 1 2 3 4 5 6 |

[條目](https://xshelp.xq.com.tw/XSHelp/?HelpName=PI&group=CONSTANT)

### 9.3 流程控制 `CONTROLFLOW`（37 個名稱，16 頁）

| 名稱（含別名） | 用途（xshelp 首句摘要） |
|------|------|
| `If` `Then` `Else` | 條件成立時執行哪個動作 |
| `Begin` `End` | 用在 If、While、For 等控制指令內包住多行 |
| `For` `To` `DownTo` | 計數迴圈 |
| `While` | 條件迴圈 |
| `Repeat` `Until` | 後測迴圈 |
| `Switch` `Case` `Default` | 判斷變數值符合哪個運算式 |
| `Once` | 只需要執行一次的程式碼 |
| `Break` | 跳出迴圈 |
| `Return` | 中斷正在執行的腳本 |
| `And` `Or` `Not` `Xor` | 邏輯運算 |
| `True` `False` | 邏輯值 |
| `Cross` `Crosses` `Above` `Below` `Over` `Under`，及組合 `Cross Above/Below/Over/Under`、`Crosses Above/Below/Over/Under` | 穿越判斷（見 §4） |

`Default` 有兩種用法：一是 `Switch` 內「都不符合時」的分支；二是 `GetField` / `GetSymbolField` 的命名參數，指定 K 棒沒有資料時回傳的值，例如 `GetField("本益比", "D", Default := 0)`。後者的條目在 `CONTROLFLOW` 與 `DECLARATION` 各掛一頁，內容相同。

### 9.4 宣告 `DECLARATION`（51 個名稱）

| 名稱（含別名） | 用途（xshelp 首句摘要） |
|------|------|
| `Var` `Vars` `Variable` `Variables` | 宣告變數並給預設值 |
| `Array` `Arrays` | 宣告陣列變數 |
| `Input` `Inputs` | 宣告腳本參數名稱與型別 |
| `IntraBarPersist` | 控制變數在逐筆洗價時是否回捲（見 §7） |
| `Numeric` `NumericSimple` `NumericSeries` `NumericRef` `NumericArray` `NumericArrayRef` | 函數腳本參數：數值類 |
| `String` `StringSimple` `StringSeries` `StringRef` `StringArray` `StringArrayRef` | 函數腳本參數：字串類 |
| `TrueFalse` `TrueFalseSimple` `TrueFalseSeries` `TrueFalseRef` `TrueFalseArray` `TrueFalseArrayRef` | 函數腳本參數：布林類 |
| `Ret` | 內建變數，決定警示與選股腳本的結果 |
| `RetVal` | 函數腳本的回傳值 |
| `RetMsg` | 警示觸發時顯示的訊息 |
| `RetSound` | 警示觸發時的提醒音效 |
| `Rank` | 選股腳本專用，宣告排行作業 |
| `Group` | 宣告清單，再以 `GetSymbolGroup` 取值 |
| `SymbolGroup` | 指標腳本 input 中設定清單類型 |
| `inputkind` | `input` 宣告時的命名參數 |
| `dict` `daterange` `symbolprice` | 搭配 `inputkind` 產生選項（一般選項／日期範圍／開高低收） |
| `quickedit` | 指標腳本 `input` 搭配 `inputkind` 時可另加 |
| `checkbox` | 搭配 `plot` 系列的**命名參數**，寫法 `checkbox:=1`（把指標變成下拉式選單，1＝預設繪出、0＝預設不繪，見 builtin-functions.md `Plot` 一列） |
| `order` | 搭配 `OutputField` 的**命名參數**，寫法 `order:=-1`（指定選股結果欄位的排序，見 builtin-functions.md `OutputField` 一列） |
| `param` | 搭配大戶持股與散戶持股，調整級距 |
| `Adjusted` | 搭配 `GetField` / `GetSymbolField`，選擇原始或還原資料 |
| `Default` | `GetField` / `GetSymbolField` 無資料時的回傳值（見 §9.3 末） |
| `axis` | `Plot` 系列的命名參數，指定畫在哪條 Y 軸，官方範例庫可見 `axis:=1`、`axis:=2`、`axis:=11`（例：`plot2(value4,"主力累計買賣超",checkbox:=1,axis:=2)`）；xshelp 條目頁為空，**各值的精確編碼待查證** |
| `Asc` `Desc` | 索引有此名稱，但 xshelp 條目頁為空、官方範例庫零命中；用途**待查證**（2026-09-24 重新查證仍無資料） |
| `Bool` `Int` `Float` `Double` | **保留字**，見 §9.5 |

### 9.5 保留字（4 個）

`Bool` `Int` `Float` `Double`

xshelp 原文：「此文字為系統預先保留的文字，目前並沒有任何作用。」（[條目](https://xshelp.xq.com.tw/XSHelp/?HelpName=Double&group=DECLARATION)）。
全站只有這 4 個名稱使用「保留字」頁；它們**不能當型別使用**，也不要當變數名稱。

---

## 待補（後續蒸餾）

- [ ] 各型別關鍵字的精確語意差異（`Simple` vs `Series` vs `Ref` 的記憶體/求值模型）以 xshelp 校對補強。
- [x] `switch/case`、`repeat/until`、`while` 的完整語法範式 → 已補（§3.1，出處見各段）。
