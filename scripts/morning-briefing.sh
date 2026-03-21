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

# Build the prompt for Claude
PROMPT="$(cat <<PROMPT_EOF
You are generating a morning briefing. Today is $TODAY.

Here is the current state of memory and tasks:

$CONTEXT

Instructions:
1. First, use the Google Calendar tool (gcal_list_events) to check today's calendar events.
2. Then, use the Gmail tool (gmail_search_messages) to check for important recent emails from the last 24 hours.
3. Based on ALL of this — memory files, active tasks, calendar, and email — generate a morning briefing.

Format the briefing EXACTLY as a Slack message using this structure (use Slack mrkdwn, not markdown):

*Morning Briefing — $TODAY*

*Where You Left Off*
[1-2 sentences on what was last being worked on, based on active.md and memory]

*Today's Calendar*
[List today's events with times. If none, say "Clear day — no meetings."]

*Inbox Highlights*
[2-3 notable emails if any. If nothing important, say "Nothing urgent."]

*3 Priorities for Today*
1. [most important thing]
2. [second priority]
3. [third priority]

*One Thing to Watch*
[Something from the memory files — a pattern, a reminder, something worth noticing today]

Output ONLY the briefing text. No explanation, no preamble.
PROMPT_EOF
)"

log "Running claude to generate briefing"

# Run claude in non-interactive mode with the project context
BRIEFING=$(cd "$PROJECT_DIR" && claude --print --dangerously-skip-permissions "$PROMPT" 2>>"$LOG_FILE") || {
  log "ERROR: claude command failed"
  exit 1
}

if [[ -z "$BRIEFING" ]]; then
  log "ERROR: Empty briefing generated"
  exit 1
fi

log "Briefing generated, sending to Slack"

# Escape the briefing for JSON
ESCAPED_BRIEFING=$(echo "$BRIEFING" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')

# Post to Slack
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" \
  -X POST \
  -H 'Content-type: application/json' \
  --data "{\"text\": ${ESCAPED_BRIEFING}}" \
  "$SLACK_WEBHOOK_URL")

if [[ "$HTTP_CODE" == "200" ]]; then
  log "Briefing sent to Slack successfully"
else
  log "ERROR: Slack returned HTTP $HTTP_CODE"
  exit 1
fi

log "Morning briefing complete"
