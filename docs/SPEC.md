# xs_helper — Project Spec

## 版本資訊

| 欄位 | 內容 |
|------|------|
| 版本 | v1.2 |
| 基於 | v1.1 |
| 建立日期 | 2026-05-30 |
| 修改日期 | 2026-08-04 |
| 動機 | v1 首次定義 Claude Code plugin；v1.1 收斂 reference 與 Claude 封裝；v1.2 新增 Codex 原生 manifest、marketplace、skill metadata 與完整雙平台文件，兩端共用同一份 XS knowledge base。 |
| 前提 | 通用模型本身不具備完整 XS 知識；XS 為 XQ 專屬 DSL，無公開編譯器 / LSP，知識來源為三個官方 GitHub 範例庫＋官方說明站 |

---

### Overview

`xs_helper` 是一個同時支援 **Claude Code 與 Codex** 的 plugin。使用者在 Claude Code 輸入 `/xs`，或在 Codex 使用 `$xs`，即可載入「XS 專家模式」：AI agent 會依據 XQ全球贏家自行開發的 **XScript（XS）** 語言規範，協助使用者

1. 撰寫 / 修改 XS 自動化腳本（自動交易、選股、指標、警示、函數五大類型其一）；
2. 回答「某個 XS 函數 / 欄位 / 關鍵字怎麼用」這類規範性問題。

核心難點：通用模型原生不熟悉 XS（小眾、繁中、券商專屬 DSL）。因此本 plugin 的本質是**把 XS 的語法、內建函數、欄位、各腳本類型慣例，以蒸餾後的 reference 形式內建進 skill**，讓 Claude Code 與 Codex 載入相同的正確知識後再作答，避免幻覺出不存在的函數。

**使用對象**：使用 XQ全球贏家、需要撰寫 / 維護 XS 腳本，且在 Claude Code 或 Codex 環境工作的量化 / 程式交易使用者。

---

### Goals

- **G1（不幻覺）**：XS Skill 產生或引用的 XS 函數 / 欄位 / 關鍵字，**100% 存在於內建 reference 清單或經官方站查證**，不得編造。
- **G2（類型正確）**：產出的腳本符合「使用者指定腳本類型」的結構與可用函數限制（例：選股腳本不得用自動交易專屬的下單函數）。
- **G3（規範問答）**：使用者問「XX 函數怎麼用」時，AI agent 能依官方定義回答簽名、參數、回傳與一個可用範例。
- **G4（低摩擦）**：Claude Code 以 `/xs`、Codex 以 `$xs` 明確觸發，也能由 description 自動觸發；使用者不需要重貼語法手冊。
- **G5（可驗證）**：雙平台 manifest、marketplace、skill metadata 與文件由 stdlib 測試及 Codex validator 驗證；`xs_lint.py` 維持可手動執行。

---

### Features

#### F1. XS Skill — XS 專家模式（核心）

- 使用者輸入 Claude Code `/xs <自然語言需求>`、Codex `$xs <自然語言需求>`，或提出可自動匹配的 XS 請求後，AI agent：
  1. 判定使用者要的**腳本類型**（自動交易 / 函數 / 指標 / 選股 / 警示），不明確時反問；
  2. 載入對應的 reference（語法 + 該類型可用函數 + 範例）；
  3. 產出 XS 程式碼，或回答規範問題。
- **行為契約**：使用者做 A（描述需求或提問）→ 系統做 B（載入 reference、依規範生成 / 解說）→ 結果 C（一段可貼回 XQ Script Editor 的 XS 程式碼，或一段帶官方定義與範例的解說）。
- **啟動路徑**：
  1. **Claude Code 手動**：使用者輸入 `/xs`。
  2. **Codex 手動**：使用者輸入 `$xs`。
  3. **自動**：兩端依 SKILL.md 的 `description` 作**語意判斷**自行載入——非字面 keyword 比對。因此 `description` 必須明確列出觸發詞（`XS / XScript / XQ / 全球贏家 / .xs / 選股條件 / 自動交易腳本…`）。
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

