#!/usr/bin/env python3
"""Bring home anything that got put somewhere that is not a place.

edit_world took its "to" on trust, so a thing moved to a name that was not a
place stayed in the file and vanished from the world: not rendered, not listed,
not reachable. tools.py now refuses that. This finds the ones already lost and
puts them back where they were sent from, or in his front room.

Safe to run more than once.
"""
import json, pathlib

HERE = pathlib.Path(__file__).resolve().parent
WP = HERE / "world" / "world.json"
w = json.loads(WP.read_text())
OK = set(w["places"]) | {"_carried", "_box", "_gone"}

HOME = {"shelf_library": "library", "shelf": "library",
        "workshop": "house_main", "shed": "yard"}

moved = []
for o in w["objects"]:
    pl = o.get("place")
    if pl in OK:
        continue
    to = HOME.get(pl, "house_main")
    o["place"] = to
    moved.append(f"{o.get('name', o['id'])}: {pl} -> {to}")

if moved:
    WP.write_text(json.dumps(w, indent=1))
    print("  brought home:")
    for m in moved:
        print("    " + m)
else:
    print("  nothing was lost.")
