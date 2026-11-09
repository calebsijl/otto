#!/bin/bash
# Bring his life back down from the server to this Mac.
#   ./pull.sh root@YOUR-IP
set -e
T="$1"; [ -n "$T" ] || { echo "usage: ./pull.sh user@server-ip"; exit 1; }
D="$(cd "$(dirname "$0")" && pwd)"
echo "fetching his memory, world, pages and clock from $T ..."
rsync -az "$T:otto/memory/"  "$D/memory/"
rsync -az "$T:otto/site/"    "$D/site/"
rsync -az "$T:otto/world/world.json" "$D/world/world.json"
for f in state.json inbox.jsonl outbox.jsonl log.jsonl thoughts.jsonl; do
  rsync -az "$T:otto/$f" "$D/$f" 2>/dev/null || true
done
python3 - <<'PY'
import json, pathlib
s = json.loads(pathlib.Path('state.json').read_text())
print(f"\nhe is on tick {s['tick']}, {s['clock'][:16].replace('T',' ')}, at {s['location']}.")
k = pathlib.Path('memory/kept.md')
if k.exists(): print(f"{len(k.read_text().splitlines())} things he has decided are his.")
PY