當需求涉及 reference 未涵蓋的冷門函數 / 欄位，SKILL.md 指示 AI agent 使用目前環境可用的網頁查詢或瀏覽工具查詢 `https://xshelp.xq.com.tw/XSHelp/` 對應子頁，再作答；查得後在回覆中標明「此為線上查詢結果」。

#### F4. `.xs` 編輯驗證 Hook（已於 v0.2.0 移除）

> **狀態（v0.2.0）：** 此 hook 已移除。原因：以 `python` 執行腳本，但目標使用者端常無 Python / `python` 不在 PATH，hook 掛 `Write|Edit` 不限副檔名，導致每次存檔跳 PostToolUse 錯誤。`scripts/xs_lint.py` 保留為獨立腳本（benchmark 幻覺掃描 + 手動檢查），僅不再自動掛載。以下為原始設計記錄，保留供歷史對照。

- `PostToolUse` 掛在 `Write|Edit`，比對被編輯檔名是否為 `*.xs`；
- 命中時執行驗證腳本，對照內建「已知 token 清單」，對**未知函數名**與**明顯結構問題**（如 `if` 缺 `then`、`begin/end` 不成對）提出非阻斷式警示。
- 限制：因 XS 無公開 grammar / 編譯器，此為**啟發式檢查**，非完整語法驗證（見 Out of Scope）。

---

### Input / Output

#### Input

| 欄位 | 型別 | 必填 | 備註 |
|------|------|------|------|
| `/xs` 或 `$xs` 後的自然語言需求 | string | 是 | 撰寫需求或規範問題 |
| 腳本類型 | enum(自動交易/函數/指標/選股/警示) | 否 | 未提供時由 AI agent 推斷或反問 |
| 目標市場（選股情境） | enum(台股/陸股/港股/美股) | 否 | 影響可用選股欄位與範例選取 |
| 待檢查的 `.xs` 檔 | file path | 否 | 僅供手動執行 `scripts/xs_lint.py`；不再由 Hook 自動觸發 |

#### Output

- **腳本生成**：一段 XS 程式碼（可直接貼回 XQ Script Editor），附簡短說明使用了哪些函數 / 欄位。
- **規範問答**：函數 / 欄位的官方定義（簽名、參數、回傳）＋ 一個最小可用範例。
- **手動 lint 警示**：獨立執行 `xs_lint.py` 時列出未知 token / 結構疑點；plugin 不自動掛載 Hook。
- **錯誤狀態**：需求類型無法判定 → 反問；查詢的函數連官方文件都查無 → 明確告知「查無此函數，可能為版本差異或拼寫」，不杜撰。

---

### Out of Scope

明列**不做**的事，實作時不得自行補完：

- **XS 腳本的實際執行 / 回測**：本 plugin 不含 XS runtime，只生成與解說，不保證在 XQ 平台上的執行結果。
- **完整語法分析 / LSP / grammar**：vscode-xs 只做上色、無正式 grammar，本專案不重建編譯器級驗證；Hook 僅做啟發式檢查。
- **即時同步官方文件全量**：reference 為人工蒸餾的快照，不建立自動全量爬蟲同步（冷門查詢走 F3 fallback 即可）。
- **超出三個來源庫範圍的市場 / 功能**：來源未涵蓋者不臆測補完。
- **XQ 平台帳號 / API 整合**：本 plugin 不連 XQ 帳號、不下單、不取即時報價。

> **AI Agentic Dev 注意：** 以上為兩端共用 skill 的硬邊界。凡未列在 Features 且落在此節者，即使看似合理也不得自行實作。

---

### Tech Stack

