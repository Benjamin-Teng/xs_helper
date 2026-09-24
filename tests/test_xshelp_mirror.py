#!/usr/bin/env python3
"""xshelp_mirror 純函數測試（不連網）。"""
from __future__ import annotations

import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import xs_lint
import xshelp_mirror as m

_ASCII_IDENT = re.compile(r"^[A-Za-z_]\w*$")

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

    def test_header_warns_url_encode_and_group_code_selection(self) -> None:
        self.assertIn("URL-encode", self.text)
        self.assertIn("分組代碼", self.text)

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

    def test_name_with_backtick_raises(self) -> None:
        bad = json.loads(json.dumps(FIXTURE, ensure_ascii=False))
        bad[0]["name"] = "P`lot"
        entries = m.parse_entries(json.dumps(bad, ensure_ascii=False))
        with self.assertRaises(ValueError):
            m.build_index(entries, "2026-09-24")


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


def _make_valid_payload(n: int = m.MIN_ENTRIES) -> list[dict[str, object]]:
    """>=n 筆合成資料，涵蓋每個 FATHER_ORDER 大類，id 唯一。"""
    fathers = m.FATHER_ORDER
    return [
        {
            "id": i,
            "name": f"Name{i}",
            "Description": "GROUPCODE",
            "CategoryName": "分組",
            "father": fathers[i % len(fathers)],
        }
        for i in range(n)
    ]


class TestValidatePayload(unittest.TestCase):
    def test_valid_payload_passes(self) -> None:
        m.validate_payload(_make_valid_payload())  # 不應丟例外

    def test_empty_list_raises(self) -> None:
        with self.assertRaises(ValueError):
            m.validate_payload([])

    def test_missing_name_raises(self) -> None:
        entries = _make_valid_payload()
        entries[0] = dict(entries[0])
        del entries[0]["name"]
        with self.assertRaises(ValueError):
            m.validate_payload(entries)

    def test_empty_name_raises(self) -> None:
        entries = _make_valid_payload()
        entries[0] = dict(entries[0])
        entries[0]["name"] = ""
        with self.assertRaises(ValueError):
            m.validate_payload(entries)

    def test_duplicate_id_raises(self) -> None:
        entries = _make_valid_payload()
        entries[1] = dict(entries[1])
        entries[1]["id"] = entries[0]["id"]
        with self.assertRaises(ValueError):
            m.validate_payload(entries)

    def test_below_min_entries_raises(self) -> None:
        with self.assertRaises(ValueError):
            m.validate_payload(_make_valid_payload(m.MIN_ENTRIES - 1))

    def test_missing_father_category_raises(self) -> None:
        remaining = m.FATHER_ORDER[1:]  # 缺 FATHER_ORDER[0] 這個大類
        n = m.MIN_ENTRIES + len(remaining)
        entries: list[dict[str, object]] = [
            {
                "id": i,
                "name": f"Name{i}",
                "Description": "GROUPCODE",
                "CategoryName": "分組",
                "father": remaining[i % len(remaining)],
            }
            for i in range(n)
        ]
        with self.assertRaises(ValueError):
            m.validate_payload(entries)


class TestWriteIndexValidation(unittest.TestCase):
    def test_write_index_does_not_touch_index_file_when_mirror_invalid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            mirror_file = tmp_path / "entries.json"
            index_file = tmp_path / "xshelp-index.md"
            index_file.write_text("原有內容", encoding="utf-8")
            mirror_file.write_text(
                json.dumps({"fetched": "2026-09-24", "source": "x", "entries": []}, ensure_ascii=False),
                encoding="utf-8",
            )
            original_mirror, original_index = m.MIRROR_FILE, m.INDEX_FILE
            m.MIRROR_FILE, m.INDEX_FILE = mirror_file, index_file
            try:
                with self.assertRaises(ValueError):
                    m.write_index()
            finally:
                m.MIRROR_FILE, m.INDEX_FILE = original_mirror, original_index
            self.assertEqual(index_file.read_text(encoding="utf-8"), "原有內容")


class TestLintCoversIndexedFunctions(unittest.TestCase):
    def test_every_ascii_function_name_is_known_to_lint(self) -> None:
        tree = m.parse_index(m.INDEX_FILE.read_text(encoding="utf-8"))
        names = {n for f in ("內建函數", "系統函數") for g in tree.get(f, {}).values() for n in g}
        missing = sorted(n for n in names if _ASCII_IDENT.match(n) and n.lower() not in xs_lint.KNOWN_TOKENS)
        self.assertEqual(missing, [])


if __name__ == "__main__":
    unittest.main()
