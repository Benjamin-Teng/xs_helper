# Codex 對話式安裝文件設計

## 背景

目前文件只提供 `codex plugin ...` 終端機指令，但多數 Codex 使用者會從 VS Code IDE extension 的對話視窗開始。依目前官方介面，完整 plugin 不支援 IDE extension；IDE extension 支援獨立 skill，並可透過 `$skill-installer` 從 GitHub 安裝。

`xs-helper` 現階段只有一個共享的 `xs` skill，沒有 MCP server、connector 或 hook，因此 IDE 使用者安裝獨立 skill 不會缺少目前功能。完整 plugin 封裝仍保留給 Codex CLI 與支援 plugin 的桌面介面。

## 目標

- 讓 VS Code／Codex IDE 使用者不需先理解 shell 指令即可從對話視窗安裝。
- 明確區分「獨立 skill 安裝」與「完整 plugin 安裝」，不暗示 IDE extension 支援 plugin。
- 保留既有 Claude Code 安裝方式與橘色視覺識別。
- 保留 Codex plugin marketplace、manifest 與 CLI 安裝能力。
- 在所有產品文件與 GitHub Pages 使用一致的命令、介面名稱和驗證方式。

## 安裝入口

### 1. VS Code／Codex IDE（推薦）

文件首先呈現可直接貼入 Codex 對話框的提示：

```text
$skill-installer 請從 https://github.com/Benjamin-Teng/xs_helper/tree/main/skills/xs 安裝 xs skill
```

使用者核准下載後，開啟新對話；若 skill 未出現，重新載入 VS Code。使用 `$xs Average 怎麼用？` 驗證，也可直接提出 XS 需求讓 Codex 隱式載入。

### 2. Codex CLI 對話介面

自訂 GitHub marketplace 必須先註冊一次：

```shell
codex plugin marketplace add Benjamin-Teng/xs_helper
```

之後啟動 `codex`，在互動對話輸入 `/plugins`，切換到 `xs-tools` marketplace、開啟 `xs-helper`、選擇安裝，再開始新 session。這是完整 plugin 安裝。

### 3. Codex 終端機進階安裝

保留適合腳本化或熟悉 CLI 的完整指令：

```shell
codex plugin marketplace add Benjamin-Teng/xs_helper
codex plugin add xs-helper@xs-tools
```

安裝後開啟新 Codex session，使用 `$xs Average 怎麼用？` 驗證。

## 文件與發布頁調整

- `README.md`：Codex 安裝改為三入口，IDE 對話式流程置頂。
- `docs/index.html`：Codex 卡片先顯示 VS Code 對話式安裝，再提供 CLI plugin 流程；Claude Code 卡片維持橘色，Codex 區維持青色。
- `docs/SPEC.md` 與 `docs/architecture.md`：記錄 surface 能力差異與兩種安裝產物。
- `CHANGELOG.md`：補充 v0.3.0 的 IDE skill 安裝方式與 plugin surface 限制。
- 既有相容性測試：加入 `$skill-installer`、GitHub skill 路徑、`/plugins` 與 IDE 限制文字的覆蓋；保留所有既有 Claude 與 Codex plugin 斷言。

## 錯誤處理與邊界

- `$skill-installer` 若未立即顯示新 skill，指示重新載入 VS Code 或重啟 Codex，而不是改用不存在的 IDE plugin browser。
- 文件不得聲稱 terminal plugin 安裝會讓 plugin 出現在 IDE extension。
- 未來若 plugin 新增 MCP、connector 或 hook，必須重新評估 IDE skill 路徑是否仍具功能等價性。
- 不改動 `skills/xs/` 的工作流程與 reference，也不移除 Claude Code 或 Codex plugin 封裝。

## 驗證

- 標準函式庫測試確認所有產品文件包含 IDE 對話式安裝提示與完整 plugin 指令。
- 發布頁測試確認 Codex 區有 IDE、CLI 對話與進階終端機三個入口。
- 瀏覽器檢查桌面與手機版 modal，確認長提示可換行、複製按鈕可用、平台色彩不回歸。
- 重新執行完整 Python 測試、Claude plugin validator、Codex plugin validator 與 Codex skill validator。
