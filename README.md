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
| **新手友善安裝** | 不會寫程式也能裝：照著下方[新手安裝指引](#完全不會寫程式跟著做就能裝)三步完成 |

## 設計邊界（Out of Scope）

本 plugin **只生成與解說，不執行**。明確不做：

- XS 腳本的實際執行 / 回測（不含 XS runtime）
- 完整語法分析 / LSP / grammar（Hook 僅啟發式檢查）
- 即時同步官方文件全量（reference 為人工蒸餾快照）
- XQ 平台帳號 / API 整合（不連帳號、不下單、不取報價）

## 安裝

本 plugin 透過 marketplace `xs-tools` 散佈。在 Claude Code 中：

```shell
/plugin marketplace add Benjamin-Teng/xs_helper
/plugin install xs-helper@xs-tools
```

安裝後輸入 `/xs` 即進入 XS 專家模式。

### 完全不會寫程式？跟著做就能裝

不需要任何程式基礎，照下面三步就能裝好。你唯一要做的就是「複製指令、貼上、按 Enter」。

**第 0 步：先有 Claude Code**

你得先在電腦裝好 **Claude Code**（Anthropic 的官方工具，本 plugin 就跑在它裡面）。
還沒有的話，到 [Claude Code 官方網站](https://www.claude.com/product/claude-code) 依指示安裝並登入。裝好後打開它，你會看到一個可以打字的對話框。

**第 1 步：加入本 plugin 的來源（marketplace）**

在 Claude Code 的對話框裡，把下面這行**整行複製貼上**，然後按 Enter：

```text
/plugin marketplace add Benjamin-Teng/xs_helper
```

這行的意思是「告訴 Claude Code 去 GitHub 上的 `Benjamin-Teng/xs_helper` 找這個 plugin」。成功的話它會回報已加入名為 `xs-tools` 的來源。

**第 2 步：安裝 plugin**

接著把下面這行整行貼上，再按 Enter：

```text
/plugin install xs-helper@xs-tools
```

看到安裝成功的訊息就完成了。（若它問你要不要信任 / 啟用，選同意即可。）

**第 3 步：確認裝好了**

在對話框輸入：

```text
/xs Average 怎麼用？
```

如果 Claude 開始依 XS 規範回答 `Average` 這個函數的用法，就代表安裝成功、可以開始用了 🎉。

> 卡住了？最常見原因是第 0 步的 Claude Code 還沒登入，或指令沒整行貼上（少了開頭的 `/`）。重貼一次通常就好。

### 使用方式（兩條路徑）

- **自動觸發（主要）**：不必打任何指令——只要對話講到 XS / 選股條件 / 某個函數怎麼用，Claude 會依 skill 的 `description` 自動載入 XS 知識再作答。
- **手動觸發**：輸入 `/xs <需求>`（依環境亦可能顯示為命名空間形式 `/xs-helper:xs`）。

> ⚠️ `/xs` 是**單次注入**、不是常駐模式：它把 XS 規範塞進「那一則」prompt，沒有「退出」指令。要徹底脫離 XS 脈絡用 `/clear` 重置對話即可。

## 狀態

✅ **v0.1.1** —— reference 全數蒸餾完成、`/plugin validate` 通過、可散佈；v0.1.1 補正欄位/函數命名的中英文與版本規則。功能仍在迭代。

📊 **成效**：[skill 助益量化報表](https://benjamin-teng.github.io/xs_helper/) —— 8 個真實 XS 任務「載 skill vs 未載」對照，通過率 100% vs 75%、零幻覺 token。

reference 進度：

| reference | 狀態 |
|-----------|------|
| `language.md`（語法基礎） | ✅ 已蒸餾（grammar token × Preset 真實語法校對） |
| `xs_lint.py` 已知 token 清單 | ✅ 啟用（604 個 token：grammar 2023 快照 ∪ Preset 215 sysfnc ∪ xshelp 8 群組 bif） |
| `system-functions.md`（sysfnc） | ✅ 已蒸餾（Preset 224 函數 × 14 分類） |
| `builtin-functions.md`（bif） | ✅ 已蒸餾（xshelp 8 分類） |
| `fields.md`（三類欄位） | ✅ 已蒸餾（xshelp `Q*`/`T*`/`F*` × XQStrategy `GetField` 交叉驗證） |
| `script-types.md` + `examples/` ×5 | ✅ 已蒸餾（5 類 `{@type:}` 結構/邊界 + 各一份精選範例） |

完整規格與交接見 [docs/SPEC.md](docs/SPEC.md)，版本變動見 [CHANGELOG.md](CHANGELOG.md)。

## 知識來源

reference 蒸餾自 XQ 官方範例庫與說明站：`XScript_Preset`、`XQStrategy`、`vscode-xs`、[xshelp 官方站](https://xshelp.xq.com.tw/XSHelp/)。

## License

[MIT](LICENSE)。本 plugin 只散佈自己撰寫的程式碼與「蒸餾後的 DSL 事實」，**不含**任何來源庫的原始 `.xs`（`XScript_Preset` / `XQStrategy` 無授權檔，故未 bundle；見 [docs/SPEC.md](docs/SPEC.md) Open Q5）。
