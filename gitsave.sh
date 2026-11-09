#!/bin/bash
# Save everything otto has to github.
#
# Runs on the server, where he actually lives, because that is the only place
# his memory, his journal and the pages he writes exist. A timer calls this;
# running it by hand is fine too.
#
# It will not push if a live api key has somehow ended up in a tracked file.
set -e
cd "$(dirname "$0")"

[ -d .git ] || { echo "no repo here yet. run: ./github-setup.sh push <url>"; exit 1; }

git add -A

if git diff --cached --quiet; then
  echo "nothing new since last time"
  exit 0
fi

# last line of defence. .gitignore should already keep every .env out.
# the || true matters: with no leak the grep exits non-zero, and under set -e
# a clean scan would kill the script. which is exactly what it did.
LEAK=$(git diff --cached --name-only | while read -r f; do
  [ -f "$f" ] && grep -lE 'sk-ant-[A-Za-z0-9_-]{20}|sk-or-[A-Za-z0-9_-]{10}|AIza[A-Za-z0-9_-]{20}' "$f" 2>/dev/null
done) || true
if [ -n "$LEAK" ]; then
  echo "NOT PUSHING. a live api key is in these files:"
  echo "$LEAK" | sed 's/^/  /'
  git reset -q
  exit 1
fi

TICK=$(python3 -c "import json;print(json.load(open('state.json'))['tick'])" 2>/dev/null || echo '?')
WHEN=$(python3 -c "import json;print(json.load(open('state.json'))['clock'][:16].replace('T',' '))" 2>/dev/null || echo '')
N=$(git diff --cached --name-only | wc -l | tr -d ' ')

git commit -q -m "otto, tick $TICK ($WHEN)" -m "$N files changed" \
  || { echo "commit refused:"; git commit -m x --dry-run 2>&1 | head -5; exit 1; }
git pull --rebase -q origin main 2>/dev/null || true
git push -q origin main
echo "saved: tick $TICK, $N files"
