# Codex Plugin Compatibility Design

## Goal

Make `xs_helper` a native, installable Codex plugin while preserving its existing Claude Code plugin installation and behavior. Both hosts must consume the same `skills/xs/` implementation so the XS knowledge base has one source of truth.

## Scope

This change adds packaging, discovery metadata, platform-neutral skill instructions, documentation, and structural tests. It does not change the XS language references, add runtime execution or backtesting, reconnect the removed `.xs` edit hook, or integrate with an XQ account.

The plugin version advances from `0.2.0` to `0.3.0` because native Codex support is a new user-facing capability.

## Architecture

The repository remains a single plugin package with two host-specific entry points:

```text
xs_helper/
├── .claude-plugin/
│   ├── plugin.json
│   └── marketplace.json
├── .codex-plugin/
│   └── plugin.json
├── .agents/plugins/
│   └── marketplace.json
└── skills/xs/
    ├── SKILL.md
    ├── agents/openai.yaml
    └── references/
```

- Claude Code continues to discover the package through `.claude-plugin/`.
- Codex discovers the installable package through `.codex-plugin/plugin.json` and the repository marketplace through `.agents/plugins/marketplace.json`.
- Both manifests point to the existing `skills/` directory rather than duplicating `SKILL.md` or references.
- `skills/xs/agents/openai.yaml` provides Codex-facing display metadata and a default `$xs` prompt. Implicit invocation remains enabled.

## Manifest and Marketplace Contracts

The Claude manifest keeps its current schema and gains only the `0.3.0` version update. Its existing marketplace remains available for current Claude Code installation commands.

The Codex manifest uses the native `.codex-plugin/plugin.json` schema with:

- stable name `xs-helper`;
- version `0.3.0`;
- existing author, repository, homepage, license, and keywords;
- `skills: "./skills/"`;
- concise Codex/ChatGPT install-surface metadata;
- no MCP, app, hook, or asset fields because those components are not part of this change.

The Codex marketplace at `.agents/plugins/marketplace.json` exposes the repository-root plugin through a Git-backed `url` source pointing at `https://github.com/Benjamin-Teng/xs_helper.git`. A URL source avoids copying the package beneath `plugins/xs-helper/` merely to satisfy the path convention used by local repo marketplaces. The entry includes the required installation policy, authentication policy, and category fields. The repository retains the legacy Claude marketplace instead of replacing or redirecting it.

## Skill Portability

`skills/xs/SKILL.md` remains the shared workflow. Host-specific assumptions are replaced with capability-based instructions:

- F3 fallback requests an available web lookup or browsing tool and restricts the lookup to the official XS Help site.
- The instructions do not name Claude-only `WebFetch` or Codex-internal tool identifiers.
- Manual invocation is documented outside the workflow as `/xs` for Claude Code and `$xs` for Codex; automatic activation continues to depend on the shared description.

The XS safety boundaries remain unchanged: do not invent tokens, do not execute or backtest XS, and do not connect to accounts, place orders, or fetch live quotes.

## Documentation

Every current product-facing or maintainer-facing documentation surface must describe both supported hosts and show how to install the plugin. The XS reference files under `skills/xs/references/` are runtime knowledge rather than product documentation and remain unchanged.

Use one shared installation matrix throughout the documentation:

- Claude Code marketplace: `/plugin marketplace add Benjamin-Teng/xs_helper`, `/plugin install xs-helper@xs-tools`, then `/reload-plugins`; explicitly invoke with `/xs`.
- VS Code／Codex IDE: the IDE extension does not support full plugins（`IDE extension 目前不支援完整 plugin`）. In the conversation, use `$skill-installer 請從 https://github.com/Benjamin-Teng/xs_helper/tree/main/skills/xs 安裝 xs skill`, then explicitly invoke with `$xs`. This is feature-equivalent while the plugin contains no MCP server, connector, or hook.
- Codex CLI conversation: run `codex plugin marketplace add Benjamin-Teng/xs_helper` once, start `codex`, enter `/plugins`, and install `xs-helper` from `xs-tools`.
- Codex terminal: `codex plugin marketplace add Benjamin-Teng/xs_helper`, then `codex plugin add xs-helper@xs-tools`; explicitly invoke with `$xs` and start a new conversation after installation when necessary.

Apply that matrix to all current documentation surfaces:

- `README.md`: describe the project as a Claude Code and Codex plugin and provide separate, complete installation and usage subsections.
- `docs/index.html`: update the published GitHub Pages title, social metadata, hero, footer, and installation modal for dual-host support. The installation modal presents separate Claude Code and Codex paths instead of mixing their commands.
- `docs/SPEC.md`: advance the maintained spec to v1.2, update current goals, structure, runtime wording, acceptance criteria, and add a dual-host installation section. Preserve explicitly historical implementation records as historical facts.
- `docs/architecture.md`: add the dual-manifest/package discovery path and a concise installation section for both hosts; replace current runtime labels that incorrectly imply Claude-only tooling.
- `CHANGELOG.md`: add the `0.3.0` release entry, including both installation command paths and the Codex packaging files introduced by the release.
- This design document: retain the canonical command matrix above so future documentation changes have one reviewable source.

Benchmark facts in `docs/index.html` remain labeled with the Claude model and harness actually used. Platform compatibility copy must not rewrite historical benchmark provenance as though Codex had been evaluated.

## Validation

Add a standard-library Python test module for packaging compatibility. It verifies:

1. Claude and Codex manifests both exist, identify `xs-helper`, and report version `0.3.0`.
2. The Codex manifest points to `./skills/` and does not declare absent components.
3. Both marketplace files expose the same plugin identity with their platform-appropriate schemas.
4. `skills/xs/agents/openai.yaml` exists and supplies required interface metadata.
5. `SKILL.md` retains valid frontmatter and no longer depends on the Claude-only `WebFetch` name.
6. The existing XS lint test suite still passes.
7. Each product-facing documentation file names Claude Code, VS Code／Codex IDE, and Codex CLI; it contains the conversational `$skill-installer` path, CLI `/plugins` path, and full plugin commands without claiming the IDE supports plugins.

Run the repository tests, Codex plugin validation, Codex skill validation, HTML structural checks for the published page, and any locally available Claude plugin validation. If the Claude CLI validator is unavailable, the structural tests protect the unchanged Claude schema and the handoff states that limitation explicitly.

## Error Handling and Compatibility

- Missing optional web access does not block core offline reference usage; it only prevents cold-query F3 lookup, which the skill must report rather than guess around.
- Codex metadata stays optional to execution: a host that ignores `agents/openai.yaml` can still load `SKILL.md`.
- One host's manifest must never reference the other host's private directories.
- The Codex marketplace source resolves to the repository root, where `.codex-plugin/plugin.json` lives; it does not introduce a second copy of the plugin.
- No generated cache, local installation, or user-level Codex configuration is committed to this repository.

## Acceptance Criteria

- Existing Claude Code installation and `/xs` usage remain documented and structurally valid.
- Codex recognizes the repository as a native plugin package and can expose the shared skill as `$xs`.
- Implicit XS-related prompts remain eligible to activate the shared skill.
- There is exactly one authoritative copy of the skill instructions and references.
- README, the published GitHub Pages page, SPEC, architecture documentation, and changelog all cover Claude Code installation plus the VS Code／Codex IDE skill path and Codex CLI plugin paths.
- All automated packaging and lint tests pass.
