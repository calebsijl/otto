#!/bin/bash
# Put otto on a server so he lives without your computer, and anyone can watch.
#
#   ./deploy.sh root@1.2.3.4                     plain, http://1.2.3.4:8080
#   ./deploy.sh root@1.2.3.4 otto.yourdomain.com real website, https, no port
#
set -e
RESET=0
for a in "$@"; do [ "$a" = "--reset" ] && RESET=1; done
ARGS=(); for a in "$@"; do [ "$a" != "--reset" ] && ARGS+=("$a"); done
TARGET="${ARGS[0]}"; DOMAIN="${ARGS[1]}"
[ -n "$TARGET" ] || { echo "usage: ./deploy.sh user@server-ip [domain]"; exit 1; }
DIR="$(cd "$(dirname "$0")" && pwd)"
[ -f "$DIR/.env" ] || { echo "no .env here. his api key has to go with him."; exit 1; }
grep -q 'ANTHROPIC_API_KEY\|OPENROUTER_API_KEY\|GEMINI_API_KEY' "$DIR/.env" \
  || { echo ".env has no api key in it."; exit 1; }

ssh "$TARGET" 'mkdir -p ~/otto'
# Was he paused? A deploy used to start him again whatever you had done, which
# is a nasty surprise when you have deliberately stopped him to work on his
# world. Remember the answer and put it back the way it was.
WAS_TICKING=$(ssh "$TARGET" 'systemctl is-active --quiet otto-tick.timer && echo yes || echo no' 2>/dev/null || echo yes)
[ "$WAS_TICKING" = "no" ] && echo "==> he is paused, and this will leave him paused"
LIVES=$(ssh "$TARGET" '[ -f ~/otto/state.json ] && echo yes || echo no')

if [ "$LIVES" = "yes" ] && [ "$RESET" -eq 0 ]; then
  echo "==> he is already living up there. updating his code, leaving his life alone."
  echo "    (his memory, world, pages, journal and clock stay as they are)"
  KEEP=(--exclude 'memory/' --exclude 'world/world.json' --exclude 'state.json'
        --exclude 'site/journal.md' --exclude 'site/*.md' --exclude 'site/*.txt'
        --exclude 'inbox.jsonl' --exclude 'outbox.jsonl'
        --exclude 'log.jsonl' --exclude 'thoughts.jsonl' --exclude '.env')
else
  if [ "$RESET" -eq 1 ]; then
    echo "==> --reset: replacing everything up there with what is on this mac."
  else
    echo "==> first time. sending everything."
  fi
  KEEP=()
fi

echo "==> sending otto to $TARGET"
rsync -az \
  --exclude '__pycache__' --exclude 'runs' --exclude '.git' \
  --exclude '*.log' --exclude 'library/.text' --exclude 'venv/' \
  "${KEEP[@]}" "$DIR/" "$TARGET:otto/"
# .env only if he has not got one yet
ssh "$TARGET" '[ -f ~/otto/.env ]' || rsync -az "$DIR/.env" "$TARGET:otto/.env"

TZ_NAME="$(readlink /etc/localtime 2>/dev/null | sed 's|.*/zoneinfo/||')"
[ -n "$TZ_NAME" ] || TZ_NAME="UTC"
echo "==> setting him up (his clock will run on $TZ_NAME, same as yours)"
ssh "$TARGET" "DOMAIN='$DOMAIN' TZ_NAME='$TZ_NAME' WAS_TICKING='$WAS_TICKING' bash -s" <<'REMOTE'
set -e
cd ~/otto
SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"

export DEBIAN_FRONTEND=noninteractive LC_ALL=C.UTF-8 LANG=C.UTF-8
# his day should line up with yours, not with the datacentre's
if [ -n "$TZ_NAME" ] && [ "$(cat /etc/timezone 2>/dev/null)" != "$TZ_NAME" ]; then
  $SUDO timedatectl set-timezone "$TZ_NAME" 2>/dev/null || true
  echo "    clock set to $TZ_NAME ($(date '+%H:%M %A'))"
fi
echo "    installing what he needs (a minute or so)"
$SUDO apt-get update -qq >/dev/null 2>&1
$SUDO apt-get install -y -qq python3 python3-venv curl cron >/dev/null 2>&1

# Ubuntu 24.04 will not let pip install system-wide, so he gets his own venv
PY_BIN="$HOME/otto/venv/bin/python3"
if [ ! -x "$PY_BIN" ]; then
  python3 -m venv "$HOME/otto/venv"
fi
"$HOME/otto/venv/bin/pip" install --quiet --upgrade pip >/dev/null 2>&1 || true
if ! "$HOME/otto/venv/bin/pip" install --quiet anthropic; then
  echo "!! could not install the anthropic package. stopping."
  exit 1
fi
"$PY_BIN" -c "import anthropic" || { echo "!! anthropic did not import."; exit 1; }
echo "    python ready"
chmod +x *.py *.sh 2>/dev/null || true

# a key, so strangers can watch but not send him things
grep -q '^OTTO_KEY=' .env || \
  echo "OTTO_KEY=$(head -c 24 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9' | head -c 24)" >> .env
grep -q '^PORT=' .env || echo "PORT=8080" >> .env
grep -q '^OTTO_EVERY=' .env || echo "OTTO_EVERY=15min" >> .env
EVERY=$(grep '^OTTO_EVERY=' .env | cut -d= -f2)
KEY=$(grep '^OTTO_KEY=' .env | cut -d= -f2)

