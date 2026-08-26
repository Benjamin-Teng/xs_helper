from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


class TestPluginManifests(unittest.TestCase):
    def test_both_hosts_publish_version_0_4_0(self) -> None:
        claude = load_json(".claude-plugin/plugin.json")
        codex = load_json(".codex-plugin/plugin.json")
        self.assertEqual(claude["name"], "xs-helper")
        self.assertEqual(codex["name"], "xs-helper")
        self.assertEqual(claude["version"], "0.4.0")
        self.assertEqual(codex["version"], "0.4.0")

    def test_codex_manifest_points_to_shared_skill_only(self) -> None:
        manifest = load_json(".codex-plugin/plugin.json")
        self.assertEqual(manifest["skills"], "./skills/")
        self.assertNotIn("apps", manifest)
        self.assertNotIn("mcpServers", manifest)
        self.assertNotIn("hooks", manifest)
        self.assertEqual(manifest["interface"]["displayName"], "XS Helper")


class TestMarketplaces(unittest.TestCase):
    def test_claude_marketplace_still_exposes_xs_helper(self) -> None:
        marketplace = load_json(".claude-plugin/marketplace.json")
        self.assertEqual(marketplace["name"], "xs-tools")
        self.assertEqual(marketplace["plugins"][0]["name"], "xs-helper")

    def test_codex_marketplace_exposes_repository_root_plugin(self) -> None:
        marketplace = load_json(".agents/plugins/marketplace.json")
        entry = marketplace["plugins"][0]
        self.assertEqual(marketplace["name"], "xs-tools")
        self.assertEqual(entry["name"], "xs-helper")
        self.assertEqual(entry["source"]["source"], "url")
        self.assertEqual(
            entry["source"]["url"],
            "https://github.com/Benjamin-Teng/xs_helper.git",
        )
        self.assertEqual(entry["policy"]["installation"], "AVAILABLE")
        self.assertEqual(entry["policy"]["authentication"], "ON_INSTALL")
        self.assertEqual(entry["category"], "Productivity")


