# CLAUDE.md

## Persistent Memory

At the start of every session, read all files in the `memory/` directory:

- `memory/decisions.md` — Key decisions and their rationale
- `memory/people.md` — People and their context
- `memory/preferences.md` — User preferences
- `memory/personality.md` — How you think, communicate, and show up
- `memory/use.md` — How the memory system works

Use the information in these files to maintain continuity across sessions. Reference past decisions, remember people, and respect stated preferences.

## Updating Memory

Before ending a session, review what happened and update the memory files with any new:

- Decisions that were made (with date and reasoning)
- People who were mentioned
- Preferences that were expressed or clarified

## Task Tracking

Two systems exist — keep them in sync:

1. **`todos/active.md`** — Markdown file for the morning briefing and quick reference
2. **Supabase `todos` table** — Real-time dashboard at `/dashboard` (project: `leah-todos`, id: `swnhmrljpafvaojaytkv`)

When completing a task, update both: mark it done in Supabase (`status = 'done'`) and move it to "Recently Completed" in `active.md`.

## Supabase Access

Use the Supabase MCP tools (`execute_sql`, `apply_migration`, etc.) to interact with the `leah-todos` project directly. The project ID is `swnhmrljpafvaojaytkv`.
