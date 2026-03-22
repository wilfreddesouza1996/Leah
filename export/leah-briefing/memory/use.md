# Use

How this memory system works and guidelines for maintaining it.

## Purpose

This directory stores persistent context across Claude Code sessions. Files here are read at the start of every session and updated at the end.

## Files

- **decisions.md** — Records of key decisions, their rationale, and alternatives considered
- **people.md** — People mentioned in conversations with relevant context
- **personality.md** — How Claude should think, communicate, and make decisions; the static operational soul
- **personality-dy.md** — Ra's dynamic personality module. Auto-updates synchronously with the end-of-run consolidation cycle. Changes require Wilfred's approval. Contains: identity, core directives, voice, behavioral modes, self-model (TMoP mapping), growth protocol.
- **preferences.md** — User preferences for code style, tools, workflows, and communication
- **ra-learning-spec.md** — Full specification for Ra's computational psychiatry learning system (beliefs, prediction errors, runs, policies, formulas, TMoP parameter mapping)
- **use.md** — This file; documents the memory system itself

## Guidelines

- Keep entries concise and scannable
- Use dates when recording decisions
- Remove outdated information rather than letting it accumulate
- Don't store sensitive information (passwords, tokens, secrets)
