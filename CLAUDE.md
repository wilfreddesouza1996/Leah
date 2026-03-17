# CLAUDE.md — AI Assistant Guide for Leah

## Project Overview

**Leah** is a code assistant project. This file documents the repository structure, development conventions, and guidance for AI assistants working in this codebase.

---

## Repository State

This repository is in its initial phase. Currently it contains:

```
Leah/
├── CLAUDE.md       # This file
└── README.md       # Project description
```

As the project grows, this file should be updated to reflect the actual architecture, tech stack, and conventions established.

---

## Git Workflow

### Branches
- `main` — production-ready code; do not push directly
- `master` — mirrors main; do not push directly
- `claude/<feature-name>` — AI-generated feature branches

### Commit Conventions
- Use clear, imperative commit messages: `Add feature X`, `Fix bug in Y`, `Refactor Z`
- Keep commits focused on a single concern
- Do not bundle unrelated changes in one commit

### Pull Requests
- Always develop on a feature branch
- Describe what changed and why in the PR body
- Link related issues when applicable

---

## Development Guidelines for AI Assistants

### General Principles
1. **Read before editing** — Always read a file before modifying it
2. **Minimal changes** — Only change what is necessary; avoid refactoring unrelated code
3. **No over-engineering** — Implement the simplest solution that works
4. **No speculative features** — Do not add functionality that was not requested
5. **Security first** — Never introduce SQL injection, XSS, command injection, or other OWASP vulnerabilities

### Code Quality
- Prefer clarity over cleverness
- Do not add comments to self-evident code
- Do not add docstrings, type annotations, or error handling unless asked
- Avoid adding dead code or backwards-compatibility shims for removed features

### File Operations
- Prefer editing existing files over creating new ones
- Do not create `README.md` or documentation files unless explicitly requested
- Do not use emojis in code or documentation unless asked

---

## When the Tech Stack Is Established

Once the project has a defined tech stack, update this file with:

- **Language & runtime** (e.g., Node.js 20, Python 3.12)
- **Framework** (e.g., Next.js, FastAPI, Express)
- **Package manager** (e.g., npm, pnpm, uv, pip)
- **Test runner and how to run tests** (e.g., `npm test`, `pytest`)
- **Lint/format commands** (e.g., `npm run lint`, `ruff check .`)
- **Build command** (e.g., `npm run build`)
- **Environment variables** (describe required vars and how to set them up)
- **Key architectural patterns** (e.g., module structure, data flow, state management)

---

## Asking for Help / Giving Feedback

- `/help` — Get help with Claude Code
- Report issues at: https://github.com/anthropics/claude-code/issues
