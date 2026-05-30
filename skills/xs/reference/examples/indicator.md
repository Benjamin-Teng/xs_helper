# 範例：指標（indicator）

> 蒸餾自 `XScript_Preset/指標/`（`主圖指標/BBand軌道線.xs`、`技術指標/Aroon.xs`）。
> 型別 / 邊界見 `script-types.md §3`。

## 主圖指標 — 布林通道（畫三條線）

```xs
{@type:indicator}
input: Length(20, "MA的天數"), UpperBand(2, "上通道倍數"), LowerBand(2, "下通道倍數");
variable: mid(0), up(0), down(0);

up   = BollingerBand(Close, Length,  UpperBand);
mid  = Average(Close, Length);
down = BollingerBand(Close, Length, -1 * LowerBand);

plot1(up,  "UB");                                // 第 1 條線
plot2(mid, "BBandMA");                           // 第 2 條線
plot3(down, "LB");                               // 第 3 條線
```

## 副圖指標 — Aroon

```xs
{@type:indicator}
input: length(25); setinputname(1, "計算週期");
variable: aroon_up(0), aroon_down(0), aroon_osc(0);

aroon_up   = (length - NthHighestBar(1, high, length)) / length * 100;
aroon_down = (length - NthLowestBar(1, low,  length)) / length * 100;
aroon_osc  = aroon_up - aroon_down;

plot1(aroon_up,   "aroon_up");
plot2(aroon_down, "aroon_down");
plot3(aroon_osc,  "aroon_oscillator");
```

- 輸出全靠 `plotN(值, "名稱")`；**不下單、不 `ret`**。
- 函數見 `system-functions.md`（`BollingerBand`/`Average`/`NthHighestBar`/`NthLowestBar`）。
