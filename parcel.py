#!/usr/bin/env python3
"""Send otto a thing. It turns up at the post office.

  ./parcel.py a small brass telescope
  ./parcel.py --paint teal      a heavy can with a nozzle on the top
  ./parcel.py --paint "#2f5d7c" a tin and a stiff brush

With --paint the thing paints in that colour and runs out after a few goes.
Whatever you call it is all he is told: he has to work out how it works.
"""
import sys, re, pathlib, argparse
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import jload, jsave, jappend, WORLD, STATE, INBOX

ap = argparse.ArgumentParser(add_help=True)
ap.add_argument("--paint", metavar="COLOUR", help="it paints, in this colour")
ap.add_argument("--goes", type=int, default=6, help="how many goes before it is empty")
ap.add_argument("--note", default="came in the post.", help="what he reads if he looks at it")
ap.add_argument("words", nargs="*", help="what it is called")
a = ap.parse_args()

name = " ".join(a.words).strip()
if not name:
    sys.exit("usage: ./parcel.py a small brass telescope")

w = jload(WORLD); s = jload(STATE)
oid = re.sub(r"[^a-z0-9]+", "_", name.lower())[:28] + f"_{s['tick']}"
thing = {"id": oid, "name": name, "place": "post_office",
         "tags": ["gift"], "note": a.note, "from": "caleb"}
if a.paint:
    thing["tags"].append("paint")
    thing["colour"] = a.paint
    thing["left"] = max(1, a.goes)
w["objects"].append(thing)
jsave(WORLD, w)
jappend(INBOX, {"t": s["clock"], "text": "there is a parcel for you at the post office.",
                "read": False})
print(f"{name} is waiting at the post office.")
if a.paint:
    print(f"it paints {a.paint}, {thing['left']} goes. he is not told either of those.")
