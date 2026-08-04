# Codex Plugin Compatibility Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `xs_helper` a native Codex plugin without regressing Claude Code support, and document both installation paths on every product-facing documentation surface.

**Architecture:** Keep `skills/xs/` as the only workflow and reference source. Add independent Claude and Codex manifests plus marketplaces that point to the shared skill, make the skill's online fallback tool-neutral, and protect the package and documentation contracts with standard-library tests.

**Tech Stack:** JSON manifests, YAML skill metadata, Markdown, static HTML/CSS/JavaScript, Python 3 `unittest`, Codex plugin/skill validators.

## Global Constraints

- Preserve `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, and Claude Code `/xs` installation behavior.
- Add `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, and `skills/xs/agents/openai.yaml` for native Codex support.
- Both hosts consume the existing `skills/xs/`; do not duplicate `SKILL.md` or `reference/`.
- Set both plugin manifests to strict semver `0.3.0`.
- Codex explicit invocation is `$xs`; Claude Code explicit invocation is `/xs`; implicit invocation remains enabled.
- The shared skill must not name Claude-only `WebFetch` or Codex-internal tool identifiers.
- Keep the existing XS boundaries: no invented tokens, runtime execution, backtesting, account connection, order placement, or live quotes.
- Add both installation paths to `README.md`, `docs/index.html`, `docs/SPEC.md`, `docs/architecture.md`, `CHANGELOG.md`, and the design documentation; do not add installation prose to `skills/xs/reference/`.
- Preserve the published benchmark's historical Claude Opus 4.8 provenance; do not imply it was rerun with Codex.
- Use only Python standard-library modules in repository tests.

---

### Task 1: Add the dual-host packaging contract

**Files:**
- Create: `tests/test_plugin_compatibility.py`
- Create: `.codex-plugin/plugin.json`
- Create: `.agents/plugins/marketplace.json`
- Create: `skills/xs/agents/openai.yaml`
- Modify: `.claude-plugin/plugin.json`
- Modify: `skills/xs/SKILL.md`

**Interfaces:**
- Consumes: existing Claude manifest, marketplace `xs-tools`, and shared `skills/xs/` directory.
- Produces: Codex manifest `name=xs-helper`, `version=0.3.0`, `skills=./skills/`; Codex marketplace entry `xs-helper@xs-tools`; skill UI name `XS Helper`; platform-neutral F3 fallback.

- [ ] **Step 1: Write the failing packaging tests**

Create `tests/test_plugin_compatibility.py` with this initial content:

```python
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
```

- [ ] **Step 2: Run the packaging tests and verify RED**

Run:

```powershell
python -m unittest tests.test_plugin_compatibility -v
```

Expected: failures for missing `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, and `skills/xs/agents/openai.yaml`; the version and `WebFetch` assertions also fail.

- [ ] **Step 3: Add the native Codex manifest**

Create `.codex-plugin/plugin.json` with this contract:

```json
{
  "name": "xs-helper",
  "version": "0.3.0",
  "description": "依 XQ 全球贏家的 XScript 規範撰寫、修改與解說 XS 腳本。",
  "author": {
    "name": "benjamin31588",
    "email": "benjamin31588@gmail.com",
    "url": "https://github.com/Benjamin-Teng"
  },
  "homepage": "https://benjamin-teng.github.io/xs_helper/",
  "repository": "https://github.com/Benjamin-Teng/xs_helper",
  "license": "MIT",
  "keywords": ["xscript", "xs", "xq", "全球贏家", "選股", "自動交易", "技術指標", "量化交易"],
  "skills": "./skills/",
  "interface": {
    "displayName": "XS Helper",
    "shortDescription": "依 XQ 規範撰寫與解說 XScript 腳本",
    "longDescription": "使用內建 XS 語法、函數、欄位與腳本類型 reference，協助撰寫、修改及解說 XQ 全球贏家的 XScript 腳本。",
    "developerName": "benjamin31588",
    "category": "Productivity",
    "capabilities": ["Read", "Write"],
    "websiteURL": "https://benjamin-teng.github.io/xs_helper/",
    "defaultPrompt": [
      "用 XS 寫一個台股選股條件。",
      "解釋這段 XScript 並檢查函數與欄位。"
    ]
  }
}
```

- [ ] **Step 4: Add the Codex marketplace entry**

Create `.agents/plugins/marketplace.json`:

```json
{
  "name": "xs-tools",
  "interface": {
    "displayName": "XS Tools"
  },
  "plugins": [
    {
      "name": "xs-helper",
      "source": {
        "source": "url",
        "url": "https://github.com/Benjamin-Teng/xs_helper.git"
      },
      "policy": {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL"
      },
      "category": "Productivity"
    }
  ]
}
```

- [ ] **Step 5: Add Codex skill UI metadata**

Create `skills/xs/agents/openai.yaml`:

```yaml
interface:
  display_name: "XS Helper"
  short_description: "依 XQ 規範撰寫、修改與解說 XScript（XS）腳本"
  default_prompt: "Use $xs to write, revise, or explain an XQ XScript (XS) script."

