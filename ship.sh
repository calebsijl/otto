#!/bin/bash
# RUN ON ANY COMPUTER. Replaces the rsync part of deploy.sh.
#   ./ship.sh                 push your commits, then update the server
#   ./ship.sh root@1.2.3.4    same, for a different server
# github is the only thing that moves code. nothing is copied by hand.
set -e
cd "$(dirname "$0")"
TARGET="${1:-root@165.232.137.53}"
[ -z "$(git status --porcelain)" ] || { echo "you have uncommitted changes. commit them first:"; git status --short; exit 1; }
git pull --rebase -q origin main
git push -q origin main
echo "pushed $(git log -1 --format='%h %s')"
ssh "$TARGET" 'cd ~/otto && ./update.sh'
