# 五種腳本類型（script types）

> 🚧 骨架佔位 — 待蒸餾。
> **來源**：Preset/Strategy 各類型 `{@type:}` 範例的結構慣例；觸發模型見記憶
> `xs-execution-trigger-model`。每類型須列：結構慣例、可用 / 禁用函數邊界、觸發模型。

## 待蒸餾內容

| 類型 | `{@type:}` | 觸發模型 | 結構慣例（待補） | 邊界（待補） |
|------|-----------|---------|------|------|
| 自動交易 | `autotrade` | 即時，換棒必觸發+洗價疊加，**控管第一次洗價** | `SetPosition` 主導 | 禁選股欄位 |
| 函數 | `function` | 被呼叫才執行 | `input:` + `retval=` | 不下單 |
| 指標 | `indicator` | 每棒運算，盤中逐 Tick 重畫 | `Plot[n]` / `SetPlotLabel` | 不下單 |
| 選股 | `filter` | 排程/單次洗價，非即時 Tick | `input:` + `ret=1` + `GetField` + `OutputField`/`SetTotalBar` | 限選股/資料欄位、禁下單函數 |
| 警示 | `sensor` | 即時，換棒必觸發+洗價疊加，觸發設定去重 | `Alert(...)` | 不下單 |

## 待補重點

- [ ] 每類型一段最小可用骨架（含正確 `{@type:}` 表頭）
- [ ] ⭐ 自動交易：第一次洗價控管慣例（`if CurrentBar...` / 換 Bar 重設）
- [ ] ⭐ 涉及盤中累計：必用 `intraBarPersist`（見 language.md）
- [ ] 選股 vs 即時腳本的欄位可用性邊界（交叉引用 fields.md）
