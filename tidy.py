#!/usr/bin/env python3
"""Clear out his old experiments. He keeps what he learned; the debris goes."""
import sys, pathlib, argparse, re
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import WORLD, jload, jsave

ap = argparse.ArgumentParser()
ap.add_argument("--where", default="library", help="which place to clear (default: library)")
ap.add_argument("--all", action="store_true", help="every test piece he made, anywhere")
ap.add_argument("--dry", action="store_true", help="list what would go, change nothing")
a = ap.parse_args()

TEST = re.compile(r"arch|tube|beam|bridge|strip|plank|truss|fold", re.I)
w = jload(WORLD)
doomed = [o for o in w["objects"]
          if o.get("made_by") == "otto"
          and (a.all or o.get("place") == a.where)
          and TEST.search(o.get("id","") + " " + o.get("name",""))]
if not doomed:
    print("nothing to clear."); raise SystemExit
for o in doomed:
    print(f"  {o['name'][:46]:48} {o.get('place')}")
if a.dry:
    print(f"\n{len(doomed)} pieces. run without --dry to clear them."); raise SystemExit
w["objects"] = [o for o in w["objects"] if o not in doomed]
jsave(WORLD, w)
print(f"\ncleared {len(doomed)} test pieces. {len(w['objects'])} things left in the world.")
print("his notes, knowledge and pages are untouched, so he still knows what he learned.")
