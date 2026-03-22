#!/usr/bin/env bash
# =============================================================================
# SETUP SCHEDULER — Morning Briefing (via PM2)
# =============================================================================
#
# Run this once to start the daily briefing scheduler.
# Run it again to restart/update.
#
# Usage:
#   ./scripts/setup-cron.sh            # Start scheduler (default 8 AM)
#   BRIEFING_DEBUG=1 ./scripts/morning-briefing.sh   # Test run
#
# =============================================================================
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BRIEFING_SCRIPT="$PROJECT_DIR/scripts/morning-briefing.sh"
SCHEDULER_SCRIPT="$PROJECT_DIR/scripts/scheduler.mjs"

echo "=== Morning Briefing Scheduler Setup ==="
echo ""

# Make briefing script executable
chmod +x "$BRIEFING_SCRIPT"
echo "1. Made briefing script executable"

# Check .env
if [[ ! -f "$PROJECT_DIR/.env" ]] || grep -q 'YOUR/WEBHOOK/URL' "$PROJECT_DIR/.env" 2>/dev/null; then
  echo ""
  echo "WARNING: Slack webhook not configured yet!"
  echo "  Edit $PROJECT_DIR/.env and set your real SLACK_WEBHOOK_URL"
  echo "  Get one at: https://api.slack.com/apps → Incoming Webhooks"
  echo ""
fi

# Stop existing instance if running
npx --yes pm2 delete leah-briefing 2>/dev/null || true

# Start scheduler with PM2
echo "2. Starting scheduler with PM2..."
npx --yes pm2 start "$SCHEDULER_SCRIPT" \
  --name leah-briefing \
  --cwd "$PROJECT_DIR" \
  --log "$PROJECT_DIR/scripts/briefing.log" \
  --time

echo ""
echo "3. Scheduler is running."
npx --yes pm2 list

echo ""
echo "=== Done ==="
echo ""
echo "Useful commands:"
echo "  Status:         npx pm2 list"
echo "  Logs:           npx pm2 logs leah-briefing"
echo "  Restart:        npx pm2 restart leah-briefing"
echo "  Stop:           npx pm2 stop leah-briefing"
echo "  Remove:         npx pm2 delete leah-briefing"
echo "  Test briefing:  BRIEFING_DEBUG=1 $BRIEFING_SCRIPT"
echo "  View log file:  cat $PROJECT_DIR/scripts/briefing.log"
