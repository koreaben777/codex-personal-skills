---
name: general-review-loop
description: Use when a multi-step task needs a Planner to set scope, route work to already-existing Developer and Review Team Codex App chat tasks or threads in the same project, inspect evidence, and close one bounded review or fixback cycle.
---

# General Review Loop

Planner leads the work to verified completion. Apply the loop to code, documents, research, operations, and other multi-step tasks.

## Existing-thread routing (mandatory)

This loop is reuse-only. Before routing any work:

1. Resolve the canonical project identity: normalized project root or `cwd`, repository/worktree, and branch/`HEAD` when relevant. A different worktree or branch is not automatically the same project context.
2. Enumerate the already-existing Codex App tasks/chat threads and inspect their metadata or context. Select the existing Developer thread and the existing Review Team thread or threads whose project identity matches. Record their exact task/thread IDs and current ownership/status.
3. Reuse those exact task/thread IDs for every handoff. Never create, fork, clone, or open a new thread as part of this loop. Never replace a missing role with a subagent or with the current Planner chat.
4. Match by project identity and role, not by title alone. If more than one existing thread matches and ownership or scope is ambiguous, stop and report `BLOCKED` rather than guessing.
5. If a required existing Developer or Review Team thread is absent, inaccessible, or mismatched, report `BLOCKED` and request the existing thread ID or user resolution. Do not create a replacement thread.

## Execution model (important)

This is a cross-chat-thread collaboration protocol using already-existing Codex App tasks or chat threads in the same project. A "thread" here means an independently addressable Codex App task, not a subagent session inside the current task.

- Do not create, fork, or open a new task/thread as an implicit or explicit step of this skill.
- Do not start, spawn, or turn on subagents as a substitute for an existing Developer or Review Team thread.
- Do not treat one current chat as if it already contains the Developer or Review Team threads.
- In the Planner thread, send a bounded handoff to the selected existing Developer or Review Team task/thread and wait for its factual report; never invent a returned result.
- If an existing task/thread or communication route is unavailable, report the work as pending or `BLOCKED`; do not create a new thread or silently substitute a subagent or the current Planner chat.
- Planner may still perform small read-only, documentation, or coordination work directly, as stated below.
- Thread creation/forking and subagent orchestration are outside this skill. Handle them only in a separate, explicitly requested workflow.

## Core cycle

1. **Understand**: identify the goal, deliverables, constraints, risk, authority, and missing information. Separate assessment from execution.
2. **Assign**: Planner handles small read-only, documentation, or coordination tasks. Route specialized, long, parallel, or independently reviewed work to an already-existing Developer or Review Team Codex App task/thread for the same project. Never duplicate a running slice or route to a newly created thread.
3. **Execute**: give one owner in the selected existing task/thread the objective, inputs, outputs, acceptance checks, exclusions, and stop boundaries. Preserve unrelated work and pause irreversible or external actions until authorized.
4. **Review**: inspect the actual output or changed state against the request and checks. Classify facts as `reported`, `observed`, or `not verified`; check artifacts, references, tests, and current docs when relevant.
5. **Decide**:
   - complete only when required outputs exist and evidence agrees;
   - send one focused correction for a missing output, failed check, or contradiction;
   - ask when identity, scope, authority, or a critical input is ambiguous;
   - start a new cycle for unrelated follow-up work.

## Bounded cross-thread review

When work spans already-existing Codex App tasks/chat threads or worktrees in the same project, apply one bounded review cycle:

1. Resolve the project by `cwd` or worktree, then record the exact existing Codex task/thread IDs, branch, and `HEAD`. Do not match by title alone, confuse a subagent session with a task/thread, create a replacement thread, or duplicate a running owner.
2. Write an immutable evidence ledger before routing. Include the requested scope, `git status`, intended diff, plan/spec, tests, artifacts, and current-state documents.
3. Route exactly one next action: owner fixback when required evidence is missing or contradictory, or independent review when completion evidence is concrete and consistent.
4. After a fixback, inspect the returned state and re-review the same scope. Do not silently start a second fixback cycle.
5. Record findings as closed, still open, newly found, or low-risk cleanup, with a final `PASS`, `NEEDS_WORK`, or `BLOCKED` outcome.

## Ownership

| Role | Responsibility |
|---|---|
| Planner | scope, sequencing, routing, ownership, evidence, final decision, and approval gates in the coordinating task/thread |
| Developer | the assigned implementation or investigation in a separate task/thread and a factual completion report |
| Review Team | independent quality or acceptance review in one or more separate task/threads when the risk or task requires it |

Planner may review direct work. Use an independent Review Team task/thread when a second judgment materially reduces risk; skip ceremonial review for trivial read-only work.

## Handoff contract

Every cross-thread handoff to an existing task/thread states context, scope, inputs, outputs, acceptance checks, exclusions, safety boundaries, and report fields. A completion message from another task/thread is evidence to inspect, not proof.

For a Review Team handoff, also provide the immutable report path, exact independent checks, read-only boundary, severity-ordered findings, and the required verdict marker.

## Outcomes

- `PASS`: report the verified result and close that cycle. Do not infer permission to publish, deploy, delete, or alter external state.
- `NEEDS_WORK`: send one focused correction with the observed finding and acceptance check, then review the returned result again.
- `BLOCKED`: state the missing authority, input, or identity and do not guess.

## Quick Reference

| Situation | Next action |
|---|---|
| Small read-only task | Planner handles it directly |
| Specialized or long implementation/investigation | Route one bounded slice to an already-existing Developer task/thread in the same project |
| Independent quality review required | Route one bounded slice to an already-existing Review Team task/thread in the same project |
| No matching existing role thread | Report `BLOCKED`; request the existing thread ID or user resolution; do not create/fork a thread |
| Developer or Review Team reports completion | Inspect output and evidence |
| Required output missing or contradicted | Focused correction |
| High-risk external action | Review first; require clear authorization |
| Unrelated next request | New cycle |

## Common Mistakes

- Routing everything instead of assessing Planner-owned work.
- Creating or forking a new Developer or Review Team thread instead of reusing the existing same-project thread.
- Interpreting a Codex task/chat thread as a subagent session, or spawning a subagent because an existing role thread is missing.
- Treating the current chat as the Developer or Review Team's completed thread without an actual handoff and report.
- Treating “done” or “tests passed” as verification.
- Mixing unrelated tasks into a reviewed slice.
- Sending multiple overlapping instructions before the owner returns.
- Treating delivery of a handoff as completion.
- Routing by thread title without confirming project identity.
- Expanding a completed review into an unrequested second cycle.
