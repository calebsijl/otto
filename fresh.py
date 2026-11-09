#!/usr/bin/env python3
"""Give him a clean head. The world stays exactly as it is; he forgets.

Clears: everything he knows, everything he kept, his notes, his wishes, his
journal, his pages, his messages, his thoughts, the log, and every object he
built. Keeps: all the places, the books on the shelf, everything you sent him,
and anything that came with the world.
"""
import sys, json, shutil, pathlib, argparse, datetime
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import (ROOT, STATE, WORLD, NOTES, KEPT, KNOWS, SEEN, WISHES,
                    INBOX, OUTBOX, LOG, SITE, jload, jsave)

ap = argparse.ArgumentParser()
ap.add_argument("--keep-world-objects", action="store_true",
                help="leave the things he built standing")
ap.add_argument("--dry", action="store_true", help="say what would go, change nothing")
a = ap.parse_args()

mind = [NOTES, KEPT, KNOWS, SEEN, WISHES, INBOX, OUTBOX, LOG,
        ROOT / "thoughts.jsonl", ROOT / "memory" / "bookmarks.json",
        ROOT / "memory" / "aside.json"]
pages = [p for p in SITE.glob("*") if p.is_file()
         and p.name not in ("console.html", "world.html", "otto.glb")]
w = jload(WORLD)
built = [o for o in w["objects"] if o.get("made_by") == "otto"]

print(f"forgetting:  {sum(1 for p in mind if p.exists())} memory files")
print(f"removing:    {len(pages)} pages he wrote"
      + ("".join(f"\n               /{p.name}" for p in pages[:8])))
if not a.keep_world_objects:
    print(f"clearing:    {len(built)} things he built")
print(f"keeping:     {len(w['places'])} places, the books, and "
      f"{sum(1 for o in w['objects'] if o.get('from')=='caleb')} things from you")

if a.dry:
    print("\n--dry, so nothing was changed.")
    raise SystemExit

arch = ROOT / "runs" / f"before-{datetime.datetime.now():%Y%m%d-%H%M}"
arch.mkdir(parents=True, exist_ok=True)
for p in mind:
    if p.exists(): shutil.copy(p, arch / p.name); p.unlink()
for p in pages:
    shutil.copy(p, arch / p.name); p.unlink()
if not a.keep_world_objects:
    w["objects"] = [o for o in w["objects"] if o.get("made_by") != "otto"]
    jsave(WORLD, w)

now = datetime.datetime.now()
s = jload(STATE)
jsave(STATE, {
    "name": s.get("name", "otto"), "species": "hedgehog", "tick": 0,
    "clock": now.isoformat(timespec="seconds"), "real": now.isoformat(timespec="seconds"),
    "asleep": False,
    "needs": {"energy": 0.80, "fullness": 0.60, "warmth": 0.70, "calm": 0.60, "wonder": 0.50},
    "location": "house_main", "carrying": [], "coins": 12,
    "doing": {"verb": "idle", "what": ""}, "weather": "", "mood": "settled"})

print(f"\ndone. the old one is in runs/{arch.name} if you ever want it.")
print(f"he wakes at {now:%H:%M} in his front room knowing nothing, in a world")
print("with a river, an orchard, a shelf of books, and something odd at the top of the lane.")
