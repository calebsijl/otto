#!/usr/bin/env python3
"""The back lane, and the internet cafe on it.

The old lane was full: every frontage on it was taken, so the village could not
grow along it at all. This adds a second street behind his house, which is the
first thing that makes the place a neighbourhood rather than a corridor, and it
gives the houses and the library backs.

The cafe is the first building in his world that was designed rather than
generated. world.html builds it from BUILDERS.cafe; the place just says
build:"cafe" and which way it faces.

Safe to run more than once. Run it on the server: deploy.sh never sends
world/world.json.
"""
import json, pathlib

HERE = pathlib.Path(__file__).resolve().parent
WP = HERE / "world" / "world.json"
w = json.loads(WP.read_text())
places, objects = w["places"], w["objects"]
have = {o["id"] for o in objects}
did = []

# ---- the back lane -------------------------------------------------------
LANE = {
    "name": "the back lane",
    "kind": "street",
    "pos": [-17, 0, -2], "size": [6, 0, 26],
    "warmth": 0.2,
    "exits": ["yard", "cafe", "library", "hedge"],
    "description": ("a narrow way behind the houses, hedge on one side and the backs "
                    "of things on the other. nobody sweeps it."),
}
if "back_lane" not in places:
    places["back_lane"] = LANE; did.append("back_lane")
else:
    places["back_lane"].update(LANE)

# ---- the cafe ------------------------------------------------------------
CAFE = {
    "name": "the internet cafe",
    "kind": "shop",
    "build": "cafe",            # hand-designed: see BUILDERS.cafe in world.html
    "face": "west",             # the frontage looks onto the back lane
    "pos": [-10.5, 0, 0.5], "size": [7, 4.6, 7],
    "warmth": 0.55,
    "exits": ["back_lane"],
    "description": ("one room off the back lane. three tables, and on each one a "
                    "machine. the light in here is the wrong colour and there is a "
                    "sound under everything."),
}
if "cafe" not in places:
    places["cafe"] = CAFE; did.append("cafe")
else:
    places["cafe"].update(CAFE)

# make every new link two-way, which is the rule here now
for a, b in (("yard", "back_lane"), ("hedge", "back_lane"),
             ("library", "back_lane"), ("back_lane", "cafe")):
    for x, y in ((a, b), (b, a)):
        if x in places and y in places:
            ex = places[x].setdefault("exits", [])
            if y not in ex:
                ex.append(y)

# ---- what is in it -------------------------------------------------------
# He has no word for any of this. He meets the thing, works out what it does,
# and the word is his to earn or to invent.
THINGS = [
    ("cafe_screen_a", "a machine with a face that lights up",
     "the face is cold white and it is not warm to touch. things move on it when "
     "you press the board in front of it."),
    ("cafe_board_a", "a flat board covered in little squares",
     "every square has a mark on it. pressing one puts that mark on the lit face."),
    ("cafe_mouse_a", "a smooth lump on a cord",
     "it slides. when it slides, an arrow on the lit face slides the same way."),
    ("cafe_screen_b", "a second machine, its face dark",
     "the same as the lit one but nothing on it. there is a switch underneath."),
    ("cafe_counter", "the counter",
     "nobody behind it, same as everywhere. a bowl with coins in it and a card "
     "saying what an hour costs."),
    ("cafe_hum", "a sound under everything",
     "low, and it does not stop. you feel it in the table more than you hear it."),
]
for oid, nm, note in THINGS:
    if oid not in have:
        objects.append({"id": oid, "name": nm, "place": "cafe",
                        "tags": ["fixed"], "note": note})
        have.add(oid); did.append(oid)

WP.write_text(json.dumps(w, indent=1))
print("  added: " + (", ".join(did) if did else "nothing new, the rest was updated"))

oneway = [(a, b) for a, v in places.items() for b in v.get("exits", [])
          if b in places and a not in places[b].get("exits", [])]
print(f"  one-way links: {len(oneway)}")

# nothing may overlap anything
def bx(p):
    x, _, z = p["pos"]; sx, _, sz = p["size"]
    return (x-sx/2, x+sx/2, z-sz/2, z+sz/2)
ids = [k for k, v in places.items() if v.get("pos") and v.get("size")]
clash = 0
for i, a in enumerate(ids):
    for b in ids[i+1:]:
        p, q = bx(places[a]), bx(places[b])
        if p[0] < q[1] and p[1] > q[0] and p[2] < q[3] and p[3] > q[2]:
            print(f"  CLASH {a} / {b}")
            clash += 1
print(f"  overlapping places: {clash}")
