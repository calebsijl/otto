#!/usr/bin/env python3
"""Make his house a house: a kitchen, a bigger bedroom, a washroom behind it.

Safe to run twice. Nothing he has made or been given is touched, and nothing
here tells him what anything is for.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import WORLD, jload, jsave

PLACES = {
 "kitchen": {
   "name": "the kitchen", "pos": [-15.8, 0, -12.5], "size": [6, 3.9, 5],
   "kind": "indoor", "style": "brick", "warmth": 0.72, "building": "home",
   "label": "the kitchen", "exits": ["house_main"],
   "description": ("narrow, warmer than the front room when the slab is going, and it smells "
                   "of whatever was last on it. one small window, high up."),
 },
 "washroom": {
   "name": "the washroom", "pos": [-9.3, 0, -26.5], "size": [5, 3.9, 5],
   "kind": "indoor", "style": "brick", "warmth": 0.30, "building": "home",
   "label": "the washroom", "exits": ["house_back"],
   "description": ("the cold end of the house. stone underfoot, a drip you cannot find, and "
                   "the wall at the far end has something flat and shining set into it."),
 },
}

# the bedroom grows and shuffles up so it meets the front room wall to wall
BEDROOM = {"pos": [-9.3, 0, -20.5], "size": [7, 3.9, 7], "building": "home"}

JOINS = {"house_main": ["kitchen"], "house_back": ["washroom"]}

THINGS = [
 {"id": "cooking_slab", "place": "kitchen", "name": "a flat iron slab over a firebox",
  "tags": ["surface", "fixed", "hob"], "shape": "slab",
  "note": ("black, heavy, and cold most of the time. there is a hatch underneath for "
           "wood. it takes a long while to come up to heat and a long while to lose it.")},
 {"id": "stone_sink", "place": "kitchen", "name": "a shallow stone sink",
  "tags": ["fixed", "water"],
  "note": ("worn into a dip in the middle. the tap above it is stiff and the water comes "
           "in coughs, very cold.")},
 {"id": "jar_shelf", "place": "kitchen", "name": "a shelf of jars",
  "tags": ["surface", "fixed"],
  "note": ("most of them are empty and clean. two or three have something in that you have "
           "not opened. the lids are on tight.")},
 {"id": "pan", "place": "kitchen", "name": "one heavy pan on a hook",
  "tags": ["tool", "cook", "gather"],
  "note": "bigger than your head. the handle is long enough that you can use both paws."},
 {"id": "nightstand", "place": "house_back", "name": "the nightstand",
  "tags": ["surface", "fixed", "nightstand"],
  "note": ("just big enough for whatever you are still thinking about when you lie down. "
           "there is a ring on it from something wet.")},
 {"id": "tin_bath", "place": "washroom", "name": "a tin bath much too big for you",
  "tags": ["fixed", "wash"], "shape": "bath",
  "note": ("you could lie down in it twice over. it rings when you knock it. filling it "
           "would take a great many jugs.")},
 {"id": "jug", "place": "washroom", "name": "a white jug with a chip out of the lip",
  "tags": ["tool", "water", "gather"],
  "note": "heavier than it looks when it is full."},
 {"id": "the_glass", "place": "washroom", "name": "something flat set into the wall",
  "tags": ["fixed", "strange"], "shape": "glass",
  "note": ("cold, flat, and held in a wooden frame. there is another washroom in it, the "
           "same as this one but turned the wrong way round, and when you move, something "
           "small and dark and spiked moves in there too, at exactly the same moment. it "
           "will not do anything you do not do first.")},
]

w = jload(WORLD)
added = []

for pid, spec in PLACES.items():
    if pid in w["places"]:
        w["places"][pid].update({k: v for k, v in spec.items() if k != "exits"})
    else:
        w["places"][pid] = dict(spec); added.append(pid)

w["places"]["house_back"].update(BEDROOM)
w["places"]["house_main"]["building"] = "home"
w["places"]["house_main"]["size"] = [7, 3.9, 7]
w["places"]["house_back"]["description"] = (
    "where he sleeps. bigger than it was, with the bed under the cold wall, a shelf, "
    "and a shutter on the window that has never quite closed.")

for a, bs in JOINS.items():                      # exits both ways, no duplicates
    for b in bs:
        for x, y in ((a, b), (b, a)):
            ex = w["places"][x].setdefault("exits", [])
            if y not in ex: ex.append(y)

by_id = {o["id"]: o for o in w["objects"]}
for t in THINGS:
    if t["id"] in by_id:
        # keep anything he has done to it (moved, painted, carried), refresh the rest
        o = by_id[t["id"]]
        for k, v in t.items():
            if k != "place": o[k] = v
    else:
        w["objects"].append(dict(t)); added.append(t["id"])

jsave(WORLD, w)
print("added:", ", ".join(added) if added else "nothing, it was all there already")
for pid in ("house_main", "kitchen", "house_back", "washroom"):
    p = w["places"][pid]
    print(f"  {pid:11} {str(p['pos']):18} {str(p['size']):14} -> {', '.join(p['exits'])}")
