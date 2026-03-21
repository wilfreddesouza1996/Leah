#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SYSTEMD_DIR="$HOME/.config/systemd/user"

echo "=== Leah Morning Briefing Setup ==="
echo ""

# 1. Slack webhook
if [[ -f "$PROJECT_DIR/.env" ]]; then
  source "$PROJECT_DIR/.env"
fi

if [[ -z "${SLACK_WEBHOOK_URL:-}" || "$SLACK_WEBHOOK_URL" == *"YOUR/WEBHOOK/URL"* ]]; then
  echo "Step 1: Slack Webhook"
  echo "  Create one at: https://api.slack.com/apps → Your App → Incoming Webhooks"
  echo "  Add it to the channel you want DMs in."
  echo ""
  read -rp "  Paste your Slack webhook URL: " webhook_url
  echo ""

  if [[ -n "$webhook_url" ]]; then
    # Write/update .env
    if [[ -f "$PROJECT_DIR/.env" ]]; then
      sed -i "s|^SLACK_WEBHOOK_URL=.*|SLACK_WEBHOOK_URL=$webhook_url|" "$PROJECT_DIR/.env"
    else
      echo "SLACK_WEBHOOK_URL=$webhook_url" > "$PROJECT_DIR/.env"
    fi
    echo "  Saved to .env"
  else
    echo "  Skipped. Set SLACK_WEBHOOK_URL in .env manually before the first briefing."
  fi
else
  echo "Step 1: Slack webhook already configured."
fi

echo ""

# 2. Systemd timer
echo "Step 2: Scheduling (systemd timer, daily at 8AM)"

mkdir -p "$SYSTEMD_DIR"

cat > "$SYSTEMD_DIR/morning-briefing.service" <<EOF
[Unit]
Description=Leah Morning Briefing
After=network-online.target

[Service]
Type=oneshot
ExecStart=$PROJECT_DIR/scripts/morning-briefing.sh
Environment=PATH=/opt/node22/bin:/usr/local/bin:/usr/bin:/bin
WorkingDirectory=$PROJECT_DIR
EOF

cat > "$SYSTEMD_DIR/morning-briefing.timer" <<EOF
[Unit]
Description=Run Leah Morning Briefing daily at 8AM

[Timer]
OnCalendar=*-*-* 08:00:00
Persistent=true

[Install]
WantedBy=timers.target
EOF

if systemctl --user daemon-reload 2>/dev/null; then
  systemctl --user enable --now morning-briefing.timer
  echo "  Timer enabled and started."
  echo ""
  systemctl --user status morning-briefing.timer --no-pager || true
else
  echo "  systemd user session not available."
  echo "  Alternative: add this to your crontab (crontab -e):"
  echo ""
  echo "    0 8 * * * $PROJECT_DIR/scripts/morning-briefing.sh"
  echo ""
fi

echo ""

# 3. Test run
echo "Step 3: Test"
read -rp "  Run a test briefing now? (y/n): " run_test

if [[ "$run_test" == "y" ]]; then
  echo ""
  echo "  Running briefing..."
  "$PROJECT_DIR/scripts/morning-briefing.sh" && echo "  Done. Check Slack." || echo "  Failed. Check scripts/briefing.log"
fi

echo ""
echo "Setup complete. Briefings will run daily at 8AM."
echo "  - Edit schedule: systemctl --user edit morning-briefing.timer"
echo "  - Run manually:  ./scripts/morning-briefing.sh"
echo "  - Check logs:    cat scripts/briefing.log"
echo "  - Disable:       systemctl --user disable morning-briefing.timer"
