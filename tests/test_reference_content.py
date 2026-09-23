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

import xs_lint


def read_ref(name: str) -> str:
    return (REFS / name).read_text(encoding="utf-8")


def xs_blocks(text: str) -> list[str]:
    return re.findall(r"```xs\n(.*?)```", text, re.DOTALL)


class TestReferenceCodeBlocksLintClean(unittest.TestCase):
    def test_every_xs_block_has_no_lint_warning(self) -> None:
        for path in sorted(REFS.glob("*.md")):
            for i, block in enumerate(xs_blocks(path.read_text(encoding="utf-8"))):
                with self.subTest(file=path.name, block=i):
                    code = xs_lint.strip_comments(block)
                    self.assertEqual(xs_lint.check_unknown_tokens(code) + xs_lint.check_structure(code), [])


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
        self.assertRegex(self.code, r"case \d+ to \d+:")
        blocks = xs_blocks(read_ref("language.md"))
        self.assertTrue(
            any(len(re.findall(r"\bswitch\s*\(", block, re.IGNORECASE)) >= 2 for block in blocks),
            "expected at least one xs block with a nested switch (>=2 `switch(` occurrences)",
        )


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


class TestTypeSemantics(unittest.TestCase):
    def test_simple_series_ref_explained_with_source(self) -> None:
        text = read_ref("language.md")
        self.assertIn("僅適用於函數腳本", text)
        self.assertIn("HelpName=NumericRef", text)
        self.assertIn("HelpName=Numeric&group=DECLARATION", text)


class TestXshelpFunctionsCovered(unittest.TestCase):
    # 2026-09-24 以 xshelp rest 索引窮舉 *FUNC 分類（a-z 逐字母查 rest?a=<字母>，以 id 去重，
    # 436 個函數）後，比對 builtin-functions.md + system-functions.md 反引號名單，原本漏收的
    # 42 個函數。GetBarOffset 已收錄（builtin-functions.md），不在此名單。無欄位/非函數需排除。
    # 全部 42 個皆已補入 builtin-functions.md 對應表格（4 個 FIELDFUNC/GENERALFUNC 補漏，
    # 38 個新分類「9. SDT 函數（SDTFUNC）」，含 SDT_Sum / SDT_Sum_L）。
    MISSING_BEFORE: tuple[str, ...] = (
        "GetfieldFiscalQ",
        "GetfieldFiscalY",
        "GetSymbolFieldStartOffset",
        "GetSymbolFieldTime",
        "SDT_Average",
        "SDT_Average_L",
        "SDT_GetKeys",
        "SDT_GetKeys_L",
        "SDT_GetString",
        "SDT_GetString_L",
        "SDT_GetValue",
        "SDT_GetValue_L",
        "SDT_HasKey",
        "SDT_HasKey_L",
        "SDT_Max",
        "SDT_Max_L",
        "SDT_Median",
        "SDT_Median_L",
        "SDT_Min",
        "SDT_Min_L",
        "SDT_RemoveAll",
        "SDT_RemoveAll_L",
        "SDT_RemoveKey",
        "SDT_RemoveKey_L",
        "SDT_SetColumnName",
        "SDT_SetColumnName_L",
        "SDT_SetString",
        "SDT_SetStringIf",
        "SDT_SetStringIf_L",
        "SDT_SetString_L",
        "SDT_SetValue",
        "SDT_SetValueIf",
        "SDT_SetValueIf_L",
        "SDT_SetValue_L",
        "SDT_Sort",
        "SDT_SortKey",
        "SDT_SortKey_L",
        "SDT_SortString",
        "SDT_SortString_L",
        "SDT_Sort_L",
        "SDT_Sum",
        "SDT_Sum_L",
    )

    def test_previously_missing_functions_now_documented(self) -> None:
        text = read_ref("builtin-functions.md") + read_ref("system-functions.md")
        for name in self.MISSING_BEFORE:
            with self.subTest(name=name):
                self.assertIn(f"`{name}`", text)


if __name__ == "__main__":
    unittest.main()
