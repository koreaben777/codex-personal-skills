---
name: route-developer-review
description: Use when a Codex project uses separate Planner, Developer, and Review Team threads and the user asks to inspect implementation status, reconcile repository evidence, or decide the next thread handoff.
---

# Route Developer Review

## Overview

Treat the three-thread setup as an evidence-backed state machine. Inspect the Developer claim, persist a non-overwriting triage record, then send at most one instruction: Developer fixback or Review Team review.

## Workflow

1. Identify the project root and its existing `Developer` and `Review Team` threads. Match by project/cwd before title. If multiple matches remain, stop and ask; never route by title alone. Do not create a replacement thread unless the user explicitly requests one.
2. Read the Developer's latest completed turn and status. If it is still running, do not duplicate work; report that state or wait as requested.
3. Inspect live evidence: `git status`, intended diff, applicable spec/plan, tests, artifacts, and current-state docs. A Developer final answer is a claim, not proof. Preserve unrelated dirty changes.
4. Read [references/contracts.md](references/contracts.md). Create a unique, exclusive triage record under the repository's established review/status directory. If none exists, use `docs/reviews/YYYY-MM-DD-HHMM-developer-handoff-triage.md`. Never overwrite an earlier record or ask Review Team to edit it.
5. Classify the result using the decision contract below.
6. Send one scoped prompt to the selected existing thread using the reference contract. Omit model overrides unless requested.
7. Report the record, route, thread, and reason. Delivery is not completion.

## Decision Contract

| Observable state | Route |
|---|---|
| Required deliverable missing, observed check failing, stale current docs, known defect, artifact mismatch, or unresolved review feedback | Developer only |
| Developer reports completion with concrete verification, required deliverables are observed, artifacts/docs do not contradict the report, and no known finding remains | Review Team only |
| Target thread is running | Do not send duplicate work |
| Project/thread identity is ambiguous or required authority is missing | Stop and ask the user |

Exactly one route may be active. Do not send a known-broken slice to Review Team or speculative cleanup to Developer after review readiness.

Planner need not duplicate every expensive test before routing. Independent reruns and code-quality judgment belong to Review Team. An item listed as `Not Verified` is not itself a defect; route it to Developer only when it exposes a missing required deliverable or contradicts observed evidence.

## Evidence Rules

- Separate `reported`, `observed`, and `not verified` facts.
- Run proportionate read-only checks; do not implement the fix in the Planner thread.
- Preserve historical reports. Route stale current-state corrections unless a factual Planner update is explicitly authorized.
- Use unique timestamps or the repository's sequence convention. A fixed filename such as `developer-implementation-review.md` is unsafe unless the repository explicitly treats it as a replaceable current-state file.
- Review Team writes a separate review artifact and returns `PASS` or `CHANGES_REQUESTED`; it does not mutate the Planner triage record or implementation.
