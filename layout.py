#!/usr/bin/env python3
"""Put the furniture where the plan says, and give it a real model.

`at` is an offset from the middle of the room, `face` is which way it looks in
radians (0 looks south, down the +z axis), `shape` picks the model. Anything
without an `at` still finds its own spot round the edge of the room, which is
what you want for whatever he drops or is sent.
"""
import sys, pathlib, math
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import WORLD, jload, jsave

LAYOUT = {
  # the front room
  "stove":     {"at": [-2.22, -2.70], "face": 0.0,    "shape": "range",
                "name": "the range",
                "note": ("long, black and heavier than the house. two plates on the hot end, "
                         "three doors, and a fire you can see through a little window in the "
                         "middle one. the flue goes straight up through the ceiling. it is the "
                         "best thing you own.")},
  "table":     {"at": [ 2.69, -2.20], "face": -math.pi/2, "shape": "worktable",
                "name": "a work table",
                "note": "plank top, one drawer, and scored all over from things you have done on it."},
  "armchair":  {"at": [ 1.70,  2.45], "face": -2.496, "shape": "rushchair",
                "name": "a chair with a woven seat",
                "note": ("turned legs, four spindles up the back and a curved top rail worn pale "
                         "where you lean on it. the seat is woven out of reed in four triangles "
                         "that meet in the middle. it creaks and holds.")},
}

w = jload(WORLD)
by_id = {o["id"]: o for o in w["objects"]}
done = []
for oid, spec in LAYOUT.items():
    o = by_id.get(oid)
    if not o:
        print(f"  ! {oid} is not in the world"); continue
    o.update(spec); done.append(oid)
jsave(WORLD, w)
print("placed:", ", ".join(done))
for oid in done:
    o = by_id[oid]
    print(f"  {oid:10} {o['name'][:34]:36} at {o['at']}  face {round(o['face'],2)}")
