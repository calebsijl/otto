#!/usr/bin/env python3
"""Put the thing at the end of the lane into THIS world, and let him get on it.

deploy.sh never pushes world/world.json, on purpose, so anything added to the
world on the mac never reaches the server. This script is safe to run anywhere
and more than once: it creates the object if this world has not got it, adds
the ride tag if it has, and prints what it actually found either way.

Nothing here tells him what it is.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import WORLD, jload, jsave

PLACE = "lane_top"
THING = {
    "id": "the_leaning_thing",
    "name": "something leaning against the end wall",
    "place": PLACE,
    "tags": ["fixed", "strange", "ride"],
    "shape": "tandem",
    "at": [-3.0, -1.0],     # along the left-hand wall, out of the middle of the lane
    "face": 0,              # lying with the lane, not slewed across it
    "note": ("two rings, taller than you, one behind the other, held apart by a frame of "
             "thin bars. there are two seats along the top, one in front of the other, and "
             "two sets of bent handles. the rings turn when you push them and the whole "
             "thing wants to fall over. it is cold and it has been rained on. you have no "
             "idea what it is, what it is for, or who left it here."),
}

w = jload(WORLD)
places = w.get("places", {})
objs = w.setdefault("objects", [])
changed = []

if PLACE not in places:
    print(f"!! there is no {PLACE} in this world. nothing done.")
    print("   places here:", ", ".join(sorted(places))[:300])
    raise SystemExit(1)

o = next((q for q in objs if q.get("id") == THING["id"]), None)

if o is None:
    objs.append(dict(THING))
    o = objs[-1]
    changed.append("created it, this world did not have one")
else:
    tags = o.setdefault("tags", [])
    for t in ("fixed", "strange", "ride"):
        if t not in tags:
            tags.append(t); changed.append(f"added the {t} tag")
    if o.get("shape") != "tandem":
        o["shape"] = "tandem"; changed.append("set its shape")
    if o.get("place") != PLACE:
        changed.append(f"left it where it was, at {o.get('place')}")
    if not isinstance(o.get("at"), list):
        o["at"] = list(THING["at"]); changed.append("moved it out of the middle of the lane")
    if o.get("face") is None:
        o["face"] = 0; changed.append("straightened it")

if changed:
    jsave(WORLD, w)

print("world file:", WORLD)
print()
for c in changed:
    print("  -", c)
if not changed:
    print("  - nothing to change, it was already right")
print()
print("  id:    ", o["id"])
print("  place: ", o.get("place"), " ", places[o.get("place", PLACE)].get("name", ""))
print("  tags:  ", ", ".join(o.get("tags", [])))
print("  shape: ", o.get("shape"), " at:", o.get("at"), " face:", o.get("face"))
print()
print(f"  this world has {len(objs)} objects in {len(places)} places")
mine = [q["id"] for q in objs if q.get("made_by") == "otto"]
print(f"  {len(mine)} of them he made himself" + (": " + ", ".join(mine[-5:]) if mine else ""))
