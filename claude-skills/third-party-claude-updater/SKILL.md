---
name: third-party-claude-updater
description: Safely check and update third-party Claude Code plugins, skills, and MCP tooling. Use when the user asks to inspect, update, preserve, or automate updates for ponytail, open-code-review, i-have-adhd, archify, graphify, aside, codebase-memory-mcp, superpowers, or other third-party Claude Code plugins/skills without overwriting local custom work.
---

# Third-party Claude Code Updater

Use the bundled script first. It separates safe updates from manual-review items.

```bash
python "${CLAUDE_SKILL_DIR:-$HOME/.claude/skills/third-party-claude-updater}/scripts/check_updates.py" --apply-safe
```

Add `--json` for machine-readable output. Without `--apply-safe` the script only reports.

## Inventory

| Item | Kind | Update path |
|---|---|---|
| `ponytail@ponytail` | marketplace plugin | `claude plugin marketplace update ponytail` → `claude plugin update ponytail` |
| `open-code-review@open-code-review` | marketplace plugin | `claude plugin marketplace update open-code-review` → `claude plugin update open-code-review` |
| `i-have-adhd@i-have-adhd` | marketplace plugin | `claude plugin marketplace update i-have-adhd` → `claude plugin update i-have-adhd` |
| `ocr` | CLI backing open-code-review | `npm install -g @alibaba-group/open-code-review` |
| `archify` | skill, `~/.claude/skills/archify` | `npx -y skills add tt-a1i/archify --skill archify --agent claude-code --global --copy --yes` |
| `graphify` | skill + CLI + MCP | `uv tool upgrade graphifyy` → `graphify install --platform claude` |
| `aside` | CLI + stdio MCP server | `aside --update` (same binary serves `aside mcp`) |
| `codebase-memory-mcp` | MCP server (upstream tracked only) | clean tag clone; never replace binaries or remote config |
| `superpowers` | upstream plugin clone | compare only; do not overwrite a customized local copy |
| ported skills | local, no upstream | manual review; compare against the `~/.codex/skills` original |

## Policy

- Apply automatically only when the update path is official and low-risk:
  - `ponytail@ponytail`, `open-code-review@open-code-review`, and `i-have-adhd@i-have-adhd`: refresh the marketplace, then `claude plugin update`. Plugin changes need a restart to take effect — say so, do not restart anything yourself.
  - `graphify`: `uv tool upgrade graphifyy`, then re-run the vendor installer. The installer rewrites `~/.claude/skills/graphify` and its `~/.claude/CLAUDE.md` registration line; that is expected.
- Do not auto-merge or replace:
  - `archify`: report the manifest version delta. Re-running the vendor installer overwrites the skill directory, so confirm no local edits first.
  - `aside`: report the version. `aside --update` touches a user-installed binary and an MCP server Claude Code is actively running — leave it to the user.
  - `codebase-memory-mcp`: keep a clean latest-tag clone; do not replace MCP binaries or remote host config.
  - `superpowers`: clone upstream only for comparison; keep any local pinned or customized install.
  - `aside-workflow`, `general-review-loop`, `route-developer-review`, and this skill: locally authored ports. Report drift against the `~/.codex/skills` counterpart; never overwrite either side automatically.
- Never delete dirty worktrees. Create new clean clone paths instead.
- Never push.
- Mask secrets; do not print raw session text.

## Output

Report:

- safe updates applied
- items already current
- items blocked by dirty worktree or conflicts
- clean clone paths created
- manual review items
- whether a Claude Code restart is required to load updated plugins
