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
    └── reference/
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

Update `README.md` so the project is described as a Claude Code and Codex plugin. Keep separate installation subsections:

- Claude Code: preserve the current marketplace commands and `/xs` behavior.
- Codex: document adding the repository marketplace, installing the plugin through supported Codex surfaces, explicit `$xs` invocation, and implicit activation.

Update project status and compatibility wording where it would otherwise claim Claude-only support. Record the `0.3.0` change in `CHANGELOG.md`. Historical sections in `docs/SPEC.md` remain historical; only current overview, target-user, structure, acceptance, and platform descriptions are updated where necessary.

## Validation

Add a standard-library Python test module for packaging compatibility. It verifies:

1. Claude and Codex manifests both exist, identify `xs-helper`, and report version `0.3.0`.
2. The Codex manifest points to `./skills/` and does not declare absent components.
3. Both marketplace files expose the same plugin identity with their platform-appropriate schemas.
4. `skills/xs/agents/openai.yaml` exists and supplies required interface metadata.
5. `SKILL.md` retains valid frontmatter and no longer depends on the Claude-only `WebFetch` name.
6. The existing XS lint test suite still passes.

Run the repository tests, Codex plugin validation, Codex skill validation, and any locally available Claude plugin validation. If the Claude CLI validator is unavailable, the structural tests protect the unchanged Claude schema and the handoff states that limitation explicitly.

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
- All automated packaging and lint tests pass.
