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
        # xshelp inputkind 官方範例整段：Dict / DateRange / SymbolPrice 呼叫與宣告名稱都不應誤報
        code = (
            'input: U(1, "單位", inputkind:=Dict(["金額",1],["張數",2]));\n'
            'input: D(20180301, "日期", inputkind:=daterange(20160301,20190301,"D"));\n'
            'input: P(200, "價格", inputkind:=SymbolPrice());\n'
        )
        self.assertEqual(xs_lint.check_unknown_tokens(code), [])

    def test_xshelp_gap_filled_functions_not_flagged(self) -> None:
        # 2026-09-24 xshelp 函數目錄窮舉補列：FIELDFUNC/GENERALFUNC 漏收與新分類 SDTFUNC
        code = (
            'Value1 = GetfieldFiscalQ("月營收");\n'
            'Value2 = GetfieldFiscalY("月營收");\n'
            'Value3 = GetSymbolFieldStartOffset("1101.TW", "月營收");\n'
            'Value4 = GetSymbolFieldTime("1101.TW", "月營收");\n'
            "SDT_SetValue(sym, 1, Close);\n"
            "Value5 = SDT_GetValue(sym, 1);\n"
            "Value6 = SDT_Average_L(1);\n"
            "SDT_Sort(1, keyarr);\n"
        )
        self.assertEqual(xs_lint.check_unknown_tokens(code), [])

    def test_declaration_names_not_flagged(self) -> None:
        # issue #2：var/input/... 宣告的名稱不是函數呼叫
        cases = [
            "var: acc(0), idx(0);",
            "Vars: a1(0), b2(0);",
            "Variable: v1(0);",
            "Variables: v2(0), v3(0);",
            'input: pv(numericsimple, "成交金額");',
            "Inputs: len1(5), len2(10);",
            "var: intraBarPersist _last_date(0), intrabarpersist _cnt(0);",
            "Array: MAArray[](0); Arrays: a[10](0);",
            "Group: myGroup();",
            "var:\n    first_v(0),\n    second_v(0);",
        ]
        for code in cases:
            with self.subTest(code=code):
                self.assertEqual(xs_lint.check_unknown_tokens(code), [])

    def test_calls_inside_declarations_still_checked(self) -> None:
        # 宣告只豁免「名稱」；初始值與命名參數裡的真實呼叫仍要檢查
        warns = xs_lint.check_unknown_tokens(
            'var: x(FooBar(1)), y(0);\ninput: z(0, "z", inputkind:=BazQux());'
        )
        self.assertEqual(sorted(w.split("：")[1].split("（")[0] for w in warns), ["bazqux", "foobar"])

    def test_named_parameter_colon_equals_is_not_declaration(self) -> None:
        # `checkbox:=1` 的 `:` 不是宣告冒號，後面的未知呼叫仍要警示
        warns = xs_lint.check_unknown_tokens('plot1(close, "c", checkbox:=1); Foo(1);')
        self.assertTrue(any("foo" in w for w in warns))

    def test_unterminated_declarations_scan_linearly(self) -> None:
        # 未打分號的宣告不可讓每個 var: 各自重掃尾段（O(n²)）。
        # 16000 行：線性約 0.01 秒；平方級實測外推約 50 秒以上。
        import time

        t0 = time.perf_counter()
        warns = xs_lint.check_unknown_tokens(("var:\n" * 16000) + "Foo();")
        self.assertLess(time.perf_counter() - t0, 1.0)
        self.assertTrue(any("foo" in w for w in warns))

    def test_same_name_called_outside_declaration_is_checked(self) -> None:
        # 豁免只作用在宣告位置；宣告外同名的呼叫照常檢查
        warns = xs_lint.check_unknown_tokens("var: mine(0);\nvalue1 = mine(1);")
        self.assertTrue(any("mine" in w for w in warns))

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
