# AGENTS.md

給 Codex 等 agent（含唯讀沙箱中的 code review）的專案指引。

## 專案

`xs-helper`：XQ 全球贏家 XScript（XS）的 Claude Code／Codex plugin。runtime 知識全在 `skills/xs/`（`SKILL.md` + `references/`）；`scripts/xs_lint.py` 是 stdlib-only 的 `.xs` 啟發式檢查；`tests/` 是 stdlib `unittest`。規格見 `docs/SPEC.md`，變更紀錄見 `CHANGELOG.md`。

## 驗證指令（零寫入，唯讀沙箱可跑）

以下指令都實測過不會在 repo 產生任何檔案，review 時請直接執行、不要只做靜態推導：

```sh
# 單元測試（-B 不寫 __pycache__）
python -B -m unittest discover -s tests

# lint 腳本煙霧測試（應 exit 0）
echo '{"tool_input":{"file_path":"x.xs"}}' | python -B scripts/xs_lint.py

# Markdown lint（全域安裝的 markdownlint-cli2；設定檔 .markdownlint-cli2.jsonc）
markdownlint-cli2 "skills/**/*.md" README.md CHANGELOG.md
```

**不要用** `uv run`、`uvx`、`pip`：它們需要寫入快取或虛擬環境，在唯讀沙箱一定失敗，失敗不代表程式有問題。`ruff`、`ty` 只能透過 `uvx` 執行，因此 review 環境裡無法跑，由維護者在本機補跑。

## 內容正確性

- XS 的函數、欄位、關鍵字以 XQ 官方 xshelp（<https://xshelp.xq.com.tw/XSHelp/>）為準。vscode-xs grammar 收錄的名稱不代表可用，例如 `Bool` `Int` `Float` `Double` 在 xshelp 標為保留字，見 `skills/xs/references/language.md` §9。
- 版本號要在 `.claude-plugin/plugin.json`、`.codex-plugin/plugin.json`、`.claude-plugin/marketplace.json` 三處一致，`tests/test_plugin_compatibility.py` 會檢查。
- xshelp 名稱索引 `skills/xs/references/xshelp-index.md` 由 `python -B scripts/xshelp_mirror.py fetch` 再 `python -B scripts/xshelp_mirror.py index` 重生；`fetch` 需要網路，唯讀 review 沙箱內不要執行。`fetch` 會拒絕覆寫成筆數變少或遺漏既有 id 的鏡像；確認是官方真的刪除條目時才加 `--allow-shrink` 覆蓋。
