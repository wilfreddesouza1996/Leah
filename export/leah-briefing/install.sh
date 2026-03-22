#!/usr/bin/env bash
# =============================================================================
# INSTALL — Leah Morning Briefing (Portable)
# =============================================================================
#
# USAGE:
#   1. Unzip/untar this folder anywhere on your machine
#   2. cd into this folder
#   3. Run: ./install.sh
#   4. Edit .env with your real Slack webhook URL
#   5. Test: BRIEFING_DEBUG=1 ./scripts/morning-briefing.sh
#
# REQUIREMENTS:
#   - Node.js (v18+)     → for PM2 scheduler
#   - Python 3           → for JSON encoding
#   - claude CLI          → for generating the briefing
#   - curl               → for posting to Slack
#
# =============================================================================
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"

echo "=== Leah Morning Briefing — Install ==="
echo ""
echo "Installing from: $HERE"
echo ""

# --- Check dependencies ------------------------------------------------------
MISSING=()
command -v node    >/dev/null 2>&1 || MISSING+=("node (Node.js)")
command -v python3 >/dev/null 2>&1 || MISSING+=("python3")
command -v claude  >/dev/null 2>&1 || MISSING+=("claude (Claude CLI)")
command -v curl    >/dev/null 2>&1 || MISSING+=("curl")

if [[ ${#MISSING[@]} -gt 0 ]]; then
  echo "ERROR: Missing required tools:"
  for m in "${MISSING[@]}"; do echo "  - $m"; done
  echo ""
  echo "Install them and re-run this script."
  exit 1
fi
echo "1. All dependencies found."

# --- Make scripts executable --------------------------------------------------
chmod +x "$HERE/scripts/morning-briefing.sh"
chmod +x "$HERE/scripts/setup-cron.sh"
echo "2. Scripts made executable."

# --- Check .env ---------------------------------------------------------------
if [[ ! -f "$HERE/.env" ]]; then
  echo "SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL" > "$HERE/.env"
  echo ""
  echo "   CREATED .env — you MUST edit it with your real Slack webhook URL:"
  echo "   $HERE/.env"
  echo ""
elif grep -q 'YOUR/WEBHOOK/URL' "$HERE/.env" 2>/dev/null; then
  echo ""
  echo "   WARNING: .env still has placeholder webhook URL."
  echo "   Edit: $HERE/.env"
  echo ""
else
  echo "3. .env looks configured."
fi

# --- Install PM2 globally (or use npx) ----------------------------------------
if ! command -v pm2 >/dev/null 2>&1; then
  echo "4. Installing PM2..."
  npm install -g pm2 2>/dev/null || {
    echo "   Could not install pm2 globally. Will use npx instead."
  }
else
  echo "4. PM2 already installed."
fi

# --- Stop any existing instance ------------------------------------------------
(pm2 delete leah-briefing 2>/dev/null || npx --yes pm2 delete leah-briefing 2>/dev/null) || true

# --- Start the scheduler ------------------------------------------------------
PM2_CMD="pm2"
command -v pm2 >/dev/null 2>&1 || PM2_CMD="npx --yes pm2"

$PM2_CMD start "$HERE/scripts/scheduler.mjs" \
  --name leah-briefing \
  --cwd "$HERE" \
  --log "$HERE/scripts/briefing.log" \
  --time

echo ""
echo "5. Scheduler started."
$PM2_CMD list

# --- Auto-start on reboot (optional) ------------------------------------------
echo ""
echo "Optional: To auto-start on reboot, run:"
echo "  pm2 save && pm2 startup"
echo ""

echo "=== Installation Complete ==="
echo ""
echo "Files:"
echo "  Config:     $HERE/.env"
echo "  Briefing:   $HERE/scripts/morning-briefing.sh"
echo "  Scheduler:  $HERE/scripts/scheduler.mjs"
echo "  Memory:     $HERE/memory/"
echo "  Todos:      $HERE/todos/"
echo "  Log:        $HERE/scripts/briefing.log"
echo ""
echo "Commands:"
echo "  Test now:     BRIEFING_DEBUG=1 $HERE/scripts/morning-briefing.sh"
echo "  View logs:    cat $HERE/scripts/briefing.log"
echo "  Status:       pm2 list"
echo "  Restart:      pm2 restart leah-briefing"
echo "  Stop:         pm2 stop leah-briefing"
echo "  Remove:       pm2 delete leah-briefing"
echo ""
echo "To change the schedule, edit SCHEDULE_HOUR in $HERE/scripts/scheduler.mjs"
echo "then run: pm2 restart leah-briefing"
