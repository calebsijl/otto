#!/usr/bin/env python3
"""Give Otto the working tandem he asked for.

The old one at the top of the lane is gone as far as he is concerned (he
creased the frame at four coins and wrote it off). tandem.py later put a copy of
that same cold, rained-on one back, which is not what he asked for.

This swaps it for a sound one, in the same spot, and tells him it is there.
Run it ON THE SERVER, because deploy.sh never sends world.json:

    ssh root@165.232.137.53 'cd ~/otto && python3 newtandem.py && ./gitsave.sh'

Safe to run twice. Add --dry to see what it would do without writing.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import WORLD, STATE, INBOX, jload, jsave, jappend

DRY = "--dry" in sys.argv
PLACE = "lane_top"
OLD = "the_leaning_thing"
NEW = "tandem_working"

NAME = "the tandem, the one you asked for"
NOTE = ("two rings, one behind the other, held apart by a frame of straight tubes. "
        "two seats along the top and two sets of handles. the rings are true and spin "
        "without a sound, the hubs are packed and the chain is new and oiled. the frame "
        "is steel, red, and about as heavy as two sacks of flour. it stands on its own "
        "stand and it is yours.")


def boxes(world):
    out = []
    for pid, p in world["places"].items():
        if pid == PLACE or not p.get("pos") or not p.get("size"):
            continue
        x, _, z = p["pos"]; w, _, d = p["size"]
        out.append((x - w/2, x + w/2, z - d/2, z + d/2))
    return out


def hits(x, z, hx, hz, bad):
    return any(x + hx > x0 and x - hx < x1 and z + hz > z0 and z - hz < z1
               for x0, x1, z0, z1 in bad)


def spot(world):
    """Across the dead end of the lane if clear, else along a side, else the middle."""
    p = world["places"][PLACE]
    px, _, pz = p["pos"]; pw, _, pd = p["size"]
    bad = boxes(world)
    tries = [(dx, dz, 1.5708, 1.7, 0.5)
             for dz in (-(pd/2 - 1.2), pd/2 - 1.2) for dx in (0.0, 0.8, -0.8)]
    tries += [(dx, dz, 0.0, 0.5, 1.7)
              for dx in (pw/2 - 1.3, -(pw/2 - 1.3))
              for dz in (pd/2 - 2.2, 0.0, -(pd/2 - 2.2))]
    for dx, dz, face, hx, hz in tries:
        if not hits(px + dx, pz + dz, hx, hz, bad):
            return [round(dx, 2), round(dz, 2)], face
    return [0.0, 0.0], 1.5708


w = jload(WORLD); s = jload(STATE)
if PLACE not in w["places"]:
    sys.exit(f"there is no {PLACE} in this world. nothing done.")

objs = w["objects"]
if any(o.get("id") == NEW for o in objs):
    sys.exit("the working tandem is already there. nothing done.")

old = next((o for o in objs if o.get("id") == OLD), None)
at, face = (old["at"], old.get("face", 1.5708)) if old and old.get("at") else spot(w)
if s.get("riding") == OLD:
    s["riding"] = None
if OLD in s.get("carrying", []):
    s["carrying"].remove(OLD)

new = {"id": NEW, "name": NAME, "place": PLACE, "shape": "tandem",
       "tags": ["fixed", "ride", "gift"], "note": NOTE, "from": "caleb",
       "at": at, "face": face}
print("remove:", OLD if old else "(old one not present)")
print("add:   ", NEW, "at", at, "face", face, "in", PLACE)
if DRY:
    sys.exit("dry run, nothing written.")

if old:
    objs.remove(old)
objs.append(new)
jsave(WORLD, w); jsave(STATE, s)
jappend(INBOX, {"t": s["clock"], "read": False,
                "text": "the tandem you asked for is at the top of the lane, against the end wall."})
print("done. he will read it on his next tick.")
