#!/bin/bash
# Removes the twice-daily schedule.
LABEL="com.marketplace-finder.twice-daily"
launchctl bootout "gui/$(id -u)/$LABEL" 2>/dev/null || true
rm -f "$HOME/Library/LaunchAgents/$LABEL.plist"
echo "Schedule removed."
