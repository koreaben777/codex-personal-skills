---
name: team-based-review-loop
description: Run a one-cycle team-based implementation review, feedback delivery, fixback wait, and re-review workflow for Codex threads. Use when the user asks to review an implementation from another Codex thread with a reviewer team, send findings back to an implementation thread, require @codex-fable5-style fixes, preserve the same @ponytail and agency-router review roles, document both initial and follow-up reviews, or save the review loop as a reusable repo workflow.
---

# Team Based Review Loop

## Overview

Use this skill to coordinate a strict one-cycle review loop across Codex threads:
initial review, documented findings, implementation-thread fixback, same-team re-review, and final documentation.

## Workflow

1. Identify the target implementation thread and worktree.
   - Use Codex thread tools to locate the thread by title or id.
   - Record thread id, worktree path, branch, and HEAD.
   - Do not push unless the user explicitly asks.

2. Run the initial review with the same four lanes.
   - `@ponytail`: over-implementation and deletion candidates.
   - `agency-router` / `codebase-onboarding`: logical flow review from input -> use case -> storage -> artifact.
   - `agency-router` / `technical-writer`: plan, README, skill, and artifact contract mismatch.
   - `agency-router` / `reality-checker`: validation status, evidence gaps, edge bugs, CLI exits, privacy boundaries, persistence, parsing, and idempotency.
   - Use subagents only when the user explicitly asks for them or has already authorized this loop.

3. Verify locally before reporting.
   - Run the project's relevant test command.
   - Reproduce high-risk findings directly when cheap.
   - Keep secret values masked in output.
   - Separate "tests pass" from "ready"; passing tests do not close untested product or privacy gaps.

4. Document the initial review.
   - Save a Markdown report under `docs/reviews/`.
   - Include target thread, worktree, branch/HEAD, role lanes, evidence checked, findings by severity, closed/non-issues, and next re-review checks.
   - Use absolute file paths in findings.

5. Send findings to the implementation thread.
   - Tell the thread to read the review document.
   - Require `@codex-fable5` style execution: inspect first, add focused failing checks, make minimal fixes, verify with evidence, and self-review before claiming completion.
   - Require the final implementation response to start with a stable marker such as `[TEAM_REVIEW_FIX_DONE]`.
   - Ask for changed files, commit/HEAD, verification commands, and residual risk.

6. Wait for completion, then re-review.
   - Poll the implementation thread until the marker appears or the thread blocks.
   - Re-run the same four review lanes with the same scope.
   - Re-run local verification and the previous reproductions.
   - Do not silently expand into a second fixback cycle unless the user requested another loop.

7. Document the re-review.
   - Save a second Markdown report under `docs/reviews/`.
   - Split findings into: closed, still open, newly found, and low-risk cleanup.
   - State whether the loop outcome is PASS, NEEDS WORK, or BLOCKED.

## Severity Rules

- P1: privacy/security leak, data loss, core MVP flow impossible, or direct contradiction of the MVP promise.
- P2: expected user path fails, plan contract drift, non-idempotent persistence, unsafe CLI behavior, or external failure breaking unrelated local work.
- P3: stale docs, over-specified tests, dead future scaffolding, small cleanup, or explicit MVP limitation that is documented but still worth tracking.

## Report Template

Use this compact structure:

```markdown
# Team Based Review Loop N - Initial/Re-Review Findings

Date:
Target thread:
Target worktree:
Branch / HEAD:
Status: PASS | NEEDS WORK | BLOCKED

## Evidence Checked
## Closed Findings
## Findings
## Ponytail Cleanup
## Next Minimal Checks
```

## Guardrails

- Keep reports in the user's language.
- Keep code identifiers and commands exactly as they appear.
- Never print secrets, tokens, private key material, or raw credential values.
- Never remote-push from the review loop unless explicitly requested.
- If the implementation thread changes files while review docs are being written, do not revert its changes; read the current state and continue.
