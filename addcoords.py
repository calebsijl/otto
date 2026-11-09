#!/usr/bin/env python3
"""Give otto's existing places a position in space, without disturbing anything else.
Safe to run more than once. New places he invents get placed automatically."""
import sys, json, pathlib, math
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import WORLD, jload, jsave

LAYOUT = {
 "house_main": {
  "pos": [
   -9.3,
   0,
   -13.5
  ],
  "size": [
   7,
   3.9,
   7
  ],
  "kind": "indoor"
 },
 "house_back": {
  "pos": [
   -9.3,
   0,
   -24.0
  ],
  "size": [
   6,
   3.1,
   6
  ],
  "kind": "indoor"
 },
 "lane_top": {
  "pos": [
   0.0,
   0,
   -12.0
  ],
  "size": [
   8,
   0,
   14
  ],
  "kind": "street"
 },
 "lane_bottom": {
  "pos": [
   0.0,
   0,
   12.0
  ],
  "size": [
   8,
   0,
   16
  ],
  "kind": "street"
 },
 "shop_general": {
  "pos": [
   10.8,
   0,
   -13.5
  ],
  "size": [
   7,
   4.7,
   7
  ],
  "kind": "shop"
 },
 "shop_oddments": {
  "pos": [
   10.8,
   0,
   6.0
  ],
  "size": [
   7,
   4.7,
   7
  ],
  "kind": "shop"
 },
 "post_office": {
  "pos": [
   10.8,
   0,
   19.5
  ],
  "size": [
   7,
   3.9,
   7
  ],
  "kind": "civic"
 },
 "library": {
  "pos": [
   -10.8,
   0,
   16.5
  ],
  "size": [
   8,
   5.5,
   8
  ],
  "kind": "civic"
 },
 "yard": {
  "pos": [
   -20.2,
   0,
   -19.5
  ],
  "size": [
   9,
   0,
   9
  ],
  "kind": "earth"
 },
 "hedge": {
  "pos": [
   -24.8,
   0,
   -3.0
  ],
  "size": [
   5,
   0,
   18
  ],
  "kind": "hedge"
 },
 "pond": {
  "pos": [
   -26.4,
   0,
   21.0
  ],
  "size": [
   11,
   0,
   11
  ],
  "kind": "water"
 },
 "stream": {
  "pos": [
   -12.4,
   0,
   31.5
  ],
  "size": [
   16,
   0,
   5
  ],
  "kind": "water"
 },
 "far_bank": {
  "pos": [
   -12.4,
   0,
   40.5
  ],
  "size": [
   9,
   0,
   6
  ],
  "kind": "earth"
 }
}

for path in (WORLD, WORLD.parent / "seed.json"):
    if not path.exists():
        continue
    w = jload(path)
    extra = 0
    for pid, place in w["places"].items():
        if pid in LAYOUT:
            place.update(LAYOUT[pid])
        elif "pos" not in place:
            # somewhere he made himself: put it out past the known lane
            a = (abs(hash(pid)) % 360) * math.pi / 180
            place["pos"]  = [round(math.cos(a)*22, 1), 0, round(math.sin(a)*22, 1)]
            place["size"] = [6, 4, 6]
            place["kind"] = "indoor"
            extra += 1
    jsave(path, w)
    print(f"{path.name}: {len(w['places'])} places positioned"
          + (f", {extra} of them his own" if extra else ""))
print("done. nothing else in the file was touched.")
