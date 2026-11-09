#!/usr/bin/env python3
"""What the eating house is serving. You write it, he eats it.

    ./menu.py                                   show what is on
    ./menu.py "roast parsnips, 2" "apple pie, 1"   set it
    ./menu.py --add "a bowl of soup, 1"         add one dish
"""
import sys, pathlib, argparse, re
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import WORLD, jload, jsave

DEFAULT = ["a plate of buttered potatoes, 2",
           "brown stew with bread, 3",
           "a baked apple with cream, 2"]

ap = argparse.ArgumentParser()
ap.add_argument("dishes", nargs="*", help='each as "name, price"')
ap.add_argument("--add", action="append", default=[])
a = ap.parse_args()

w = jload(WORLD)
on = [o for o in w["objects"] if "menu" in o.get("tags", [])]

if not a.dishes and not a.add:
    if on:
        print("on at the eating house:")
        for o in on:
            print(f"  {o['name']}   {o.get('price', 2)} coins")
    else:
        print("nothing is on. set it with:  ./menu.py \"roast parsnips, 2\"")
    raise SystemExit

if a.dishes:
    w["objects"] = [o for o in w["objects"] if "menu" not in o.get("tags", [])]
    wanted = a.dishes
else:
    wanted = [f"{o['name']}, {o.get('price',2)}" for o in on] + a.add
    w["objects"] = [o for o in w["objects"] if "menu" not in o.get("tags", [])]

for line in wanted or DEFAULT:
    name, _, price = line.rpartition(",")
    name = (name or line).strip()
    try: price = int(price.strip())
    except ValueError: price = 2
    oid = "dish_" + re.sub(r"[^a-z0-9]+", "_", name.lower())[:26].strip("_")
    w["objects"].append({
        "id": oid, "name": name, "place": "restaurant",
        "tags": ["food", "shop", "infinite", "hot", "menu"], "price": price,
        "note": "on today. it comes out hot and they put it down in front of you."})

jsave(WORLD, w)
print("on at the eating house:")
for o in w["objects"]:
    if "menu" in o.get("tags", []):
        print(f"  {o['name']}   {o.get('price',2)} coins")
print("\nhe will find it when he next goes in hungry.")
