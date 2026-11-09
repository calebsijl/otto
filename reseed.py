"""Write world/seed.json from the world as it stands.

reset.py restores the world from seed.json. That file was last written when
the village had eight places in it, so running reset.py would have thrown
away two thirds of the world without saying so. This brings the seed up to
date: the world as it is now, minus anything otto made or was given, with
the far places shut again so a reset really does start him over.

Run this whenever the built world changes. It never touches world.json.
"""
import sys, pathlib, json, shutil, datetime
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import WORLD, jload

SEED = WORLD.parent / "seed.json"
HIDDEN = ["lane_out", "church", "station", "town_road", "wharf_lane"]

w = jload(WORLD)
P = {k: json.loads(json.dumps(v)) for k, v in w["places"].items()}
O = [o for o in w["objects"]
     if o.get("made_by") != "otto" and o.get("from") != "caleb"
     and o.get("place") != "_carried"]

dropped = len(w["objects"]) - len(O)
for k, v in P.items():
    v.pop("found", None)
    if k in HIDDEN:
        v["known"] = False
    else:
        v.pop("known", None)

if SEED.exists():
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M")
    shutil.copy(SEED, SEED.with_suffix(f".json.{stamp}.bak"))
    old = json.loads(SEED.read_text())
    print(f"old seed: {len(old.get('places', {}))} places, "
          f"{len(old.get('objects', []))} things  (backed up)")

SEED.write_text(json.dumps({"places": P, "objects": O}, indent=2))
print(f"new seed: {len(P)} places, {len(O)} things  "
      f"({dropped} of his own left out)")
print("shut again on a reset:", ", ".join(HIDDEN))
