"""Take the new quarters' goods off sale, and put a letter on the honesty box.

The town and the wharf opened with a dozen things he could buy, which is more
than the lane has and more than he has coins for. They stay on the shelves as
things he can look at and want; he just cannot carry them off yet. The old
village stock and all the food are untouched.

Idempotent.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import WORLD, jload, jsave

OFF = {"nails_tray", "iron_wire", "gear_tray", "mainspring", "battens",
       "pitch_tub", "glass_panes", "paper_ream", "ink_tin",
       "tin_whistle", "strings_card"}

BEHIND = ("it is behind the counter, and nobody has said a price. you could "
          "stand and look at it for a while, which is what you do.")

w = jload(WORLD)
O = w["objects"]

took = []
for o in O:
    if o["id"] in OFF and "shop" in o.get("tags", []):
        o["tags"] = [t for t in o["tags"] if t not in ("shop", "infinite")]
        if "fixed" not in o["tags"]:
            o["tags"].append("fixed")
        o.pop("price", None)
        o["note"] = o.get("note", "").rstrip() + " " + BEHIND
        took.append(o["name"])

LETTER = {
 "id": "box_letter",
 "name": "a letter on top of the box",
 "place": "lane_bottom",
 "at": [1.4, -2.2],
 "face": 0,
 "tags": ["fixed"],
 "note": (
   "one sheet, weighted down with a stone, in a hand that slopes. it says: "
   "THIS BOX IS HOW IT WORKS HERE. put a thing you have made through the slot "
   "and leave it. do not wait about. somebody will want it, and somebody will "
   "leave what they think it was worth, and that is what you will find in the "
   "bottom next time you look. a thing that actually works is worth more than "
   "a thing that only looks like it. nobody checks and nobody is watching. "
   "it has gone on like this for longer than anyone remembers.")
}
O[:] = [o for o in O if o["id"] != LETTER["id"]]
O.append(LETTER)

jsave(WORLD, w)
print(f"off sale ({len(took)}): " + ", ".join(took))
print("still buyable: the lane's own stock, and all the food")
print("added: a letter on top of the honesty box, at the bottom of the lane")
