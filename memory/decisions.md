# Decisions

Key decisions made during sessions. Update this file when significant choices are made.

## Format

- **[Date] Decision**: Brief description
  - Context: Why this decision was made
  - Alternatives considered: What else was evaluated

## Log

- **[2026-03-21] Built persistent memory system**
  - Context: Needed continuity across Claude Code sessions
  - Structure: memory/ directory with decisions.md, people.md, preferences.md, personality.md, use.md
  - Stop hook injects reminder to update memory before session ends

- **[2026-03-21] Morning briefing via claude --print + Slack webhook**
  - Context: Daily 8AM briefing that reads memory, todos, calendar, and email
  - Approach: Shell script runs `claude --print` with a prompt that uses Google Calendar and Gmail MCP tools, posts result to Slack via webhook
  - Scheduling: systemd user timer (with cron fallback)
  - Slack webhook stored in .env (gitignored)

- **[2026-03-21] Real-time todo dashboard — Next.js + Supabase**
  - Context: Needed a live dashboard where agents can update task status and it reflects instantly
  - Supabase project: `leah-todos` (id: swnhmrljpafvaojaytkv, region: us-east-1, org: Weave)
  - Table: `public.todos` with realtime enabled via `supabase_realtime` publication
  - Fields: id, title, status (pending/in_progress/done), priority (low/medium/high), assigned_agent, updated_at, created_at
  - RLS enabled with open policy for dashboard access
  - Auto-updating `updated_at` via trigger
  - Frontend: Next.js app in `/dashboard`, system fonts (no Google Fonts dependency)
