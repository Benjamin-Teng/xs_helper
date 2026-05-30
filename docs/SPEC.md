# xs_helper — Project Spec

## 版本資訊

| 欄位 | 內容 |
|------|------|
| 版本 | v1.1 |
| 基於 | v1（首次定義） |
| 建立日期 | 2026-05-30 |
| 修改日期 | 2026-05-30 |
| 動機 | v1 首次定義：一個 Claude Code plugin，讓 Claude 能依 XQ全球贏家的 XScript（XS）語言規範，協助使用者撰寫自動化腳本、回答 XS 用法問題。v1.1（實作 session）：收斂全部 Open Questions、折入來源探勘校正、建立 plugin 骨架，詳見文末「實作進度（Session 交接）」。 |
| 前提 | Claude 模型本身不具備 XS 知識；XS 為 XQ 專屬 DSL，無公開編譯器 / LSP，知識來源為三個官方 GitHub 範例庫＋官方說明站 |

---

### Overview

`xs_helper` 是一個 **Claude Code plugin**。使用者在 Claude Code 輸入 `/xs`，即進入「XS 專家模式」：Claude 會依據 XQ全球贏家自行開發的 **XScript（XS）** 語言規範，協助使用者

1. 撰寫 / 修改 XS 自動化腳本（自動交易、選股、指標、警示、函數五大類型其一）；
2. 回答「某個 XS 函數 / 欄位 / 關鍵字怎麼用」這類規範性問題。

核心難點：Claude 原生不認識 XS（小眾、繁中、券商專屬 DSL）。因此本 plugin 的本質是**把 XS 的語法、內建函數、欄位、各腳本類型慣例，以蒸餾後的 reference 形式內建進 skill**，讓 Claude 在被呼叫時載入正確知識後再作答，避免幻覺出不存在的函數。

**使用對象**：使用 XQ全球贏家、需要撰寫 / 維護 XS 腳本，且在 Claude Code 環境工作的量化 / 程式交易使用者（即本專案作者本人為首要使用者）。

---

### Goals

- **G1（不幻覺）**：`/xs` 產生或引用的 XS 函數 / 欄位 / 關鍵字，**100% 存在於內建 reference 清單**，不得編造。
- **G2（類型正確）**：產出的腳本符合「使用者指定腳本類型」的結構與可用函數限制（例：選股腳本不得用自動交易專屬的下單函數）。
- **G3（規範問答）**：使用者問「XX 函數怎麼用」時，Claude 能依官方定義回答簽名、參數、回傳與一個可用範例。
- **G4（低摩擦）**：使用者只需 `/xs` 一個入口，不需要記得貼語法手冊；冷門查詢由 plugin 自動 fallback 到官方文件。
- **G5（可驗證）**：編輯 `.xs` 檔時，hook 能對未知函數 / 明顯語法問題提出警示。

---

### Features

#### F1. `/xs` Skill — XS 專家模式（核心）

- 使用者輸入 `/xs <自然語言需求>`，Claude：
  1. 判定使用者要的**腳本類型**（自動交易 / 函數 / 指標 / 選股 / 警示），不明確時反問；
  2. 載入對應的 reference（語法 + 該類型可用函數 + 範例）；
  3. 產出 XS 程式碼，或回答規範問題。
- **行為契約**：使用者做 A（描述需求或提問）→ 系統做 B（載入 reference、依規範生成 / 解說）→ 結果 C（一段可貼回 XQ Script Editor 的 XS 程式碼，或一段帶官方定義與範例的解說）。
- **啟動路徑（雙路徑）**：
  1. **手動**：使用者輸入 `/xs`，確定性觸發。
  2. **自動**：Claude 依 SKILL.md 的 `description` 作**語意判斷**自行載入——非字面 keyword 比對。因此 `description` 必須明確列出觸發詞（`XS / XScript / XQ / 全球贏家 / .xs / 選股條件 / 自動交易腳本…`），這是自動觸發命中率的關鍵，也是整個 skill 最重要的一行。
  - 注意：自動觸發為**機率性**，description 寫好命中率高但非 100% 保證；若需「保證觸發」須改用 Hook（見 Open Q2 路線 B）。

#### F2. 內建 XS Reference（knowledge base）

蒸餾自三個範例庫＋官方說明站，以 markdown 內建於 skill。分檔：

