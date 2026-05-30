---
name: xs
description: >-
  XScript (XS) 專家模式 — 依 XQ 全球贏家自行開發的 XScript 語言規範，協助使用者撰寫或修改
  自動交易、函數、指標、選股、警示這五類 XS 腳本，並回答「某個 XS 函數 / 欄位 / 關鍵字怎麼用」。
  當對話出現以下任一情境時使用本 skill：提到 XS、XScript、XQ、全球贏家、.xs 檔；要寫
  選股條件 / 自動交易腳本 / 技術指標腳本 / 警示條件；問到 XS 的函數、欄位、關鍵字、語法；
  出現 SetPosition、GetField、Plot、ret=1、洗價、intraBarPersist、{@type:} 等 XS 專屬語彙。
---

# XS 專家模式

> ⚠️ 骨架階段：以下流程已定，`reference/` 內容尚待蒸餾（見各檔 TODO）。在 reference 補齊前，
> 函數 / 欄位 / 簽名一律走線上查證（F3 Fallback），不得憑記憶杜撰。

依 XQ 全球贏家的 **XScript（XS）** 規範作答。XS 是券商專屬 DSL，**不得**用你對其他語言的直覺臆測函數名或欄位名——只用 reference 收錄、或經 F3 線上查證確認存在的 token。

## 工作流程

1. **判定腳本類型**（5 類，對應原始碼 `{@type:}` 標記）：
   | 類型 | `{@type:}` | 特徵 |
   |------|-----------|------|
   | 自動交易 | `autotrade` | 用 `SetPosition` 下單；需控管第一次洗價 |
   | 函數 | `function` | 被呼叫才執行；`retval` 回傳 |
   | 指標 | `indicator` | `Plot` 畫線 |
   | 選股 | `filter` | `ret=1` 篩選；`GetField("中文欄位")` |
   | 警示 | `sensor` | `Alert` 通知；靠觸發設定去重 |

   類型不明確時**反問**，不要猜。選股情境再問目標市場（台股/陸股/港股/美股），影響可用欄位。

2. **載入對應 reference**（依需求只讀需要的檔，避免一次全載）：
   - [language.md](reference/language.md) — 關鍵字、流程控制、運算子、內建變數
   - [builtin-functions.md](reference/builtin-functions.md) — 內建函數（bif）
   - [system-functions.md](reference/system-functions.md) — 系統函數（sysfnc）
   - [fields.md](reference/fields.md) — 報價 / 資料 / 選股 三類欄位
   - [script-types.md](reference/script-types.md) — 5 類結構與可用 / 禁用函數邊界
   - [examples/](reference/examples/) — 每類型一份精選範例

3. **產出**：
   - **腳本生成**：可直接貼回 XQ Script Editor 的 XS 程式碼，開頭帶正確 `{@type:}`，附簡短說明用到哪些函數 / 欄位。
   - **規範問答**：函數 / 欄位的官方定義（簽名、參數、回傳）＋ 一個最小可用範例。

## F3 Fallback（冷門查詢）

reference 未涵蓋的函數 / 欄位 → 以 WebFetch 查 XSHelp 官方站，查得後在回覆標明「此為線上查詢結果」：

- 清單頁：`https://xshelp.xq.com.tw/XSHelp/lists?a=<代碼>`
  （函數：`GENERALFUNC` 等；資料欄位：`TBASIC`/`TPRICE`/`TVOLUME`/`TCHIP`…；選股欄位：`FBASIC`/`FFINANCE`/`FOFTEN`…）
- 細節頁：`https://xshelp.xq.com.tw/XSHelp/?HelpName=<名稱>&group=<代碼>`（中文名需 URL-encode）

查無此函數 → 明確告知「查無，可能版本差異或拼寫」，**不杜撰**。

## 硬邊界（不得逾越）

- 不執行 / 回測 XS；只生成與解說。
- 不臆測不存在的函數 / 欄位。
- 不連 XQ 帳號、不下單、不取即時報價。
