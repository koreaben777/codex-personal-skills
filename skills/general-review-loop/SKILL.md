---
name: general-review-loop
description: Use when a multi-step task needs a Planner to set scope, assign ownership, inspect evidence, and close one bounded review or fixback cycle.
---

# General Review Loop

Planner leads the work to verified completion. Apply the loop to code, documents, research, operations, and other multi-step tasks.

## Core cycle

1. **Understand**: identify the goal, deliverables, constraints, risk, authority, and missing information. Separate assessment from execution.
2. **Assign**: Planner handles small read-only, documentation, or coordination tasks. Delegate specialized, long, parallel, or independently reviewed work. Never duplicate a running slice.
3. **Execute**: give one owner the objective, inputs, outputs, acceptance checks, exclusions, and stop boundaries. Preserve unrelated work and pause irreversible or external actions until authorized.
4. **Review**: inspect the actual output or changed state against the request and checks. Classify facts as `reported`, `observed`, or `not verified`; check artifacts, references, tests, and current docs when relevant.
5. **Decide**:
   - complete only when required outputs exist and evidence agrees;
   - send one focused correction for a missing output, failed check, or contradiction;
   - ask when identity, scope, authority, or a critical input is ambiguous;
   - start a new cycle for unrelated follow-up work.

## Bounded cross-thread review

When work spans Codex threads or worktrees, apply one bounded review cycle:

1. Resolve the project by `cwd` or worktree, then record exact thread IDs, branch, and `HEAD`. Do not match by title alone or duplicate a running owner.
2. Write an immutable evidence ledger before routing. Include requested scope, `git status`, intended diff, plan/spec, tests, artifacts, and current-state documents.
3. Route exactly one next action: owner fixback when required evidence is missing or contradictory, or independent review when completion evidence is concrete and consistent.
4. After a fixback, inspect the returned state and re-review the same scope. Do not silently start a second fixback cycle.
5. Record findings as closed, still open, newly found, or low-risk cleanup, with a final `PASS`, `NEEDS_WORK`, or `BLOCKED` outcome.

## Ownership

| Role | Responsibility |
|---|---|
| Planner | scope, sequencing, ownership, evidence, final decision, and approval gates |
| Worker | assigned implementation or investigation and a factual completion report |
| Reviewer | independent quality or acceptance review when risk requires it |

Planner may review direct work. Use an independent Reviewer when a second judgment materially reduces risk; skip ceremonial review for trivial read-only work.

## Handoff contract

Every delegation states context, scope, inputs, outputs, acceptance checks, exclusions, safety boundaries, and report fields. A completion message is evidence to inspect, not proof.

For a review handoff, also provide the immutable report path, exact independent checks, read-only boundary, severity-ordered findings, and the required verdict marker.

## Outcomes

- `PASS`: report the verified result and close that cycle. Do not infer permission to publish, deploy, delete, or alter external state.
- `NEEDS_WORK`: send one focused correction with the observed finding and acceptance check, then review the returned result again.
- `BLOCKED`: state the missing authority, input, or identity and do not guess.

## Common mistakes

- Delegating everything instead of assessing Planner-owned work.
- Treating “done” or “tests passed” as verification.
- Mixing unrelated tasks into a reviewed slice.
- Sending multiple overlapping instructions before the owner returns.
- Routing by thread title without confirming project identity.
- Expanding a completed review into an unrequested second cycle.
