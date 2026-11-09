#!/usr/bin/env python3
"""Build a mockup of the internet cafe, in his village but not in his world.

Writes site/mock/cafe.json, which is his real world plus the proposed building.
Nothing here touches world.json. Look at it with:

    http://localhost:8080/world.html?mock=cafe

Run it again after any edit and reload the page.
"""
import json, pathlib, datetime

HERE = pathlib.Path(__file__).resolve().parent
w = json.loads((HERE / "world" / "world.json").read_text())

# A small shopfront on the west side of the bottom lane, in the gap between the
# top of the lane and the library. Deliberately the one modern thing in a
# village of cobbles and cast iron: a place that got these machines a long time
# ago and has not changed since.
# An ordinary building. The anachronism is not the bricks, it is the light:
# every window in this village is amber, and this one is cold. That reads at a
# hundred paces and it does not need a single modern surface to do it.
w["places"]["cafe"] = {
    "name": "the internet cafe",
    "kind": "shop",
    "style": "brick",
    "lamp": "#cfe6f2",
    "pos": [-8.5, 0, 2.0],
    "size": [6, 4.2, 6],
    "warmth": 0.55,
    "exits": ["lane_bottom"],
    "description": ("one room off the lane. three tables, and on each one a machine. "
                    "the light in here is the wrong colour and there is a sound under "
                    "everything."),
}
w["places"]["lane_bottom"].setdefault("exits", []).append("cafe")

# He has no word for any of this, so none of it is named. He meets the thing,
# works out what it does, and the word is his to earn or invent.
THINGS = [
    ("cafe_screen_a", "a machine with a face that lights up",
     "the face is cold white and it is not warm to touch. things move on it when you "
     "touch the board in front of it."),
    ("cafe_board_a", "a flat board covered in little squares",
     "every square has a mark on it. pressing one makes a mark appear on the lit face."),
    ("cafe_mouse_a", "a smooth lump on a cord",
     "it slides. when it slides, an arrow on the lit face slides the same way."),
    ("cafe_screen_b", "a second machine, its face dark",
     "the same as the lit one but nothing on it. there is a switch underneath."),
    ("cafe_counter", "the counter",
     "nobody behind it, same as everywhere. a bowl with coins in it and a card "
     "saying what an hour costs."),
    ("cafe_hum", "a sound under everything",
     "low, and it does not stop. you feel it in the table more than you hear it."),
    ("cafe_stool", "a stool at the middle table",
     "too tall for you. the one at the end table is not."),
    ("cafe_cables", "black cords going into the wall",
     "they come out of the backs of the machines and go in behind the skirting."),
]
w["objects"] = [o for o in w["objects"] if not o["id"].startswith("cafe_")]
for oid, nm, note in THINGS:
    w["objects"].append({"id": oid, "name": nm, "place": "cafe",
                         "tags": ["fixed"], "note": note})

out = HERE / "site" / "mock"
out.mkdir(parents=True, exist_ok=True)
(out / "cafe.json").write_text(json.dumps(w, indent=1))

now = datetime.datetime.now().replace(hour=15, minute=40, second=0, microsecond=0)
(out / "cafe-state.json").write_text(json.dumps({
    "name": "otto", "species": "hedgehog", "tick": 0,
    "clock": now.isoformat(timespec="seconds"), "asleep": False,
    "needs": {"energy": .8, "fullness": .6, "warmth": .7, "calm": .6, "wonder": .5},
    "location": "cafe", "carrying": [], "coins": 12,
    "doing": {"verb": "idle", "what": ""}, "weather": "", "mood": "settled"}, indent=1))

print(f"mockup written: {len(w['places'])} places, cafe at {w['places']['cafe']['pos']}")
print("look at it:  http://localhost:8080/world.html?mock=cafe")
