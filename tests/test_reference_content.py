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
        self.assertRegex(self.code, r"switch\s*\(")
        self.assertRegex(self.code, r"case \d+ to \d+:")


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


if __name__ == "__main__":
    unittest.main()
