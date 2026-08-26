# 範例：函數（function 家族）

> 蒸餾自 `XScript_Preset/函數/`（`邏輯判斷/CountIF.xs`、`邏輯判斷/CrossOver.xs`、
> `日期相關/FormatMQY.xs`）。三子型別與回傳機制見 `script-types.md §5`。

## 數值函數 `{@type:function}` — `CountIF`

```xs
{@type:function}
SetBarMode(1);                                   // 時間序列模式
input: TrueAndFalse(truefalseseries), Length(numericsimple);
variable: variableA(0);

variableA = 0;
for Value1 = 0 to Length - 1 begin
    if TrueAndFalse[Value1] then variableA = variableA + 1;
end;
CountIF = variableA;                             // 回傳：對函數名賦值
```

- `input` 用**型別關鍵字**宣告：`truefalseseries`（布林序列）、`numericsimple`（單值）。
- 回傳＝對與檔名同名的變數 `CountIF` 賦值。

## 布林函數 `{@type:function_bool}` — `CrossOver`

```xs
{@type:function_bool}
SetBarMode(1);
input: SeriesA(numericseries), SeriesB(numericseries);

// 上一根 A 在 B 之下或相等、這一根 A 在 B 之上 → 向上穿越
CrossOver = SeriesA[1] <= SeriesB[1] and SeriesA[0] > SeriesB[0];
```

- 回布林，呼叫端寫 `if CrossOver(FastMA, SlowMA) then ...`。
- `numericseries` 才能取 `[n]` 回看。

## 字串函數 `{@type:function_string}` — `FormatMQY`

```xs
{@type:function_string}
SetBarMode(1);
input: Date1(numericsimple);
value1 = ceiling(month(Date1)/3);

switch (Barfreq) begin                           // 依執行頻率回不同格式
    case "M","AM": FormatMQY = FormatDate("yyyyMM", Date1);
    case "Q":      FormatMQY = FormatDate("yyyy", Date1) + "Q" + NumToStr(value1,0);
    case "Y":      FormatMQY = FormatDate("yyyy", Date1);
    default:       FormatMQY = FormatDate("yyyyMMdd", Date1);
end;
```

- 回字串，子標記必須 `function_string`，否則型別不符。
- 函數**不下單、不 plot、不 ret**，純運算回值。
