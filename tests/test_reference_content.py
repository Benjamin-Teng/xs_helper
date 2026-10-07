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


_DECLARATION_RE = re.compile(
    r"\b(?P<kind>inputs?|vars?|variables?)\s*:(?!=)(?P<body>.*?);",
    re.IGNORECASE | re.DOTALL,
)
_DECLARED_NAME_RE = re.compile(
    r"(?:^|,)\s*(?:intraBarPersist\s+)?(?P<name>[A-Za-z_]\w*)\s*\(",
    re.IGNORECASE,
)
_LINEARREG_RE = re.compile(
    r"\b(?P<receiver>[A-Za-z_]\w*)\s*=\s*LinearReg\s*\((?P<arguments>[^()]*)\)",
    re.IGNORECASE | re.DOTALL,
)


def linearreg_compatibility_issues(block: str) -> list[str]:
    """驗證單一 XS code block 中平坦的 LinearReg 相容性範例。

    此處刻意不是 XS parser：只檢查 skill 內範例所需的直接參數與宣告形式，且宣告
    必須出現在同一 code block、每次呼叫之前。
    """
    code = xs_lint.strip_comments(block)
    issues: list[str] = []
    for call in _LINEARREG_RE.finditer(code):
        variables: set[str] = set()
        for declaration in _DECLARATION_RE.finditer(code, 0, call.start()):
            names = {
                name.group("name").lower()
                for name in _DECLARED_NAME_RE.finditer(declaration.group("body"))
            }
            if not declaration.group("kind").lower().startswith("input"):
                variables.update(names)

        arguments = [argument.strip() for argument in call.group("arguments").split(",")]
        if len(arguments) != 7 or any(not argument for argument in arguments):
            issues.append("LinearReg 必須有七個非空參數")
            continue
        if call.group("receiver").lower() not in variables:
            issues.append("LinearReg 接收變數必須先宣告為 variable")

        outputs = arguments[3:]
        output_names = [output.lower() for output in outputs]
        if any(name not in variables for name in output_names):
            issues.append("LinearReg 四個輸出必須先宣告為 variable")
        if len(set(output_names)) != 4:
            issues.append("LinearReg 四個輸出必須互異")
        if any(name in {"slope", "angle"} for name in output_names):
            issues.append("LinearReg 輸出不可獨立命名為 slope 或 angle")
    return issues


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


class TestGapFillingTask7(unittest.TestCase):
    """Task 7 (2026-09-24)：驗收測試發現的 4 個推測缺口，逐一改成明講或標「待查證」。"""

    def test_rank_offset_supported_explicitly(self) -> None:
        text = read_ref("language.md")
        self.assertIn("_bias10.pos[1]", text)
        self.assertIn("支援 `[n]` 位移", text)

    def test_symbolprice_series_usage_is_silent(self) -> None:
        text = read_ref("language.md")
        # xshelp 對「宣告出來的變數能否像序列一樣用（Average / [n]）」與
        # 「範例預設值 200 代表什麼」都沒有說明，須明講待查證，不可自行補語意。
        self.assertIn("xshelp 未說明", text)
        self.assertIn("待查證", text)

    def test_controlflow_keywords_not_restricted_by_script_type_in_xshelp(self) -> None:
        text = read_ref("language.md")
        self.assertIn("xshelp 條目未限定腳本類型", text)
        # 官方範例庫的實際分佈要寫進去佐證，且是可查證的計數，不是憑印象寫的語意。
        self.assertIn("Once", text)
        self.assertIn("自動交易", text)
        self.assertIn("突破整理格局.xs", text)

    def test_outputfield_signature_matches_xshelp_overloads(self) -> None:
        text = read_ref("builtin-functions.md")
        # xshelp fulldesc 逐字列出的四種重載（序號版）
        self.assertIn("OutputField(輸出序號, 數值)", text)
        self.assertIn("OutputField(輸出序號, 數值, 小數位數)", text)
        self.assertIn("OutputField(輸出序號, 數值, 小數位數, 輸出欄位名稱)", text)
        # order 範例把字串放在「小數位數」的位置，與上面簽名的位置定義互相矛盾，
        # 必須明講這個落差，不能假裝兩段來源一致。
        self.assertIn("第 2 個位置參數應該是「小數位數」", text)

    def test_plot_numbered_forms_and_series_reference(self) -> None:
        text = read_ref("builtin-functions.md")
        # xshelp desc 逐字列出的 Plot1 三種重載
        self.assertIn("Plot1(指標數值)", text)
        self.assertIn("Plot1(指標數值，繪圖序列名稱)", text)
        self.assertIn("Plot1(指標數值，繪圖序列名稱，checkbox:=1)", text)
        # fulldesc 的兩個關鍵事實：最多 999 條、Plot1~Plot99 可當數列引用
        self.assertIn("999", text)
        self.assertIn("Plot1到Plot99除了可以是一個函數之外，也可以在腳本內被當成數列來引用", text)
        # 範例#2 逐字（含 Plot2 - Plot1 這行數列引用）
        self.assertIn("Value1 = Plot2 - Plot1;", text)
        # 當數列讀的能力必須明講只到 Plot1~Plot99，不能延伸到 Plot100~Plot999
        self.assertIn("當數列讀的能力明確只到 `Plot1`～`Plot99`", text)
        self.assertIn("並未提到它們也能像 `Plot1`～`Plot99` 那樣被當成數列讀", text)


