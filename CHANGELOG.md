# Changelog

本檔記錄 `xs-helper` plugin 對外可見的版本變動，格式參考 [Keep a Changelog](https://keepachangelog.com/)，版本遵循 [Semantic Versioning](https://semver.org/)。

開發迭代期（無 tag）以 commit SHA 作版本；自 v0.1.0 起正式起 semver。

## [0.1.0] - 2026-05-31

首個正式發行版本，plugin 達可散佈狀態。

### Added

- **`/xs` Skill** — XS 專家模式：判定腳本類型 → 載入對應 reference → 產出 XS 程式碼或規範解說，含官方文件 F3 fallback 指示與硬邊界。
- **內建 XS Reference**（蒸餾自 XQ 官方範例庫與說明站）：
  - `language.md` — grammar 五類 token × Preset 真實語法校對，`intraBarPersist` 列一級概念。
  - `system-functions.md` — Preset 224 個 sysfnc × 官方 14 分類。
  - `builtin-functions.md` — xshelp 8 分類內建函數。
  - `fields.md` — 報價 `Q*` / 資料 `T*` / 選股 `F*` 三類欄位，× XQStrategy `GetField` 交叉驗證。
  - `script-types.md` + `examples/*.md` ×5 — 五類 `{@type:}` 腳本結構/觸發模型/邊界 + 各一份精選範例。
- **`.xs` 編輯驗證 Hook**（`PostToolUse: Write|Edit` → `xs_lint.py`）：對照 604 個 token（grammar 2023 快照 ∪ Preset 215 sysfnc ∪ xshelp 8 群組 bif）的啟發式檢查，對未收錄函數與明顯結構問題提出非阻斷式警示。
- **散佈基礎建設**：`.claude-plugin/marketplace.json`（marketplace `xs-tools`）、`plugin.json` 起 semver `0.1.0`、MIT LICENSE。

[0.1.0]: https://github.com/Benjamin-Teng/xs_helper/releases/tag/v0.1.0