policy:
  allow_implicit_invocation: true
```

- [ ] **Step 6: Make the shared skill platform-neutral and bump Claude's version**

In `.claude-plugin/plugin.json`, change only `"version": "0.2.0"` to `"version": "0.3.0"`.

In `skills/xs/SKILL.md`, replace the F3 opening instruction with:

```markdown
reference 未涵蓋的函數 / 欄位 → 使用目前環境可用的網頁查詢或瀏覽工具查 XSHelp 官方站；查得後在回覆標明「此為線上查詢結果」：
```

Do not add host-specific invocation instructions to the skill body; keep `/xs` and `$xs` in product documentation and UI metadata.

- [ ] **Step 7: Run packaging tests and validators to verify GREEN**

Run:

```powershell
python -m unittest tests.test_plugin_compatibility -v
python 'C:\Users\ben0315\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py' .
python 'C:\Users\ben0315\.codex\skills\.system\skill-creator\scripts\quick_validate.py' skills/xs
```

Expected: all packaging tests pass; both validators exit `0` without errors.

- [ ] **Step 8: Commit the packaging deliverable**

```powershell
git add .claude-plugin/plugin.json .codex-plugin/plugin.json .agents/plugins/marketplace.json skills/xs/SKILL.md skills/xs/agents/openai.yaml tests/test_plugin_compatibility.py
git commit -m "feat: add native Codex plugin packaging"
```

---

### Task 2: Document both installation paths in every Markdown surface

**Files:**
- Modify: `tests/test_plugin_compatibility.py`
- Modify: `README.md`
- Modify: `docs/SPEC.md`
- Modify: `docs/architecture.md`
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: canonical marketplace name `xs-tools`, plugin name `xs-helper`, Claude command `/xs`, Codex command `$xs`.
- Produces: consistent dual-host installation guidance in every current product-facing Markdown document.

- [ ] **Step 1: Add failing documentation coverage tests**

Append this class to `tests/test_plugin_compatibility.py` before the `if __name__ == "__main__"` block:

```python
class TestMarkdownDocumentation(unittest.TestCase):
    DOCUMENTS = (
        "README.md",
        "CHANGELOG.md",
        "docs/SPEC.md",
        "docs/architecture.md",
        "docs/superpowers/specs/2026-08-04-codex-plugin-compatibility-design.md",
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
```

- [ ] **Step 2: Run the documentation test and verify RED**

Run:

```powershell
python -m unittest tests.test_plugin_compatibility.TestMarkdownDocumentation -v
```

Expected: failures identify `README.md`, `CHANGELOG.md`, `docs/SPEC.md`, and `docs/architecture.md` as missing Codex commands.

- [ ] **Step 3: Rewrite README installation and usage as a two-host contract**

Make these concrete changes in `README.md`:

- Change the lead and overview from Claude-only to “Claude Code 與 Codex plugin”.
- Replace model-specific wording such as “Claude 模型本身” with “通用模型本身”.
- Rename the feature row from `` `/xs` Skill `` to “XS Skill (`/xs` / `$xs`)”.
- Replace `WebFetch` with “可用的網頁查詢工具”.
- Split `## 安裝` into `### Claude Code` and `### Codex`.
- Keep the existing Claude block unchanged and add:

```shell
codex plugin marketplace add Benjamin-Teng/xs_helper
codex plugin add xs-helper@xs-tools
```

- State that Codex users explicitly invoke with `$xs <需求>` and Claude Code users with `/xs <需求>`; both may activate implicitly from XS-related prompts.
- Update status to `v0.3.0` and name both validation paths.

- [ ] **Step 4: Update the maintained project specification**

In `docs/SPEC.md`:

- Change the version table to `v1.2`, base to `v1.1`, modification date to `2026-08-04`, and note native Codex compatibility.
- Rewrite current Overview, target user, Goals G1/G3/G4, F1, F3, Input/Output, Tech Stack, Project Structure, Acceptance Criteria, and current Non-Functional Requirements using host-neutral “AI agent” language where behavior is shared.
- Add both manifest and marketplace paths to Project Structure.
- Add a `### 安裝與啟動` section containing both complete command sequences and `/xs` versus `$xs` invocation.
- Leave historical v1.1 session records intact, but label them as Claude-era history when a current reader could confuse them with the v1.2 package.

- [ ] **Step 5: Update architecture documentation**

In `docs/architecture.md`:

- Set current status to `v0.3.0` and describe the shared runtime as `/xs` on Claude Code and `$xs` on Codex.
- Add a `## 雙平台封裝與安裝` section before Phase 1 with a compact tree of `.claude-plugin/`, `.codex-plugin/`, `.agents/plugins/`, and shared `skills/xs/`.
- Include both complete command sequences from the global constraints.
- Change runtime F3 labels from `WebFetch` to “可用網頁工具”.
- Preserve removed-hook diagrams as historical records and keep that status explicit.

- [ ] **Step 6: Add the 0.3.0 changelog entry with install commands**

Insert before `0.2.0`:

```markdown
## [0.3.0] - 2026-08-04

### Added

- Codex 原生 plugin manifest、marketplace 與 `$xs` skill UI metadata；Claude Code 與 Codex 共用同一份 `skills/xs/`。
- Codex 安裝：`codex plugin marketplace add Benjamin-Teng/xs_helper` → `codex plugin add xs-helper@xs-tools`。

### Changed

- Claude Code 安裝仍為 `/plugin marketplace add Benjamin-Teng/xs_helper` → `/plugin install xs-helper@xs-tools` → `/reload-plugins`。
- F3 fallback 改為平台中立的網頁查詢指示；README、GitHub Pages、SPEC 與架構文件加入雙平台說明。
```

Add `[0.3.0]: https://github.com/Benjamin-Teng/xs_helper/releases/tag/v0.3.0` to the link list.

- [ ] **Step 7: Run documentation and packaging tests to verify GREEN**

Run:

```powershell
python -m unittest tests.test_plugin_compatibility -v
```

Expected: every documentation and packaging assertion passes.

- [ ] **Step 8: Commit the Markdown documentation deliverable**

```powershell
git add README.md CHANGELOG.md docs/SPEC.md docs/architecture.md tests/test_plugin_compatibility.py
git commit -m "docs: add Claude Code and Codex installation guides"
```

---

### Task 3: Update and verify the published GitHub Pages installation experience

**Files:**
- Modify: `tests/test_plugin_compatibility.py`
- Modify: `docs/index.html`

**Interfaces:**
- Consumes: the same canonical installation commands and invocation names used by Markdown documentation.
- Produces: dual-host page metadata, hero copy, footer copy, and an installation modal with separate Claude Code and Codex sections.

- [ ] **Step 1: Add failing published-page tests**

Append this class before the test module's `if __name__ == "__main__"` block:

```python
class TestPublishedPage(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = (ROOT / "docs/index.html").read_text(encoding="utf-8")

    def test_page_metadata_and_release_are_dual_host(self) -> None:
        self.assertIn("Claude Code 與 Codex", self.html)
        self.assertIn("v0.3.0", self.html)

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
```

- [ ] **Step 2: Run the page tests and verify RED**

Run:

```powershell
python -m unittest tests.test_plugin_compatibility.TestPublishedPage -v
```

Expected: dual-host metadata, `v0.3.0`, Codex commands, and `$xs` assertions fail; benchmark provenance assertion passes.

- [ ] **Step 3: Update page metadata, hero, and footer**

In `docs/index.html`:

- Change `<title>`, `og:title`, and `twitter:title` to `xs-helper — Claude Code 與 Codex 的 XS 助手`.
- Keep the benchmark tag `Claude Code Skill Benchmark` and all `Claude Opus 4.8` labels unchanged.
- Change the hero heading to `xs-helper：Claude Code 與 Codex 的 XS 助手` and version to `v0.3.0`.
- Explain in the lead that the same XS skill is available as `/xs` in Claude Code and `$xs` in Codex, while the displayed benchmark used Claude Opus 4.8.
- Change the footer product sentence to identify a shared Claude Code and Codex plugin; preserve the benchmark provenance line.

- [ ] **Step 4: Split the install modal into two platform sections**

Add `.platform-install` and `.platform-install + .platform-install` styles that preserve the existing modal width and add a divider between hosts. Replace the modal body with two clearly headed groups:

```html
<section class="platform-install" aria-labelledby="install-claude">
  <h3 id="install-claude">Claude Code 安裝</h3>
  <!-- existing three commands and /xs verification -->
</section>
<section class="platform-install" aria-labelledby="install-codex">
  <h3 id="install-codex">Codex 安裝</h3>
  <!-- codex marketplace add, codex plugin add, and $xs verification -->
</section>
```

Keep copy buttons attached to every command. Explain that a new Codex conversation may be needed after installation and that both hosts support implicit activation for XS-related prompts.

- [ ] **Step 5: Run page and full compatibility tests to verify GREEN**

Run:

```powershell
python -m unittest tests.test_plugin_compatibility.TestPublishedPage -v
python -m unittest discover -s tests -v
```

Expected: all page tests pass, followed by all repository tests passing with no errors.

- [ ] **Step 6: Commit the published-page deliverable**

```powershell
git add docs/index.html tests/test_plugin_compatibility.py
git commit -m "docs: add Codex install flow to published page"
```

---

### Task 4: Run final cross-host validation

**Files:**
- Verify: `.claude-plugin/plugin.json`
- Verify: `.claude-plugin/marketplace.json`
- Verify: `.codex-plugin/plugin.json`
- Verify: `.agents/plugins/marketplace.json`
- Verify: `skills/xs/SKILL.md`
- Verify: `skills/xs/agents/openai.yaml`
- Verify: all documentation and tests changed above.

**Interfaces:**
- Consumes: complete dual-host package and documentation.
- Produces: evidence that static tests, Codex validators, and available Claude validation succeed without uncommitted accidental changes.

- [ ] **Step 1: Run the complete Python suite**

```powershell
python -m unittest discover -s tests -v
```

Expected: all existing `xs_lint` tests and new compatibility tests pass.

- [ ] **Step 2: Validate the Codex plugin and skill**

```powershell
python 'C:\Users\ben0315\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py' .
python 'C:\Users\ben0315\.codex\skills\.system\skill-creator\scripts\quick_validate.py' skills/xs
```

Expected: both commands exit `0` with valid manifest/frontmatter output.

- [ ] **Step 3: Run Claude validation when the installed CLI exposes it**

First inspect availability:

```powershell
claude --version
```

If available, run the repository's previously used validation command:

```text
/plugin validate .
```

If the local Claude CLI cannot execute slash commands non-interactively, record that constraint in the final handoff; do not claim the validator ran. The unchanged Claude marketplace contract and new static tests remain the available evidence.

- [ ] **Step 4: Check diff hygiene and repository state**

```powershell
git diff --check
git status --short
git log -5 --oneline
```

Expected: no whitespace errors; only intended files are changed or all planned commits are clean; the design, packaging, Markdown, and published-page commits are visible.

- [ ] **Step 5: Perform the verification-before-completion gate**

Invoke `verification-before-completion`, rerun its required fresh checks, and report exact test counts plus any validator limitation. Do not describe Codex installation as live-tested unless an actual installation was performed through an installed marketplace.
