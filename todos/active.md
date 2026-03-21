# Active Tasks

Current work in progress. Update as tasks start, shift, or complete.

## In Progress

- Morning briefing — needs Slack webhook URL to go live
- Dashboard — built, needs `npm run dev` test on local machine

## Upcoming

- Connect Google Calendar + Gmail MCP auth for headless briefing runs
- Deploy dashboard (Vercel or similar)

## Blocked

- Slack webhook: waiting on user to create Slack app + paste URL into `.env`
- Scheduling: cron/systemd timer needs to be set up on user's actual machine via `./scripts/setup-briefing.sh`

## Recently Completed

- [2026-03-21] Built persistent memory system (memory/, CLAUDE.md, Stop hook)
- [2026-03-21] Wrote personality.md
- [2026-03-21] Built real-time todo dashboard (Next.js + Supabase)
- [2026-03-21] Created Supabase project (leah-todos) with todos table + realtime
- [2026-03-21] Wrote morning briefing script with graceful MCP fallback
