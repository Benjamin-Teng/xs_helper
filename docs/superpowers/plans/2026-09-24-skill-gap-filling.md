# XS Skill 缺口填補 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 補上 v0.5.1 高強度測試中發現的 skill reference 缺口（Plot／OutputField 命名參數、流程控制語法、Rank 與參數 UI 宣告、型別語意、漏收的 xshelp 函數），讓依 skill 寫腳本時不必再「照 `for` 類推」或避開 `Rank`。

**Architecture:** 純 reference 文件蒸餾（`skills/xs/references/*.md`）＋一支新的 stdlib 測試檔守住兩件事：①每個缺口的關鍵語法確實收錄；②reference 內所有 `xs` 程式碼區塊都能通過 `scripts/xs_lint.py`（無未知呼叫、無結構問題）。只有任務 6 可能動到 `xs_lint.py` 的 `KNOWN_TOKENS`。

**Tech Stack:** Markdown、Python 3 stdlib `unittest`、`scripts/xs_lint.py`、`curl`（抓 xshelp 原始 HTML／JSON）。

**Spec:** [`docs/superpowers/specs/2026-09-24-skill-gap-filling-design.md`](../specs/2026-09-24-skill-gap-filling-design.md)

## Global Constraints

- **來源優先序：xshelp 官方站條目頁 > 官方範例庫（sysjust-xq/XScript_Preset、sysjust-xq/XQStrategy）> 其他。** 兩者衝突以 xshelp 為準；查不到的一律標「待查證」，不得用訓練記憶補值（SPEC G1）。
- xshelp 條目頁：`https://xshelp.xq.com.tw/XSHelp/?HelpName=<名稱>&group=<GROUP>`；站內索引：`https://xshelp.xq.com.tw/XSHelp/rest?a=<字串>`。用 `curl` 抓原始內容，不用摘要工具。
- 官方範例庫只在本機 clone 參考、**不得**把原始 `.xs` 整檔放進 repo（授權未明，見 SPEC Open Q5）；reference 內只放蒸餾後的片段（每段 ≤ 15 行）並註明出處檔名。
- 本計畫是 **build-time 蒸餾**：要實際編輯 `.md`，不可丟給 runtime F3（SPEC 第 340 行）。
- 每個新增的 `xs` 程式碼區塊必須完整（`begin`/`end`、`if`/`then` 成對），並通過 `xs_lint`；新增內容一律附 xshelp 條目連結或官方庫出處。
- 品質關卡：`python -B -m unittest discover -s tests`、`uvx ruff check scripts tests --no-cache`、`uvx ty check --extra-search-path scripts scripts tests`、`markdownlint-cli2` 對改動的 `.md`，全部 0 error。
- 分支：`feat/skill-gap-filling`；每個任務一個 commit，commit 訊息結尾附 repo 規定的 Co-Authored-By 與 Claude-Session 兩行。
- 審查：為節省 Codex 額度，**不做逐任務 Codex review**；在任務 4 完成後與任務 8 完成後各跑一輪 `codex-companion.mjs adversarial-review --base main`，只審差異、附總整理。內容正確性（是否忠於 xshelp）由 fresh Claude subagent 在同樣兩個檢查點核對。

## 不在本計畫範圍（寫明原因）

| 缺口 | 不做的原因 | 後續 |
|---|---|---|
| 各 bif 多載細節全量蒸餾（`builtin-functions.md` 待補第 1 條） | 上百個函數，維持「需要時走 F3 現查」較划算 | 維持現行策略 |
| `QPRICE`／`TPRICE` 等欄位前綴的完整中文清單（`fields.md` 待補） | 資料來源尚未定位：前綴不是 xshelp 條目名 | 另開調查 |
| 關鍵字當變數名是否會編譯錯誤（`language.md` §2） | 沒有任何官方文字來源，只能在 XQ 編輯器實測 | 請使用者實測後回填 |
| `Asc`、`Desc` 的用途 | xshelp 條目頁為空、官方庫零命中 | 更新查證日期，維持待查證 |

