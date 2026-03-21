#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_FILE="$PROJECT_DIR/scripts/briefing.log"

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"; }

log "Starting morning briefing"

# Load env
if [[ -f "$PROJECT_DIR/.env" ]]; then
  set -a
  source "$PROJECT_DIR/.env"
  set +a
fi

if [[ -z "${SLACK_WEBHOOK_URL:-}" || "$SLACK_WEBHOOK_URL" == *"YOUR/WEBHOOK/URL"* ]]; then
  log "ERROR: SLACK_WEBHOOK_URL not configured in .env"
  exit 1
fi

# Gather context from memory and todos
CONTEXT=""
for f in "$PROJECT_DIR"/memory/*.md; do
  [[ -f "$f" ]] && CONTEXT+="
--- $(basename "$f") ---
$(cat "$f")
"
done

if [[ -f "$PROJECT_DIR/todos/active.md" ]]; then
  CONTEXT+="
--- active.md (todos) ---
$(cat "$PROJECT_DIR/todos/active.md")
"
fi

TODAY=$(date '+%A, %B %d, %Y')

# Build the prompt — instruct Claude to TRY MCP tools, fall back gracefully
read -r -d '' PROMPT <<PROMPT_EOF || true
You are generating a morning briefing. Today is $TODAY.

Here is the current state of memory and tasks:

$CONTEXT

Instructions:
1. Try to use gcal_list_events to check today's calendar. If the tool is unavailable or errors, skip with "Calendar not connected."
2. Try to use gmail_search_messages to check recent emails (last 24h). If unavailable or errors, skip with "Email not connected."
3. Generate the briefing from whatever data you have. Memory and todos are always available.

Format as a Slack message (Slack mrkdwn, NOT markdown):

*Morning Briefing — $TODAY*

*Where You Left Off*
[1-2 sentences from active.md and memory files]

*Today's Calendar*
[Events with times, or "Calendar not connected." / "Clear day — no meetings."]

*Inbox Highlights*
[2-3 notable emails, or "Email not connected." / "Nothing urgent."]

*3 Priorities for Today*
1. [most important]
2. [second]
3. [third]

*One Thing to Watch*
[A pattern, reminder, or thing worth noticing from memory files]

Output ONLY the briefing text. No preamble, no explanation, no markdown fences.
PROMPT_EOF

log "Running claude to generate briefing"

# --print: non-interactive output only
# --dangerously-skip-permissions: no interactive prompts in headless mode
# Run from project dir so CLAUDE.md and .mcp.json are picked up
BRIEFING=$(cd "$PROJECT_DIR" && claude --print --dangerously-skip-permissions "$PROMPT" 2>>"$LOG_FILE") || {
  log "ERROR: claude command failed (exit $?)"
  exit 1
}

if [[ -z "$BRIEFING" ]]; then
  log "ERROR: Empty briefing generated"
  exit 1
fi

log "Briefing generated ($(echo "$BRIEFING" | wc -c) bytes), sending to Slack"

# Escape for JSON safely
ESCAPED_BRIEFING=$(printf '%s' "$BRIEFING" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')

# Post to Slack
HTTP_RESPONSE=$(curl -s -w "\n%{http_code}" \
  -X POST \
  -H 'Content-type: application/json' \
  --data "{\"text\": ${ESCAPED_BRIEFING}}" \
  "$SLACK_WEBHOOK_URL")

HTTP_BODY=$(echo "$HTTP_RESPONSE" | head -n -1)
HTTP_CODE=$(echo "$HTTP_RESPONSE" | tail -1)

if [[ "$HTTP_CODE" == "200" ]]; then
  log "Briefing sent to Slack successfully"
else
  log "ERROR: Slack returned HTTP $HTTP_CODE — $HTTP_BODY"
  exit 1
fi

log "Morning briefing complete"
