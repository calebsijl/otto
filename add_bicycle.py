#!/usr/bin/env python3
"""Leave something at the end of the lane. He has never seen one and will not be told."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import WORLD, jload, jsave

# Everything he can read is the name, the id and the note. None of them say what it is.
THING = {
 "id": "the_leaning_thing",
 "name": "something leaning against the end wall",
 "place": "lane_top",
 "tags": ["fixed", "strange"],
 "shape": "tandem",          # the renderer reads this. he never sees it.
 "note": ("two rings, taller than you, one behind the other, held apart by a frame of "
          "thin bars. there are two seats along the top, one in front of the other, and "
          "two sets of bent handles. the rings turn when you push them and the whole "
          "thing wants to fall over. it is cold and it has been rained on. you have no "
          "idea what it is, what it is for, or who left it here."),
}

w = jload(WORLD)
if any(o["id"] == THING["id"] for o in w["objects"]):
    print("it is already there.")
else:
    w["objects"].append(dict(THING))
    jsave(WORLD, w)
    print("left at the top of the lane, next to his house.")
print()
print("what he can read about it:")
print(f"  name: {THING['name']}")
print(f"  note: {THING['note'][:70]}...")
print()
print("nothing he is shown contains the word. the renderer knows, he does not.")
