#!/bin/bash
# Runs one search and emails the result. Called by launchd twice a day (see install_schedule.sh).
# A random 0-15 minute delay keeps the timing from looking mechanical.
cd "$(dirname "$0")" || exit 1
mkdir -p logs
sleep $((RANDOM % 900))
source .venv/bin/activate
{
  echo "=== $(date) ==="
  python finder.py run --no-open --email
} >> logs/scheduled.log 2>&1