class TestXshelpIndexWiring(unittest.TestCase):
    def test_skill_lists_index_and_f3_uses_rest_api(self) -> None:
        skill = (ROOT / "skills" / "xs" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("](references/xshelp-index.md)", skill)
        self.assertIn("rest?a=", skill)

    def test_f3_step2_requires_url_encoding_chinese_names(self) -> None:
        skill = (ROOT / "skills" / "xs" / "SKILL.md").read_text(encoding="utf-8")
        self.assertIn("URL-encode", skill)

    def test_fields_points_to_index_for_full_lists(self) -> None:
        text = read_ref("fields.md")
        self.assertIn("xshelp-index.md", text)


class TestXqCompilerCompatibilityFeedback(unittest.TestCase):
    def setUp(self) -> None:
        self.skill = (ROOT / "skills" / "xs" / "SKILL.md").read_text(encoding="utf-8")

    def test_linearreg_example_is_structurally_compatible(self) -> None:
        blocks = xs_blocks(self.skill)
        linearreg_blocks = [block for block in blocks if re.search(r"\bLinearReg\s*\(", block, re.IGNORECASE)]
        self.assertEqual(len(linearreg_blocks), 1)
        self.assertEqual(linearreg_compatibility_issues(linearreg_blocks[0]), [])

    def test_linearreg_example_is_pasteable_indicator_with_input(self) -> None:
        block = next(
            block for block in xs_blocks(self.skill) if re.search(r"\bLinearReg\s*\(", block, re.IGNORECASE)
        )
        self.assertTrue(block.startswith("{@type:indicator}"))
        self.assertRegex(block, r"(?im)^input\s*:")

    def test_linearreg_structure_accepts_case_and_newline_variants(self) -> None:
        block = """INPUT: length(20);
VARIABLE: status(0), outputOne(0), outputTwo(0), outputThree(0), outputFour(0);
STATUS = linearreg(
    CLOSE, length, 0,
    outputOne, outputTwo, outputThree, outputFour
);"""
        self.assertEqual(linearreg_compatibility_issues(block), [])

    def test_linearreg_structure_accepts_generic_first_three_parameters(self) -> None:
        block = """input: period(20);
variable: status(0), outputOne(0), outputTwo(0), outputThree(0), outputFour(0);
status = LinearReg(priceSeries, windowSize, projectionTarget, outputOne, outputTwo, outputThree, outputFour);"""
        self.assertEqual(linearreg_compatibility_issues(block), [])

    def test_linearreg_structure_rejects_incompatible_examples(self) -> None:
        valid = """input: length(20);
variable: status(0), outputOne(0), outputTwo(0), outputThree(0), outputFour(0);
status = LinearReg(Close, length, 0, outputOne, outputTwo, outputThree, outputFour);"""
        cases = {
            "missing_receiver": valid.replace("status(0), ", ""),
            "missing_output": valid.replace("outputFour(0);", "").replace("outputFour);", "missingOutput);"),
            "six_parameters": valid.replace(", outputFour);", ");"),
            "eight_parameters": valid.replace("outputFour);", "outputFour, extraOutput);"),
            "empty_parameter": valid.replace("outputTwo,", ","),
            "reserved_slope": valid.replace("outputOne", "slope"),
            "reserved_angle": valid.replace("outputTwo", "angle"),
            "duplicate_output": valid.replace("outputFour);", "outputThree);"),
            "late_declaration": valid.replace(
                "variable: status(0), outputOne(0), outputTwo(0), outputThree(0), outputFour(0);\n",
                "",
            ) + "\nvariable: status(0), outputOne(0), outputTwo(0), outputThree(0), outputFour(0);",
            "commented_declaration": valid.replace(
                "variable: status(0), outputOne(0), outputTwo(0), outputThree(0), outputFour(0);",
                "// variable: status(0), outputOne(0), outputTwo(0), outputThree(0), outputFour(0);",
            ),
        }
        for name, block in cases.items():
            with self.subTest(name=name):
                self.assertNotEqual(linearreg_compatibility_issues(block), [])

        # 宣告不能跨 fenced block 串接；前一區塊的 variable 對下一區塊無效。
        first_block = "variable: status(0), outputOne(0), outputTwo(0), outputThree(0), outputFour(0);"
        second_block = "input: length(20);\n" + valid.split("\n", 2)[2]
        self.assertEqual(linearreg_compatibility_issues(first_block), [])
        self.assertNotEqual(linearreg_compatibility_issues(second_block), [])

    def test_feedback_is_not_presented_as_official_or_default_protection_rule(self) -> None:
        self.assertIn("不是 xshelp 官方定義", self.skill)
        self.assertIn("部分 XQ 版本", self.skill)
        self.assertIn("只有使用者明確要求「交由 XQ 保護」時", self.skill)
        self.assertIn("這不是一般預設規則", self.skill)


if __name__ == "__main__":
    unittest.main()
