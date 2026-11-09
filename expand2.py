#!/usr/bin/env python3
"""Second expansion: an orchard, somewhere to eat, and architecture on every building.
Safe on a living world. Run as often as you like."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import WORLD, jload, jsave

PLACES = {
 "orchard": {
   "name": "the orchard", "kind": "earth", "style": "",
   "description": "four old pear trees in a row, further apart than they look from the lane. the ground is soft with fallen fruit and the wasps are busy.",
   "warmth": 0.4, "pos": [-24.0, 0, -32.0], "size": [14, 0, 11],
   "exits": ["yard", "lane_top"]},
 "restaurant": {
   "name": "the eating house", "kind": "shop", "style": "timber",
   "description": "three tables, a counter, and a kitchen you can hear but not see. warm in a way the lane never is. you have to pay.",
   "warmth": 0.85, "pos": [10.8, 0, -1.0], "size": [8, 5.5, 8],
   "exits": ["lane_top"]},
}

OBJECTS = [
 {"id":"pear_tree_a","name":"the first pear tree","place":"orchard","tags":["tree","fixed","pear"],
  "note":"the oldest. leans south. the fruit at the top is always best and always out of reach."},
 {"id":"pear_tree_b","name":"the second pear tree","place":"orchard","tags":["tree","fixed","pear"],
  "note":"straight, and younger. a branch comes low enough to matter."},
 {"id":"pear_tree_c","name":"the third pear tree","place":"orchard","tags":["tree","fixed","pear"],
  "note":"half dead on one side, loaded on the other."},
 {"id":"pear_tree_d","name":"the fourth pear tree","place":"orchard","tags":["tree","fixed","pear"],
  "note":"the one nearest the wall. windfalls collect against it."},
 {"id":"windfalls","name":"fallen pears in the grass","place":"orchard","tags":["food","infinite","forage","sweet"],
  "note":"bruised, warm from the ground, and sweeter than anything in the shop."},
 {"id":"wasps","name":"wasps on the fallen fruit","place":"orchard","tags":["fixed","alive"],
  "note":"busy with their own business. they have not noticed you."},
 {"id":"orchard_wall","name":"the old wall","place":"orchard","tags":["fixed","stone"],
  "note":"brick, mostly. one part has come down and nobody has put it back."},
 {"id":"eh_counter","name":"the counter","place":"restaurant","tags":["fixed"],
  "note":"too high for you by a long way. there is a step someone has left."},
 {"id":"eh_table","name":"a table by the stove","place":"restaurant","tags":["fixed","sit"],
  "note":"the warmest seat in the lane."},
 {"id":"hot_supper","name":"a hot supper","place":"restaurant","tags":["food","shop","infinite","hot"],
  "price":2, "note":"whatever is on. it costs two coins and it is worth it."},
 {"id":"eh_stove","name":"the kitchen stove","place":"restaurant","tags":["warm","fixed"],
  "note":"you cannot see it. you can feel it through the wall."},
]

# architecture, so the lane is not eight identical boxes
STYLES = {
 "house_main":"brick", "house_back":"brick", "shop_general":"shopfront",
 "shop_oddments":"timber", "post_office":"stone", "library":"stone_tall",
 "restaurant":"timber",
}

w = jload(WORLD)
ap = ao = 0
for pid, p in PLACES.items():
    if pid not in w["places"]:
        w["places"][pid] = dict(p); ap += 1
    else:
        w["places"][pid].update({k:v for k,v in p.items() if k != "exits"})
for pid, p in PLACES.items():
    for e in p["exits"]:
        if e in w["places"]:
            if pid not in w["places"][e]["exits"]: w["places"][e]["exits"].append(pid)
            if e not in w["places"][pid]["exits"]: w["places"][pid]["exits"].append(e)
for pid, style in STYLES.items():
    if pid in w["places"]: w["places"][pid]["style"] = style

have = {o["id"] for o in w["objects"]}
for o in OBJECTS:
    if o["id"] not in have:
        w["objects"].append(dict(o)); ao += 1

jsave(WORLD, w)
print(f"added {ap} places, {ao} things.")
print(f"world is now {len(w['places'])} places, {len(w['objects'])} objects.")
print("he can eat pears off the ground for nothing, or pay two coins for a hot supper.")
