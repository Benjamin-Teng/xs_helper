# Changelog

本檔記錄 `xs-helper` plugin 對外可見的版本變動，格式參考 [Keep a Changelog](https://keepachangelog.com/)，版本遵循 [Semantic Versioning](https://semver.org/)。

開發迭代期（無 tag）以 commit SHA 作版本；自 v0.1.0 起正式起 semver。

## [0.3.0] - 2026-08-04

### Added

- **Codex 原生 plugin 支援**：新增 `.codex-plugin/plugin.json`、`.agents/plugins/marketplace.json` 與 `$xs` skill UI metadata；Claude Code 與 Codex 共用同一份 `skills/xs/`。
- **Codex 安裝**：`codex plugin marketplace add Benjamin-Teng/xs_helper` → `codex plugin add xs-helper@xs-tools`。

### Changed

- **Claude Code 安裝維持相容**：`/plugin marketplace add Benjamin-Teng/xs_helper` → `/plugin install xs-helper@xs-tools` → `/reload-plugins`，並以 `/xs` 手動觸發。
- F3 fallback 改為平台中立的網頁查詢指示；README、GitHub Pages、SPEC 與架構文件加入雙平台說明。

## [0.2.0] - 2026-06-02

### Removed

- **`.xs` 編輯驗證 Hook**（`PostToolUse: Write|Edit` → `xs_lint.py`）：移除自動觸發的 hook。
  原因：hook 以 `python` 執行腳本，但目標使用者（XQ 全球贏家交易者，多為 Windows、非開發者）機器上常無 Python 或 `python` 不在 PATH；hook 掛 `Write|Edit` 不限副檔名，導致這些使用者**每次存檔都跳 PostToolUse 錯誤**，傷害遠大於離線 lint 的邊際價值。
  `scripts/xs_lint.py`（604 token 啟發式檢查）保留為獨立腳本，供 benchmark 幻覺掃描與手動檢查使用，僅不再自動掛載。

## [0.1.1] - 2026-05-31

reference 校正與新手友善文件；新增對外量化報表（GitHub Pages）。

### Fixed

- **`fields.md` / `builtin-functions.md`** — 補正欄位/函數命名規則（經官方 xshelp 一手查證）：
  - 欄位/資訊函數家族（`GetField` / `GetSymbolField` / `GetSymbolInfo` / `GetQuote` + `*Date`/`Check*`/`IsSupport*` 變體）欄位名**中文或英文皆可**，立為全家族通則（先前 reference 僅示中文，易誤導偏好中文）。
  - 反例標注：`GetInfo` 只吃固定英文關鍵字、`GetSymbolGroup` 清單類型用中文名。
  - `CallFunction` 標 `⚠️ 版本相關`：自 **v6.20** 起函數可用中文名，且中文名函數須透過 `CallFunction` 呼叫；並立「版本分水嶺以 `vX.XX` 標注」之 reference 慣例。

### Added

- **量化助益報表**（`docs/index.html`，GitHub Pages）：以 skill-creator 評測流程跑 8 個真實 XS 任務（載 skill vs baseline），呈現通過率、幻覺防護、腳本類型標記等差距。
- **README 新手安裝指引** — 完全不會寫程式也能照著裝。

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

[0.3.0]: https://github.com/Benjamin-Teng/xs_helper/releases/tag/v0.3.0
[0.2.0]: https://github.com/Benjamin-Teng/xs_helper/releases/tag/v0.2.0
[0.1.1]: https://github.com/Benjamin-Teng/xs_helper/releases/tag/v0.1.1
[0.1.0]: https://github.com/Benjamin-Teng/xs_helper/releases/tag/v0.1.0
