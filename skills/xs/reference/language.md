# XS 語言基礎（language）

> 🚧 骨架佔位 — 待蒸餾。
> **來源**：grammar `keyword.control` / `keyword.skipword` / `keyword.operator` / `variable.*`（離線 token），
> 名單以 xshelp「關鍵字」分類為準校對（grammar 為 2023 快照，可能落後）。

## 待蒸餾內容

- [ ] **宣告**：`Variable/Var/Vars`、`Input/Inputs`、`Array/Arrays`、型別（`Numeric*`/`String*`/`TrueFalse*`/`Bool/Int/Float/Double`）、`retval/ret/retmsg`
- [ ] **流程控制**：`if/then/else`、`begin/end`、`for/to/downto`、`while`、`repeat/until`、`switch/case/default`、`once`、`break/return`
- [ ] **運算子**：`+ - * / =`、`<= >= <>`、`+= -=`、邏輯 `and/or/not/xor`、關係 `cross above/below`、`over/under`
- [ ] **內建變數**：`Value1..N`、`Condition1..N`、`Position`、`Filled`
- [ ] **常數**：`PI`、`Monday`..`Sunday`
- [ ] **註解語法**：`// 行註解`、`{ 區塊註解 }`
- [ ] ⭐ **`intraBarPersist`** 變數修飾子（逐筆洗價回捲語意）— 一級概念，附「一般變數 vs intraBarPersist」對比表
- [ ] **忽略字（skipword）**：`A/An/At/By/Of/On/The…`（提升可讀性的語法糖）
