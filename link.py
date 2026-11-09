#!/usr/bin/env python3
"""A gate between the yard and the orchard.

The orchard already had a way into the yard, but the yard had no way back into
the orchard: the only one-way link in the whole world, and selftest has been
failing on it. Standing in his own yard he had to go in through the back door,
through the front room, up the lane and in from the top.

Safe to run more than once. Run it on the server, because deploy.sh never
sends world/world.json.
"""
import json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
WP = HERE / "world" / "world.json"
w = json.loads(WP.read_text())
places = w["places"]

changed = []
for a, b in (("yard", "orchard"),):
    if a not in places or b not in places:
        print(f"  {a} or {b} is not in this world; nothing to do")
        continue
    ex = places[a].setdefault("exits", [])
    if b in ex:
        print(f"  {a} already opens onto {b}")
    else:
        ex.append(b)
        changed.append(f"{a} -> {b}")

# say it is a gate, so he can find out it is one rather than being told
note = "a gate in the hedge, into the orchard."
yard = places.get("yard", {})
if changed and note not in (yard.get("description") or ""):
    yard["description"] = ((yard.get("description") or "").rstrip() + " " + note).strip()

if changed:
    WP.write_text(json.dumps(w, indent=1))
    print("  opened: " + ", ".join(changed))
else:
    print("  nothing to change")

# prove it: no one-way links left anywhere
oneway = [(a, b) for a, v in places.items() for b in v.get("exits", [])
          if b in places and a not in places[b].get("exits", [])]
print(f"  one-way links left in the world: {len(oneway)}")
for a, b in oneway:
    print(f"    {a} -> {b}")
sys.exit(1 if oneway else 0)