## 檔案結構

| 檔案 | 動作 | 職責 |
|---|---|---|
| `tests/test_reference_content.py` | 新增 | 缺口收錄斷言＋reference 程式碼區塊 lint 關卡 |
| `skills/xs/references/builtin-functions.md` | 修改 | 繪圖與選股輸出的命名參數、補漏收函數 |
| `skills/xs/references/language.md` | 修改 | 流程控制語法、Rank、參數 UI 宣告、型別語意、§9.4 更正、待補清單 |
| `skills/xs/references/system-functions.md` | 修改 | 待補清單狀態 |
| `scripts/xs_lint.py` | 視任務 6 結果修改 | 補漏收的可呼叫函數名 |
| `CHANGELOG.md`、`README.md`、`docs/effort-stats.json` 等 | 修改（任務 8） | 發版 |

---

### Task 1: reference 內容測試骨架＋程式碼區塊 lint 關卡

**Files:**

- Create: `tests/test_reference_content.py`

**Interfaces:**

- Produces: `REFS`（`Path`，指向 `skills/xs/references`）、`read_ref(name: str) -> str`、`xs_blocks(text: str) -> list[str]`；後續任務在同一檔新增 `TestCase` 類別。

- [ ] **Step 1: 寫測試檔**

```python
#!/usr/bin/env python3
"""reference 內容測試：缺口收錄斷言 + 所有 xs 程式碼區塊通過 xs_lint（stdlib）。"""
from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REFS = ROOT / "skills" / "xs" / "references"
sys.path.insert(0, str(ROOT / "scripts"))

import xs_lint  # noqa: E402


def read_ref(name: str) -> str:
    return (REFS / name).read_text(encoding="utf-8")


def xs_blocks(text: str) -> list[str]:
    return re.findall(r"```xs\n(.*?)```", text, re.S)


class TestReferenceCodeBlocksLintClean(unittest.TestCase):
    def test_every_xs_block_has_no_lint_warning(self) -> None:
        for path in sorted(REFS.glob("*.md")):
            for i, block in enumerate(xs_blocks(path.read_text(encoding="utf-8"))):
                with self.subTest(file=path.name, block=i):
                    code = xs_lint.strip_comments(block)
                    self.assertEqual(xs_lint.check_unknown_tokens(code) + xs_lint.check_structure(code), [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 執行，確認基準通過**

Run: `python -B -m unittest tests.test_reference_content -v`
Expected: PASS（2026-09-24 基準：34 個區塊全部無警示）。

- [ ] **Step 3: ruff／ty**

Run: `uvx ruff check tests --no-cache && uvx ty check --extra-search-path scripts tests`
Expected: `All checks passed!`

- [ ] **Step 4: Commit**

```bash
git add tests/test_reference_content.py
git commit -m "test: gate every xs code block in references through xs_lint"
```

---

### Task 2: `Plot`／`OutputField` 的命名參數

**Files:**

- Modify: `skills/xs/references/builtin-functions.md`（繪圖與選股輸出表格，`Plot` 與 `OutputField` 兩列，約第 76、83 行）
- Modify: `skills/xs/references/language.md` §9.4（`checkbox`、`order`、`Asc Desc axis` 三列）
- Test: `tests/test_reference_content.py`

- [ ] **Step 1: 寫失敗測試**（附加到測試檔）

```python
class TestPlotAndOutputFieldNamedParams(unittest.TestCase):
    def test_plot_checkbox_is_named_parameter(self) -> None:
        text = read_ref("builtin-functions.md")
        self.assertIn("checkbox:=", text)
        self.assertNotIn("(order, value [, name [, checkbox]])", text)

    def test_outputfield_documents_order_named_parameter(self) -> None:
        text = read_ref("builtin-functions.md")
        self.assertIn("order:=", text)
        self.assertIn("輸出序號", text)

    def test_axis_usage_recorded_with_source(self) -> None:
        text = read_ref("language.md")
        self.assertIn("axis:=", text)
