# xs_helper

> 一個 Claude Code plugin，讓 Claude 依 **XQ全球贏家** 的 **XScript（XS）** 語言規範，協助你撰寫自動化腳本、回答 XS 用法問題。

## 這是什麼

`xs_helper` 是一個 [Claude Code](https://docs.claude.com/en/docs/claude-code) plugin。在 Claude Code 輸入 `/xs` 即進入「XS 專家模式」，Claude 會載入內建的 XS 語言規範後再作答，協助你：

1. **撰寫 / 修改 XS 腳本** —— 自動交易、函數、指標、選股、警示五大類型；
2. **回答規範性問題** —— 某個 XS 函數 / 欄位 / 關鍵字怎麼用。

### 為什麼需要它

XS 是 XQ全球贏家專屬、繁體中文、小眾的 DSL，沒有公開的編譯器或 LSP，Claude 模型本身**不具備 XS 知識**。本 plugin 把 XS 的語法、內建函數、欄位、各腳本類型慣例，以蒸餾後的 reference 形式內建進 skill，讓 Claude 被呼叫時載入正確知識再回答，**避免幻覺出不存在的函數**。

## 功能

| 功能 | 說明 |
|------|------|
| **`/xs` Skill** | 判定腳本類型 → 載入對應 reference → 產出 XS 程式碼或規範解說 |
| **內建 XS Reference** | 語法、內建函數、系統函數、欄位、腳本類型慣例，皆內建為 markdown |
| **官方文件 Fallback** | 冷門函數 / 欄位以 WebFetch 查 [XS 線上說明](https://xshelp.xq.com.tw/XSHelp/) 後作答 |
| **`.xs` 編輯驗證 Hook** | 編輯 `.xs` 檔時對未知函數 / 明顯結構問題提出非阻斷式警示 |

## 設計邊界（Out of Scope）

本 plugin **只生成與解說，不執行**。明確不做：

- XS 腳本的實際執行 / 回測（不含 XS runtime）
- 完整語法分析 / LSP / grammar（Hook 僅啟發式檢查）
- 即時同步官方文件全量（reference 為人工蒸餾快照）
- XQ 平台帳號 / API 整合（不連帳號、不下單、不取報價）

## 狀態

🚧 **SPEC 階段** —— 規格已定案，尚未進入實作。完整規格見 [docs/SPEC.md](docs/SPEC.md)。

## 知識來源

reference 蒸餾自 XQ 官方範例庫與說明站：`XScript_Preset`、`XQStrategy`、`vscode-xs`、[xshelp 官方站](https://xshelp.xq.com.tw/XSHelp/)。

## License

待定（見 SPEC Open Questions：範例庫授權待查）。
