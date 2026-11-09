"""Stand the station up in the world.

town.py put the place there. This gives it the builder that draws the
platform, the canopy, the building and the line running left to right, and
points the engine, the clock, the bench and two lamps at their geometry.

Idempotent.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import WORLD, jload, jsave

HALF_PI = 1.5708

w = jload(WORLD)
P, O = w["places"], w["objects"]
st = P.get("station")
if not st:
    print("there is no station. run town.py first.")
    sys.exit(1)

st["kind"] = "earth"        # the builder draws it; it must not also be a block
st["build"] = "station"
st["size"] = [22, 6, 13]    # deep enough for the line, the platform and the building
st.pop("style", None)

def o(id, name, at, shape, face, tags, note, **kw):
    d = dict(id=id, name=name, place="station", at=at, shape=shape, face=face,
             tags=tags, note=note)
    d.update(kw); return d

WANT = {
 "dead_train": o("dead_train", "the engine", [6.0, 4.0], "deadtrain", 0,
   ["fixed"],
   "black, and taller than the church door, standing at the platform with its "
   "tender and two carriages behind it. cold all the way through. the stack is "
   "split open and something is nesting in it, a wheel is off and lying in the "
   "ballast, and the last carriage has gone into the ground up to its windows. "
   "there is grass growing between the rails underneath it, which tells you "
   "how long it has been since anybody needed it to go anywhere.",
   solid=True),
 "stopped_clock": o("stopped_clock", "the station clock", [-7.0, 1.3],
   "stationclock", -HALF_PI, ["fixed"],
   "on a bracket at the platform edge, with the hands at twenty past four. it "
   "is wrong twice a day and right twice a day and nobody has wound it either "
   "way."),
 "platform_bench": o("platform_bench", "a bench on the platform", [-2.0, -0.8],
   "bench", -HALF_PI, ["sit", "fixed"],
   "cast ends and wooden slats, facing the empty rails. somebody sat here a "
   "long time ago waiting for this."),
 "station_lamp_a": o("station_lamp_a", "a lamp on the platform", [3.0, -0.9],
   "lamppost", 0, ["fixed", "warm"],
   "the same cast post as the ones down on the river walk, and it still comes "
   "up at dusk, over a platform nobody stands on."),
 "station_lamp_b": o("station_lamp_b", "a lamp on the platform", [-9.0, -0.9],
   "lamppost", 0, ["fixed", "warm"],
   "the far one. between the two of them the platform is lit all night for "
   "nobody at all."),
}

O[:] = [x for x in O if x["id"] not in WANT]
O.extend(WANT.values())
jsave(WORLD, w)

print(f"the station: {st['size'][0]} by {st['size'][2]}, builder '{st['build']}'")
for k, v in WANT.items():
    print(f"   {v['shape']:13} {v['name']}")
