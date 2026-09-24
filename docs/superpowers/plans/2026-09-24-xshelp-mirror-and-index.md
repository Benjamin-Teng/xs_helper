# xshelp 本機鏡像＋名稱索引 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 用一支 stdlib 腳本把 xshelp 全站索引抓成本機鏡像（不進 repo），並由鏡像產生只含名稱的 `references/xshelp-index.md`，讓 agent 離線就能確認 XS 名稱是否存在、精準組出 F3 查詢網址。

**Architecture:** `scripts/xshelp_mirror.py` 分兩層：純函數（解析 API 回應、抽 og:description、產生與解析索引 Markdown）全部可離線單元測試；`fetch`／`index` 兩個子命令負責網路與檔案 I/O。鏡像放 `sources/xshelp/entries.json`（已被 gitignore），索引檔隨 skill 散佈，並用測試守住索引與 `xs_lint.KNOWN_TOKENS` 的一致性。

**Tech Stack:** Python 3 stdlib（`json`、`re`、`html`、`urllib`）、`unittest`、Markdown。

**Spec:** [`docs/superpowers/specs/2026-09-24-xshelp-mirror-and-index-design.md`](../specs/2026-09-24-xshelp-mirror-and-index-design.md)

## Global Constraints

- 全量查詢網址固定為 `https://xshelp.xq.com.tw/XSHelp/rest?a=`（空字串），不得改用 a–z 窮舉（會漏 28 筆）。
- 索引檔只可包含：條目名稱、分組代碼、分組中文名、大類中文名、筆數、日期、網址樣板與用法說明。**不得**包含任何 `desc`／`fulldesc`／og:description 內容。
- 鏡像只寫到 `sources/xshelp/`（`.gitignore` 已含 `sources/`）；任何鏡像檔都不得 commit。
- 腳本 stdlib only，以 `python -B scripts/xshelp_mirror.py <子命令>` 執行（與 `xs_lint.py` 相同慣例，不用 uv 虛擬環境、不安裝套件）。
- 單元測試不得連網；只有 Task 2 的 `fetch` 步驟連網。
- `skills/xs/references/` 必須維持扁平、只有 `.md`（`TestSkillLayoutForFixedDirInstallers`）。
- 品質關卡：`python -B -m unittest discover -s tests`、`uvx ruff check scripts tests --no-cache`、`uvx ty check --extra-search-path scripts scripts tests`、`markdownlint-cli2` 對改動的 `.md`，全部 0 error。
- 分支 `feat/xshelp-mirror-index`；每個任務一個 commit，訊息結尾附 Co-Authored-By 與 Claude-Session 兩行。
- 審查：逐任務由 Claude subagent 審查；Codex 只在 Task 6 發版前跑一輪 `adversarial-review --base main`（附總整理，不逐筆看資料）。

---

### Task 1: 鏡像與索引的純函數＋單元測試

**Files:**

- Create: `scripts/xshelp_mirror.py`
- Create: `tests/test_xshelp_mirror.py`

**Interfaces:**

- Produces（後續任務使用）：
  - `parse_entries(raw: str) -> list[dict[str, object]]`：只保留 `id`、`name`、`Description`、`CategoryName`、`father`、`desc`、`fulldesc`。
  - `og_description(html: str) -> str`：抽 `<meta property="og:description" content="...">`（屬性順序不拘）並做 HTML unescape；找不到回 `""`。
  - `build_index(entries: list[dict[str, object]], fetched: str) -> str`：產生索引 Markdown（決定性）。
  - `parse_index(text: str) -> dict[str, dict[str, list[str]]]`：`{大類: {分組代碼: [名稱…]}}`。
  - 常數 `REST_ALL`、`PAGE_URL`、`MIRROR_FILE`、`INDEX_FILE`、`FATHER_ORDER`。

- [ ] **Step 1: 寫失敗測試** `tests/test_xshelp_mirror.py`

