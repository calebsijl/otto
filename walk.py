"""Make the back bank into the river walk properly.

The migration already renamed it and put the furniture there. This gives the
place a paved surface and kerbs (kind street, which is also cheaper to walk
on), points each piece of furniture at its new geometry, and spaces the lamps
and benches down the fifty-odd paces of it rather than bunching them.

Idempotent.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import WORLD, jload, jsave

w = jload(WORLD)
P, O = w["places"], w["objects"]
rb = P.get("river_bank")
if not rb:
    print("there is no river bank. run town.py first.")
    sys.exit(1)

rb["kind"] = "street"          # paved, with kerbs, and quicker underfoot
rb["paving"] = "flag"          # slabs laid end to end, not brick
rb["warmth"] = 0.4

def o(id, name, at, shape, tags, note):
    # face 0 points at +x, which on this stretch is the water. without it the
    # renderer turns every loose thing 1.2 radians as a default, which had the
    # benches looking across the path and the beds lying over it.
    return dict(id=id, name=name, place="river_bank", at=at, shape=shape,
                face=0, tags=tags, note=note)

LAMP = ("a lamp post", ["fixed", "warm"],
        "a cast post with a glass case on top of it. at dusk something in it "
        "comes up slowly the colour of an ember, and then the water has one of "
        "these in it too, wobbling.")
BENCH = ("a bench facing the water", ["sit", "fixed"],
         "iron ends and wooden slats, set back off the path so your feet do "
         "not get walked over. it faces the river and nothing else.")

WANT = {}
for i, z in enumerate([-19, -7, 6, 18]):
    WANT[f"walk_lamp_{i}"] = o(f"walk_lamp_{i}", LAMP[0], [1.5, z], "lamppost",
                               LAMP[1], LAMP[2])
for i, z in enumerate([-13, 0, 12]):
    WANT[f"walk_bench_{i}"] = o(f"walk_bench_{i}", BENCH[0], [-1.5, z], "bench",
                                BENCH[1], BENCH[2])
for i, z in enumerate([-21, 15]):
    WANT[f"walk_bed_{i}"] = o(f"walk_bed_{i}", "a planted bed", [-2.4, z], "bed",
                              ["fixed", "gather"],
                              "a long bed cut into the grass on the path side, "
                              "planted in rows and weeded by somebody who has "
                              "not given up. there is something out in every "
                              "month of the year, which cannot be an accident.")

GONE = {"walk_lamp_a", "walk_lamp_b", "walk_bench_a", "walk_bench_b", "flower_beds"}
before = len(O)
O[:] = [x for x in O if x["id"] not in GONE and x["id"] not in WANT]
have = {x["id"] for x in O}
O.extend(WANT.values())

# three things were here when it was still the back bank. the made path has
# replaced the rough grass; the rest still fit, they just want a spot.
for x in O:
    if x["id"] == "rough_grass":
        x["name"] = "the verge"
        x["at"] = [-3.0, 4.0]
        x["note"] = ("the strip of grass between the path and the backs of the "
                     "shops, mown but not fussed over. this is where the path "
                     "stops being a path.")
    if x["id"] == "driftwood":  x["at"] = [3.0, -16.0]
    if x["id"] == "back_wall":  x["at"] = [-3.2, -9.0]

# the two that were moved off the stream want spacing, not the same spot
for x in O:
    if x["id"] == "reeds":        x["place"], x["at"] = "river_bank", [2.6, -3.0]
    if x["id"] == "flat_stone":   x["place"], x["at"] = "river_bank", [2.4, 9.0]

jsave(WORLD, w)
print(f"the river walk: {rb['kind']}, {len(WANT)} pieces of furniture "
      f"({sum(1 for k in WANT if 'lamp' in k)} lamps, "
      f"{sum(1 for k in WANT if 'bench' in k)} benches, "
      f"{sum(1 for k in WANT if 'bed' in k)} beds)")
print(f"things in the world: {before} -> {len(O)}")
