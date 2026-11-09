#!/usr/bin/env python3
"""Add the outdoors to otto's world. Safe on a living world; run as often as you like."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import WORLD, jload, jsave

PLACES = {
 "yard": {
   "name": "the yard behind his house", "kind": "earth",
   "description": "soil, a leaf pile he has been adding to, and the back wall of his own house. his, in a way the lane is not.",
   "warmth": 0.4, "pos": [-20.2, 0, -19.5], "size": [9, 0, 9],
   "exits": ["house_back", "hedge"]},
 "hedge": {
   "name": "under the hedge", "kind": "hedge",
   "description": "a low green tunnel running the length of the gardens. dark, dry, full of small noises. nothing bigger than him can get in here.",
   "warmth": 0.55, "pos": [-24.8, 0, -3.0], "size": [5, 0, 18],
   "exits": ["yard", "pond"]},
 "pond": {
   "name": "the pond", "kind": "water",
   "description": "bigger than it looks from the bank. reeds at one end, a flat stone at the other, and the whole sky lying on it.",
   "warmth": 0.25, "pos": [-26.4, 0, 21.0], "size": [11, 0, 11],
   "exits": ["hedge", "stream"]},
 "stream": {
   "name": "the stream", "kind": "water",
   "description": "it leaves the pond and goes under the lane. about two of him wide, moving fast, and nowhere to cross.",
   "warmth": 0.25, "pos": [-12.4, 0, 31.5], "size": [16, 0, 5],
   "exits": ["pond", "lane_bottom"]},
 "far_bank": {
   "name": "the far bank", "kind": "earth",
   "description": "the other side of the stream. you have looked at it a great many times. you have never been on it.",
   "warmth": 0.35, "pos": [-12.4, 0, 40.5], "size": [9, 0, 6],
   "exits": ["stream"]},
}

OBJECTS = [
 {"id":"leaf_pile","name":"a pile of leaves","place":"yard","tags":["soft","nest","gather"],
  "note":"dry at the bottom, damp on top. good for a nest if he wanted one."},
 {"id":"flowerpot","name":"a cracked flowerpot on its side","place":"yard","tags":["shelter","fixed"],
  "note":"the crack goes most of the way round."},
 {"id":"twigs","name":"a scatter of twigs","place":"yard","tags":["material","gather"],
  "note":"different thicknesses. some snap, some bend."},
 {"id":"beetles","name":"beetles under the leaf pile","place":"yard","tags":["food","infinite","forage"],
  "note":"you can hear them before you see them."},
 {"id":"hedge_roots","name":"the hedge roots","place":"hedge","tags":["fixed","shelter"],
  "note":"woven together over years into something like a low roof."},
 {"id":"snail_shells","name":"old snail shells","place":"hedge","tags":["material","gather"],
  "note":"empty. curved, light, surprisingly stiff."},
 {"id":"worms","name":"worms in the soft ground","place":"hedge","tags":["food","infinite","forage"],
  "note":""},
 {"id":"reeds","name":"reeds at the pond edge","place":"pond","tags":["material","gather","fixed"],
  "note":"hollow all the way down, and straight."},
 {"id":"flat_stone","name":"a flat stone at the water's edge","place":"pond","tags":["sit","fixed","warm_in_sun"],
  "note":"holds the day's heat longer than anything else here."},
 {"id":"pond_water","name":"the water","place":"pond","tags":["water","fixed","swim"],
  "note":"cold at the edge, colder further out. you can swim, it turns out."},
 {"id":"the_gap","name":"the gap the stream makes","place":"stream","tags":["fixed","gap"],
  "note":"about two of him across. nothing spans it. you have measured it with your eye a hundred times."},
 {"id":"stream_water","name":"the running water","place":"stream","tags":["water","fixed"],
  "note":"faster than the pond. it does not stop."},
 {"id":"bank_stones","name":"loose stones on the bank","place":"stream","tags":["material","gather"],
  "note":"flat ones, round ones, one almost square."},
 {"id":"unknown_plant","name":"a plant you do not know","place":"far_bank","tags":["fixed"],
  "note":"you have only ever seen it from the other side."},
]

w = jload(WORLD)
added_p = added_o = 0
for pid, p in PLACES.items():
    if pid not in w["places"]:
        w["places"][pid] = dict(p); added_p += 1
    else:
        w["places"][pid].update({k: v for k, v in p.items() if k != "exits"})
# wire the new places into the old ones, both directions
link = {"house_back": "yard", "lane_bottom": "stream"}
for a, b in link.items():
    if a in w["places"] and b not in w["places"][a]["exits"]:
        w["places"][a]["exits"].append(b)
for pid, p in PLACES.items():
    for e in p["exits"]:
        if e in w["places"] and pid not in w["places"][e]["exits"]:
            w["places"][e]["exits"].append(pid)

have = {o["id"] for o in w["objects"]}
for o in OBJECTS:
    if o["id"] not in have:
        w["objects"].append(dict(o)); added_o += 1

jsave(WORLD, w)
print(f"added {added_p} places and {added_o} things.")
print(f"the world is now {len(w['places'])} places and {len(w['objects'])} objects.")
print("there is a stream with a gap in it that nothing spans.")
