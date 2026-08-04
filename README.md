# xs_helper

> 一個同時支援 Claude Code 與 Codex 的 plugin，依 **XQ全球贏家** 的 **XScript（XS）** 語言規範，協助你撰寫自動化腳本、回答 XS 用法問題。

## 這是什麼

`xs_helper` 是一個 [Claude Code](https://docs.claude.com/en/docs/claude-code) 與 [Codex](https://developers.openai.com/codex/) plugin。在 Claude Code 輸入 `/xs`，或在 Codex 使用 `$xs`，即可載入「XS 專家模式」後再作答，協助你：

1. **撰寫 / 修改 XS 腳本** —— 自動交易、函數、指標、選股、警示五大類型；
2. **回答規範性問題** —— 某個 XS 函數 / 欄位 / 關鍵字怎麼用。

### 為什麼需要它

XS 是 XQ全球贏家專屬、繁體中文、小眾的 DSL，沒有公開的編譯器或 LSP，通用模型本身**不具備完整 XS 知識**。本 plugin 把 XS 的語法、內建函數、欄位、各腳本類型慣例，以蒸餾後的 reference 形式內建進 skill，讓 AI agent 被呼叫時載入正確知識再回答，**避免幻覺出不存在的函數**。

## 功能

| 功能 | 說明 |
|------|------|
| **XS Skill（`/xs` / `$xs`）** | 判定腳本類型 → 載入對應 reference → 產出 XS 程式碼或規範解說 |
| **內建 XS Reference** | 語法、內建函數、系統函數、欄位、腳本類型慣例，皆內建為 markdown |
| **官方文件 Fallback** | 冷門函數 / 欄位以環境可用的網頁查詢工具查 [XS 線上說明](https://xshelp.xq.com.tw/XSHelp/) 後作答 |

## 設計邊界（Out of Scope）

本 plugin **只生成與解說，不執行**。明確不做：

- XS 腳本的實際執行 / 回測（不含 XS runtime）
- 完整語法分析 / LSP / grammar（不重建編譯器級驗證）
- 即時同步官方文件全量（reference 為人工蒸餾快照）
- XQ 平台帳號 / API 整合（不連帳號、不下單、不取報價）

## 安裝

本 plugin 透過 marketplace `xs-tools` 散佈；Claude Code 與 Codex 共用同一份 XS skill 與 reference。

### Claude Code

在 Claude Code 中執行：

```shell
/plugin marketplace add Benjamin-Teng/xs_helper
/plugin install xs-helper@xs-tools
/reload-plugins
```

> `/reload-plugins` 讓剛裝好的 plugin 立即生效，不必重開 Claude Code。安裝後以 `/xs <需求>` 明確觸發。

### Codex

在終端機執行：

```shell
codex plugin marketplace add Benjamin-Teng/xs_helper
codex plugin add xs-helper@xs-tools
```

安裝後開啟新的 Codex 對話，輸入 `$xs <需求>` 明確觸發。Codex CLI 或 IDE 也可先輸入 `/skills` 查看已載入的 skill。

### 使用方式（兩條路徑）

- **自動觸發（主要）**：不必打任何指令——只要對話講到 XS / 選股條件 / 某個函數怎麼用，Claude Code 或 Codex 會依 skill 的 `description` 自動載入 XS 知識再作答。
- **Claude Code 手動觸發**：輸入 `/xs <需求>`（依環境亦可能顯示為命名空間形式 `/xs-helper:xs`）。
- **Codex 手動觸發**：輸入 `$xs <需求>`。

> ⚠️ `/xs` 與 `$xs` 都是把 XS 規範載入目前請求或對話脈絡，不是另一個 XS runtime；要徹底脫離 XS 脈絡，請開新對話或使用所在環境的清除對話功能。

## 狀態

✅ **v0.3.0** —— 同時提供 Claude Code 與 Codex 原生 manifest / marketplace，兩端共用同一份 skill；Codex plugin 與 skill validator 通過。v0.2.0 移除的 `.xs` 編輯驗證 Hook 維持不掛載，`xs_lint.py` 保留為獨立腳本。功能仍在迭代。

📊 **成效**：[skill 助益量化報表](https://benjamin-teng.github.io/xs_helper/) —— 8 個真實 XS 任務「載 skill vs 未載」對照，通過率 100% vs 75%、零幻覺 token。

reference 進度：

| reference | 狀態 |
|-----------|------|
| `language.md`（語法基礎） | ✅ 已蒸餾（grammar token × Preset 真實語法校對） |
| `xs_lint.py` 已知 token 清單 | ✅ 內建（604 個 token：grammar 2023 快照 ∪ Preset 215 sysfnc ∪ xshelp 8 群組 bif）；供 benchmark 幻覺掃描與手動檢查的獨立腳本 |
| `system-functions.md`（sysfnc） | ✅ 已蒸餾（Preset 224 函數 × 14 分類） |
| `builtin-functions.md`（bif） | ✅ 已蒸餾（xshelp 8 分類） |
| `fields.md`（三類欄位） | ✅ 已蒸餾（xshelp `Q*`/`T*`/`F*` × XQStrategy `GetField` 交叉驗證） |
| `script-types.md` + `examples/` ×5 | ✅ 已蒸餾（5 類 `{@type:}` 結構/邊界 + 各一份精選範例） |

完整規格與交接見 [docs/SPEC.md](docs/SPEC.md)，版本變動見 [CHANGELOG.md](CHANGELOG.md)。

## 知識來源

reference 蒸餾自 XQ 官方範例庫與說明站：`XScript_Preset`、`XQStrategy`、`vscode-xs`、[xshelp 官方站](https://xshelp.xq.com.tw/XSHelp/)。

## License

[MIT](LICENSE)。本 plugin 只散佈自己撰寫的程式碼與「蒸餾後的 DSL 事實」，**不含**任何來源庫的原始 `.xs`（`XScript_Preset` / `XQStrategy` 無授權檔，故未 bundle；見 [docs/SPEC.md](docs/SPEC.md) Open Q5）。
