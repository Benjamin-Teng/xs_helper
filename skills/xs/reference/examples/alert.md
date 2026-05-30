# 範例：警示（sensor）

> 蒸餾自 `XScript_Preset/警示/!語法範例/`（`1.基本語法.xs`、`3.getquote.xs`）。
> 型別 / 邊界見 `script-types.md §4`。

> ⚠️ **警示用 `ret = 1` 觸發，不是 `Alert()`**。實證 Preset 警示 359 檔有 333 檔用
> `ret=1`、0 檔用 `Alert()`（`Alert()` 是自動交易的通知函數）。

## 技術條件觸發（短均上穿長均）

```xs
{@type:sensor}
input: shortlength(5), longlength(20);
SetInputName(1, "短天期");

value1 = Close - Close[1];                        // close[1]＝前一根收盤
value2 = AbsValue(value1) / Close;                // 當根漲跌幅
value3 = Average(value2, longlength);             // 長期平均漲跌幅
value4 = Average(value2, shortlength);            // 短期平均漲跌幅
if value4 Crosses Over value3 then ret = 1;       // 黃金交叉 → 觸發
```

## 盤中即時報價觸發（外盤漲停）

```xs
{@type:sensor}
value1 = GetQuote("Ask");                         // 賣出價（可寫 q_Ask）
value2 = GetQuote("DailyUplimit");                // 漲停價
value3 = GetQuote("Bid");                         // 買進價
if value1 = value2 and value1/value3 <= 1.005 then ret = 1;
```

- `GetQuote("欄位")` / `q_欄位` 取盤中即時數據（委買賣、內外盤、漲停價…），**僅即時段有效**。
- 觸發頻率（每根 Bar 一次 / 持續）由 XQ 警示設定去重，腳本只判「成立否」。
- 即時報價欄位見 `fields.md`（`Q*` / `q_*`）。
