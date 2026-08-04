from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def load_json(relative_path: str) -> dict:
    return json.loads((ROOT / relative_path).read_text(encoding="utf-8"))


class TestPluginManifests(unittest.TestCase):
    def test_both_hosts_publish_version_0_3_0(self) -> None:
        claude = load_json(".claude-plugin/plugin.json")
        codex = load_json(".codex-plugin/plugin.json")
        self.assertEqual(claude["name"], "xs-helper")
        self.assertEqual(codex["name"], "xs-helper")
        self.assertEqual(claude["version"], "0.3.0")
        self.assertEqual(codex["version"], "0.3.0")

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


if __name__ == "__main__":
    unittest.main()
