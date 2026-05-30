# 範例：選股（filter）

> 蒸餾自 `XQStrategy/`（四市場庫）＋ `XScript_Preset/選股/00.語法範例/`。
> 型別 / 邊界 / 跨市場差異見 `script-types.md §2`、欄位見 `fields.md`。

## 基本結構（`GetField` + `ret`）

```xs
{@type:filter}
// GetField 第 1 參數＝欄位中文名，第 2 參數＝期別（D/W/M/Q/Y），省略則用執行頻率
Ret = GetField("每股稅後淨利(元)", "Y") > 5;       // 最新年度 EPS > 5 元 → 入選
```

## 帶可調參數 + 輸出欄（台股，站上 N 期均價）

```xs
{@type:filter}
input: N(5); SetInputName(1, "期別");
SetTotalBar(3);                                  // 回看資料筆數

Value1 = Average(GetField("Close"), N);
if GetField("Close") > Value1 then ret = 1;      // 股價 > N 期均價

SetOutputName1("均價");
OutputField1(Value1);                            // 結果表多顯示一欄「均價」
```

## 跨市場：美股成交量創 N 期新低

> 來源：`XQStrategy/04美股的選股條件/01常用/成交量/成交量創N期新低.xs`。
> 四市場（台 / 陸 / 港 / 美）語法一致，差異只在**可用欄位與欄位中文名**。

```xs
{@type:filter}
input: N(2);
SetTotalBar(3);
if GetField("成交量") < Lowest(GetField("成交量")[1], N) then ret = 1;
SetOutputName1("成交量");
OutputField1(GetField("成交量"));
```

- `ret = 1`＝此檔**入選**（與 sensor 的「觸發警示」寫法同、意義不同）。
- **限選股 / 資料欄位**；禁下單函數；無盤中即時 tick（`GetQuote` 不適用）。
- 冷門欄位（`fields.md` 未收）走 SKILL.md F3 線上查證，不杜撰。
