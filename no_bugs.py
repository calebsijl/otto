#!/usr/bin/env python3
"""He does not eat insects. Takes them out and leaves the proper food."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import WORLD, jload, jsave
BUGS = {"beetles", "worms", "snails_bank", "wasps"}
w = jload(WORLD)
gone = [o["name"] for o in w["objects"] if o["id"] in BUGS]
w["objects"] = [o for o in w["objects"] if o["id"] not in BUGS]
# the leaf pile stays, it is just not lunch any more
for o in w["objects"]:
    if o["id"] == "leaf_pile":
        o["tags"] = [t for t in o["tags"] if t not in ("food", "forage")]
jsave(WORLD, w)
print("removed:", ", ".join(gone) if gone else "nothing, already done")
print("he eats off the menu, out of the shop, or off the orchard floor now.")
