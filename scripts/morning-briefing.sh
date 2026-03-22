#!/usr/bin/env bash
# =============================================================================
# MORNING BRIEFING — Leah / Ra
# =============================================================================
#
# WHAT THIS DOES:
#   1. Reads your memory files (memory/*.md) and todos (todos/active.md)
#   2. Asks Claude to generate a morning briefing using those + calendar + email
#   3. Posts the briefing to your Slack channel via webhook
#
# HOW TO RUN MANUALLY:
#   cd /home/user/Leah && ./scripts/morning-briefing.sh
#
# HOW TO DEBUG:
#   1. Check the log:  cat /home/user/Leah/scripts/briefing.log
#   2. Run with debug:  BRIEFING_DEBUG=1 ./scripts/morning-briefing.sh
#      (this prints everything to terminal instead of just logging)
#   3. Common failures:
#      - "SLACK_WEBHOOK_URL not configured" → edit .env, set your webhook URL
#      - "claude command failed" → make sure 'claude' CLI is on your PATH
#      - "Slack returned HTTP 4xx" → your webhook URL is wrong or expired
#
# =============================================================================
set -euo pipefail

# --- CONFIGURATION -----------------------------------------------------------
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
LOG_FILE="$PROJECT_DIR/scripts/briefing.log"
ENV_FILE="$PROJECT_DIR/.env"
MAX_LOG_LINES=500  # Keep log from growing forever

# --- HELPERS -----------------------------------------------------------------
log() {
  local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $*"
  echo "$msg" >> "$LOG_FILE"
  # In debug mode, also print to terminal
  if [[ "${BRIEFING_DEBUG:-0}" == "1" ]]; then
    echo "$msg"
  fi
}

die() {
  log "FATAL: $*"
  exit 1
}

# Trim log file if it gets too long
trim_log() {
  if [[ -f "$LOG_FILE" ]] && (( $(wc -l < "$LOG_FILE") > MAX_LOG_LINES )); then
    tail -n "$MAX_LOG_LINES" "$LOG_FILE" > "$LOG_FILE.tmp" && mv "$LOG_FILE.tmp" "$LOG_FILE"
    log "Log trimmed to last $MAX_LOG_LINES lines"
  fi
}

# --- STEP 1: Load .env -------------------------------------------------------
# The .env file holds your SLACK_WEBHOOK_URL. If it's missing or the URL is
# still the placeholder, the script stops here.
log "=== Starting morning briefing ==="

if [[ -f "$ENV_FILE" ]]; then
  set -a
  source "$ENV_FILE"
  set +a
  log "Loaded .env"
else
  die ".env file not found at $ENV_FILE — run: echo 'SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL' > $ENV_FILE"
fi

if [[ -z "${SLACK_WEBHOOK_URL:-}" || "$SLACK_WEBHOOK_URL" == *"YOUR/WEBHOOK/URL"* ]]; then
  die "SLACK_WEBHOOK_URL not configured. Edit $ENV_FILE and paste your real Slack webhook URL."
fi
log "Slack webhook configured (ends with ...${SLACK_WEBHOOK_URL: -8})"

# --- STEP 2: Gather context from memory + todos ------------------------------
# Reads every .md file in memory/ and the active todos file.
# This becomes the "brain dump" that Claude uses to write the briefing.
CONTEXT=""

for f in "$PROJECT_DIR"/memory/*.md; do
  if [[ -f "$f" ]]; then
    CONTEXT+="
--- $(basename "$f") ---
$(cat "$f")
"
  fi
done

if [[ -f "$PROJECT_DIR/todos/active.md" ]]; then
  CONTEXT+="
--- active.md (todos) ---
$(cat "$PROJECT_DIR/todos/active.md")
"
fi

if [[ -z "$CONTEXT" ]]; then
  die "No memory files or todos found. Is the memory/ directory populated?"
fi

log "Gathered context ($(echo "$CONTEXT" | wc -c) bytes from memory + todos)"

# --- STEP 3: Build the prompt ------------------------------------------------
# This prompt tells Claude exactly what format to produce.
# It tries MCP tools (Google Calendar, Gmail) but gracefully skips if unavailable.
TODAY=$(date '+%A, %B %d, %Y')

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

# --- STEP 4: Run Claude to generate the briefing -----------------------------
# --print: non-interactive, just output the result
# --dangerously-skip-permissions: needed in headless/cron mode (no TTY to approve)
# We run from PROJECT_DIR so Claude picks up CLAUDE.md and .mcp.json if present.
log "Calling claude --print to generate briefing..."

BRIEFING=$(cd "$PROJECT_DIR" && claude --print --dangerously-skip-permissions "$PROMPT" 2>>"$LOG_FILE") || {
  die "claude command failed (exit $?). Check that 'claude' is in PATH and authenticated. Try running manually: cd $PROJECT_DIR && claude --print 'hello'"
}

if [[ -z "$BRIEFING" ]]; then
  die "Claude returned an empty briefing. Check the log for errors above."
fi

log "Briefing generated ($(echo "$BRIEFING" | wc -c) bytes)"

if [[ "${BRIEFING_DEBUG:-0}" == "1" ]]; then
  echo ""
  echo "--- GENERATED BRIEFING ---"
  echo "$BRIEFING"
  echo "--- END BRIEFING ---"
  echo ""
fi

# --- STEP 5: Post to Slack ---------------------------------------------------
# Escapes the briefing text as a JSON string, wraps it in Slack's payload format,
# and POSTs it to the webhook URL.
ESCAPED_BRIEFING=$(printf '%s' "$BRIEFING" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))') || {
  die "Failed to JSON-encode briefing. Is python3 installed?"
}

log "Posting to Slack..."

HTTP_RESPONSE=$(curl -s -w "\n%{http_code}" \
  --max-time 30 \
  -X POST \
  -H 'Content-type: application/json' \
  --data "{\"text\": ${ESCAPED_BRIEFING}}" \
  "$SLACK_WEBHOOK_URL") || {
  die "curl failed — network issue or bad webhook URL."
}

HTTP_BODY=$(echo "$HTTP_RESPONSE" | head -n -1)
HTTP_CODE=$(echo "$HTTP_RESPONSE" | tail -1)

if [[ "$HTTP_CODE" == "200" ]]; then
  log "Briefing sent to Slack successfully"
else
  die "Slack returned HTTP $HTTP_CODE — $HTTP_BODY. If 403/404, your webhook URL may be expired. Create a new one at https://api.slack.com/apps"
fi

# --- CLEANUP -----------------------------------------------------------------
trim_log
log "=== Morning briefing complete ==="
