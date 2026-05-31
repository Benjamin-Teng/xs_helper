# 範例：自動交易（autotrade）

> 蒸餾自 `XScript_Preset/自動交易/`（基於 `常見技術分析/多頭/均線黃金交叉.xs`
> ＋ `2-下單出場方式/04-多單固定停利停損(%).xs`）。型別 / 邊界見 `script-types.md §1`。

## 均線黃金交叉進出場（最小骨架）

```xs
{@type:autotrade}
input: Shortlength(5,"短期均線期數"), Longlength(20,"長期均線期數");

settotalbar(8);
setbarback(maxlist(Shortlength, Longlength, 6));   // 指標暖機筆數

// 進場：短均黃金交叉長均；出場：死亡交叉
if Position = 0 and Average(Close,Shortlength) Cross Above Average(Close,Longlength)
    then SetPosition(1);
if Position = 1 and Average(Close,Shortlength) Cross Below Average(Close,Longlength)
    then SetPosition(0);
```

- `Position` 守門：`=0` 才判進場、`=1` 才判出場，避免重複下單。
- `SetPosition(1)` 設目標部位多 1 口、`SetPosition(0)` 平倉。

## 進場後固定停利 / 停損（%）

```xs
{@type:autotrade}
input: profit_percent(2, "停利(%)"), loss_percent(2, "停損(%)");

if Position = 0 and Average(Close,5) Cross Over Average(Close,20)
    then SetPosition(1, MARKET);                    // 市價進場

if Position = 1 and Filled = Position then begin    // 實際部位已達目標（無未成交掛單）才談停損停利
    if Close >= FilledAvgPrice * (1 + 0.01*profit_percent) then SetPosition(0)   // 停利
    else if Close <= FilledAvgPrice * (1 - 0.01*loss_percent) then SetPosition(0); // 停損
end;
```

- `FilledAvgPrice`＝成交均價，停利停損的基準價。
- 用到的函數見 `system-functions.md`（`Average`/`Cross`）、`builtin-functions.md`（交易類）。

> ⭐ 盤中「同根 Bar 只想做一次」的動作，用 `intraBarPersist` 旗標 + 換 Bar 重設
> （見 `script-types.md §1` 第一次洗價控管、`language.md §7`）。
