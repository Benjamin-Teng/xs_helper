# Codex Conversational Installation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make VS Code／Codex IDE conversational skill installation the primary Codex onboarding path while preserving full plugin installation for supported Codex surfaces and the existing Claude Code flow.

**Architecture:** Treat the shared `skills/xs/` directory as both the IDE-installable standalone skill and the skill bundled by the existing Codex plugin. Product documentation branches by host surface: IDE chat uses `$skill-installer`, Codex CLI chat uses `/plugins` after marketplace registration, and advanced terminal users retain direct `codex plugin` commands.

**Tech Stack:** Markdown, static HTML/CSS/JavaScript, Python 3 `unittest`, Claude and Codex plugin validators, browser visual QA.

## Global Constraints

- Work directly on `main`; do not create another branch or worktree.
- Preserve Claude Code installation commands, `/xs` invocation, and orange installation-card styling.
- Preserve `.codex-plugin/plugin.json`, `.agents/plugins/marketplace.json`, and full Codex plugin installation.
- Present VS Code／Codex IDE first and label it recommended.
- Use exactly `$skill-installer 請從 https://github.com/Benjamin-Teng/xs_helper/tree/main/skills/xs 安裝 xs skill` for conversational installation.
- State that plugins are not currently available in the Codex IDE extension; the standalone skill provides all current `xs-helper` functionality because the plugin has no MCP server, connector, or hook.
- Keep `codex plugin marketplace add Benjamin-Teng/xs_helper` and `codex plugin add xs-helper@xs-tools` in every maintained product document.
- Keep `/plugins` only for the Codex CLI interactive plugin browser, after marketplace registration.
- Preserve the benchmark's historical Claude Opus 4.8 provenance.
- Use only Python standard-library modules in repository tests.

---

### Task 1: Protect the three Codex installation surfaces with tests

**Files:**
- Modify: `tests/test_plugin_compatibility.py`

**Interfaces:**
- Consumes: the maintained Markdown document list and published-page HTML loaded by the existing tests.
- Produces: regression assertions for the exact IDE prompt, GitHub skill path, CLI `/plugins` flow, plugin commands, and IDE limitation.

- [ ] **Step 1: Add failing Markdown documentation assertions**

Extend `TestMarkdownDocumentation` with constants and a test:

```python
IDE_INSTALL_PROMPT = (
    "$skill-installer 請從 "
    "https://github.com/Benjamin-Teng/xs_helper/tree/main/skills/xs "
    "安裝 xs skill"
)

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
```

Add the new design spec to `DOCUMENTS` so the documentation contract includes it.

- [ ] **Step 2: Add failing published-page assertions**

Add a new `TestPublishedPage` test:

```python
def test_codex_install_card_prioritizes_ide_chat(self) -> None:
    required = (
        "VS Code／Codex IDE（推薦）",
        "$skill-installer 請從 https://github.com/Benjamin-Teng/xs_helper/tree/main/skills/xs 安裝 xs skill",
        "Codex CLI 對話介面",
        "/plugins",
        "終端機進階安裝",
        "IDE extension 目前不支援完整 plugin",
    )
    for expected in required:
        self.assertIn(expected, self.html)
```

- [ ] **Step 3: Run the new tests to verify RED**

Run:

```powershell
python -m unittest tests.test_plugin_compatibility.TestMarkdownDocumentation.test_all_product_docs_cover_codex_ide_installation tests.test_plugin_compatibility.TestPublishedPage.test_codex_install_card_prioritizes_ide_chat -v
```

Expected: failures identify the missing IDE prompt and three-surface copy in current documentation and `docs/index.html`.

- [ ] **Step 4: Commit the regression-test contract with the implementation deliverable**

Do not commit while the tests are red. Include `tests/test_plugin_compatibility.py` in the documentation commit in Task 3.

---

### Task 2: Update maintained Markdown documentation

**Files:**
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `docs/SPEC.md`
- Modify: `docs/architecture.md`
- Modify: `docs/superpowers/specs/2026-08-04-codex-plugin-compatibility-design.md`

**Interfaces:**
- Consumes: the exact installation copy protected by Task 1.
- Produces: consistent three-surface Codex onboarding in every maintained product document.

- [ ] **Step 1: Rewrite README Codex installation**

Structure the Codex subsection in this order:

````markdown
#### VS Code／Codex IDE（推薦）

在 Codex 對話框貼上：

```text
$skill-installer 請從 https://github.com/Benjamin-Teng/xs_helper/tree/main/skills/xs 安裝 xs skill
```

#### Codex CLI 對話介面

先註冊 marketplace，啟動 `codex` 後輸入 `/plugins`，從 `xs-tools` 安裝 `xs-helper`。

