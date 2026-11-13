#!/usr/bin/env python3
"""Put the thing at the end of the lane into THIS world, and let him get on it.

deploy.sh never pushes world/world.json, so anything added on the mac never
reaches the server. Safe to run anywhere, and safe to run twice.

It picks the spot by looking at what else is standing there. The first version
of this script dropped it at x -3, z -9, which is inside house_main, so it was
rendered behind his own front wall where nothing could see it.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import WORLD, jload, jsave

PLACE = "lane_top"
LONG  = 3.4          # how long the machine is, end to end, plus a little

NOTE = ("two rings, taller than you, one behind the other, held apart by a frame of "
        "thin bars. there are two seats along the top, one in front of the other, and "
        "two sets of bent handles. the rings turn when you push them and the whole "
        "thing wants to fall over. it is cold and it has been rained on. you have no "
        "idea what it is, what it is for, or who left it here.")


def boxes(world, skip):
    """Every other place's footprint, as (x0, x1, z0, z1)."""
    out = []
    for pid, p in world["places"].items():
        if pid == skip or not p.get("pos") or not p.get("size"):
            continue
        x, _, z = p["pos"]; w, _, d = p["size"]
        out.append((pid, x - w/2, x + w/2, z - d/2, z + d/2))
    return out


def clear(x, z, half_x, half_z, bad):
    for pid, x0, x1, z0, z1 in bad:
        if x + half_x > x0 and x - half_x < x1 and z + half_z > z0 and z - half_z < z1:
            return pid
    return None


def pick(world):
    """A spot inside the lane, out of the middle of it, and inside nothing else."""
    p = world["places"][PLACE]
    px, _, pz = p["pos"]; pw, _, pd = p["size"]
    bad = boxes(world, PLACE)
    best = None
    # lying across the far end of the lane first, then along either side
    tries = []
    for dz in (-(pd/2 - 1.2), pd/2 - 1.2):   # the dead end first, which is the end wall
        for dx in (0.0, 0.8, -0.8):
            tries.append((dx, dz, 1.5708, LONG/2, 0.5))      # across
    for dx in (pw/2 - 1.3, -(pw/2 - 1.3)):
        for dz in (pd/2 - 2.2, 0.0, -(pd/2 - 2.2)):
            tries.append((dx, dz, 0.0, 0.5, LONG/2))         # along
    for dx, dz, face, hx, hz in tries:
        x, z = px + dx, pz + dz
        hit = clear(x, z, hx, hz, bad)
        if hit is None:
            return [round(dx, 2), round(dz, 2)], face, None
        if best is None:
            best = hit
    return [0.0, 0.0], 1.5708, best


w = jload(WORLD)
places = w.get("places", {})
objs = w.setdefault("objects", [])

if PLACE not in places:
    print(f"!! there is no {PLACE} in this world. nothing done.")
    raise SystemExit(1)

at, face, trouble = pick(w)
if trouble:
    print(f"!! could not find a clear spot in {PLACE}, everything collided with {trouble}.")
    print("   putting it in the middle anyway so at least it is visible.")

o = next((q for q in objs if q.get("id") == "the_leaning_thing"), None)
made = o is None
if made:
    o = {"id": "the_leaning_thing", "name": "something leaning against the end wall",
         "place": PLACE, "shape": "tandem", "note": NOTE, "tags": []}
    objs.append(o)

tags = o.setdefault("tags", [])
for t in ("fixed", "strange", "ride"):
    if t not in tags:
        tags.append(t)
o["shape"] = "tandem"
o["at"] = at
o["face"] = face
jsave(WORLD, w)

p = places[PLACE]
px, _, pz = p["pos"]
print("world file:", WORLD)
print("created it" if made else "it was already here")
print()
print("  place: ", o["place"], "  centred at", p["pos"], "size", p["size"])
print("  at:    ", at, "  which is x %.1f, z %.1f in the world" % (px + at[0], pz + at[1]))
print("  face:  ", round(face, 4), "(across the lane)" if face else "(along the lane)")
print("  tags:  ", ", ".join(tags))
print()
print("  nothing else stands on that spot. nearest places:")
for pid, x0, x1, z0, z1 in sorted(
        boxes(w, PLACE),
        key=lambda b: abs((b[1]+b[2])/2 - (px+at[0])) + abs((b[3]+b[4])/2 - (pz+at[1])))[:3]:
    print("    %-14s x %.1f..%.1f  z %.1f..%.1f" % (pid, x0, x1, z0, z1))