```python
#!/usr/bin/env python3
"""xshelp_mirror 純函數測試（不連網）。"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import xshelp_mirror as m

FIXTURE = [
    {"id": 3, "name": "Plot", "Description": "GENERALFUNC", "CategoryName": "一般函數",
     "father": "內建函數", "desc": "DESC_SENTINEL_語法", "fulldesc": "FULLDESC_SENTINEL_說明", "ename": "None"},
    {"id": 1, "name": "average", "Description": "PRICEGETFUNC", "CategoryName": "價格取得",
     "father": "系統函數", "desc": "", "fulldesc": "", "abbrev": "x"},
    {"id": 2, "name": "成交價", "Description": "QPRICE", "CategoryName": "價格",
     "father": "報價欄位", "desc": "d", "fulldesc": "f"},
    {"id": 4, "name": "Bool", "Description": "DECLARATION", "CategoryName": "宣告",
     "father": "宣告", "desc": None, "fulldesc": None},
    {"id": 5, "name": "Zeta", "Description": "NEWGROUP", "CategoryName": "新分組",
     "father": "未知大類", "desc": "", "fulldesc": ""},
]


class TestParseEntries(unittest.TestCase):
    def test_keeps_only_known_fields(self) -> None:
        entries = m.parse_entries(json.dumps(FIXTURE, ensure_ascii=False))
        self.assertEqual(len(entries), 5)
        self.assertEqual(
            set(entries[0]), {"id", "name", "Description", "CategoryName", "father", "desc", "fulldesc"}
        )


class TestOgDescription(unittest.TestCase):
    def test_property_before_content(self) -> None:
        html = '<meta property="og:description" content="此文字為&quot;保留&quot;" />'
        self.assertEqual(m.og_description(html), '此文字為"保留"')

    def test_content_before_property(self) -> None:
        html = '<meta content=" 摘要 " property="og:description">'
        self.assertEqual(m.og_description(html), "摘要")

    def test_missing_returns_empty(self) -> None:
        self.assertEqual(m.og_description("<html></html>"), "")


class TestBuildIndex(unittest.TestCase):
    def setUp(self) -> None:
        self.entries = m.parse_entries(json.dumps(FIXTURE, ensure_ascii=False))
        self.text = m.build_index(self.entries, "2026-09-24")

    def test_header_has_count_date_and_usage(self) -> None:
        self.assertIn("2026-09-24", self.text)
        self.assertIn("共 5 筆", self.text)
        self.assertIn("rest?a=<名稱>", self.text)

    def test_no_description_content_leaks(self) -> None:
        for leaked in ("DESC_SENTINEL", "FULLDESC_SENTINEL"):
            self.assertNotIn(leaked, self.text)

    def test_fathers_follow_fixed_order_then_unknown(self) -> None:
        heads = [line for line in self.text.splitlines() if line.startswith("## ")]
        self.assertEqual(heads, ["## 宣告（1）", "## 內建函數（1）", "## 系統函數（1）",
                                 "## 報價欄位（1）", "## 未知大類（1）"])

    def test_deterministic(self) -> None:
        self.assertEqual(self.text, m.build_index(list(reversed(self.entries)), "2026-09-24"))

    def test_round_trip(self) -> None:
        parsed = m.parse_index(self.text)
        self.assertEqual(parsed["報價欄位"], {"QPRICE": ["成交價"]})
        self.assertEqual(parsed["系統函數"], {"PRICEGETFUNC": ["average"]})
        self.assertEqual(sum(len(n) for g in parsed.values() for n in g.values()), 5)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: 執行確認失敗**

Run: `python -B -m unittest tests.test_xshelp_mirror -v`
Expected: ERROR `ModuleNotFoundError: No module named 'xshelp_mirror'`。

- [ ] **Step 3: 實作** `scripts/xshelp_mirror.py`（本步只寫純函數與常數；子命令在 Task 2）

```python
#!/usr/bin/env python3
"""xshelp_mirror — xshelp 全站索引的本機鏡像與 references 名稱索引。

  python -B scripts/xshelp_mirror.py fetch   # rest?a= 全量 → sources/xshelp/entries.json（不進 repo）
  python -B scripts/xshelp_mirror.py index   # 鏡像 → skills/xs/references/xshelp-index.md

零第三方相依（stdlib only）。索引只收名稱與分組，不含官方說明內容。
"""
from __future__ import annotations

