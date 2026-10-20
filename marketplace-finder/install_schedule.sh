#!/bin/bash
# Installs a macOS launchd job that runs the search twice a day (08:20 and 18:20 local time)
# and emails the result. Undo with ./uninstall_schedule.sh.
set -e
cd "$(dirname "$0")"
HERE="$(pwd)"
LABEL="com.marketplace-finder.twice-daily"
PLIST="$HOME/Library/LaunchAgents/$LABEL.plist"

if [ ! -f .env ]; then
  echo "Missing .env - copy .env.example to .env and fill it in first."; exit 1
fi
chmod 600 .env
chmod +x run_scheduled.sh
mkdir -p logs "$HOME/Library/LaunchAgents"

cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key><string>$LABEL</string>
  <key>ProgramArguments</key>
  <array><string>/bin/bash</string><string>$HERE/run_scheduled.sh</string></array>
  <key>StartCalendarInterval</key>
  <array>
    <dict><key>Hour</key><integer>8</integer><key>Minute</key><integer>20</integer></dict>
    <dict><key>Hour</key><integer>18</integer><key>Minute</key><integer>20</integer></dict>
  </array>
  <key>StandardOutPath</key><string>$HERE/logs/launchd.out</string>
  <key>StandardErrorPath</key><string>$HERE/logs/launchd.err</string>
</dict>
</plist>
EOF

launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
launchctl bootstrap "gui/$(id -u)" "$PLIST"
echo "Installed. The search will run at about 08:20 and 18:20 each day (Mac must be awake and logged in)."
echo "Log: $HERE/logs/scheduled.log"