# the web side, as a service that restarts itself and survives reboots
$SUDO tee /etc/systemd/system/otto-web.service >/dev/null <<UNIT
[Unit]
Description=otto's console
After=network.target
[Service]
WorkingDirectory=$HOME/otto
# serve.py reads OTTO_KEY straight out of the environment, and without this
# line it never sees the one in .env, so writing stayed open to anybody who
# could reach the address.
EnvironmentFile=-$HOME/otto/.env
ExecStart=$PY_BIN $HOME/otto/serve.py
Restart=always
RestartSec=3
User=$(whoami)
[Install]
WantedBy=multi-user.target
UNIT

# his life, every 20 minutes, on real time
# a systemd timer, not cron. cron on a minimal ubuntu image is unreliable
# and fails silently, which is the worst combination for something that has to
# wake every twenty minutes forever.
$SUDO tee /etc/systemd/system/otto-tick.service >/dev/null <<U2
[Unit]
Description=one otto tick
[Service]
Type=oneshot
WorkingDirectory=$HOME/otto
ExecStart=$PY_BIN $HOME/otto/tick.py --realtime
User=$(whoami)
StandardOutput=append:$HOME/otto/cron.log
StandardError=append:$HOME/otto/cron.log
U2
$SUDO tee /etc/systemd/system/otto-tick.timer >/dev/null <<U3
[Unit]
Description=wake otto every $EVERY
[Timer]
OnBootSec=2min
OnUnitActiveSec=$EVERY
AccuracySec=30s
Persistent=true
[Install]
WantedBy=timers.target
U3
# and take the old cron job out, so he does not wake twice
( crontab -l 2>/dev/null | grep -v 'otto/tick.py' || true ) | crontab - 2>/dev/null || true

$SUDO systemctl daemon-reload
$SUDO systemctl enable otto-web >/dev/null 2>&1
$SUDO systemctl restart otto-web
if [ "$WAS_TICKING" = "no" ]; then
  # he was stopped on purpose: set the timer up but do not start it
  $SUDO systemctl enable otto-tick.timer >/dev/null 2>&1
  echo "    he was paused before this deploy, so he is still paused."
  echo "    start him with:  systemctl start otto-tick.timer"
else
  $SUDO systemctl enable --now otto-tick.timer >/dev/null 2>&1
  if systemctl is-active --quiet otto-tick.timer; then
    echo "    his wake-up is set: every $EVERY"
    systemctl list-timers otto-tick.timer --no-pager 2>/dev/null | sed -n 2p | sed 's/^/    next: /'
  else
    echo "    !! the wake-up timer did not start:"
    $SUDO journalctl -u otto-tick.timer -n 10 --no-pager
  fi
fi

if [ -n "$DOMAIN" ]; then
  echo "==> a real website at $DOMAIN, with https"
  if ! command -v caddy >/dev/null; then
    $SUDO apt-get install -y -qq debian-keyring debian-archive-keyring apt-transport-https >/dev/null
    curl -fsSL https://dl.cloudsmith.io/public/caddy/stable/gpg.key \
      | $SUDO gpg --batch --yes --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
    curl -fsSL https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt \
      | $SUDO tee /etc/apt/sources.list.d/caddy-stable.list >/dev/null
    $SUDO apt-get update -qq && $SUDO apt-get install -y -qq caddy >/dev/null
  fi
  printf '%s {\n    reverse_proxy localhost:8080\n}\n' "$DOMAIN" | $SUDO tee /etc/caddy/Caddyfile >/dev/null
  $SUDO systemctl restart caddy
  BASE="https://$DOMAIN"
  command -v ufw >/dev/null && { $SUDO ufw allow 80/tcp >/dev/null 2>&1; $SUDO ufw allow 443/tcp >/dev/null 2>&1; }
else
  IP=$(curl -s -4 --max-time 5 ifconfig.me || hostname -I | awk '{print $1}')
  BASE="http://$IP:8080"
  command -v ufw >/dev/null && $SUDO ufw allow 8080/tcp >/dev/null 2>&1
fi

[ -f memory/notes.jsonl ] || "$PY_BIN" ./sync_clock.py   # only on a fresh otto
sleep 2
if systemctl is-active --quiet otto-web; then
  echo "==> the console is up"
else
  echo "!! the console did not start:"; $SUDO journalctl -u otto-web -n 25 --no-pager; exit 1
fi
if [ "$WAS_TICKING" = "no" ]; then
  echo "==> not waking him, he is paused"
else
echo "==> waking him once, to check he can think"
if "$PY_BIN" ./tick.py --realtime; then
  echo "==> he is alive"
else
  echo "!! his first tick failed. the api key in .env is the usual reason."
fi
fi

echo
echo "================================================================"
echo " anyone, read only:   $BASE"
echo " you, can write:      $BASE/?key=$KEY"
echo "================================================================"
if [ "$WAS_TICKING" = "no" ]; then
  echo " he is PAUSED. start him:  systemctl start otto-tick.timer"
else
  echo " he wakes every $EVERY from now on, whatever your laptop does."
fi
echo " look in:  ssh <server> 'tail -f ~/otto/cron.log'"
REMOTE
echo
echo "done."
echo
echo "  ./deploy.sh $TARGET${DOMAIN:+ $DOMAIN}            update his code, keep his life"
echo "  ./deploy.sh $TARGET${DOMAIN:+ $DOMAIN} --reset    wipe him and start over"
echo
echo "to bring his life back down to this mac:"
echo "  rsync -az $TARGET:otto/{memory,world,site,state.json,outbox.jsonl} $DIR/"
