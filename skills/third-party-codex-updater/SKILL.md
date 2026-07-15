---
name: third-party-codex-updater
description: Safely check and update GitHub-installed third-party Codex plugins and local skills. Use when the user asks to inspect, update, preserve, or automate updates for FableCodex, Ponytail, SkillOpt-Sleep, agency-router, codebase-memory-mcp, Superpowers upstream, or other third-party Codex skills/plugins without overwriting local custom work.
---

# Third-party Codex Updater

Use the bundled script first. It separates safe updates from manual-review items.

```bash
python "${CODEX_SKILLS_DIR:-${CODEX_HOME:-$HOME/.codex}/skills}/third-party-codex-updater/scripts/check_updates.py" --apply-safe
```

## Policy

- Apply automatically only when the update path is official and low-risk:
  - `codex-fable5@fablecodex`: clean local repo, fast-forward only, tests pass, then `codex plugin add`.
  - `ponytail@ponytail`: `codex plugin marketplace upgrade ponytail`, then `codex plugin add`.
- Do not auto-merge or replace:
  - `SkillOpt-Sleep`: preserve custom branch/commit, report upstream tag and conflicts.
  - `codebase-memory-mcp`: keep a clean latest-tag clone, do not replace MCP binaries or DGX config.
  - `superpowers`: keep OpenAI-curated pinned install, clone upstream only for comparison.
  - `agency-router`: compare the six selected source roles; report manual review if they changed.
- Never delete dirty worktrees. Create new clean clone paths instead.
- Never push.
- Mask secrets; do not print raw Codex session text.

## Output

Report:

- safe updates applied
- items already current
- items blocked by dirty worktree or conflicts
- clean clone paths created
- manual review items
