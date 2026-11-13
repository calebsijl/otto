#!/usr/bin/env python3
"""Give him a clean head. The world stays exactly as it is; he forgets.

Clears: everything he knows, everything he kept, his notes, his wishes, his
journal, his pages, his messages, his thoughts, the log, the letters between
him and caleb, every object he built, and everything caleb ever sent him.
Keeps: all the places, the books on the shelf, and whatever came with the
world in the first place.
"""
import sys, json, shutil, pathlib, argparse, datetime
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import (ROOT, STATE, WORLD, NOTES, KEPT, KNOWS, SEEN, WISHES,
                    INBOX, OUTBOX, LOG, SITE, TALK, jload, jsave)

ap = argparse.ArgumentParser()
ap.add_argument("--keep-world-objects", action="store_true",
                help="leave the things he built standing")
ap.add_argument("--dry", action="store_true", help="say what would go, change nothing")
a = ap.parse_args()

mind = [NOTES, KEPT, KNOWS, SEEN, WISHES, INBOX, OUTBOX, LOG, TALK,
        ROOT / "thoughts.jsonl", ROOT / "memory" / "bookmarks.json",
        ROOT / "memory" / "aside.json"]
# The site folder holds two different kinds of thing: the pages he writes,
# which are the point of this wipe, and the machinery that renders his world,
# which is emphatically not. look.js is the whole look pass; deleting it once
# before left the world rendering raw with no obvious cause. Anything that is
# not a page he could have written stays.
KEEP = {"console.html", "world.html", "otto.glb", "look.js"}
def his(p):
    if p.name in KEEP: return False
    if p.suffix in (".bak", ".bak2") or ".bak" in p.name: return False
    if p.suffix == ".js": return False          # machinery, not writing
    return True
pages = [p for p in SITE.glob("*") if p.is_file() and his(p)]
w = jload(WORLD)
built = [o for o in w["objects"] if o.get("made_by") == "otto"]
sent  = [o for o in w["objects"] if o.get("from") == "caleb"]

print(f"forgetting:  {sum(1 for p in mind if p.exists())} memory files")
print(f"removing:    {len(pages)} pages he wrote"
      + ("".join(f"\n               /{p.name}" for p in pages[:8])))
if not a.keep_world_objects:
    print(f"clearing:    {len(built)} things he built")
print(f"clearing:    {len(sent)} things you sent him")
print(f"keeping:     {len(w['places'])} places and the books. nothing else.")

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
    # everything he made, and everything you ever posted him. a clean head in
    # a world with nothing of the old life left lying about in it.
    w["objects"] = [o for o in w["objects"]
                    if o.get("made_by") != "otto" and o.get("from") != "caleb"]
    jsave(WORLD, w)

# He wakes carrying nothing, so anything still marked as carried would sit in
# a pocket that no longer exists. Put it back in the post office, where he can
# find it again.
back = [o for o in w["objects"] if o.get("place") == "_carried"]
for o in back:
    o["place"] = "post_office"
if back:
    jsave(WORLD, w)
    print(f"put back:    {len(back)} thing(s) he was carrying, now at the post office")

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
