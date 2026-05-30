#!/usr/bin/env python3
"""xs_lint 單元測試（stdlib unittest，零第三方相依）。

執行：python -m unittest tests.test_xs_lint   （於 repo 根目錄）
或   python tests/test_xs_lint.py
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

# 讓 import 找得到 scripts/xs_lint.py
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))

import xs_lint  # noqa: E402


class TestStripComments(unittest.TestCase):
    def test_empty(self) -> None:
        self.assertEqual(xs_lint.strip_comments("").strip(), "")

    def test_line_comment(self) -> None:
        self.assertNotIn("hello", xs_lint.strip_comments("a = 1; // hello"))

    def test_block_comment(self) -> None:
        self.assertNotIn("note", xs_lint.strip_comments("{ note } a = 1;"))

    def test_string_literal_removed(self) -> None:
        # 字串內的 begin 不應殘留，否則會污染結構計數
        out = xs_lint.strip_comments('Alert("begin to buy");')
        self.assertNotIn("begin", out.lower())


class TestCheckStructure(unittest.TestCase):
    def test_empty_no_warning(self) -> None:
        self.assertEqual(xs_lint.check_structure(""), [])

    def test_balanced(self) -> None:
        code = "if c > o then begin Buy; end;"
        self.assertEqual(xs_lint.check_structure(code), [])

    def test_begin_end_mismatch(self) -> None:
        warns = xs_lint.check_structure("begin Buy;")
        self.assertTrue(any("begin" in w for w in warns))

    def test_if_without_then(self) -> None:
        warns = xs_lint.check_structure("if c > o Buy;")
        self.assertTrue(any("then" in w for w in warns))

    def test_more_then_than_if_ok(self) -> None:
        # then 多於 if 不警示（保守：只抓 if > then）
        self.assertEqual(xs_lint.check_structure("if c>o then x; then"), [])


class TestCheckUnknownTokens(unittest.TestCase):
    def test_known_passes(self) -> None:
        self.assertEqual(xs_lint.check_unknown_tokens("x = Average(close, 20);"), [])

    def test_unknown_flagged(self) -> None:
        warns = xs_lint.check_unknown_tokens("x = FooBar(close);")
        self.assertTrue(any("foobar" in w.lower() for w in warns))

    def test_numeric_suffix_normalized(self) -> None:
        # Plot2 / OutputField3 應被去尾數正規化後命中 plot / outputfield
        self.assertEqual(xs_lint.check_unknown_tokens("Plot2(close); OutputField3(high);"), [])

    def test_empty_code(self) -> None:
        self.assertEqual(xs_lint.check_unknown_tokens(""), [])

    def test_known_tokens_populated(self) -> None:
        # 蒸餾後 KNOWN_TOKENS 不應為空（否則檢查靜默停用）
        self.assertGreater(len(xs_lint.KNOWN_TOKENS), 400)


class TestGetTargetPath(unittest.TestCase):
    def test_xs_path(self) -> None:
        ev = {"tool_input": {"file_path": "C:/x/foo.XS"}}  # 大小寫不敏感
        self.assertEqual(xs_lint.get_target_path(ev), "C:/x/foo.XS")

    def test_non_xs(self) -> None:
        self.assertIsNone(xs_lint.get_target_path({"tool_input": {"file_path": "a.py"}}))

    def test_missing(self) -> None:
        self.assertIsNone(xs_lint.get_target_path({}))


if __name__ == "__main__":
    unittest.main()
