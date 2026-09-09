---
name: aside-workflow
description: Route Aside Browser work between its Codex MCP tool and direct CLI for interactive tabs, repeatable browser flows, or MCP transport failures.
---

# Aside Workflow

Use this skill only for work involving the user's Aside Browser. Do not change unrelated browser tooling.

## Route The Work

- For an interactive request involving a tab the user already has open in Aside, prefer the Aside MCP tool. Inspect the relevant tab before taking action.
- For deterministic or repeatable browser operations, prefer direct CLI invocation. Use `aside repl` for exact browser automation and `aside exec` only when an agent must interpret a changing page or task.
- `aside mcp` is a stdio server managed by Codex configuration. Do not start duplicate MCP servers manually as a fallback.

## Direct CLI Preconditions

1. Confirm `aside` is on `PATH` and record `aside --version` before diagnosing a CLI failure.
2. Treat the user's logged-in macOS session, Keychain access, and a usable Aside browser window as runtime prerequisites. CLI use does not make browser state independent of Aside.
3. Read page state before mutation. For repeatable flows, use stable locators and fixed inputs rather than passing untrusted page content into an agent prompt.

## Failure Handling

- If the MCP tool reports `Transport closed`, do not kill all `aside mcp` processes or repeatedly retry a mutating operation.
- Use a direct `aside repl` or `aside exec` fallback only when it is appropriate for the task, then report the actual outcome and any session or Keychain limitation.
- Do not create a schedule, background agent, or external action from a one-off request unless the user explicitly asks for it.