#### 終端機進階安裝
````

State that the IDE extension does not support full plugins, that this standalone skill covers all current functionality, and that a new chat or IDE reload may be needed.

- [ ] **Step 2: Apply the same capability boundary to SPEC and architecture**

In `docs/SPEC.md`, add IDE standalone-skill installation to the current install and acceptance-criteria sections. In `docs/architecture.md`, show `skills/xs/` serving both plugin hosts and standalone Codex IDE installation, and add a surface support table with rows for VS Code／Codex IDE, Codex CLI, and supported desktop plugin UI.

- [ ] **Step 3: Update changelog and compatibility design history**

Add the conversational installer prompt, `/plugins`, and IDE plugin limitation to the `0.3.0` changelog entry. Amend the original compatibility design so future maintainers do not reintroduce the inaccurate claim that all Codex surfaces accept plugins.

- [ ] **Step 4: Run Markdown tests to verify GREEN**

Run:

```powershell
python -m unittest tests.test_plugin_compatibility.TestMarkdownDocumentation -v
```

Expected: all Markdown coverage tests pass.

---

### Task 3: Redesign the published install modal around the IDE chat flow

**Files:**
- Modify: `docs/index.html`
- Modify: `tests/test_plugin_compatibility.py`

**Interfaces:**
- Consumes: the exact surface copy from Task 1 and the existing orange Claude／cyan Codex visual system.
- Produces: a responsive install modal whose Codex card presents IDE chat first, CLI chat second, and direct terminal commands last.

- [ ] **Step 1: Add three Codex subflows to the cyan card**

Inside the existing Codex platform section, add headings in this order:

```html
<h4>VS Code／Codex IDE（推薦）</h4>
<h4>Codex CLI 對話介面</h4>
<h4>終端機進階安裝</h4>
```

Place the exact `$skill-installer` prompt and copy button under the first heading. Under the second, explain one-time marketplace registration and `/plugins`. Keep both direct `codex plugin` commands under the third.

- [ ] **Step 2: Add accurate limitation and recovery copy**

Include the exact sentence `IDE extension 目前不支援完整 plugin` and explain that the current standalone skill has feature parity. Tell users to start a new chat and reload VS Code if `$xs` does not appear.

- [ ] **Step 3: Preserve responsive command layout**

Reuse `.cmd`, `.copy`, and mobile `white-space:pre-wrap; overflow-wrap:anywhere` styles. Keep `.platform-claude` orange overrides unchanged and the Codex card cyan.

- [ ] **Step 4: Run page and full tests to verify GREEN**

Run:

```powershell
python -m unittest tests.test_plugin_compatibility.TestPublishedPage -v
python -m unittest discover -s tests -v
```

Expected: all published-page tests and the full suite pass without failures.

- [ ] **Step 5: Perform browser visual QA**

Serve the repository locally, open `docs/index.html`, and inspect the modal at desktop width and 390px width. Verify that every command fits without page or `<pre>` overflow, copy buttons remain visible, the Claude card is orange, and the Codex card is cyan.

- [ ] **Step 6: Commit the documentation implementation**

```powershell
git add README.md CHANGELOG.md docs/SPEC.md docs/architecture.md docs/index.html docs/superpowers/specs/2026-08-04-codex-plugin-compatibility-design.md tests/test_plugin_compatibility.py
git commit -m "docs: add Codex conversational installation"
```

---

### Task 4: Validate and publish from main

**Files:**
- Verify: all files changed in Tasks 1–3

**Interfaces:**
- Consumes: the completed three-surface documentation update.
- Produces: fresh cross-host validation evidence and a synchronized `origin/main`.

- [ ] **Step 1: Run final test and validator gate**

Run:

```powershell
python -m unittest discover -s tests -v
claude plugin validate .
uv run --no-project --with PyYAML python C:\Users\ben0315\.codex\skills\.system\plugin-creator\scripts\validate_plugin.py .
uv run --no-project --with PyYAML python -X utf8 C:\Users\ben0315\.codex\skills\.system\skill-creator\scripts\quick_validate.py skills/xs
```

Expected: Python reports all tests passing; all three validators exit `0`.

- [ ] **Step 2: Check repository state**

Run:

```powershell
git diff --check
git status --short --branch
git log -5 --oneline
```

Expected: no uncommitted changes or whitespace errors; `main` is ahead of `origin/main` by the planned commits.

- [ ] **Step 3: Push the release documentation**

```powershell
git push origin main
```

Expected: the remote updates to the final local `main` commit.

- [ ] **Step 4: Confirm synchronization**

Run:

```powershell
git rev-parse HEAD
git rev-parse origin/main
git status --short --branch
```

Expected: local `HEAD` and `origin/main` match and the worktree is clean.
