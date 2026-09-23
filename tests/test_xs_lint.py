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

import xs_lint


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

    def test_xshelp_callable_keywords_not_flagged(self) -> None:
        # xshelp inputkind 官方範例：Dict / DateRange / SymbolPrice 以呼叫形式出現，不應誤報。
        # 只斷言這三者：宣告名稱 U( / D( / P( 被當成呼叫而誤報是既有已知限制（main 即如此），
        # 屬另案處理，不在本測試範圍。
        code = (
            'input: U(1, "單位", inputkind:=Dict(["金額",1],["張數",2]));\n'
            'input: D(20180301, "日期", inputkind:=daterange(20160301,20190301,"D"));\n'
            'input: P(200, "價格", inputkind:=SymbolPrice());\n'
        )
        warns = xs_lint.check_unknown_tokens(code)
        self.assertFalse(any(k in w for w in warns for k in ("dict", "daterange", "symbolprice")))

    def test_named_parameter_keyword_called_is_flagged(self) -> None:
        # checkbox 是 Plot 的命名參數（checkbox:=1），寫成 checkbox( 屬可疑呼叫，應警示
        warns = xs_lint.check_unknown_tokens("checkbox(1);")
        self.assertTrue(any("checkbox" in w for w in warns))

    def test_reserved_words_called_are_flagged(self) -> None:
        # xshelp 保留字「目前並沒有任何作用」，呼叫形式應警示
        for word in ("Bool", "Int", "Float", "Double"):
            with self.subTest(word=word):
                warns = xs_lint.check_unknown_tokens(f"value1 = {word}(1);")
                self.assertTrue(any(word.lower() in w for w in warns))

    def test_known_tokens_populated(self) -> None:
        # 蒸餾後 KNOWN_TOKENS 不應為空（否則檢查靜默停用）
        self.assertGreater(len(xs_lint.KNOWN_TOKENS), 400)


class TestStreamReconfigure(unittest.TestCase):
    def test_proxied_cp950_stream_switched_to_utf8(self) -> None:
        # 代理包裝過的 cp950 串流（如 Colorama）也要被轉成 UTF-8，否則中文警示會 UnicodeEncodeError
        import importlib.util
        import io

        class Proxy:
            def __init__(self, inner: io.TextIOWrapper) -> None:
                self._inner = inner

            def __getattr__(self, name: str) -> object:
                return getattr(self._inner, name)

        inner = io.TextIOWrapper(io.BytesIO(), encoding="cp950")
        saved = sys.stdout
        sys.stdout = Proxy(inner)  # type: ignore[assignment]
        try:
            spec = importlib.util.spec_from_file_location("xs_lint_fresh", xs_lint.__file__)
            assert spec is not None and spec.loader is not None
            spec.loader.exec_module(importlib.util.module_from_spec(spec))
        finally:
            sys.stdout = saved
        self.assertEqual(inner.encoding, "utf-8")


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