import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIRROR_FILE = ROOT / "sources" / "xshelp" / "entries.json"
INDEX_FILE = ROOT / "skills" / "xs" / "references" / "xshelp-index.md"
REST_ALL = "https://xshelp.xq.com.tw/XSHelp/rest?a="  # 空字串＝全量；a–z 窮舉會漏
PAGE_URL = "https://xshelp.xq.com.tw/XSHelp/?HelpName={name}&group={group}"
FATHER_ORDER = ("流程控制", "宣告", "常數", "忽略字", "內建函數", "系統函數",
                "報價欄位", "資料欄位", "選股欄位", "屬性欄位")
KEEP = ("id", "name", "Description", "CategoryName", "father", "desc", "fulldesc")

_META_RE = re.compile(r"<meta\b[^>]*>", re.IGNORECASE)
_OG_RE = re.compile(r'property\s*=\s*"og:description"', re.IGNORECASE)
_CONTENT_RE = re.compile(r'content\s*=\s*"([^"]*)"', re.IGNORECASE)
_GROUP_HEAD_RE = re.compile(r"^### (\S+) ")


def parse_entries(raw: str) -> list[dict[str, object]]:
    """rest?a= 的 JSON 陣列 → 只留需要的欄位。"""
    return [{k: e.get(k) for k in KEEP} for e in json.loads(raw)]


def og_description(page: str) -> str:
    """條目頁內文由 JS 渲染；原始 HTML 只有 og:description 有文字。"""
    for tag in _META_RE.findall(page):
        if _OG_RE.search(tag):
            found = _CONTENT_RE.search(tag)
            return html.unescape(found.group(1)).strip() if found else ""
    return ""


def _father_key(father: str) -> tuple[int, str]:
    return (FATHER_ORDER.index(father), "") if father in FATHER_ORDER else (len(FATHER_ORDER), father)


def build_index(entries: list[dict[str, object]], fetched: str) -> str:
    """產生 references 名稱索引（決定性：相同輸入 → 逐位元相同輸出）。"""
    tree: dict[str, dict[tuple[str, str], list[str]]] = {}
    for e in entries:
        group = (str(e["Description"]), str(e["CategoryName"]))
        tree.setdefault(str(e["father"]), {}).setdefault(group, []).append(str(e["name"]))
    lines = [
        "# xshelp 名稱索引",
        "",
        f"> 由 xshelp 官方站索引 API 產生（{fetched}，共 {len(entries)} 筆），只收名稱與分組，不含官方說明內容。",
        "> **用法：用搜尋找名稱，不要整份讀入。** 名稱不在本檔＝xshelp 查無，不得使用。",
        "> 確認存在後，語法與說明用 `https://xshelp.xq.com.tw/XSHelp/rest?a=<名稱>` 取回 JSON，"
        "挑 `name` 完全相符那筆的 `desc`（語法）與 `fulldesc`（說明）；",
        "> 給使用者的連結用 `https://xshelp.xq.com.tw/XSHelp/?HelpName=<名稱>&group=<分組代碼>`（中文名需 URL-encode）。",
        "> 重生：`python -B scripts/xshelp_mirror.py fetch` 後 `python -B scripts/xshelp_mirror.py index`。",
    ]
    for father in sorted(tree, key=_father_key):
        groups = tree[father]
        lines += ["", f"## {father}（{sum(len(n) for n in groups.values())}）"]
        for (code, cname) in sorted(groups):
            names = sorted(groups[(code, cname)], key=lambda s: (s.lower(), s))
            lines += ["", f"### {code} {cname}（{len(names)}）", "", " · ".join(f"`{n}`" for n in names)]
    return "\n".join(lines) + "\n"


