# Routing Contracts

Read this file whenever the skill is invoked.

## Triage Record Contract

Create a new record with these sections:

```markdown
# Developer Handoff Triage

- Timestamp:
- Cycle: unique cycle or routing-event identifier
- Project root:
- Developer thread:
- Review Team thread:
- Scope/spec:

## Reported

Developer claims, including commands and results.

## Observed

Repository files, diff/status, tests, artifacts, and documentation verified now.

## Not Verified

Checks not run or facts that remain uncertain, with reasons.

## Findings

Severity, evidence path/line when available, and required resolution.

## Decision

`DEVELOPER_FIXBACK`, `REVIEW_TEAM`, `RUNNING_NO_DUPLICATE`, or `BLOCKED_NEEDS_USER`.

## Dispatch

Target thread ID and the exact prompt sent, or why no prompt was sent.
```

## Loop Contract

The Planner owns the loop and may complete non-overlapping read-only, documentation, and coordination work directly. Code, tests, or generated implementation artifacts belong to Developer; independent quality judgment belongs to Review Team. A routing event has one active owner and one immutable triage record.

After `CHANGES_REQUESTED`, route one focused fixback to Developer and wait for a new completion record before requesting re-review. After `PASS`, stop the review cycle. Promotion, commit, push, deployment, rebuild, reindex, and service restart require a separate authorized scope and a new evidence check; they are not implied by review readiness.

Use the repository's naming convention when it already provides immutable numbered or dated review records. Otherwise use `docs/reviews/YYYY-MM-DD-HHMM-developer-handoff-triage.md`. Test for an existing path before writing; choose a later timestamp or sequence rather than overwriting.

## Review-Readiness Checks

Review Team routing requires all applicable items:

- The requested implementation scope is complete.
- Developer reports concrete focused/full verification results or repository records contain them.
- Acceptance criteria are mapped to present deliverables and no observed evidence contradicts the report.
- Generated artifacts exist, parse/open, and match referenced paths/hashes.
- Current-state docs agree with implementation; historical records remain labeled historical.
- No debug files, credentials, unintended binaries, or unrelated changes were introduced.
- No known open finding remains in the reviewed slice.

Record unavailable or intentionally skipped independent checks under `Not Verified` and assign them to Review Team. They do not force Developer fixback by themselves. A missing required artifact, an observed failure, or contradictory evidence does.

## Developer Fixback Prompt Shape

```text
Project and reviewed scope
Observed findings with file/artifact evidence
Required minimal fixes in priority order
Acceptance and verification commands
Explicit exclusions and safety boundaries
Completion marker and required report fields
No stage/commit/push unless separately authorized
```

Fixback must distinguish defects from optional improvements. Do not widen the roadmap slice.

## Review Team Prompt Shape

```text
Project, implementation scope, and triage-record path
Authoritative spec/plan and Developer evidence paths
Independent checks: diff, code, tests, artifacts, docs, safety
Read-only review boundary; no implementation edits
Findings ordered by severity with precise evidence
Separate immutable review-report path
Final verdict: PASS or CHANGES_REQUESTED
If changes are requested, include a ready-to-send Developer fixback prompt
No stage/commit/push
```

Review Team must inspect the live repository rather than merely summarize the triage record.

## Thread Selection

Use current Codex thread tools when available:

1. List/search candidate threads by title.
2. Match `cwd` or saved project to the target root.
3. Read recent turns and status from the matched thread.
4. If two candidates still match, do not guess from recency alone.
5. Send to the resolved thread and record its ID.

If thread tools are unavailable, save the triage record and return a ready-to-send prompt without claiming delivery.

## Common Mistakes

| Mistake | Correction |
|---|---|
| Trusting “all tests pass” from a message | Re-run or inspect exact repository evidence. |
| Choosing a same-named thread from another project | Require cwd/project match. |
| Updating one shared review file every cycle | Create a unique triage record and separate review output. |
| Sending both fixback and review prompts | Choose one route from observable state. |
| Treating delivery as completion | Report only that the instruction was sent. |
