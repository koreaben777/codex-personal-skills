---
name: refresh-repo-status
description: Audit a repository's current implementation, update its public README, and reconcile GitHub Issues with verified scope. Use when a user asks to check current implementation status, refresh README or project documentation, close completed issues, create or refine backlog issues, or keep public repository communication aligned with code and tests.
---

# Repository Status, README, and Issue Reconciliation

Keep the public repository description and GitHub backlog faithful to the current implementation. Treat this as a fact-finding workflow first and a writing workflow second.

## 1. Establish the authoritative state

1. Identify the repository from the current checkout and its `origin` remote.
2. Inspect `git status --short --branch`, the remote default branch, recent commits, and every relevant worktree or branch. Preserve unrelated dirty and untracked files.
3. Fetch the remote before relying on local refs when network access is available.
4. Read the current README, project specs, release/review reports, package or build metadata, and the source/tests that support user-visible claims.
5. Run the narrowest meaningful verification for the current implementation. For a Python project with a local virtualenv, prefer its test suite; otherwise use the repository's documented test command. Run `git diff --check` after edits.

Separate these states in notes and final reporting:

- **Published**: present on the remote default branch.
- **Validated locally**: verified at a named local commit or worktree but not yet published.
- **Planned**: documented or proposed work without current runtime support.

Never use an old review pass, a spec, or a prior test count as evidence for the current HEAD.

## 2. Reconcile the README

Rewrite only the sections needed to make the README accurate and visitor-friendly.

- Lead with the product value and the user workflow in the repository's primary language.
- Describe only capabilities verified in current code and tests.
- State meaningful safety, privacy, approval, compatibility, and operational limits without turning the README into an internal review log.
- Keep setup commands, artifact paths, CLI names, and prerequisites executable and exact.
- Put deferred features in a roadmap section that links to GitHub Issues; do not present them as current behavior.
- Keep the README concise. Link detailed specs and reports instead of duplicating them.
- Update the README in the same change as any user-visible change to requirements, commands, data handling, outputs, or product scope.

## 3. Reconcile GitHub Issues

Use the GitHub connector for issue reads and writes when it is available. Before any write, state the exact issue numbers and intended change.

1. List open and recently closed issues, then compare each issue's acceptance criteria with the verified implementation.
2. Close an issue only when its acceptance criteria are met on the relevant published or explicitly identified local commit. Use the appropriate completion reason.
3. Keep partially complete work open. Add a concise current-status section that distinguishes implemented prerequisites from the remaining acceptance criteria.
4. Correct stale links, terminology, and scope in existing issues.
5. Split unrelated large scopes into independent issues when they have different users, risks, or delivery paths.
6. Create a new issue only for a verified gap, regression, deferred requirement, or actionable proposal not already covered. Include background, current behavior, goal, out-of-scope constraints, and completion criteria.
7. Never put secrets, private paths, credentials, personal source content, or detailed exploit instructions in public issues.

If no issue is complete, report that explicitly; do not close an issue merely to show activity.

## 4. Apply and verify changes

- Use the repository's normal documentation and Git workflow. Do not overwrite user-owned changes.
- Do not push, merge, or update the remote default branch unless the user's request authorizes that external write. A request to update the public README or GitHub Issues authorizes those specific remote changes.
- Re-fetch or re-read the changed README and Issues after remote writes to confirm the visible state.
- For local documentation changes, check headings, links, code blocks, and trailing whitespace in addition to `git diff --check`.

## 5. Report concisely

Report:

- the published implementation status and verification evidence;
- README sections changed;
- issue numbers closed, updated, split, or created, with the reason;
- any open work that remains and why;
- commands run and whether changes were published.

Do not claim a remote update, closed issue, or passing test without direct evidence from this run.
