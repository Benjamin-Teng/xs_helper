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
import sys
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIRROR_FILE = ROOT / "sources" / "xshelp" / "entries.json"
INDEX_FILE = ROOT / "skills" / "xs" / "references" / "xshelp-index.md"
REST_ALL = "https://xshelp.xq.com.tw/XSHelp/rest?a="  # 空字串＝全量；a–z 窮舉會漏
PAGE_URL = "https://xshelp.xq.com.tw/XSHelp/?HelpName={name}&group={group}"
FATHER_ORDER = ("流程控制", "宣告", "常數", "忽略字", "內建函數", "系統函數",
                "報價欄位", "資料欄位", "選股欄位", "屬性欄位")
KEEP = ("id", "name", "Description", "CategoryName", "father", "desc", "fulldesc")
MIN_ENTRIES = 1600  # 低於此門檻視為上游異常（斷線／截斷／schema 改版），拒絕覆寫鏡像與索引

_META_RE = re.compile(r"<meta\b[^>]*>", re.IGNORECASE)
_OG_RE = re.compile(r'property\s*=\s*"og:description"', re.IGNORECASE)
_CONTENT_RE = re.compile(r'content\s*=\s*"([^"]*)"', re.IGNORECASE)
_GROUP_HEAD_RE = re.compile(r"^### (\S+) ")


def parse_entries(raw: str) -> list[dict[str, object]]:
    """rest?a= 的 JSON 陣列 → 只留需要的欄位。"""
    return [{k: e.get(k) for k in KEEP} for e in json.loads(raw)]


def validate_payload(entries: list[dict[str, object]]) -> None:
    """驗證 rest?a= 回應是否為完整全量清單，非上游斷線／截斷／schema 改版的殘缺資料。

    未過 → ValueError（呼叫端不得寫入鏡像或索引，保留既有檔案）。
    """
    if len(entries) < MIN_ENTRIES:
        raise ValueError(f"entries 只有 {len(entries)} 筆，低於 MIN_ENTRIES={MIN_ENTRIES}，疑似上游異常")
    seen_ids: set[object] = set()
    seen_fathers: set[str] = set()
    for i, e in enumerate(entries):
        for field in ("name", "Description", "CategoryName", "father"):
            value = e.get(field)
            if not isinstance(value, str) or not value:
                raise ValueError(f"entries[{i}] 的 {field!r} 非空字串: {value!r}")
        entry_id = e.get("id")
        if entry_id in seen_ids:
            raise ValueError(f"entries[{i}] 的 id 重複: {entry_id!r}")
        seen_ids.add(entry_id)
        seen_fathers.add(str(e["father"]))
    missing = [f for f in FATHER_ORDER if f not in seen_fathers]
    if missing:
        raise ValueError(f"缺少下列大類（可能是 schema 改版）: {missing}")


def og_description(page: str) -> str:
    """條目頁內文由 JS 渲染；原始 HTML 只有 og:description 有文字。"""
    for tag in _META_RE.findall(page):
        if _OG_RE.search(tag):
            found = _CONTENT_RE.search(tag)
            return html.unescape(found.group(1)).strip() if found else ""
    return ""


def _father_key(father: str) -> tuple[int, str]:
    return (FATHER_ORDER.index(father), "") if father in FATHER_ORDER else (len(FATHER_ORDER), father)


def _validate_entry(e: dict[str, object]) -> None:
    name = str(e["name"])
    for bad in ("·", "`", "\n"):
        if bad in name:
            raise ValueError(f"entry name contains {bad!r}: {name!r}")
    for field in ("Description", "CategoryName"):
        value = str(e[field])
        if any(ch.isspace() for ch in value):
            raise ValueError(f"{field} contains whitespace for entry {name!r}: {value!r}")


def build_index(entries: list[dict[str, object]], fetched: str) -> str:
    """產生 references 名稱索引（決定性：相同輸入 → 逐位元相同輸出）。"""
    tree: dict[str, dict[tuple[str, str], list[str]]] = {}
    for e in entries:
        _validate_entry(e)
        group = (str(e["Description"]), str(e["CategoryName"]))
        tree.setdefault(str(e["father"]), {}).setdefault(group, []).append(str(e["name"]))
    lines = [
        "# xshelp 名稱索引",
        "",
        f"> 由 xshelp 官方站索引 API 產生（{fetched}，共 {len(entries)} 筆），只收名稱與分組，不含官方說明內容。",
        "> **用法：用搜尋找名稱，不要整份讀入。** 名稱不在本檔＝xshelp 查無，不得使用。",
        (
            "> 確認存在後，語法與說明用 `https://xshelp.xq.com.tw/XSHelp/rest?a=<名稱>` 取回 JSON"
            "（**中文名稱需先 URL-encode**，未編碼查無結果）；`name` 完全相符者可能不只一筆"
            "（同名分屬多個分組），依分組代碼（`Description`）比對目前所需的大類挑出正確那筆，"
            "讀 `desc`（語法）與 `fulldesc`（說明）；"
        ),
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


def _get(url: str) -> str:
    with urllib.request.urlopen(url, timeout=60) as resp:
        return resp.read().decode("utf-8")


def fetch(today: str) -> int:
    """抓全量索引存成鏡像；全文為空的條目補抓條目頁 og:description。"""
    entries = parse_entries(_get(REST_ALL))
    validate_payload(entries)  # 寫入前、補抓 og:description 前先驗證，異常時不浪費請求也不覆寫鏡像
    for e in entries:
        if not (e.get("desc") or e.get("fulldesc")):
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
    validate_payload(mirror["entries"])  # 驗證通過才覆寫既有索引，異常時保留舊檔
    INDEX_FILE.write_text(build_index(mirror["entries"], mirror["fetched"]), encoding="utf-8")
    return len(mirror["entries"])


def main(argv: list[str]) -> int:
    if argv[1:] == ["fetch"]:
        try:
            print(f"鏡像 {fetch(datetime.now(UTC).date().isoformat())} 筆 → {MIRROR_FILE}")
        except ValueError as err:
            print(f"fetch 失敗，未覆寫鏡像：{err}", file=sys.stderr)
            return 1
        return 0
    if argv[1:] == ["index"]:
        try:
            print(f"索引 {write_index()} 筆 → {INDEX_FILE}")
        except ValueError as err:
            print(f"index 失敗，未覆寫索引：{err}", file=sys.stderr)
            return 1
        return 0
    print("用法：python -B scripts/xshelp_mirror.py fetch|index", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
