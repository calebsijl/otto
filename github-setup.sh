#!/bin/bash
# One-time: put otto's server on github.
#
#   ./github-setup.sh key                           make and show the deploy key
#   ./github-setup.sh push git@github.com:you/otto.git   first push, then hourly
#
# The key never leaves the server. You paste the public half into github, which
# is safe to share: it is the half that is meant to be public.
set -e
cd "$(dirname "$0")"
MODE="$1"

if [ "$MODE" = "key" ]; then
  [ -f ~/.ssh/otto_deploy ] || ssh-keygen -t ed25519 -N "" -C "otto-server" -f ~/.ssh/otto_deploy
  grep -q "Host github.com" ~/.ssh/config 2>/dev/null || cat >> ~/.ssh/config <<'SSH'
Host github.com
  IdentityFile ~/.ssh/otto_deploy
  IdentitiesOnly yes
SSH
  chmod 600 ~/.ssh/config
  echo
  echo "add this to the repo as a deploy key, and tick 'Allow write access':"
  echo "  Settings -> Deploy keys -> Add deploy key"
  echo
  cat ~/.ssh/otto_deploy.pub
  echo
  exit 0
fi

if [ "$MODE" = "push" ]; then
  URL="$2"
  [ -n "$URL" ] || { echo "usage: ./github-setup.sh push git@github.com:you/otto.git"; exit 1; }
  git config --global --get user.email >/dev/null 2>&1 || git config --global user.email "otto@the-lane"
  git config --global --get user.name  >/dev/null 2>&1 || git config --global user.name  "otto"
  git config --global --add safe.directory "$PWD" 2>/dev/null || true

  ssh -o StrictHostKeyChecking=accept-new -T git@github.com 2>&1 | head -1 || true

  [ -d .git ] || { git init -q -b main .; echo "started a repo here"; }
  git remote remove origin 2>/dev/null || true
  git remote add origin "$URL"

  ./gitsave.sh || { echo "first save failed, nothing installed"; exit 1; }
  git push -q -u origin main 2>/dev/null || true

  cat > /etc/systemd/system/otto-save.service <<'UNIT'
[Unit]
Description=save otto to github
[Service]
Type=oneshot
WorkingDirectory=/root/otto
ExecStart=/root/otto/gitsave.sh
UNIT
  cat > /etc/systemd/system/otto-save.timer <<'UNIT'
[Unit]
Description=save otto to github, hourly
[Timer]
OnBootSec=10min
OnUnitActiveSec=1h
Persistent=true
[Install]
WantedBy=timers.target
UNIT
  systemctl daemon-reload
  systemctl enable --now otto-save.timer
  echo
  echo "done. he saves himself every hour."
  systemctl list-timers otto-save.timer --no-pager | head -3
  exit 0
fi

echo "usage: ./github-setup.sh key   |   ./github-setup.sh push <url>"
exit 1
