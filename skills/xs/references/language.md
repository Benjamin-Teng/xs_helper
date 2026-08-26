# XS 語言基礎（language）

> **來源**：token 名單蒸餾自 vscode-xs grammar（`xs.tmLanguage.json`，2023 快照）的
> `keyword.control` / `keyword.skipword` / `keyword.operator` / `variable.*` 分類；
> 語法範式（宣告、流程控制寫法）以 `XScript_Preset` 真實 `.xs` 原始碼校對。
> grammar 為 2023 快照，名單可能落後最新 xshelp；冷門關鍵字以 xshelp「關鍵字」分類為準，
> 查無把握者走 SKILL.md 的 F3 線上查證，不臆測。

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
| 布林 | `TrueFalse` `TrueFalseSimpleVar` `TrueFalseSeries` `TrueFalseRef` `TrueFalseArray` `TrueFalseArrayRef` |
| 原生 | `Bool` `Int` `Float` `Double` |
| 陣列 | `Array` `Arrays` |

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

`PI`、星期常數 `Monday` `Tuesday` `Wednesday` `Thursday` `Friday` `Saturday` `Sunday`。

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

## 待補（後續蒸餾）

- [ ] 各型別關鍵字的精確語意差異（`Simple` vs `Series` vs `Ref` 的記憶體/求值模型）以 xshelp 校對補強。
- [ ] `switch/case`、`repeat/until`、`while` 的完整語法範式（目前 Preset 取樣未涵蓋，需補真實範例）。