| 層級 | 選擇 | 備註 |
|------|------|------|
| Plugin 形態 | Claude Code + Codex 雙原生封裝 | manifest 在 `.claude-plugin/plugin.json` 與 `.codex-plugin/plugin.json` |
| 知識交付 | 內建 markdown reference ＋可用網頁工具 fallback（混合制） | 核心架構；非 RAG、非外部 DB |
| Skill 內容 | 純 markdown（SKILL.md + reference/*.md） | 無 runtime 相依 |
| Lint 腳本 | Python 3 stdlib（零第三方相依） | 獨立手動工具；不由 Claude Code 或 Codex plugin 自動掛載 |
| Reference 來源 | XScript_Preset / XQStrategy / vscode-xs / xshelp 官方站 | 實作階段 clone 到 `sources/` 後蒸餾 |
| Docker | **否** | plugin 為 markdown + 輕量腳本，無容器化需求（已依規則評估） |
| 散佈方式 | Claude marketplace + Codex repo marketplace | marketplace 名稱皆為 `xs-tools`，共用 repository-root plugin |

> **AI Agentic Dev 注意：** Tech Stack 在第一個檔案產生前定案；標「待確認」者須在實作 session 開頭先收斂，不得逕自選擇。

---

### Project Structure

```text
xs_helper/
├── .claude-plugin/
│   ├── plugin.json              # Claude Code manifest
│   └── marketplace.json         # Claude Code marketplace
├── .codex-plugin/
│   └── plugin.json              # Codex 原生 manifest
├── .agents/plugins/
│   └── marketplace.json         # Codex repo marketplace
├── skills/
│   └── xs/
│       ├── SKILL.md             # 共用入口：判類型、載 reference、生成/解說、fallback 指示
│       ├── agents/
│       │   └── openai.yaml      # Codex UI metadata；$xs + implicit invocation
│       └── reference/           # 兩端共用的唯一 knowledge base
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
├── scripts/
│   └── xs_lint.py               # 獨立 .xs 啟發式驗證（不掛 hook）
├── sources/                     # 實作階段 clone 三個範例庫於此（蒸餾輸入，gitignore）
├── docs/
│   └── SPEC.md                  # 本檔
├── README.md
├── CHANGELOG.md
└── LICENSE
```

> **AI Agentic Dev 注意：** `skills/` 與 `scripts/` 一律放 plugin 根目錄；兩份 manifest 都指向同一個 `skills/`，不得複製 reference 或放進 host-specific manifest 目錄。

### 安裝與啟動

Claude Code：

```text
/plugin marketplace add Benjamin-Teng/xs_helper
/plugin install xs-helper@xs-tools
/reload-plugins
```

以 `/xs <需求>` 明確觸發。

Codex：

```shell
codex plugin marketplace add Benjamin-Teng/xs_helper
codex plugin add xs-helper@xs-tools
```

安裝後開新對話，以 `$xs <需求>` 明確觸發。兩端也能依 `description` 自動觸發。

---

### Naming Conventions

- 檔案：`kebab-case.md`（reference 與 examples）、`snake_case.py`（腳本）。
- Skill 目錄：小寫（`xs/`）；skill 名取自 SKILL.md frontmatter `name`。
- XS 範例檔內容：保留 XS 原生大小寫慣例（如 `Average`、`CurrentBar`），不改寫。
- reference 內函數條目格式統一：`名稱 / 簽名 / 參數 / 回傳 / 範例 / 來源`。

---

### Acceptance Criteria

- **AC1**：Claude Code 安裝後可用 `/xs`，Codex 安裝後可用 `$xs`；兩個 manifest 皆識別 `xs-helper@0.3.0` 並載入同一份 `skills/xs/`。
- **AC2**：輸入「幫我寫一個『連續三天放量上漲』的台股選股條件」，產出的 XS 只使用 reference 中存在的選股欄位 / 函數，結構符合「選股」類型慣例。
- **AC3**：輸入「`Average` 怎麼用？」能回出官方定義（參數、回傳）＋ 一個最小範例。
- **AC4**：產出腳本中若出現 reference 未收錄之函數，AI agent 必須走 F3 fallback 或明示不確定，**不得**直接杜撰（抽查 10 個生成案例，幻覺函數數 = 0）。
- **AC5**：stdlib 相容性測試驗證雙 manifest、雙 marketplace、Codex metadata、平台中立 fallback 與所有雙平台安裝文件；Codex plugin/skill validator 通過。
- **AC6**：五種腳本類型各至少有一份可用範例存在於 `examples/`。

---

### Non-Functional Requirements

- **可維護性**：reference 為快照，須在 SKILL.md 標注蒸餾自哪個來源 commit / 文件版本，便於日後比對更新。
- **離線可用**：核心問答與生成只依賴內建 reference，無網路時仍可運作；僅冷門 fallback 需網路。
- **零重型相依**：skill runtime 為 Markdown；獨立 lint 腳本只用 Python stdlib，終端使用者不需安裝 Python 才能載入 plugin。
- **版本策略**：自 `v0.1.0` 起採 semver；對外變動同步更新兩份 `plugin.json`。**現況：v0.3.0**，marketplace entry 不重複設 version，以 manifest 為權威。

---

### Open Questions（✅ 全數收斂於 v1.1 實作 session）

1. **知識交付機制** → ✅ **混合制**（內建 reference ＋環境可用的網頁工具 fallback）。
2. **Hook 用途** → ✅ **路線 A only**（`PostToolUse` 掛 `Write|Edit` → `.xs` 啟發式驗證）。路線 B（`UserPromptSubmit` 確定性注入）留 v2 視體感再加。
3. **Reference 建置方式** → ✅ **Claude 讀來源後人工蒸餾**（KISS）；自動 build 腳本 v2 再說。
4. **Hook 腳本語言** → ✅ **Python 3 stdlib**（跨平台）。附帶前提：使用者端需 `python` 在 PATH。ruff/ty 不裝（僅單支 stdlib 腳本）。
5. **範例庫去留** → ✅ **只蒸餾不 ship**。授權實查：vscode-xs = MIT；**XScript_Preset / XQStrategy 無 LICENSE 檔** → 更不可 bundle 原始 `.xs`，只蒸餾「DSL 事實」。`sources/` 已在 `.gitignore`。
6. **散佈方式** → ✅ **已完成 `marketplace.json`**（marketplace `xs-tools`，v0.1.0 起版）。自用階段曾以 local plugin / skills-dir 過渡，現已具可散佈狀態。〔v1.1 原決議為「暫不做」→ 改為要做 → 本版完成。〕

---

### 實作進度（Session 交接）

> v1.1 實作 session 進度快照，供下個 session 接手。細節不在此複製，指向對應檔案。

#### 已完成

- ✅ Open Questions 全收斂（見上）。
- ✅ 三來源 clone 至 `sources/`（gitignored）：`vscode-xs`(MIT) / `XScript_Preset`(無授權) / `XQStrategy`(無授權)。
- ✅ **Phase 1 FBD** → [architecture.md](architecture.md)（已 commit `5863d75`）。資料流閉合、無循環依賴。
- ✅ **Plugin 骨架**（已 commit `588c2c4`，`/plugin validate` 通過、僅 version warning）：
  - `.claude-plugin/plugin.json`（name=`xs-helper`，version 省略＝dev 用 SHA）
  - `skills/xs/SKILL.md`（`/xs` 入口，description 觸發詞 + 流程 + F3 fallback + 硬邊界）
  - `hooks/hooks.json`（PostToolUse:Write|Edit → `python xs_lint.py`）
- ✅ **語法錨點（離線、grammar 確定性）已蒸餾**（commit `47a24de`）：
  - `reference/language.md`：grammar 五類 token × Preset 真實語法校對；`intraBarPersist`
    列一級概念（回捲對比表 + `IsXLOrder.xs` 換 Bar 重設慣例）。
  - `scripts/xs_lint.py`：`KNOWN_TOKENS` 已嵌入 **604 個 token**（grammar 2023 快照 ∪ Preset 215 sysfnc ∪ xshelp 8 群組 bif，小寫）+ 數字後綴
    正規化 + 字串字面量 strip + 警示改「未收錄(可能自訂函數)」→ **達成 AC5**。
  - `tests/test_xs_lint.py`：17 個 stdlib 單元測試全過。
- ✅ **`system-functions.md` 已蒸餾**（「下一步」第 1 項完成）：`XScript_Preset/函數/` 全 **224 個 sysfnc**
  依官方 14 分類入檔，每條 `簽名（input 宣告）+ 一行語意（實作）`；開頭立共通慣例
  （回傳機制：同名變數 / `ret`/`retval` / `numericref` 回填；型別縮寫表；頻率代碼 `H`=半年）。
  含「重點函數詳解」可貼用範例（MA 族 / 極值 / 穿越 / MACD / KD / DMI / RSI / 布林 / ATR / 條件統計）。
  發現：存在中文名函數（`KO成交量擺盪指標`/`Q指標`/`KST確認指標`/`漲幅排行榜`系列）；
  `排行/` 6 支實為「自訂排行條件範本」；`xfMin_*` 不支援 XS 選股/排行/回測。
  檔尾 3 個待補項皆已標明為 **build-time、不由 F3 回寫**。
- ✅ **`builtin-functions.md`（bif）已蒸餾**（「下一步」第 2 項之一）：xshelp 8 分類
  （`GENERALFUNC`/`TIMEFUNC`/`DATEFUNC`/`STRINGFUNC`/`NUMBERFUNC`/`FIELDFUNC`/`ARRAYFUNC`/
  `TRANSACTIONFUNC`）全收，每條 `名稱 / 簽名 / 一行語意`；開頭立 bif vs sysfnc 差異 +
  欄位/報價/交易函數的腳本邊界（`GetQuote`/交易函數限即時/自動交易）。
- ✅ **`fields.md`（三類欄位）已蒸餾**（「下一步」第 2 項之二）：報價`Q*`（含 grammar `q_*`
  全名單錨定）/ 資料`T*` / 選股`F*` 七子類；選股欄位以 `XQStrategy` `GetField` 實際用例
  **交叉驗證**（高頻標 ✅）。立三類欄位×入口×腳本邊界表。`FFINANCE` 200+ 僅收高頻子集，餘走 F3。
- ✅ **`script-types.md` + `examples/*.md` ×5 已蒸餾**（「下一步」第 3 項完成）：
  - `script-types.md`：5 類 `{@type:}` 結構/觸發模型/邊界；立**跨類型回傳機制表**
    （`ret=1` 在 filter=入選 vs sensor=觸發，寫法同義不同）；`function` 家族三子型別
    （`function`/`function_bool`/`function_string`）回傳型別對應；autotrade 第一次洗價控管
    （`intraBarPersist` 旗標 + 換 Bar 重設）；末附「選哪個 `{@type:}`」速查表。
  - `examples/*.md` ×5 各一份精選範例（標 Preset/Strategy 原始檔出處）：autotrade（均線交叉
    +停利停損%）/ function（CountIF + CrossOver bool + FormatMQY string）/ indicator（BBand 主圖 +
    Aroon 副圖）/ filter（GetField 基本 + 輸出欄 + 美股跨市場）/ sensor（技術條件 + GetQuote 即時）。
  - ⚠️ **校正既有佔位假設**：警示**用 `ret=1` 觸發、非 `Alert()`**（Preset 警示 359 檔 333 用
    `ret=1`、0 用 `Alert()`；`Alert()` 實為 autotrade 通知函數）。佔位檔誤標 `Alert(...)` 已修正。
  - 型別分佈實證：autotrade 64 / filter 324 / indicator 395 / sensor 359 / function 207 /
    function_bool 16 / function_string 1。

#### 關鍵探勘校正（影響蒸餾策略，詳見 architecture.md 角色分層表）

- **xshelp 為蒸餾主幹**（活的名單權威 + bif 簽名 + 三類欄位定義），且身兼 build-time 與 runtime。grammar 是 **2023 快照已落後**，降為 Hook 離線 token 清單。
- **sysfnc 142/143 在 `XScript_Preset/函數` 有原始碼**（簽名+語意）；**bif 0 個有源**（引擎原語，簽名只能靠 xshelp）。
- 腳本類型由 `{@type:}` **確定性**分類：autotrade / function / indicator / filter / sensor。
  ⚠️ 新發現：`function` 有子型別，Preset 實見 `{@type:function_bool}`（回傳布林的函數）→ 蒸餾
  `script-types.md` 時須涵蓋 `function*` 子型別家族，勿假設只有 `function` 單一標記。
- 選股欄位走 `GetField("中文")`，掃出 498+ 種。

#### XS 語意地雷（生成正確性關鍵，已寫入 memory，蒸餾時務必納入 reference）

- `intraBarPersist`：逐筆洗價時變數不回捲 → 見 memory `xs-intrabarpersist-semantics`。
- 執行/觸發模型：歷史回放→即時、**換棒必觸發**、洗價模式×觸發設定 → 見 memory `xs-execution-trigger-model`。

#### 實作項目（原「下一步」，1~5 項全數 ✅ 完成於 v0.1.0）

> 🎉 **全數完成**：reference 蒸餾主體（語法錨點 / sysfnc / bif / 欄位 / 腳本類型 + 範例）、
> Phase 2 FBD、marketplace.json 散佈皆已落地，plugin 達可散佈狀態並已起版 `v0.1.0`。
> 以下保留為歷史記錄（含各項 commit baseline），未來新工作另起新節。

1. ~~**`system-functions.md`（sysfnc）**~~ → ✅ **已完成**（見上「已完成」節）。
2. ~~**`builtin-functions.md`（bif）+ `fields.md`（三類欄位）**~~ → ✅ **已完成**（見上「已完成」節）。
3. ~~**`script-types.md` + `examples/*.md`**~~ → ✅ **已完成**（見上「已完成」節）。
4. ~~**Phase 2 FBD**（函式層）收進 `architecture.md`~~ → ✅ **已完成**：`architecture.md`
   新增「Phase 2 — 函式層資料流」（`xs_lint.py` 6 個 public function 真實簽名 + `/xs` Skill
   程序步驟 + reference 載入 + F3 fallback + tests 消費關係），含 Phase 2 閉合性檢查表；
   檔頭升級為**常駐架構文件**（兩階段 FBD 並存）。
5. ~~**`marketplace.json`（散佈）**~~ → ✅ **已完成**：
   - `.claude-plugin/marketplace.json`（marketplace name=`xs-tools`，owner，單一 plugin entry
     `source: "./"`＝plugin 在 repo 根；version 不在 entry 重複，交由 `plugin.json` 作權威，
     避免官方文件警告的「兩處都設 version → plugin.json 靜默勝出」陷阱）。
   - **首次起 semver `v0.1.0`** 寫進 `plugin.json`（語意：功能可用但仍迭代）；同步補
     `license: MIT` + `homepage`/`repository`；新增 root `LICENSE`(MIT) 與 `CHANGELOG.md`。
   - `/plugin validate .` 通過（marketplace 模式，含對 referenced `plugin.json` 的 version/path 交叉檢查）。
   - README 更新：狀態升 v0.1.0、補安裝指引（`/plugin marketplace add Benjamin-Teng/xs_helper`
     → `/plugin install xs-helper@xs-tools`）、License 改 MIT。
   - 散佈 schema 求證自 `code.claude.com/docs/en/plugin-marketplaces`（文件網域已自
     `docs.claude.com` 遷至 `code.claude.com`）。

每個 reference 條目格式統一：`名稱 / 簽名 / 參數 / 回傳 / 範例 / 來源`（見 Naming Conventions）。
冷門 / 無源者走 SKILL.md F3 線上查證，**不杜撰**（G1）。

### 後續流程（依全域工作慣例）

- 本檔自 v1.1 起兼作 **session 交接介面**；v0.1.0 起實作項目已全數收斂，接手 session 以本檔 + `architecture.md` + memory 為輸入。未來若有新工作，另起新節（勿復用已收斂的「實作項目」清單）。
- `sources/` 為 build-time 蒸餾輸入，不 ship、不進版。
- **build-time 蒸餾 vs runtime F3 是兩件事**：reference 的所有「待補/校對」都是 build-time（須實際編輯 `.md`）；F3 是 runtime 對使用者單次提問的線上 fallback，**查完即丟、不回寫 reference**（Out of Scope「不建立自動全量同步」）。接手蒸餾時別把待補項丟給 F3。
