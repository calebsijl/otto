#!/bin/bash
# RUN ON THE SERVER. Brings the code on github into the live copy, safely.
#
# 1. save his life first (commit + push what he did since the last save), which
#    also rebases onto whatever code people have pushed meanwhile
# 2. make sure the working copy is exactly origin/main
# 3. restart the web side, and leave the tick timer however it was
set -e
cd "$(dirname "$0")"
./gitsave.sh || true
git fetch -q origin main
git pull --rebase -q origin main
chmod +x *.py *.sh 2>/dev/null || true
systemctl restart otto-web
echo "live copy is now at: $(git log -1 --format='%h %s')"
systemctl is-active --quiet otto-tick.timer && echo "he is awake" || echo "he is PAUSED (systemctl start otto-tick.timer)"
