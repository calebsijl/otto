#!/bin/bash
# Put otto on a timer so he lives whether or not a terminal is open.
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
PLIST="$HOME/Library/LaunchAgents/com.otto.tick.plist"
[ -f "$DIR/.env" ] || { echo "no .env — put your api key in it first."; exit 1; }

cat > "$DIR/run.sh" <<SH
#!/bin/bash
cd "$DIR" || exit 1
exec /usr/bin/env python3 ./tick.py --realtime >> cron.log 2>&1
SH
chmod +x "$DIR/run.sh"

mkdir -p "$HOME/Library/LaunchAgents"
cat > "$PLIST" <<PL
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>Label</key><string>com.otto.tick</string>
  <key>ProgramArguments</key><array><string>$DIR/run.sh</string></array>
  <key>StartInterval</key><integer>1200</integer>
  <key>RunAtLoad</key><true/>
  <key>StandardOutPath</key><string>$DIR/launchd.log</string>
  <key>StandardErrorPath</key><string>$DIR/launchd.log</string>
</dict></plist>
PL
launchctl unload "$PLIST" 2>/dev/null || true
launchctl load "$PLIST"
echo "otto now wakes every 20 minutes, whether or not a terminal is open."
echo
echo "  watch:  tail -f $DIR/cron.log"
echo "  stop:   launchctl unload $PLIST"
echo "  start:  launchctl load $PLIST"
echo
echo "your mac must be awake. plug it in and turn sleep off, or run: caffeinate -dimsu &"
