#!/bin/bash
# Runs one search and alerts you. Called by launchd twice a day (see install_schedule.sh).
# Always shows a macOS notification; also emails if EMAIL_TO is set in .env.
# A random 0-15 minute delay keeps the timing from looking mechanical.
cd "$(dirname "$0")" || exit 1
mkdir -p logs
sleep $((RANDOM % 900))
source .venv/bin/activate
FLAGS="--no-open --notify"
if grep -qE '^EMAIL_TO=.+' .env 2>/dev/null; then FLAGS="$FLAGS --email"; fi
{
  echo "=== $(date) ==="
  python finder.py run $FLAGS
} >> logs/scheduled.log 2>&1