```

- [ ] **Step 2: 執行確認失敗**

Run: `python -B -m unittest tests.test_reference_content.TestPlotAndOutputFieldNamedParams -v`
Expected: 3 個 FAIL。

- [ ] **Step 3: 重抓 xshelp 原文核對**（不照記憶寫）

```bash
for n in Plot OutputField; do curl -s "https://xshelp.xq.com.tw/XSHelp/rest?a=$n" > /tmp/xshelp_$n.json; done
curl -s "https://xshelp.xq.com.tw/XSHelp/?HelpName=checkbox&group=DECLARATION" -o /tmp/checkbox.html
curl -s "https://xshelp.xq.com.tw/XSHelp/?HelpName=order&group=DECLARATION" -o /tmp/order.html
```

確認：`Plot(輸出序號，指標數值，繪圖序列名稱，checkbox:=1)`；`OutputField(輸出序號, 數值, 小數位數, 輸出欄位名稱)`；`order:=-1` 由小到大、`order:=1` 由大到小，範例 `outputfield1(value1,"5日均量",order:=-1);`。

- [ ] **Step 4: 改 `builtin-functions.md` 兩列**

```markdown
| `Plot` | `(輸出序號, value [, name] [, checkbox:=0/1])` | 建立繪圖序列（第 N 條線）；`checkbox:=` 是**命名參數**，放在名稱之後，1＝預設繪出、0＝預設不繪（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=checkbox&group=DECLARATION)）。官方範例庫另見 `axis:=`、`ScaleLabel:=`、`ScaleDecimal:=` 等命名參數，語意見 language.md §9.4 |
| `OutputField` | `(輸出序號, value [, decimals [, name]] [, order:=±1])` | 設定**選股**腳本輸出欄位；第一個參數是「輸出序號」（欄位顯示順序），和命名參數 `order:=`（該欄數值排序：`-1` 由小到大、`1` 由大到小）是兩回事，例：`OutputField1(value1, "5日均量", order:=-1)`（[xshelp](https://xshelp.xq.com.tw/XSHelp/?HelpName=order&group=DECLARATION)） |
```

- [ ] **Step 5: 改 `language.md` §9.4 三列**

把 `checkbox`、`order` 兩列改成指明「命名參數，寫法 `checkbox:=1`／`order:=-1`」；把 `Asc Desc axis` 拆成兩列：

```markdown
| `axis` | `Plot` 系列的命名參數，指定畫在哪條 Y 軸，官方範例庫可見 `axis:=1`、`axis:=2`、`axis:=11`（例：`plot2(value4,"主力累計買賣超",checkbox:=1,axis:=2)`）；xshelp 條目頁為空，**各值的精確編碼待查證** |
| `Asc` `Desc` | 索引有此名稱，但 xshelp 條目頁為空、官方範例庫零命中；用途**待查證**（2026-09-24 重新查證仍無資料） |
```

- [ ] **Step 6: 跑測試與關卡**

Run: `python -B -m unittest discover -s tests && markdownlint-cli2 skills/xs/references/builtin-functions.md skills/xs/references/language.md`
Expected: 全部 PASS、0 issues。

- [ ] **Step 7: Commit**

```bash
git add skills/xs/references/builtin-functions.md skills/xs/references/language.md tests/test_reference_content.py
git commit -m "docs(references): Plot/OutputField named parameters (checkbox:=, order:=, axis:=)"
```

---

### Task 3: 流程控制語法補真實範例

**Files:**

- Modify: `skills/xs/references/language.md` §3（流程控制表格之後新增小節）
- Test: `tests/test_reference_content.py`

- [ ] **Step 1: 寫失敗測試**

```python
class TestControlFlowExamples(unittest.TestCase):
    def setUp(self) -> None:
        self.code = "\n".join(xs_blocks(read_ref("language.md"))).lower()

    def test_while_example(self) -> None:
        self.assertRegex(self.code, r"while .+ begin")

    def test_repeat_until_example(self) -> None:
        self.assertIn("repeat", self.code)
        self.assertRegex(self.code, r"until .+;")

    def test_once_condition_form(self) -> None:
        self.assertRegex(self.code, r"once\s*\(.+\)\s*begin")

    def test_switch_nested_and_case_range(self) -> None:
        self.assertRegex(self.code, r"switch\s*\(")
        self.assertRegex(self.code, r"case \d+ to \d+:")
```

- [ ] **Step 2: 執行確認失敗**

Run: `python -B -m unittest tests.test_reference_content.TestControlFlowExamples -v`
Expected: 至少 `once` 與 `case N to M` 兩項 FAIL。

- [ ] **Step 3: 取一手原文**

- `while`：`XScript_Preset/函數/交易相關/CalcVWAPDistribution.xs` 第 43、48 行附近；單行寫法見 `.../趨勢分析/SwingHigh.xs` 第 12 行。
- `repeat…until`：`XScript_Preset/選股/05.型態選股/突破整理格局.xs` 第 12–18 行。
- `Once`：`XScript_Preset/自動交易/0-基本語法/09-CancelAllOrders.xs` 第 15–18 行；xshelp `?HelpName=once&group=CONTROLFLOW`。
- `switch`：xshelp `?HelpName=switch&group=CONTROLFLOW` 全文（含 `Case 6 to 20:` 範例，逐字取用）；巢狀寫法見 `XQStrategy/01台股的選股條件/04籌碼/大戶持股人數/連續N期大戶持股人數增加.xs` 第 8–23 行。

```bash
curl -s "https://xshelp.xq.com.tw/XSHelp/?HelpName=switch&group=CONTROLFLOW" -o /tmp/switch.html
curl -s "https://xshelp.xq.com.tw/XSHelp/?HelpName=once&group=CONTROLFLOW" -o /tmp/once.html
```

- [ ] **Step 4: 在 §3 表格後新增「3.1 迴圈與分支的官方寫法」**，四段各含：一句規則＋程式碼區塊＋出處。必須寫進的規則：

- `while 條件 begin … end;`：多行用 `begin/end`，單行可省略。
- `repeat … until 條件;`：`until` 後接條件與分號；迴圈體可用 `begin/end`。
- `Once(條件) begin … end;`：**只有這一種語法**；xshelp 提到的「只做一次」另一種做法是 `var: FirstTime(false)` 加 `if` 旗標，不是 `Once` 的第二種形式。
- `switch (變數) begin case 值: … ; case 6 to 20: … ; default: … ; end;`：`case` 支援 `N to M` 範圍；`switch` 可以巢狀。

`repeat` 區塊逐字取自官方檔：

```xs
repeat
 begin
    value1 = simplehighest(high[1], period);
    value2 = simplelowest(low[1], period);
    period = period + 1;
 end;
until period >= rangemax or (value1 > value2 * (1 + limit1/100));
```

`Once` 區塊逐字取自官方檔：

```xs
Once(Position = 0 and Filled = 0 and GetInfo("TradeMode") = 1) begin
    SetPosition(1, GetField("跌停價", "D"), label:="跌停價買進委託");
    _time = TimeAdd(CurrentTime, "M", _n);
end;
```

`while` 與 `switch` 區塊依 Step 3 取得的原文逐字摘錄（≤ 15 行、`begin/end` 完整）。

- [ ] **Step 5: 更新 `language.md` 檔尾「待補」**：把「`switch/case`、`repeat/until`、`while` 的完整語法範式」改為 `- [x] … → 已補（§3.1，出處見各段）`。

- [ ] **Step 6: 跑測試與關卡**

Run: `python -B -m unittest discover -s tests && markdownlint-cli2 skills/xs/references/language.md`
Expected: 全部 PASS（含 Task 1 的 lint 關卡：新區塊不得有未知呼叫）、0 issues。

- [ ] **Step 7: Commit**

```bash
git add skills/xs/references/language.md tests/test_reference_content.py
git commit -m "docs(references): official while/repeat/Once/switch syntax with sources"
```

---

### Task 4: `Rank` 與參數 UI 宣告（`inputkind` 系列）

**Files:**

- Modify: `skills/xs/references/language.md`（§9 之前新增「§10 進階宣告：Rank 與參數 UI」，並更正 §9.4 `dict daterange symbolprice` 一列）
- Test: `tests/test_reference_content.py`

- [ ] **Step 1: 寫失敗測試**

```python
class TestRankAndInputKind(unittest.TestCase):
    def setUp(self) -> None:
        self.text = read_ref("language.md")

    def test_rank_declaration_and_properties(self) -> None:
        self.assertRegex(self.text, r"Rank \w+ begin")
        self.assertIn(".pos", self.text)
        for prop in ("`pos`", "`range`", "`pr`", "`count`", "`isvalid`", "`Q1`", "`Q3`"):
            self.assertIn(prop, self.text)
        self.assertIn("選股", self.text)

    def test_daterange_is_single_date(self) -> None:
        self.assertIn("單一日期", self.text)
        self.assertNotIn("一般選項／日期範圍／開高低收", self.text)

    def test_inputkind_examples(self) -> None:
        for token in ("inputkind:=Dict(", "daterange(", "SymbolPrice()", "quickedit:=true"):
            self.assertIn(token, self.text)
```

- [ ] **Step 2: 執行確認失敗**

Run: `python -B -m unittest tests.test_reference_content.TestRankAndInputKind -v`
Expected: 3 個 FAIL。

- [ ] **Step 3: 重抓 xshelp 原文**

```bash
for n in Rank inputkind dict daterange symbolprice quickedit; do
  curl -s "https://xshelp.xq.com.tw/XSHelp/?HelpName=$n&group=DECLARATION" -o "/tmp/$n.html"
done
```

- [ ] **Step 4: 寫 §10 兩個小節**

**10.1 `Rank`（僅選股腳本）**：規則＋屬性表＋xshelp 範例，並註明「官方範例庫無第二個用例，僅 xshelp 單一來源」。屬性表逐字依 xshelp：`pos`（名次，從 1 起）、`range`（`pos / count * 100`）、`pr`（`(N - pos) / (N - 1) * 100`）、`count`（參與排行商品數）、`value`（＝retval）、`avgvalue`、`medvalue`、`minvalue`、`maxvalue`、`Q1`、`Q3`、`isvalid`。

```xs
Rank _bias10 begin
    retval = close - average(close, 10);
end;
if _bias10.pos[1] <> _bias10.pos then ret = 1;
```

**10.2 參數 UI 宣告**：四個範例逐字取自 xshelp，並寫明讀值方式：

```xs
input: IndexPomUnit(1, "大盤融資單位", inputkind:=Dict(["金額",1],["張數",2]), quickedit:=true);
input: FdifferenceDate(20180301, "外資買賣超查詢日期", inputkind:=daterange(20160301,20190301,"D"));
input: OHLC_Opti(200, "價格：", inputkind:=SymbolPrice());
if IndexPomUnit = 1 then plot1(GetField("融資買進金額", "D")) else if IndexPomUnit = 2 then plot1(GetField("融資買進張數", "D"));
```

必寫規則：`Dict` 的值型別跟預設值一致，腳本內當一般 `input` 變數讀；`daterange(最小日期, 最大日期, "頻率")` 的變數是**單一日期**（`YYYYMMDD`），最小／最大只是 UI 可選範圍；`SymbolPrice()` 讓使用者選開高低收之一，變數仍是數值；`quickedit:=true` 只影響指標腳本的 UI，不改變讀值方式。

- [ ] **Step 5: 更正 §9.4**：`dict` `daterange` `symbolprice` 一列改成「搭配 `inputkind` 產生選項（一般選項／單一日期（附可選範圍）／開高低收之一），見 §10.2」；`Rank` 一列加「見 §10.1」。

- [ ] **Step 6: 跑測試與關卡**

Run: `python -B -m unittest discover -s tests && markdownlint-cli2 skills/xs/references/language.md`
Expected: 全部 PASS、0 issues。若 lint 關卡回報 `retval`／`average` 以外的未知 token，先查 xshelp 確認該名稱存在，再依 Task 6 的規則處理，不得直接改範例。

- [ ] **Step 7: Commit**

```bash
git add skills/xs/references/language.md tests/test_reference_content.py
git commit -m "docs(references): Rank syntax and inputkind Dict/DateRange/SymbolPrice/quickedit"
```

- [ ] **Step 8: 檢查點 A**：①派 fresh Claude subagent 對照 xshelp 原文逐項核對 Task 2–4 新增內容；②跑一輪 Codex adversarial-review（只審差異，附「已由 subagent 核對 xshelp」總整理）。findings 實測重現後才修。

---

### Task 5: 型別語意（`Simple`／`Series`／`Ref`／`Array`）

**Files:**

- Modify: `skills/xs/references/language.md` §2「型別關鍵字」之後新增說明
- Test: `tests/test_reference_content.py`

- [ ] **Step 1: 寫失敗測試**

```python
class TestTypeSemantics(unittest.TestCase):
    def test_simple_series_ref_explained_with_source(self) -> None:
        text = read_ref("language.md")
        self.assertIn("僅適用於函數腳本", text)
        self.assertIn("HelpName=NumericRef", text)
        self.assertIn("HelpName=Numeric&group=DECLARATION", text)
```

- [ ] **Step 2: 執行確認失敗**

Run: `python -B -m unittest tests.test_reference_content.TestTypeSemantics -v`
Expected: FAIL。

- [ ] **Step 3: 抓 xshelp 各型別條目全文**

```bash
for n in Numeric NumericRef NumericArray NumericArrayRef String StringRef TrueFalse TrueFalseRef; do
  curl -s "https://xshelp.xq.com.tw/XSHelp/?HelpName=$n&group=DECLARATION" -o "/tmp/type_$n.html"
done
```

- [ ] **Step 4: 寫說明**：一張表，每列一個型別家族，欄位為「xshelp 原文要點」「何時用」「條目連結」。只寫 xshelp 原文明說的語意（例如「僅適用於函數腳本內」「可以從函數內修改呼叫者傳入的數值」）；`Simple` 與 `Series` 的差別若 xshelp 沒寫，就寫「xshelp 未區分，依 §2 序列位移慣例：`Series` 可用 `x[n]` 取前值」並註明這句是 skill 慣例、不是 xshelp 原文。

- [ ] **Step 5: 更新檔尾「待補」第 1 條**為 `- [x]`，指向新說明。

- [ ] **Step 6: 跑測試與關卡**

Run: `python -B -m unittest discover -s tests && markdownlint-cli2 skills/xs/references/language.md`
Expected: PASS、0 issues。

- [ ] **Step 7: Commit**

```bash
git add skills/xs/references/language.md tests/test_reference_content.py
git commit -m "docs(references): type family semantics from xshelp entries"
```

---

### Task 6: 用 xshelp 函數目錄反查漏收的函數

**Files:**

- Modify: `skills/xs/references/builtin-functions.md`（對應分類表格補列）
- Modify: `skills/xs/references/system-functions.md`（檔尾待補 `GetBarOffset` 一條）
- Modify（視結果）: `scripts/xs_lint.py`（`KNOWN_TOKENS` 第二個 frozenset）、`tests/test_xs_lint.py`
- Test: `tests/test_reference_content.py`

- [ ] **Step 1: 產生 xshelp 函數全名單**（用與 v0.5.0 關鍵字窮舉相同的方法：對 a–z 各查一次 `rest?a=<字母>`，以 `id` 去重）

```bash
python -B - <<'EOF'
import json, string, urllib.request
seen = {}
for c in string.ascii_lowercase:
    raw = urllib.request.urlopen(f"https://xshelp.xq.com.tw/XSHelp/rest?a={c}").read().decode("utf-8")
    for e in json.loads(raw):
        seen[e["id"]] = (e["name"], e["Description"])
funcs = sorted({n for n, g in seen.values() if g.endswith("FUNC")}, key=str.lower)
json.dump(funcs, open("/tmp/xshelp_funcs.json", "w", encoding="utf-8"), ensure_ascii=False)
print(len(funcs))
EOF
```

若某些回應不是合法 JSON（v0.5.0 調查時 `a=Bool` 曾遇到），改用 `re.finditer(r'"name":"([^"]*)"[^}]*?"Description":"([^"]*)"', raw)` 解析，並記錄跳過的筆數。

- [ ] **Step 2: 比對漏收名單**

```bash
python -B - <<'EOF'
import json, re
funcs = json.load(open("/tmp/xshelp_funcs.json", encoding="utf-8"))
docs = "".join(open(f"skills/xs/references/{f}", encoding="utf-8").read() for f in ("builtin-functions.md", "system-functions.md"))
listed = {m.lower() for m in re.findall(r"`([A-Za-z_]\w*)`", docs)}
missing = [f for f in funcs if f.lower() not in listed]
print(len(missing)); print(missing)
EOF
```

- [ ] **Step 3: 寫失敗測試**：把 Step 2 印出的漏收名單（排除確認屬欄位、非函數者，排除理由寫在測試註解）寫成常數 `MISSING_BEFORE`，斷言每個名稱都出現在 `builtin-functions.md` 或 `system-functions.md`。注意：`GetBarOffset` 已收錄於 `builtin-functions.md` 第 45 行，**不要**預設它漏收；名單一律以 Step 2 實際輸出為準。若 Step 2 輸出為空，本任務只做 Step 7 並在 commit 訊息註明「窮舉比對無漏收」。

```python
class TestXshelpFunctionsCovered(unittest.TestCase):
    # 2026-09-24 以 xshelp rest 索引窮舉 *FUNC 分類後，reference 原本漏收的函數。
    # 內容＝Task 6 Step 2 的實際輸出（逐字貼上），每個名稱一個字串。
    MISSING_BEFORE: tuple[str, ...] = ()

    def test_previously_missing_functions_now_documented(self) -> None:
        text = read_ref("builtin-functions.md") + read_ref("system-functions.md")
        for name in self.MISSING_BEFORE:
            with self.subTest(name=name):
                self.assertIn(f"`{name}`", text)
```

- [ ] **Step 4: 執行確認失敗**

Run: `python -B -m unittest tests.test_reference_content.TestXshelpFunctionsCovered -v`
Expected: FAIL。

- [ ] **Step 5: 逐一補列**：每個漏收函數抓 `?HelpName=<名稱>&group=<分類碼>` 原文，依所屬分類加進 `builtin-functions.md` 對應表格，一行簽名＋一句語意（取 xshelp 首句）。漏收數量若超過 40 個，本任務只補高頻（官方範例庫呼叫次數前 40），其餘列入檔尾待補並附名單。

- [ ] **Step 6: 同步 lint 名單**：若補列的函數名不在 `xs_lint.KNOWN_TOKENS`，加到第二個 frozenset，並在 `tests/test_xs_lint.py` 加一個斷言它們不被警示的測試（寫法比照 `test_xshelp_callable_keywords_not_flagged`）。

- [ ] **Step 7: 更新 `system-functions.md` 檔尾**：`GetBarOffset` 那條改 `- [x]`，註明「`GetBarOffset` 早已收錄於 builtin-functions.md；2026-09-24 以 xshelp 函數目錄窮舉比對，漏收者已補入（或：比對無漏收）」。

- [ ] **Step 8: 跑全部關卡**

Run: `python -B -m unittest discover -s tests && uvx ruff check scripts tests --no-cache && uvx ty check --extra-search-path scripts scripts tests && markdownlint-cli2 skills/xs/references/*.md`
Expected: 全部通過。

- [ ] **Step 9: Commit**

```bash
git add skills/xs/references tests scripts/xs_lint.py
git commit -m "docs(references): add functions listed in xshelp but missing from references"
```

---

### Task 7: 驗收——用 skill 重寫原本卡住的範例

**Files:** 無 repo 變更（驗證用，產物放 scratchpad）。

- [ ] **Step 1: 派 fresh subagent**，只讀 `skills/xs/`（不得看本計畫與 spec），依下列需求各寫一支腳本：
  1. 選股：用 `Rank` 選出乖離率名次上升的股票；
  2. 指標：`inputkind:=daterange(...)` 讓使用者選查詢日期，畫出該日起的外資買賣超；
  3. 指標：`inputkind:=SymbolPrice()` 讓使用者選價格來源，畫均線；
  4. 指標：`inputkind:=Dict(...)` 加 `quickedit:=true` 切換融資金額／張數；
  5. 函數：同時用到 `while`、`repeat…until`、`Once`、`switch` 含 `case N to M`；
  6. 選股：`OutputField` 搭配 `order:=-1` 排序；
  7. 指標：`Plot` 搭配 `checkbox:=` 與 `axis:=`。
- [ ] **Step 2: 驗收條件**：七支都通過 `xs_lint`（無警示）；subagent 回報「reference 不足、只能類推」的項目為 0；另一個 fresh subagent 逐支比對用法與 reference 新段落一致。
- [ ] **Step 3**：任何一項不過，回到對應任務補 reference，再重跑本任務。

---

### Task 8: 發版 v0.6.0

skill 本體新增內容，依 semver 為 minor。**照 memory「發版／進版流程」執行**，要點：

- [ ] **Step 1**：`grep -rn "0\.5\.1\|0_5_1"` 逐筆對帳並替換（兩份 `plugin.json`、marketplace entry、測試斷言與測試函式名、SPEC、architecture、README 狀態段）；「vX.Y.Z（含）以上」這種最低版本字串不改。
- [ ] **Step 2**：CHANGELOG 新增 `## [0.6.0]`（Added：Task 2–6 各一條；Fixed：`checkbox` 位置參數誤寫、`daterange` 語意誤寫），底部補比較連結；README 狀態段寫本版重點。
- [ ] **Step 3**：`docs/effort-stats.json` 追加 `v0.6.0` 一筆 history：`xshelp_entries_verified` 加上本次實際重抓核對的條目數（Task 2–6 的 curl 條目逐一計數）、`skill_generated_test_scripts` 加 7、`codex_review_rounds` 照實際輪數、`lint_validation_script_runs` 加 Task 7 的 7 支；`snapshot` 重算（測試數、commit 數、天數、reference 內容數字）。`TestEffortStats` 必須通過。
- [ ] **Step 4**：檢查點 B——Codex adversarial-review 一輪（只審差異＋總整理），通過後 ff 合併 main、打 `v0.6.0` annotated tag、push、`gh release create`（格式照前一版），確認 `releases/latest` 為 v0.6.0、Pages 部署完成。
- [ ] **Step 5**：更新本機 plugin：`claude plugin marketplace update xs-tools` 再 `claude plugin update xs-helper@xs-tools`，用 `claude plugin details xs-helper@xs-tools` 確認 0.6.0。