class TestCodexSkillMetadata(unittest.TestCase):
    def test_openai_yaml_exposes_xs_and_allows_implicit_invocation(self) -> None:
        metadata = (ROOT / "skills/xs/agents/openai.yaml").read_text(encoding="utf-8")
        self.assertIn('display_name: "XS Helper"', metadata)
        self.assertIn("$xs", metadata)
        self.assertIn("allow_implicit_invocation: true", metadata)

    def test_skill_fallback_is_host_neutral(self) -> None:
        skill = (ROOT / "skills/xs/SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("WebFetch", skill)
        self.assertIn("xshelp.xq.com.tw", skill)
        self.assertIn("網頁", skill)


class TestMarkdownDocumentation(unittest.TestCase):
    IDE_INSTALL_PROMPT = (
        "$skill-installer 請從 "
        "https://github.com/Benjamin-Teng/xs_helper/tree/main/skills/xs "
        "安裝 xs skill"
    )
    DOCUMENTS = (
        "README.md",
        "CHANGELOG.md",
        "docs/SPEC.md",
        "docs/architecture.md",
        "docs/superpowers/specs/2026-08-04-codex-plugin-compatibility-design.md",
        "docs/superpowers/specs/2026-08-04-codex-conversation-install-design.md",
    )

    def test_all_product_docs_cover_both_installation_paths(self) -> None:
        required = (
            "Claude Code",
            "Codex",
            "/plugin marketplace add Benjamin-Teng/xs_helper",
            "/plugin install xs-helper@xs-tools",
            "codex plugin marketplace add Benjamin-Teng/xs_helper",
            "codex plugin add xs-helper@xs-tools",
        )
        for relative_path in self.DOCUMENTS:
            with self.subTest(path=relative_path):
                text = (ROOT / relative_path).read_text(encoding="utf-8")
                for expected in required:
                    self.assertIn(expected, text)

    def test_manual_invocation_is_host_specific(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        self.assertIn("`/xs", readme)
        self.assertIn("`$xs", readme)

    def test_all_product_docs_cover_codex_ide_installation(self) -> None:
        required = (
            "VS Code",
            "Codex IDE",
            self.IDE_INSTALL_PROMPT,
            "/plugins",
            "不支援",
        )
        for relative_path in self.DOCUMENTS:
            with self.subTest(path=relative_path):
                text = (ROOT / relative_path).read_text(encoding="utf-8")
                for expected in required:
                    self.assertIn(expected, text)


class TestPublishedPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = (ROOT / "docs/index.html").read_text(encoding="utf-8")

    def test_page_metadata_and_release_are_dual_host(self) -> None:
        self.assertIn("Claude Code 與 Codex", self.html)
        self.assertIn("v0.4.0", self.html)

    def test_install_modal_contains_separate_host_commands(self) -> None:
        required = (
            "Claude Code 安裝",
            "Codex 安裝",
            "/plugin marketplace add Benjamin-Teng/xs_helper",
            "/plugin install xs-helper@xs-tools",
            "codex plugin marketplace add Benjamin-Teng/xs_helper",
            "codex plugin add xs-helper@xs-tools",
            "/xs Average 怎麼用？",
            "$xs Average 怎麼用？",
        )
        for expected in required:
            self.assertIn(expected, self.html)

    def test_benchmark_provenance_remains_claude_opus(self) -> None:
        self.assertIn("Claude Opus 4.8", self.html)
        self.assertIn("Claude Code Skill Benchmark", self.html)

    def test_claude_install_card_uses_orange_platform_theme(self) -> None:
        self.assertIn("--claude:#d97757", self.html)
        self.assertIn('class="platform-install platform-claude"', self.html)
        self.assertIn(".platform-claude h3::before", self.html)

    def test_codex_install_card_prioritizes_ide_chat(self) -> None:
        required = (
            "VS Code／Codex IDE（推薦）",
            (
                "$skill-installer 請從 https://github.com/Benjamin-Teng/"
                "xs_helper/tree/main/skills/xs 安裝 xs skill"
            ),
            "Codex CLI 對話介面",
            "/plugins",
            "終端機進階安裝",
            "IDE extension 目前不支援完整 plugin",
        )
        for expected in required:
            self.assertIn(expected, self.html)


class TestSkillLayoutForFixedDirInstallers(unittest.TestCase):
    """AC7: installers that only index the spec directory name must see every reference.

    Shioaji Pro (and any Agent Skills-spec loader) lists ``<skill>/references`` by that
    exact name, flat, and parses frontmatter line-by-line. A singular ``reference/``,
    a nested ``references/examples/``, or a ``>-`` block-scalar description all end up
    silently dropped (observed as ``references: []`` in the installed package record).
    """

    SKILL_DIR = ROOT / "skills/xs"
    EXPECTED_REFERENCES = frozenset(
        {
            "language.md",
            "builtin-functions.md",
            "system-functions.md",
            "fields.md",
            "script-types.md",
            "example-auto-trade.md",
            "example-function.md",
            "example-indicator.md",
            "example-screening.md",
            "example-alert.md",
        }
    )

    def test_skill_dir_uses_spec_directory_names_only(self) -> None:
        entries = {p.name for p in self.SKILL_DIR.iterdir()}
        self.assertEqual(entries, {"SKILL.md", "agents", "references"})
        self.assertFalse((self.SKILL_DIR / "reference").exists())

    def test_references_dir_is_flat_markdown(self) -> None:
        refs = self.SKILL_DIR / "references"
        names = {p.name for p in refs.iterdir()}
        self.assertEqual(names, self.EXPECTED_REFERENCES)
        for p in refs.iterdir():
            with self.subTest(path=p.name):
                self.assertTrue(p.is_file())
                self.assertEqual(p.suffix, ".md")

    def test_skill_md_links_only_to_flat_references(self) -> None:
        text = (self.SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        self.assertNotIn("](reference/", text)
        self.assertNotIn("examples/", text)
        linked = set(re.findall(r"\]\(references/([^)]+)\)", text))
        self.assertEqual(linked, self.EXPECTED_REFERENCES)

    def test_frontmatter_description_is_single_line_scalar(self) -> None:
        text = (self.SKILL_DIR / "SKILL.md").read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1]
        lines = [line for line in frontmatter.splitlines() if line.strip()]
        keys = {line.split(":", 1)[0] for line in lines}
        self.assertEqual(keys, {"name", "description"}, "every frontmatter line must be key: value")
        description = next(line for line in lines if line.startswith("description:"))
        value = description.split(":", 1)[1].strip()
        self.assertNotIn(value, {"|", ">", ">-", "|-"})
        self.assertGreater(len(value), 50)

    def test_claude_marketplace_entry_publishes_version(self) -> None:
        # Installers that read the Claude marketplace take the version from the entry,
        # not from plugin.json (Sinotrade's shioaji entry carries one; the Codex
        # marketplace schema is unverified for this field, so it stays manifest-only).
        entry = next(p for p in load_json(".claude-plugin/marketplace.json")["plugins"] if p["name"] == "xs-helper")
        self.assertEqual(entry["version"], "0.4.0")

    def test_maintained_docs_contain_no_obsolete_singular_reference_path(self) -> None:
        stale = re.compile(r"skills/xs/reference/|\]\(reference/|reference/examples/")
        # CHANGELOG is history and legitimately names the old path when describing the rename.
        maintained = (
            *(d for d in TestMarkdownDocumentation.DOCUMENTS if d != "CHANGELOG.md"),
            "skills/xs/SKILL.md",
        )
        for relative_path in maintained:
            with self.subTest(path=relative_path):
                text = (ROOT / relative_path).read_text(encoding="utf-8")
                self.assertIsNone(stale.search(text), f"obsolete reference/ path in {relative_path}")


if __name__ == "__main__":
    unittest.main()