- `language.md`：關鍵字、流程控制（`if/then/begin/end` 等）、宣告、運算子、內建變數（`value1`…）。
- `builtin-functions.md`：內建函數（general/time/date/string/math/field/array/transaction）。
- `system-functions.md`：系統函數（價格、技術指標、統計、趨勢、邏輯判斷、選擇權、跨週期、成交量…）。
- `fields.md`：三類欄位（報價欄位 / 資料欄位 / 選股欄位）及其適用情境。
- `script-types.md`：五種腳本類型各自的結構慣例、可用 / 禁用函數邊界。
- `examples/`：每類型一份精選範例（自動交易 / 函數 / 指標 / 選股 / 警示），標註出處。

#### F3. 官方文件 Fallback

當需求涉及 reference 未涵蓋的冷門函數 / 欄位，SKILL.md 指示 Claude 以 WebFetch 查詢 `https://xshelp.xq.com.tw/XSHelp/` 對應子頁，再作答；查得後在回覆中標明「此為線上查詢結果」。

#### F4. `.xs` 編輯驗證 Hook

- `PostToolUse` 掛在 `Write|Edit`，比對被編輯檔名是否為 `*.xs`；
- 命中時執行驗證腳本，對照內建「已知 token 清單」，對**未知函數名**與**明顯結構問題**（如 `if` 缺 `then`、`begin/end` 不成對）提出非阻斷式警示。
- 限制：因 XS 無公開 grammar / 編譯器，此為**啟發式檢查**，非完整語法驗證（見 Out of Scope）。

---

### Input / Output

#### Input

| 欄位 | 型別 | 必填 | 備註 |
|------|------|------|------|
| `/xs` 後的自然語言需求 | string | 是 | 撰寫需求或規範問題 |
| 腳本類型 | enum(自動交易/函數/指標/選股/警示) | 否 | 未提供時由 Claude 推斷或反問 |
| 目標市場（選股情境） | enum(台股/陸股/港股/美股) | 否 | 影響可用選股欄位與範例選取 |
| 被編輯的 `.xs` 檔（Hook 觸發） | file path | — | 由 PostToolUse 事件提供，非使用者手動輸入 |

#### Output

- **腳本生成**：一段 XS 程式碼（可直接貼回 XQ Script Editor），附簡短說明使用了哪些函數 / 欄位。
- **規範問答**：函數 / 欄位的官方定義（簽名、參數、回傳）＋ 一個最小可用範例。
- **Hook 警示**：在 PostToolUse 後輸出警示文字，列出未知 token / 結構疑點；無問題則靜默。
- **錯誤狀態**：需求類型無法判定 → 反問；查詢的函數連官方文件都查無 → 明確告知「查無此函數，可能為版本差異或拼寫」，不杜撰。

---

### Out of Scope

明列**不做**的事，實作時不得自行補完：

- **XS 腳本的實際執行 / 回測**：本 plugin 不含 XS runtime，只生成與解說，不保證在 XQ 平台上的執行結果。
- **完整語法分析 / LSP / grammar**：vscode-xs 只做上色、無正式 grammar，本專案不重建編譯器級驗證；Hook 僅做啟發式檢查。
- **即時同步官方文件全量**：reference 為人工蒸餾的快照，不建立自動全量爬蟲同步（冷門查詢走 F3 fallback 即可）。
- **超出三個來源庫範圍的市場 / 功能**：來源未涵蓋者不臆測補完。
- **XQ 平台帳號 / API 整合**：本 plugin 不連 XQ 帳號、不下單、不取即時報價。

> **AI Agentic Dev 注意：** 以上為 Claude 的硬邊界。凡未列在 Features 且落在此節者，即使看似合理也不得自行實作。

---

### Tech Stack

