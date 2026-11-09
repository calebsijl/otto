"""Set how tall the trees stand.

The renderer grows every tree at its natural size and then scales it by this
one number, so the whole wood comes up or down together. 1.0 is the height
you approved in the mockup. Pear trees in the orchard are left alone, since
they are meant to be small enough to pick from.

    python3 treesize.py          what it is now
    python3 treesize.py 1.2      taller
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import WORLD, jload, jsave

w = jload(WORLD)
if len(sys.argv) > 1:
    v = float(sys.argv[1])
    if not 0.3 <= v <= 3.0:
        print("that is not a sensible multiplier. 0.3 to 3.0.")
        sys.exit(1)
    w["tree_scale"] = v
    jsave(WORLD, w)
    print(f"trees now stand at {v}x")
else:
    print(f"trees stand at {w.get('tree_scale', 1.0)}x")
