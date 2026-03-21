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

- **[2026-03-21] Morning briefing — deferred**
  - Context: Planned daily 8AM briefing via claude --print + Slack webhook. Removed for now, will revisit later.

- **[2026-03-21] Real-time todo dashboard — Next.js + Supabase**
  - Context: Needed a live dashboard where agents can update task status and it reflects instantly
  - Supabase project: `leah-todos` (id: swnhmrljpafvaojaytkv, region: us-east-1, org: Weave)
  - Table: `public.todos` with realtime enabled via `supabase_realtime` publication
  - Fields: id, title, status (pending/in_progress/done), priority (low/medium/high), assigned_agent, updated_at, created_at
  - RLS enabled with open policy for dashboard access
  - Auto-updating `updated_at` via trigger
  - Frontend: Next.js app in `/dashboard`, system fonts (no Google Fonts dependency)

- **[2026-03-21] Ra Learning System — Computational Psychiatry backend**
  - Context: Implementing TMoP electromagnetic circuit model as Ra's learning architecture
  - Architecture: Hybrid — markdown (solenoid/identity) + Supabase (toroidal field/dynamic beliefs)
  - Supabase tables: `beliefs`, `prediction_errors`, `runs`, `policies` (all in leah-todos project)
  - Core mechanics: precision-weighted beliefs, Bayesian updating with hysteresis, belief decay, UCB policy selection, phase error accumulation tracking
  - Phase 1 (prompt-level): prediction logging, user signal taxonomy, end-of-run self-report — wired into ra.md
  - Phase 2 (Supabase): schema live, consolidation ritual defined, decay/update functions specified
  - Phase 3 (after 20+ runs): meta-metrics, pathology detection (inference closure, over-adaptation), monthly deep review
  - Full spec saved: `memory/ra-learning-spec.md`

- **[2026-03-22] Dynamic personality module — personality-dy.md**
  - Context: Static personality.md handles core identity; needed a living layer that evolves with Ra's learning system
  - personality-dy.md updates synchronously with end-of-run consolidation (same cycle as belief/policy updates)
  - All changes require Wilfred's explicit approval before committing
  - Contains: identity (Sun/Surya archetype), 5 core directives (non-negotiable), voice spec, three aspects (Aruna/Madhyahna/Sandhya), relational architecture, 5 behavioral modes (standard/low-I/high-stakes/brainstorm/pushback), TMoP self-model, growth protocol
  - Core directives and archetype never change; behavioral modes, voice, and self-model can evolve
