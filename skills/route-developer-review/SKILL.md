---
name: route-developer-review
description: Use when a project has separate Planner, Developer, and Review Team threads and work must be coordinated across implementation evidence, independent review, fixback cycles, or approval-gated promotion.
---

# Planner Developer Review Loop

## Overview

Planner is the coordination owner and evidence judge. The workflow is a bounded loop: Planner may handle inspection, documentation, and coordination directly; Developer owns implementation; Review Team independently judges review readiness and defects. The result returns to Planner before the next decision.

## Roles

| Role | Owns | Must not do |
|---|---|---|
| Planner | project/thread identity, scope, live evidence, triage record, route decision, approval gates | treat a Developer report as proof or duplicate a running implementation |
| Developer | scoped code, tests, artifacts, and isolated-workspace implementation | widen scope or commit/push without explicit authorization |
| Review Team | read-only independent review and a separate `PASS`/`CHANGES_REQUESTED` report | edit implementation or the Planner triage record |

## Loop

1. Resolve the project root and existing `Developer` and `Review Team` threads by `cwd` or saved project. Record exact IDs. A same-named thread in another project is not a match. If identity or authority remains ambiguous, stop with `BLOCKED_NEEDS_USER`.
2. Read the latest completed turn and current status. If the target thread is running, do not send duplicate work. Planner may continue only with non-overlapping inspection, documentation, or coordination work.
3. Build an evidence ledger before routing: separate `Reported`, `Observed`, and `Not Verified`. Inspect `git status`, intended diff, applicable plan/spec, tests, artifacts, current-state docs, and safety boundaries. Preserve unrelated dirty changes.
4. Choose the owner. Planner handles read-only investigation, factual status updates, documentation, and triage. Send implementation or artifact work to Developer. Send independent quality judgment to Review Team only after the requested slice is review-ready.
5. Create one new, immutable triage record for each routing event using [references/contracts.md](references/contracts.md). Never overwrite an earlier cycle and never ask Review Team to edit it.
6. Activate exactly one route:
   - missing required deliverable, observed failure, stale current docs, artifact mismatch, or unresolved known finding -> `DEVELOPER_FIXBACK`;
   - concrete Developer completion evidence, present deliverables, consistent docs/artifacts, and no known finding -> `REVIEW_TEAM`;
   - running target -> `RUNNING_NO_DUPLICATE`;
   - ambiguous identity or missing authority -> `BLOCKED_NEEDS_USER`.

## Review Outcomes

- `PASS`: report the review and stop the code-review cycle. Commit, promotion, push, deploy, reindex, rebuild, or service restart is a separate authorized scope. If authorized, create a new promotion triage record and re-check the exact candidate before routing it.
- `CHANGES_REQUESTED`: send one focused Developer fixback covering required findings and acceptance checks. Wait for completion, create a new triage record, then route the corrected slice to Review Team. Optional cleanup is allowed only when it is inside the same reviewed scope and does not obscure the required fix.
- New work after `PASS`: start a new bounded cycle; do not append unrelated work to a reviewed slice.

## Prompt Contracts

Developer prompts contain: project and isolated workspace, exact scope, evidence-backed findings, minimal fixes in priority order, acceptance tests/artifacts, exclusions and safety boundaries, completion marker, and the no-stage/no-commit/no-push rule unless separately authorized.

Review prompts contain: project and scope, triage/spec/report paths, exact independent checks, read-only boundary, separate immutable report path, severity-ordered findings, and a final `PASS` or `CHANGES_REQUESTED` verdict.

## Guardrails

- Delivery of a prompt is not completion; verify the resulting thread and repository state.
- Never route by title alone, send both routes for one state, or trust “all tests pass” without evidence.
- Do not merge or push merely because Review Team returned `PASS`; preserve the explicit promotion gate.
- Do not expose secrets, raw user data, or unnecessary session text in records or prompts.

## Quick Reference

| State | Planner action |
|---|---|
| Planner-only inspection/docs | perform directly if non-overlapping |
| Developer running | wait; no duplicate implementation |
| Developer incomplete or contradicted | one Developer fixback |
| Developer complete and evidence-consistent | one Review Team request |
| Review `CHANGES_REQUESTED` | Developer fixback, then re-review |
| Review `PASS` | report; separate promotion authorization |
