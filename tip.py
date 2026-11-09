#!/usr/bin/env python3
"""The tip, and the honesty box.

Two things the village was missing, and between them they are why everything he
has ever built is made of paper.

The tip is a heap of thrown-out made things at the bottom end of the lane. Free,
and it changes. Up to now every material he could get for nothing was natural:
twigs, snail shells, reeds, stones, driftwood. Nothing with a mechanism in it,
nothing he could take apart. So he folded paper, because paper was what the shop
sold and the shop was the only place things came from.

The honesty box is how the village pays. He leaves something he made in it and
some time later there are coins there instead. Nobody is behind it, because
nobody is ever behind anything here. The village simply answers.

Safe to run more than once. Run it on the server: deploy.sh never sends
world/world.json.
"""
import json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent
WP = HERE / "world" / "world.json"
w = json.loads(WP.read_text())
places, objects = w["places"], w["objects"]
have = {o["id"] for o in objects}
added = []

def place(pid, **kw):
    if pid in places:
        print(f"  {pid} is already here")
        return False
    places[pid] = kw
    added.append(pid)
    return True

def thing(oid, **kw):
    if oid in have:
        return
    objects.append(dict(kw, id=oid))
    have.add(oid)
    added.append(oid)

# ---- the tip -------------------------------------------------------------
if place("tip",
         name="the tip",
         kind="earth",
         pos=[10, 0, 22], size=[8, 0, 8],
         exits=["lane_bottom"],
         description=("where the village puts what it has finished with. a low heap, "
                      "gone through by rain. things in it are not yours or anyone's.")):
    places["lane_bottom"].setdefault("exits", []).append("tip")

# Things with a mechanism in them, which is the whole point. Named plainly: he
# meets the word by meeting the thing, which is how he is allowed to learn one.
SCRAP = [
    ("scrap_wire",   "a coil of thin wire", "springy. it holds a bend if you make it sharp enough."),
    ("scrap_spring", "a small spring", "pushes back when you squash it, and keeps doing it."),
    ("scrap_tin",    "a flattened tin", "thin metal, bright where the rain has not got at it."),
    ("scrap_glass",  "a piece of thick glass", "edges gone smooth. things look bent through it."),
    ("scrap_clock",  "a clock that has stopped", "a case, a face, and a lot of small parts behind it."),
    ("scrap_brass",  "a strip of brass", "heavier than it looks and it does not rust."),
    ("scrap_cork",   "a handful of corks", "light, and they squeeze."),
    ("scrap_magnet", "a small grey bar", "it sticks to the tin and not to the cork."),
]
for oid, nm, note in SCRAP:
    thing(oid, name=nm, place="tip", tags=["material", "gather", "scrap"], note=note)

# ---- the honesty box -----------------------------------------------------
thing("honesty_box",
      name="a wooden box on a post",
      place="lane_bottom",
      tags=["fixed", "box"],
      note=("open at the top, with a slot in the lid. there is nothing in it. "
            "whatever is left in it does not stay left."))

# ---- somewhere to go, none of it known yet -------------------------------
# These exist but he has not found them. An unknown place is not in his prompt
# at all, so it costs nothing until the day he works out it is there.
place("lane_out",
      name="the way out of the village",
      kind="street", known=False,
      pos=[-16, 0, -40], size=[6, 0, 20],
      exits=["orchard"],
      description="a track going away from the village, between hedges, uphill.")
place("church",
      name="the church",
      kind="civic", known=False,
      pos=[-30, 0, -62], size=[10, 8, 16],
      exits=["lane_out"],
      description=("a tower with a spire on it, and a long low part behind. "
                   "the door is shut. you can see it from a long way off."))
place("woods",
      name="the woods",
      kind="earth", known=False,
      pos=[6, 0, -56], size=[22, 0, 18],
      exits=["lane_out"],
      description="tall straight trees, close together, and it is darker under them.")

# keep the new places where this script says they are, even on a re-run, so a
# position can be corrected without wiping his world and starting again
GEOM = {"lane_out": ([-14, 0, -46], [6, 0, 18]),
        "church":   ([-30, 0, -62], [10, 8, 16]),
        "woods":    ([6, 0, -56],   [22, 0, 18]),
        "tip":      ([10, 0, 22],   [8, 0, 8])}
for pid, (pos, size) in GEOM.items():
    if pid in places:
        places[pid]["pos"], places[pid]["size"] = pos, size

# What the church is made of, in the viewer's terms. An english parish church:
# low chancel at the east end, taller nave, south porch, stepped buttresses, a
# west tower with a broach spire, and a lych gate where the path arrives.
if "church" in places:
    places["church"].update({
        "style": "stone",
        "gable": True,
        "tower": {"h": 21, "spire": 15},
        "chancel": {"len": 6},
        "porch": {"side": 1},
        "buttresses": {"count": 3},
        "lychgate": {"away": 9},
    })

# things that are a way of finding out somewhere else is there
MARKS = [
    ("gap_orchard", "orchard", "lane_out",
     "a gap in the top corner",
     "the hedge stops and starts again, and the grass between is worn flat."),
    ("tower_far", "lane_out", "church",
     "something standing up above the trees",
     "too far to make out. it is taller than it is wide and it comes to a point."),
    ("dark_trees", "lane_out", "woods",
     "a dark line along the top of the field",
     "trees, closer together than the ones in the orchard, and no light between them."),
]
for oid, where, reveals, nm, note in MARKS:
    if oid not in have and where in places:
        objects.append({"id": oid, "name": nm, "place": where,
                        "tags": ["fixed"], "note": note, "reveals": reveals})
        have.add(oid); added.append(oid)

# make the new links two-way, which is the rule here now
for a, b in (("orchard", "lane_out"), ("lane_out", "church"), ("lane_out", "woods")):
    if a in places and b in places:
        for x, y in ((a, b), (b, a)):
            ex = places[x].setdefault("exits", [])
            if y not in ex:
                ex.append(y)

WP.write_text(json.dumps(w, indent=1))
print("  added: " + (", ".join(added) if added else "nothing, it was all here"))

oneway = [(a, b) for a, v in places.items() for b in v.get("exits", [])
          if b in places and a not in places[b].get("exits", [])]
print(f"  one-way links: {len(oneway)}")
unknown = [p for p, v in places.items() if v.get("known") is False]
print(f"  places he has not found yet: {', '.join(unknown) or 'none'}")