def parse_index(text: str) -> dict[str, dict[str, list[str]]]:
    """build_index 的反向：{大類: {分組代碼: [名稱…]}}。"""
    tree: dict[str, dict[str, list[str]]] = {}
    father = code = ""
    for line in text.splitlines():
        if line.startswith("## "):
            father = line[3:].rsplit("（", 1)[0]
            tree[father] = {}
        elif line.startswith("### "):
            head = _GROUP_HEAD_RE.match(line)
            code = head.group(1) if head else ""
            tree[father][code] = []
        elif line.startswith("`") and father and code:
            tree[father][code] += [n.strip("`") for n in line.split(" · ")]
    return tree
```

- [ ] **Step 4: 執行確認通過**

Run: `python -B -m unittest tests.test_xshelp_mirror -v`
Expected: 9 個測試 PASS。

- [ ] **Step 5: 關卡**

Run: `uvx ruff check scripts tests --no-cache && uvx ty check --extra-search-path scripts scripts tests && python -B -m unittest discover -s tests`
Expected: 全部通過。

- [ ] **Step 6: Commit**

```bash
git add scripts/xshelp_mirror.py tests/test_xshelp_mirror.py
git commit -m "feat(scripts): xshelp mirror/index pure functions with offline tests"
```

---

### Task 2: `fetch`／`index` 子命令，產生並提交索引檔

**Files:**

- Modify: `scripts/xshelp_mirror.py`（加 `fetch`、`index`、`main`）
- Create（產物）: `skills/xs/references/xshelp-index.md`
- Test: `tests/test_xshelp_mirror.py`（加「已提交索引檔」測試）

**Interfaces:**

- Consumes: Task 1 的全部純函數與常數。
- Produces: `fetch(today: str) -> int`（回寫入筆數）、`write_index() -> int`（回索引筆數）、`main(argv: list[str]) -> int`；已提交的 `skills/xs/references/xshelp-index.md`。

- [ ] **Step 1: 寫失敗測試**（附加到 `tests/test_xshelp_mirror.py`）

```python
class TestShippedIndex(unittest.TestCase):
    """隨 skill 散佈的索引檔：可解析、筆數一致、含已知名稱、不含說明內容、大小受控。"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.text = m.INDEX_FILE.read_text(encoding="utf-8")
        cls.tree = m.parse_index(cls.text)

    def test_count_in_header_matches_names(self) -> None:
        total = sum(len(n) for g in self.tree.values() for n in g.values())
        self.assertIn(f"共 {total} 筆", self.text)
        self.assertGreaterEqual(total, 1600)

    def test_contains_known_names_by_father(self) -> None:
        flat = {f: {n for g in grp.values() for n in g} for f, grp in self.tree.items()}
        self.assertIn("Plot", flat["內建函數"])
        self.assertIn("Bool", flat["宣告"])
        self.assertIn("SDT_Sum", flat["內建函數"])
        self.assertIn("QPRICE", {code for code in self.tree["報價欄位"]})

    def test_size_is_bounded(self) -> None:
        self.assertLess(len(self.text.encode("utf-8")), 80_000)

    def test_no_markup_from_descriptions(self) -> None:
        self.assertNotIn("<br", self.text)
        self.assertNotIn("fulldesc\":", self.text)
```

- [ ] **Step 2: 執行確認失敗**

Run: `python -B -m unittest tests.test_xshelp_mirror.TestShippedIndex -v`
Expected: ERROR `FileNotFoundError`（索引檔尚未產生）。

- [ ] **Step 3: 實作子命令**（附加到 `scripts/xshelp_mirror.py`；檔首 import 補 `sys`、`urllib.parse`、`urllib.request`、`from datetime import date`）

```python
def _get(url: str) -> str:
    with urllib.request.urlopen(url, timeout=60) as resp:  # noqa: S310 - 固定 https 官方網址
        return resp.read().decode("utf-8")


def fetch(today: str) -> int:
    """抓全量索引存成鏡像；全文為空的條目補抓條目頁 og:description。"""
    entries = parse_entries(_get(REST_ALL))
    for e in entries:
        if not ((e.get("desc") or "") or (e.get("fulldesc") or "")):
            url = PAGE_URL.format(name=urllib.parse.quote(str(e["name"])), group=e["Description"])
            e["og_description"] = og_description(_get(url))
    MIRROR_FILE.parent.mkdir(parents=True, exist_ok=True)
    MIRROR_FILE.write_text(
        json.dumps({"fetched": today, "source": REST_ALL, "entries": entries}, ensure_ascii=False, indent=1),
        encoding="utf-8",
    )
    return len(entries)


def write_index() -> int:
    mirror = json.loads(MIRROR_FILE.read_text(encoding="utf-8"))
    INDEX_FILE.write_text(build_index(mirror["entries"], mirror["fetched"]), encoding="utf-8")
    return len(mirror["entries"])


def main(argv: list[str]) -> int:
    if argv[1:] == ["fetch"]:
        print(f"鏡像 {fetch(date.today().isoformat())} 筆 → {MIRROR_FILE}")
        return 0
    if argv[1:] == ["index"]:
        print(f"索引 {write_index()} 筆 → {INDEX_FILE}")
        return 0
    print("用法：python -B scripts/xshelp_mirror.py fetch|index", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

若 ruff 對 `# noqa: S310` 回報 RUF100（該規則未啟用），移除該註解即可（Task 1 已遇過同樣情況）。

- [ ] **Step 4: 執行（連網）並檢查鏡像不進 git**

```bash
python -B scripts/xshelp_mirror.py fetch
python -B scripts/xshelp_mirror.py index
git status --porcelain sources/        # Expected: 空（sources/ 被 gitignore）
git check-ignore sources/xshelp/entries.json   # Expected: 印出該路徑
```

Expected: fetch 印出約 1621 筆；index 印出相同筆數。若少於 1600，停下回報（API 行為可能改變）。

- [ ] **Step 5: 決定性驗證**：再跑一次 `python -B scripts/xshelp_mirror.py index`，`git diff --stat skills/xs/references/xshelp-index.md` 應無差異（相同鏡像 → 相同輸出）。

- [ ] **Step 6: 跑測試與關卡**

Run: `python -B -m unittest discover -s tests && uvx ruff check scripts tests --no-cache && uvx ty check --extra-search-path scripts scripts tests && markdownlint-cli2 skills/xs/references/xshelp-index.md`
Expected: 全部通過（含既有的扁平 references 佈局測試）。markdownlint 若對索引檔報錯，修 `build_index` 的輸出格式，不得手改產物。

- [ ] **Step 7: Commit**

```bash
git add scripts/xshelp_mirror.py tests/test_xshelp_mirror.py skills/xs/references/xshelp-index.md
git commit -m "feat(references): generate xshelp name index from local mirror"
```

---

### Task 3: skill 與文件接上索引

**Files:**

- Modify: `skills/xs/SKILL.md`（reference 清單加索引；F3 段改走索引＋`rest?a=`）
- Modify: `skills/xs/references/fields.md`（第 87 行附近「完整中文清單走 F3」、第 211 行起「待補」）
- Modify: `docs/index.html`（「10 份參考文件」→「11 份」）、`README.md`（同類敘述若有）、`AGENTS.md`（重生指令）、`docs/SPEC.md`（來源政策：鏡像不進 repo、索引隨 skill 散佈）
- Test: `tests/test_reference_content.py`、`tests/test_plugin_compatibility.py`

- [ ] **Step 1: 寫失敗測試**（附加到 `tests/test_reference_content.py`）

```python
class TestXshelpIndexWiring(unittest.TestCase):
    def test_skill_lists_index_and_f3_uses_rest_api(self) -> None:
        skill = (ROOT / "skills" / "xs" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("](references/xshelp-index.md)", skill)
        self.assertIn("rest?a=", skill)

    def test_fields_points_to_index_for_full_lists(self) -> None:
        text = read_ref("fields.md")
        self.assertIn("xshelp-index.md", text)
```

並把 `tests/test_plugin_compatibility.py` 中檢查頁面文字的地方（若有斷言「10 份」）改為「11 份」；若沒有，新增一條斷言頁面含「11 份參考文件」。

- [ ] **Step 2: 執行確認失敗**

Run: `python -B -m unittest tests.test_reference_content.TestXshelpIndexWiring -v`
Expected: 2 個 FAIL。

- [ ] **Step 3: 改 `SKILL.md`**

- reference 清單新增一行：`- [xshelp-index.md](references/xshelp-index.md) — xshelp 全站名稱索引（只有名稱與分組；用搜尋確認名稱是否存在，不要整份讀入）`
- F3 段改為三步：①在 `xshelp-index.md` 搜尋名稱，確認存在與所屬分組代碼；不在索引＝查無，不得使用。②用 `https://xshelp.xq.com.tw/XSHelp/rest?a=<名稱>` 取 JSON，挑 `name` 完全相符那筆，讀 `desc`（語法）與 `fulldesc`（說明）；條目頁內文由 JS 渲染，直接抓 HTML 通常只剩摘要。③回覆標明「此為線上查詢結果」，附條目頁連結 `?HelpName=<名稱>&group=<分組代碼>`。保留原有「查無此函數 → 明確告知」與不杜撰規則。

- [ ] **Step 4: 改 `fields.md`**：第 87 行附近「完整中文清單走 F3」改為「完整名稱清單見 [xshelp-index.md](xshelp-index.md) 的『報價欄位』『資料欄位』『選股欄位』各分組；語意再走 F3」；檔尾待補中「完整中文清單未收錄」一條改 `- [x]`，註明「名稱清單已由 xshelp-index.md 提供（2026-09-24）」。

- [ ] **Step 5: 改其他文件**

- `docs/index.html`：「安裝後技能會列出 10 份參考文件」→「11 份」，括號內補「名稱索引」。
- `AGENTS.md`「內容正確性」節加一條：xshelp 名稱索引由 `python -B scripts/xshelp_mirror.py fetch` 再 `index` 重生（fetch 需要網路，review 沙箱內不要執行）。
- `docs/SPEC.md` 來源表（第 121 行附近）與「不做」相關段落：補一句「xshelp 全量鏡像只存本機 `sources/xshelp/`；隨 skill 散佈的只有名稱索引 `xshelp-index.md`（不含說明內容），手動重生」。

- [ ] **Step 6: 跑測試與關卡**

Run: `python -B -m unittest discover -s tests && markdownlint-cli2 skills/xs/SKILL.md skills/xs/references/fields.md AGENTS.md docs/SPEC.md`
Expected: 全部通過。

- [ ] **Step 7: Commit**

```bash
git add skills/xs/SKILL.md skills/xs/references/fields.md docs/index.html AGENTS.md docs/SPEC.md tests
git commit -m "docs(skill): wire xshelp name index into F3 and field lists"
```

---

### Task 4: lint 名單與索引一致性

**Files:**

- Modify: `scripts/xs_lint.py`（`KNOWN_TOKENS` 第二個 frozenset 與來源註解）
- Test: `tests/test_xshelp_mirror.py`

- [ ] **Step 1: 寫失敗測試**（附加到 `tests/test_xshelp_mirror.py`）

```python
import re as _re

import xs_lint

_ASCII_IDENT = _re.compile(r"^[A-Za-z_]\w*$")


class TestLintCoversIndexedFunctions(unittest.TestCase):
    def test_every_ascii_function_name_is_known_to_lint(self) -> None:
        tree = m.parse_index(m.INDEX_FILE.read_text(encoding="utf-8"))
        names = {n for f in ("內建函數", "系統函數") for g in tree.get(f, {}).values() for n in g}
        missing = sorted(n for n in names if _ASCII_IDENT.match(n) and n.lower() not in xs_lint.KNOWN_TOKENS)
        self.assertEqual(missing, [])
```

- [ ] **Step 2: 執行確認失敗或通過**

Run: `python -B -m unittest tests.test_xshelp_mirror.TestLintCoversIndexedFunctions -v`
Expected: 多半 FAIL 並列出 `missing`（v0.6.0 只比對過 reference，未比對 lint 與 xshelp 全量）。若已 PASS，於 commit 訊息註明「無漏收」並跳到 Step 5。

- [ ] **Step 3: 補名單**：把 `missing` 全部轉小寫加入 `KNOWN_TOKENS` 第二個 frozenset；來源註解加「5. xshelp 名稱索引（`references/xshelp-index.md`）中大類為內建函數／系統函數的 ASCII 名稱，由 `TestLintCoversIndexedFunctions` 守住」。不得加回 `bool`／`int`／`float`／`double`。

- [ ] **Step 4: 跑全部關卡**

Run: `python -B -m unittest discover -s tests && uvx ruff check scripts tests --no-cache && uvx ty check --extra-search-path scripts scripts tests`
Expected: 全部通過。另以 `python -B -c` 印出新增數量，寫進 commit 訊息。

- [ ] **Step 5: Commit**

```bash
git add scripts/xs_lint.py tests/test_xshelp_mirror.py
git commit -m "fix(xs_lint): cover every ASCII xshelp function name from the index"
```

---

### Task 5: 驗收——agent 只靠 skill 回答名稱存在與否

**Files:** 無 repo 變更（產物放 scratchpad）。

- [ ] **Step 1: controller 準備題目**（不告訴受測 agent 答案）：從 `xshelp-index.md` 隨機挑 6 個真實名稱（至少 2 個欄位分組、1 個 `SDT_*`、1 個只出現在索引而不在其他 reference 的名稱），再自擬 6 個看似合理但索引中不存在的名稱（例如把真實函數名改一個字母）。
- [ ] **Step 2: 派 fresh subagent**，只讀 `skills/xs/`、不得上網、不得讀 `docs/`：對 12 個名稱各回答「存在／不存在、所屬分組代碼、F3 查詢網址」，再寫一支選股腳本，用到一個只出現在索引的欄位名稱。
- [ ] **Step 3: 驗收條件**：12 題全對；網址格式符合 SKILL.md F3；腳本通過 `xs_lint`、欄位名稱與索引逐字相同。未過則回到 Task 3 修 SKILL.md 說明後重跑。

---

### Task 6: 發版 v0.7.0

skill 新增 reference，依 semver 為 minor。**照 memory「發版／進版流程」執行**，要點：

- [ ] **Step 1**：`grep -rn "0\.6\.0\|0_6_0"` 逐筆對帳替換（兩份 `plugin.json`、marketplace entry、測試斷言與測試函式名、SPEC、architecture、README 狀態段）；最低版本字串不改。
- [ ] **Step 2**：CHANGELOG `## [0.7.0]`（Added：xshelp 名稱索引、鏡像腳本、F3 改走索引 API、欄位完整名稱清單；Fixed：lint 名單補齊 xshelp ASCII 函數），README 狀態段寫本版重點與 reference 11 份。
- [ ] **Step 3**：`docs/effort-stats.json` 追加 `v0.7.0` history（`xshelp_entries_verified` 不增加——索引是名稱清單、不是逐條內容核對；`skill_generated_test_scripts` 加 Task 5 的 1 支；`lint_validation_script_runs` 加 1；`codex_review_rounds` 照實際輪數），snapshot 重算（reference 11 份、token 數、測試數、commit 數、版本數）。
- [ ] **Step 4**：Codex adversarial-review 一輪（只審差異＋總整理），通過後 ff 合併 main、打 `v0.7.0` tag、push、`gh release create`，確認 `releases/latest` 與 Pages。
- [ ] **Step 5**：`claude plugin marketplace update xs-tools` 再 `claude plugin update xs-helper@xs-tools`，確認 0.7.0。
