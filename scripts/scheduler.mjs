// =============================================================================
// SCHEDULER — Runs morning-briefing.sh on a daily schedule using PM2
// =============================================================================
//
// HOW IT WORKS:
//   This script wakes up every minute and checks if it's time to run.
//   When the hour and minute match the schedule, it executes morning-briefing.sh.
//   PM2 keeps this script running in the background (survives terminal close).
//
// WHY NOT CRON?
//   This environment doesn't have cron or systemd user timers installed.
//   PM2 + a simple JS scheduler is the next best thing.
//
// HOW TO CHANGE THE TIME:
//   Edit SCHEDULE_HOUR and SCHEDULE_MINUTE below.
//   Then restart: pm2 restart leah-briefing
//
// =============================================================================

import { execSync } from 'child_process';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';
import { appendFileSync, existsSync } from 'fs';

// --- SCHEDULE CONFIG --------------------------------------------------------
const SCHEDULE_HOUR   = 8;   // 0-23 (8 = 8 AM)
const SCHEDULE_MINUTE = 0;   // 0-59

// --- PATHS ------------------------------------------------------------------
const __dirname = dirname(fileURLToPath(import.meta.url));
const PROJECT_DIR = join(__dirname, '..');
const BRIEFING_SCRIPT = join(__dirname, 'morning-briefing.sh');
const LOG_FILE = join(__dirname, 'briefing.log');

// --- HELPERS ----------------------------------------------------------------
function log(msg) {
  const ts = new Date().toISOString().replace('T', ' ').slice(0, 19);
  const line = `[${ts}] [scheduler] ${msg}\n`;
  appendFileSync(LOG_FILE, line);
  console.log(line.trim());
}

// Track whether we already ran this minute (prevents double-fire)
let lastRunDate = '';

function checkAndRun() {
  const now = new Date();
  const hour = now.getHours();
  const minute = now.getMinutes();
  const dateKey = `${now.getFullYear()}-${now.getMonth()}-${now.getDate()}`;

  if (hour === SCHEDULE_HOUR && minute === SCHEDULE_MINUTE && lastRunDate !== dateKey) {
    lastRunDate = dateKey;
    log(`Trigger: it's ${String(hour).padStart(2,'0')}:${String(minute).padStart(2,'0')} — running briefing`);

    try {
      if (!existsSync(BRIEFING_SCRIPT)) {
        log(`ERROR: Script not found at ${BRIEFING_SCRIPT}`);
        return;
      }
      execSync(`bash "${BRIEFING_SCRIPT}"`, {
        cwd: PROJECT_DIR,
        timeout: 120_000, // 2 minute timeout
        stdio: ['ignore', 'pipe', 'pipe'],
      });
      log('Briefing completed successfully');
    } catch (err) {
      log(`ERROR: Briefing failed — ${err.message}`);
      if (err.stderr) log(`STDERR: ${err.stderr.toString().slice(0, 500)}`);
    }
  }
}

// --- MAIN -------------------------------------------------------------------
log(`Scheduler started. Briefing scheduled for ${String(SCHEDULE_HOUR).padStart(2,'0')}:${String(SCHEDULE_MINUTE).padStart(2,'0')} daily.`);
log(`Briefing script: ${BRIEFING_SCRIPT}`);
log(`Checking every 30 seconds...`);

// Check every 30 seconds (cheap, catches the minute window reliably)
setInterval(checkAndRun, 30_000);

// Also check immediately on startup
checkAndRun();
