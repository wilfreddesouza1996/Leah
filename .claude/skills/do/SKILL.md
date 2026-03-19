---
name: do
description: Execute a phased implementation plan using subagents. Use when asked to execute, run, or carry out a plan — especially one created by make-plan.
---

# Do Plan

You are an ORCHESTRATOR. Deploy subagents to execute *all* work. Do not do the work yourself except to coordinate, route context, and verify that each subagent completed its assigned checklist.

## Orchestration Model

- Route concrete implementation and reads to subagents
- Reserve yourself for: coordination, routing context, and final verification
- Enforce the subagent reporting contract

### Subagent Reporting Contract (MANDATORY)

Each subagent response must include:
1. Files read/modified
2. Checklist items completed
3. Actual output (code written, commands run, results)
4. Any blockers or deviations from the plan

Reject and redeploy the subagent if it doesn't provide concrete evidence of work done.

## Phase Execution

Execute phases sequentially. Do not skip phases.

### For Each Phase

1. Deploy subagent(s) with the phase tasks and documentation references
2. Verify the subagent completed all checklist items
3. If subagent report is incomplete: redeploy with the missing items
4. Confirm phase complete before moving to next

## Key Principles

- **No Self-Implementation:** You orchestrate; subagents implement
- **Sequential Phases:** Do not parallelize phases that depend on each other
- **Verify Each Phase:** Confirm work before moving forward
- **Documentation First:** Always pass documentation references to subagents
