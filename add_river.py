#!/usr/bin/env python3
"""A river running behind the houses. Safe on a living world."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import WORLD, jload, jsave

PLACES = {
 "river": {
   "name": "the river", "kind": "water",
   "description": "it runs the whole length of the back of the houses and keeps going both ways. wider than the stream and slower. the shallow end at the top is barely over your head and the bottom end is not.",
   "warmth": 0.25, "pos": [30.0, 0, 2.0], "size": [9, 0, 54],
   "exits": ["river_bank"]},
 "river_bank": {
   "name": "the back bank", "kind": "earth",
   "description": "the strip of rough grass between the backs of the shops and the water. nobody comes here. it is the best place in the lane and you found it yourself.",
   "warmth": 0.4, "pos": [21.5, 0, 2.0], "size": [7, 0, 50],
   "exits": ["river", "lane_top", "lane_bottom"]},
}

OBJECTS = [
 {"id":"shallows","name":"the shallows at the top end","place":"river",
  "tags":["water","swim","fixed","shallow","play"],
  "note":"gravel underfoot and the water moving over it. you can stand up in this bit."},
 {"id":"deep_pool","name":"the deep pool","place":"river","tags":["water","swim","fixed","deep"],
  "note":"dark green and you cannot see the bottom. you have not been in this bit."},
 {"id":"stepping_stones","name":"four stepping stones","place":"river","tags":["fixed","stone","cross"],
  "note":"someone put them here a long time ago. the third one is missing and the gap is too wide."},
 {"id":"river_reeds","name":"a bed of reeds","place":"river","tags":["material","gather","fixed"],
  "note":"taller than the pond ones and hollow all the way down."},
 {"id":"driftwood","name":"driftwood caught on the bend","place":"river_bank","tags":["material","gather"],
  "note":"smooth, light, and already the right sort of shape for things."},
 {"id":"back_wall","name":"the backs of the shops","place":"river_bank","tags":["fixed"],
  "note":"nobody paints this side. there is a drainpipe you could climb if you were braver."},
 {"id":"rough_grass","name":"rough grass","place":"river_bank","tags":["fixed","soft"],
  "note":"long enough to disappear in."},
 {"id":"snails_bank","name":"snails on the wet stones","place":"river_bank",
  "tags":["food","infinite","forage"], "note":""},
]

w = jload(WORLD); ap = ao = 0
for pid, p in PLACES.items():
    if pid not in w["places"]: w["places"][pid] = dict(p); ap += 1
    else: w["places"][pid].update({k:v for k,v in p.items() if k != "exits"})
for pid, p in PLACES.items():
    for e in p["exits"]:
        if e in w["places"]:
            if pid not in w["places"][e]["exits"]: w["places"][e]["exits"].append(pid)
            if e not in w["places"][pid]["exits"]: w["places"][pid]["exits"].append(e)
if "stream" in w["places"] and "river" not in w["places"]["stream"]["exits"]:
    w["places"]["stream"]["exits"].append("river")
    w["places"]["river"]["exits"].append("stream")

have = {o["id"] for o in w["objects"]}
for o in OBJECTS:
    if o["id"] not in have: w["objects"].append(dict(o)); ao += 1
jsave(WORLD, w)
print(f"added {ap} places, {ao} things. world is {len(w['places'])} places, {len(w['objects'])} objects.")
print("there is a river behind the houses with a shallow end he can stand up in,")
print("a deep end he has not been in, and stepping stones with the third one missing.")