| 層級 | 選擇 | 備註 |
|------|------|------|
| Plugin 形態 | Claude Code 官方 plugin | manifest 在 `.claude-plugin/plugin.json` |
| 知識交付 | 內建 markdown reference ＋ WebFetch fallback（混合制） | 核心架構；非 RAG、非外部 DB |
| Skill 內容 | 純 markdown（SKILL.md + reference/*.md） | 無 runtime 相依 |
| Hook 腳本 | Python 3 stdlib（零第三方相依）**（待確認，見 Open Q4）** | 以 `${CLAUDE_PLUGIN_ROOT}` 定位；跨平台 |
| Reference 來源 | XScript_Preset / XQStrategy / vscode-xs / xshelp 官方站 | 實作階段 clone 到 `sources/` 後蒸餾 |
| Docker | **否** | plugin 為 markdown + 輕量腳本，無容器化需求（已依規則評估） |
| 散佈方式 | skills-dir / local plugin（自用優先）**（待確認，見 Open Q6）** | 是否做 marketplace.json 待定 |

> **AI Agentic Dev 注意：** Tech Stack 在第一個檔案產生前定案；標「待確認」者須在實作 session 開頭先收斂，不得逕自選擇。

---

### Project Structure

```
xs_helper/
├── .claude-plugin/
│   └── plugin.json              # manifest（唯一放這層的檔）
├── skills/
│   └── xs/
│       ├── SKILL.md             # /xs 入口：判類型、載 reference、生成/解說、fallback 指示
│       └── reference/
│           ├── language.md
│           ├── builtin-functions.md
│           ├── system-functions.md
│           ├── fields.md
│           ├── script-types.md
│           └── examples/
│               ├── auto-trade.md   # 自動交易
│               ├── function.md     # 函數
│               ├── indicator.md    # 指標
│               ├── screening.md    # 選股
│               └── alert.md        # 警示
├── hooks/
│   └── hooks.json               # PostToolUse: Write|Edit → xs_lint
├── scripts/
│   └── xs_lint.py               # .xs 啟發式驗證（對照已知 token 清單）
├── sources/                     # 實作階段 clone 三個範例庫於此（蒸餾輸入，gitignore）
├── docs/
│   └── SPEC.md                  # 本檔
├── README.md
├── CHANGELOG.md
└── LICENSE
```

> **AI Agentic Dev 注意：** 元件目錄（skills/、hooks/、scripts/）一律放 plugin 根目錄，**不得**放進 `.claude-plugin/`，否則載入不到。

---

### Naming Conventions

- 檔案：`kebab-case.md`（reference 與 examples）、`snake_case.py`（腳本）。
- Skill 目錄：小寫（`xs/`）；skill 名取自 SKILL.md frontmatter `name`。
- XS 範例檔內容：保留 XS 原生大小寫慣例（如 `Average`、`CurrentBar`），不改寫。
- reference 內函數條目格式統一：`名稱 / 簽名 / 參數 / 回傳 / 範例 / 來源`。

---

### Acceptance Criteria

- **AC1**：安裝後輸入 `/xs`，skill 被觸發且 XS context 被載入（`/plugin validate` 通過、`plugin.json` 含必填 `name`）。
- **AC2**：輸入「幫我寫一個『連續三天放量上漲』的台股選股條件」，產出的 XS 只使用 reference 中存在的選股欄位 / 函數，結構符合「選股」類型慣例。
- **AC3**：輸入「`Average` 怎麼用？」能回出官方定義（參數、回傳）＋ 一個最小範例。
- **AC4**：產出腳本中若出現 reference 未收錄之函數，Claude 必須走 F3 fallback 或明示不確定，**不得**直接杜撰（抽查 10 個生成案例，幻覺函數數 = 0）。
- **AC5**：對一個含未知函數的 `.xs` 檔執行 Edit，Hook 輸出該未知函數的警示；對乾淨檔則靜默。
- **AC6**：五種腳本類型各至少有一份可用範例存在於 `examples/`。

---

### Non-Functional Requirements

- **可維護性**：reference 為快照，須在 SKILL.md 標注蒸餾自哪個來源 commit / 文件版本，便於日後比對更新。
- **離線可用**：核心問答與生成只依賴內建 reference，無網路時仍可運作；僅冷門 fallback 需網路。
- **零重型相依**：Hook 腳本只用 Python stdlib，避免使用者端額外安裝。
- **版本策略**：開發迭代期 `plugin.json` 的 `version` 留空（用 git commit SHA 當版本），穩定後再起 semver；一旦設了 `version` 就須每次改動進版，否則使用者收不到更新。

---

### Open Questions（✅ 全數收斂於 v1.1 實作 session）

1. **知識交付機制** → ✅ **混合制**（內建 reference ＋ WebFetch fallback）。
2. **Hook 用途** → ✅ **路線 A only**（`PostToolUse` 掛 `Write|Edit` → `.xs` 啟發式驗證）。路線 B（`UserPromptSubmit` 確定性注入）留 v2 視體感再加。
3. **Reference 建置方式** → ✅ **Claude 讀來源後人工蒸餾**（KISS）；自動 build 腳本 v2 再說。
4. **Hook 腳本語言** → ✅ **Python 3 stdlib**（跨平台）。附帶前提：使用者端需 `python` 在 PATH。ruff/ty 不裝（僅單支 stdlib 腳本）。
5. **範例庫去留** → ✅ **只蒸餾不 ship**。授權實查：vscode-xs = MIT；**XScript_Preset / XQStrategy 無 LICENSE 檔** → 更不可 bundle 原始 `.xs`，只蒸餾「DSL 事實」。`sources/` 已在 `.gitignore`。
6. **散佈方式** → ✅ **local plugin / skills-dir 自用優先**；`marketplace.json` 暫不做。

---

### 實作進度（Session 交接）

> v1.1 實作 session 進度快照，供下個 session 接手。細節不在此複製，指向對應檔案。

#### 已完成

- ✅ Open Questions 全收斂（見上）。
- ✅ 三來源 clone 至 `sources/`（gitignored）：`vscode-xs`(MIT) / `XScript_Preset`(無授權) / `XQStrategy`(無授權)。
- ✅ **Phase 1 FBD** → [architecture.md](architecture.md)（已 commit `5863d75`）。資料流閉合、無循環依賴。
- ✅ **Plugin 骨架**（純新增，**尚未 commit**，待 `/plugin validate` 過再 commit）：
  - `.claude-plugin/plugin.json`（name=`xs-helper`，version 省略＝dev 用 SHA）
  - `skills/xs/SKILL.md`（`/xs` 入口，description 觸發詞 + 流程 + F3 fallback + 硬邊界）
  - `skills/xs/reference/*.md` ×5 + `examples/*.md` ×5（**佔位**，各標蒸餾來源 + TODO）
  - `hooks/hooks.json`（PostToolUse:Write|Edit → `python xs_lint.py`）
  - `scripts/xs_lint.py`（結構檢查可用；`KNOWN_TOKENS` 為空＝未知函數檢查待蒸餾）

#### 關鍵探勘校正（影響蒸餾策略，詳見 architecture.md 角色分層表）

- **xshelp 為蒸餾主幹**（活的名單權威 + bif 簽名 + 三類欄位定義），且身兼 build-time 與 runtime。grammar 是 **2023 快照已落後**，降為 Hook 離線 token 清單。
- **sysfnc 142/143 在 `XScript_Preset/函數` 有原始碼**（簽名+語意）；**bif 0 個有源**（引擎原語，簽名只能靠 xshelp）。
- 腳本類型由 `{@type:}` **確定性**分類：autotrade / function / indicator / filter / sensor。
- 選股欄位走 `GetField("中文")`，掃出 498+ 種。

#### XS 語意地雷（生成正確性關鍵，已寫入 memory，蒸餾時務必納入 reference）

- `intraBarPersist`：逐筆洗價時變數不回捲 → 見 memory `xs-intrabarpersist-semantics`。
- 執行/觸發模型：歷史回放→即時、**換棒必觸發**、洗價模式×觸發設定 → 見 memory `xs-execution-trigger-model`。

#### 下一步（依序）

1. 待 `/plugin validate` 通過 → commit 骨架（訊息：`feat: plugin 骨架（manifest + /xs skill + hook + reference 佔位）`）。
2. **蒸餾 reference**（核心工作）：xshelp 名單為主幹 × Preset sysfnc 用法 × Strategy 選股欄位交叉驗證 × grammar 生 `xs_lint.py` 的 `KNOWN_TOKENS`。
3. 各類型挑一份 examples、補齊 `script-types.md` 邊界與第一次洗價慣例。
4. Phase 2 FBD（函式層）收進 architecture.md。

### 後續流程（依全域工作慣例）

- 本檔自 v1.1 起兼作 **session 交接介面**；接手 session 以本檔 + `architecture.md` + memory 為輸入，直接進「下一步」。
- `sources/` 為 build-time 蒸餾輸入，不 ship、不進版。
