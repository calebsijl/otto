"""The rest of the village plan: the wharf, the town, the station, the river walk.

The plan you approved on the map. Three places give up their ground (pond,
stream, far bank), the woods move out east, and seventeen new ones go in:
a working waterfront south of the lane, a proper little town an orchard's
walk north past the way out, and a station behind the church with one old
train sitting in it.

Data only. The new buildings render with the styles the world already has.
The station's train, and the ember lamps along the river walk, are geometry
and come after this.

Idempotent: run it twice and the second run changes nothing.
"""
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import WORLD, jload, jsave

GOES = ["pond", "stream", "far_bank"]        # their ground is wanted
MOVES = {"woods": "woods_new"}               # the woods go east, out past the town

# ----------------------------------------------------------------- the places
NEW = {
 # ---- the wharf, south, on the water -------------------------------------
 "wharf_lane": dict(
   name="down to the water", kind="street", pos=[-3,0,23], size=[6,0,14],
   warmth=.2, known=False, exits=["lane_bottom","wharf_row"],
   description="a cut between two walls that drops away south, going down the "
     "whole way. you can smell the water before you can see it, and under that, "
     "tar."),
 "wharf_row": dict(
   name="wharf row", kind="street", pos=[-2,0,34], size=[30,0,6],
   warmth=.3, exits=["wharf_lane","wharf_w1","wharf_w3","wharf_w4","wharf_w5","wharf"],
   description="a long flat street with the working side of the village on it. "
     "everything here is open at the front so you can see the work happening, "
     "and all of it is louder than the lane."),
 "wharf_w1": dict(
   name="the boatyard", kind="shop", style="timber", pos=[-13,0,26], size=[7,5.5,7],
   warmth=.45, exits=["wharf_row"],
   description="a shed with no front wall and a boat upside down in the middle "
     "of it, bigger than your house. shavings up to your chin in the corners."),
 "wharf_w3": dict(
   name="the sawmill", kind="shop", style="timber", pos=[-12,0,42], size=[8,5.5,7],
   warmth=.4, exits=["wharf_row"],
   description="the loudest building there is. a blade under a table turns "
     "wood into two pieces of wood and sawdust hangs in the light like weather."),
 "wharf_w4": dict(
   name="the bath house", kind="civic", style="brick", pos=[-1,0,42], size=[8,5,7],
   warmth=.85, exits=["wharf_row"],
   description="hot inside, and so full of steam that the far wall is a rumour. "
     "the floor is wet stone and everything echoes twice."),
 "wharf_w5": dict(
   name="the glasshouse", kind="shop", style="stone", pos=[9,0,42], size=[8,4.5,7],
   warmth=.7, exits=["wharf_row"],
   description="a building made mostly of windows, warm as a pocket, with more "
     "green things in it than the orchard. the air is wet and smells of soil."),
 "wharf": dict(
   name="the wharf", kind="earth", pos=[19,0,33], size=[10,0,8],
   warmth=.25, exits=["wharf_row","river"],
   description="flat stone right out to the edge, and then the river, moving "
     "past faster than you expect. there is no rail. you keep well back and "
     "then you do not."),

 # ---- the town, north, past the way out ----------------------------------
 "town_road": dict(
   name="market row", kind="street", pos=[3,0,-52], size=[28,0,6],
   warmth=.3, known=False, exits=["lane_out","town_t1","town_t2","town_t3",
                                  "town_square","woods_new"],
   description="a street with shops down both sides and more people on it in "
     "one morning than the lane sees in a month. nobody here knows your name, "
     "which is strange and not entirely bad."),
 "town_square": dict(
   name="the square", kind="street", pos=[3,0,-60], size=[10,0,10],
   warmth=.3, exits=["town_road","town_t4","town_t5","town_t6"],
   description="an open square of flagstones with a pump in the middle of it "
     "and buildings taller than anything at home standing round all four sides."),
 "town_t1": dict(
   name="the ironmonger", kind="shop", style="brick", pos=[-6,0,-45], size=[7,6,7],
   warmth=.4, exits=["town_road"],
   description="dark, and every wall is drawers. whatever you are making, the "
     "part you need is in one of these drawers and the man knows which."),
 "town_t2": dict(
   name="the printer", kind="shop", style="brick", pos=[3,0,-45], size=[7,6,7],
   warmth=.5, exits=["town_road"],
   description="ink, hot metal and paper. a machine the size of a cart comes "
     "down on a sheet, lifts off, and the sheet has words on it."),
 "town_t3": dict(
   name="the clockmaker", kind="shop", style="timber", pos=[12,0,-45], size=[7,6,7],
   warmth=.55, exits=["town_road"],
   description="small, quiet, and ticking from every direction at slightly "
     "different times. there are more wheels in this one room than in the "
     "whole village."),
 "town_t4": dict(
   name="the music shop", kind="shop", style="timber", pos=[-6,0,-59], size=[7,6,7],
   warmth=.5, exits=["town_square"],
   description="instruments hung up by their necks like washing. somebody is "
     "always half playing something in the back and stopping before the end."),
 "town_t5": dict(
   name="the bakery", kind="shop", style="brick", pos=[12,0,-59], size=[7,6,7],
   warmth=.8, exits=["town_square"],
   description="the warmest doorway in the world. you can stand in it for a "
     "long time before anyone minds."),
 "town_t6": dict(
   name="the market hall", kind="civic", style="stone_tall", pos=[3,0,-70], size=[9,7,7],
   warmth=.35, exits=["town_square"],
   description="a roof on stone legs with nothing between them, so the weather "
     "comes through but the rain does not. trestles stacked against the end wall."),
 "station": dict(
   name="the station", kind="civic", style="stone", pos=[-13,0,-79], size=[22,6,9],
   warmth=.3, known=False, exits=["church","town_t6"],
   description="a long low building with a canopy over a stone platform, and "
     "standing at the platform, an engine and two carriages that have not moved "
     "in a very long time. there is nobody here. the clock has stopped at "
     "twenty past four."),

 # ---- and the woods, moved out east of the town --------------------------
 "woods_new": dict(
   name="the woods", kind="earth", pos=[27,0,-58], size=[16,0,16],
   warmth=.2, exits=["town_road"],
   description="proper trees, close together, and the light goes green and "
     "goes quiet. the ground is all needles and gives slightly under you."),
}

# ---- ways in from places that already exist (added both ways) -------------
LINKS = [("lane_bottom", "wharf_lane"),
         ("lane_out",    "town_road"),
         ("church",      "station"),
         ("town_t6",     "station"),
         ("river",       "wharf")]

# ---- and the ways that no longer go anywhere -----------------------------
UNLINK = [("lane_bottom","stream"), ("hedge","pond"), ("river","stream"),
          ("lane_out","woods")]

# ----------------------------------------------------- the back bank rebuilt
WALK = dict(
  name="the river walk",
  description="a made path along the water, flagstones laid end to end the "
    "whole length of it, with benches set back off it and a lamp every so "
    "often on a cast post. somebody planted the beds and somebody still weeds "
    "them. at dusk the lamps come up the colour of an ember and the water "
    "goes the same colour back.")

# ------------------------------------------------------- things in the places
def o(id, name, place, at, tags, note, **kw):
    d = dict(id=id, name=name, place=place, at=at, tags=tags, note=note)
    d.update(kw); return d

THINGS = [
 # the three ways of finding the new quarters
 o("worn_path","a path worn through the grass","lane_bottom",[-2.6,6.4],
   ["fixed"],"the grass is flattened in a line going off south between two "
   "walls, the way grass goes when the same feet do the same thing for years. "
   "something down there is worth walking to.", shape="slab", reveals="wharf_lane"),
 o("milestone","a milestone","lane_out",[1.8,-6.2],
   ["fixed"],"a squat stone with a flat face and a number cut into it, leaning "
   "the way everything old leans. the number is how far it is to somewhere, and "
   "the somewhere is further up this road.", shape="post", reveals="town_road"),
 o("timetable_board","a board on the lych gate","church",[3.4,6.0],
   ["fixed"],"a wooden board with paper under glass, gone brown, listing times "
   "in two columns. whatever it is listing times for is behind the church and "
   "nobody has changed the paper in years.", shape="slab", reveals="station"),

 # the boatyard
 o("plank_offcuts","offcuts of planking","wharf_w1",[-2.1,1.8],
   ["material","gather"],"ends of boards sawn off and stacked against the wall, "
   "because nobody here throws wood away. some are longer than you are.",
   shape="beam"),
 o("pitch_tub","a tub of pitch","wharf_w1",[1.9,-1.4],
   ["shop","material","infinite"],"black, sticky, and it smells like a road in "
   "summer. it goes on the outside of a hull so the water stays on the outside "
   "too.", price=1, shape="box"),
 # the sawmill
 o("saw_bench","the saw bench","wharf_w3",[0,-1.2],
   ["fixed"],"a long table with a slot down the middle and a blade standing up "
   "through it. the blade is not turning. you are glad the blade is not turning.",
   shape="beam"),
 o("sawdust_heap","a heap of sawdust","wharf_w3",[-2.6,2.0],
   ["material","gather","warm"],"dry, soft, and warmer than the floor. you "
   "could sleep in this very happily if it were not somebody's sawdust.",
   shape="pile"),
 o("battens","a bundle of battens","wharf_w3",[2.4,1.6],
   ["shop","material","infinite"],"thin square sticks, all cut the same length "
   "and tied with twine. the most useful shape there is.", price=1, shape="beam"),
 # the bath house
 o("hot_tap","the hot tap","wharf_w4",[-2.4,-2.0],
   ["fixed","warm","wash"],"brass, and stiff, and it goes if you lean your "
   "whole weight on it. what comes out is hot enough to make the room vanish.",
   shape="tube"),
 o("bath_bench","a slatted bench","wharf_w4",[1.8,1.6],
   ["sit","fixed","warm"],"slats worn pale and smooth by people sitting on them "
   "wet. it is the warmest thing to sit on anywhere.", shape="beam"),
 # the glasshouse
 o("glass_panes","a stack of glass panes","wharf_w5",[-2.2,-1.8],
   ["shop","material","infinite"],"flat, cold, sharp at the edges, and the room "
   "looks slightly wrong through them. you would have to be careful with these.",
   price=2, shape="sheet"),
 o("seedlings","trays of seedlings","wharf_w5",[1.6,1.4],
   ["fixed"],"hundreds of them in shallow trays, every single one leaning the "
   "same way, towards the light.", shape="box"),
 # the wharf itself
 o("mooring_rings","the mooring rings","wharf",[-3.0,1.0],
   ["fixed"],"iron hoops set into the stone edge, rubbed bright on the inside "
   "where ropes have pulled on them. nothing is tied to any of them now.",
   shape="rope"),
 o("crane_post","the old crane","wharf",[2.4,-1.2],
   ["fixed"],"a timber post with an arm across the top and a chain hanging off "
   "the end. you can push it round and it goes, slowly, complaining the whole "
   "way.", shape="post"),

 # the ironmonger
 o("nails_tray","a tray of nails","town_t1",[-1.9,-1.6],
   ["shop","material","infinite"],"sorted by length into wooden compartments. "
   "there are more sizes of nail in this tray than you knew there were sizes "
   "of anything.", price=1, shape="pile"),
 o("iron_wire","a coil of soft wire","town_t1",[1.7,-1.9],
   ["shop","material","infinite"],"grey and soft, wound on a wooden spool. it "
   "bends where you bend it and then it stays bent.", price=1, shape="rope"),
 o("vice","the vice","town_t1",[0.4,1.9],
   ["fixed"],"bolted to the end of the counter. you turn the handle and it "
   "holds whatever is in its jaws harder than you could hold anything.",
   shape="box"),
 # the printer
 o("press","the press","town_t2",[0,-1.4],
   ["fixed"],"iron, and taller than the man working it. it comes down on a "
   "sheet with a sound you feel through the floor. he lets it down slowly when "
   "he notices you watching.", shape="box"),
 o("paper_ream","a ream of paper","town_t2",[-2.2,1.7],
   ["shop","material","infinite"],"white sheets cut square and stacked, more "
   "than you could cover in a year of writing.", price=1, shape="sheet"),
 o("ink_tin","a tin of ink","town_t2",[2.0,1.5],
   ["shop","material","infinite"],"thick black stuff, not runny the way you "
   "expected. it goes onto the roller, never onto the paper.", price=1,
   shape="box"),
 # the clockmaker
 o("gear_tray","a tray of brass gears","town_t3",[-1.8,-1.7],
   ["shop","material","infinite"],"wheels with teeth round the edge, every one "
   "a different size, lying loose in a tray like coins. they are made to turn "
   "each other.", price=1, shape="pile"),
 o("mainspring","a mainspring","town_t3",[1.9,-1.5],
   ["shop","material","infinite"],"a flat ribbon of steel wound tight into a "
   "drum. it wants to come undone, and it will, for days, if it is let out "
   "slowly enough.", price=2, shape="rope"),
 o("regulator","the clock on the wall","town_t3",[0,2.0],
   ["fixed"],"a tall case with a weight swinging in it. it is the only thing "
   "in the town that is never wrong.", shape="slab"),
 # the music shop
 o("tin_whistle","a tin whistle","town_t4",[-1.6,-1.6],
   ["shop","infinite"],"a metal tube with six holes down it. you can get a "
   "noise out of it straight away and a tune out of it eventually.", price=1,
   shape="tube"),
 o("strings_card","a card of wound strings","town_t4",[1.8,-1.4],
   ["shop","material","infinite"],"wire wound on a paper card. they are sold "
   "to be played, but they are also simply very good string.", price=1,
   shape="rope"),
 # the bakery
 o("loaves","the day's loaves","town_t5",[0,-1.8],
   ["food","shop","infinite","hot"],"still warm underneath. the crust ticks "
   "quietly while it cools.", price=1, shape="dome"),
 # the market hall
 o("trestles","trestles stacked against the wall","town_t6",[-2.6,1.8],
   ["material","gather"],"folding wooden legs, dozens of them, leaning in a "
   "stack. on a market morning they are tables and the rest of the week they "
   "are this.", shape="beam"),
 # the station
 o("dead_train","the engine","station",[-4.0,-1.4],
   ["fixed"],"black, and taller than the church door, standing at the platform "
   "with two carriages behind it. cold all the way through. there is grass "
   "growing up between the rails under it, which tells you how long it has "
   "been since anybody needed it to go anywhere.", shape="beam"),
 o("platform_bench","a bench on the platform","station",[3.6,1.2],
   ["sit","fixed"],"cast ends and wooden slats, facing the empty rails. "
   "somebody sat here a long time ago waiting for this.", shape="beam"),
 o("stopped_clock","the station clock","station",[5.8,-2.2],
   ["fixed"],"on a bracket over the platform, with hands at twenty past four. "
   "it is wrong twice a day and right twice a day and nobody has wound it "
   "either way.", shape="slab"),

 # the river walk
 o("walk_bench_a","a bench facing the water","river_bank",[-1.4,-14.0],
   ["sit","fixed"],"iron ends and five wooden slats, set back off the path so "
   "your feet do not get walked over. it faces the river and nothing else.",
   shape="beam"),
 o("walk_bench_b","a bench under the lamp","river_bank",[-1.4,9.0],
   ["sit","fixed"],"the same bench again, further along, with a lamp post right "
   "behind it. this is the one to sit on when it is going dark.", shape="beam"),
 o("walk_lamp_a","a lamp post","river_bank",[1.6,-8.0],
   ["fixed","warm"],"a cast post with a glass case on top of it. at dusk "
   "something in it comes up slowly the colour of an ember, and then the water "
   "has one of these in it too, wobbling.", shape="post"),
 o("walk_lamp_b","a lamp post","river_bank",[1.6,6.0],
   ["fixed","warm"],"another of the lamp posts, far enough along that the dark "
   "between them is properly dark.", shape="post"),
 o("flower_beds","the planted beds","river_bank",[1.4,-1.0],
   ["fixed","gather"],"long beds cut into the grass on the path side, planted "
   "in rows and weeded by somebody who has not given up. there is something "
   "out in every month of the year, which cannot be an accident.", shape="pile"),

 # the streets themselves, so nowhere is just a corridor
 o("wharf_handrail","a rope handrail","wharf_lane",[2.4,0.0],
   ["fixed"],"a rope through iron eyes down one wall, because the slope is "
   "steep enough that people have wanted something to hold. it is tarred and "
   "it comes off on your paws.", shape="rope"),
 o("tar_barrels","barrels under a tarpaulin","wharf_row",[-11.0,1.4],
   ["fixed"],"a row of them against the wall with a sheet pulled over the top "
   "and tied down. whatever is in them, it is the smell of the whole street.",
   shape="tube"),
 o("row_lamp","a lamp on a bracket","wharf_row",[7.0,-1.6],
   ["fixed","warm"],"out from the wall on an iron arm, high up out of the way "
   "of the work. it is lit before it needs to be, every day.", shape="post"),
 o("market_stalls","stalls along the kerb","town_road",[-6.0,1.2],
   ["fixed"],"trestle tables with awnings over them, pulled out across the "
   "front of the shops, selling what the shop behind does not. you have to "
   "walk round them.", shape="box"),
 o("town_gutter","a gutter running the length of it","town_road",[9.0,-1.4],
   ["fixed","water"],"a stone channel at the edge with water going along it "
   "faster than the river does. things float in it. you could race something "
   "down this.", shape="slab"),
 o("the_pump","the pump","town_square",[0.0,0.0],
   ["fixed","water"],"iron, waist-high on a person, with a curved handle and a "
   "worn stone trough under the spout. it takes both your shoulders and then "
   "the water comes.", shape="post"),
 o("notice_board","the notice board","town_square",[-3.6,-3.2],
   ["fixed"],"a glass case on legs with papers pinned behind it, layered over "
   "each other, the old ones gone yellow underneath the new. things that have "
   "happened and things that are going to.", shape="slab"),
 # the woods, which were empty the whole time they were in the old place
 o("fallen_trunk","a fallen trunk","woods_new",[-4.0,2.6],
   ["fixed","sit"],"down across the slope and going soft, with bark coming off "
   "in sheets. there is a whole other world living under the bark and you can "
   "lift it and look.", shape="beam"),
 o("deadfall","deadfall branches","woods_new",[3.0,-3.4],
   ["material","gather"],"dry sticks all over the floor in every length there "
   "is, free, and nobody wants them. this is the best place in the world if "
   "you are building something.", shape="beam"),
 o("fungi","fungi on the north side","woods_new",[-2.0,-5.0],
   ["fixed","gather"],"growing in steps up the shaded side of the trunks, and "
   "they are not the same two weeks running. some are the colour of nothing "
   "else here.", shape="dome"),
 o("needle_floor","the needle floor","woods_new",[5.2,4.0],
   ["fixed","warm"],"inches of dropped needles, dry underneath, and it gives "
   "under you and springs back. you can hear yourself walking on it and "
   "nothing else.", shape="sheet"),
 # and the back lane, which has had nothing in it since it was cut through
 o("lane_drain","the drain","back_lane",[-1.8,-6.0],
   ["fixed","water"],"an iron grating in the low point of the lane with a hole "
   "under it that goes further down than you can see. things go in and do not "
   "come back.", shape="slab"),
 o("stacked_crates","stacked crates","back_lane",[1.6,4.0],
   ["material","gather"],"behind the backs of the shops, slatted wooden boxes "
   "stacked higher than you, some broken. the broken ones are nobody's.",
   shape="box"),
]

# things the vanishing places were holding that are worth keeping
RELOCATE = {"reeds": "river_bank", "flat_stone": "river_bank",
            "bank_stones": "wharf", "paddle_wheel_124": "wharf"}

# ============================================================== do it
w = jload(WORLD)
P, O = w["places"], w["objects"]

if "town_road" in P and "wharf_row" in P and "station" in P:
    s = P["station"]
    if s["pos"] == NEW["station"]["pos"]:
        print("already done. nothing changed.")
        sys.exit(0)
    was = list(s["pos"])
    s["pos"] = list(NEW["station"]["pos"])
    s["size"] = list(NEW["station"]["size"])
    s["description"] = NEW["station"]["description"]
    for a, b in (("church", "station"), ("town_t6", "station")):
        for x, y in ((a, b), (b, a)):
            if x in P and y not in P[x].setdefault("exits", []):
                P[x]["exits"].append(y)
    jsave(WORLD, w)
    print(f"station moved {was} -> {s['pos']}, now between the church and the "
          "market hall, with ways in from both.")
    sys.exit(0)

# ---- clash check first. nothing is written if anything overlaps.
def rect(p):
    x, z = p["pos"][0], p["pos"][2]
    sx, sz = p["size"][0], p["size"][2]
    return (x - sx/2, x + sx/2, z - sz/2, z + sz/2)

def hits(a, b):
    return not (a[1] <= b[0] or b[1] <= a[0] or a[3] <= b[2] or b[3] <= a[2])

standing = {k: v for k, v in P.items()
            if k not in GOES and k not in MOVES and v.get("kind") != "indoor"}
clash = []
items = list(NEW.items())
for i, (k, v) in enumerate(items):
    r = rect(v)
    for k2, v2 in standing.items():
        if hits(r, rect(v2)):
            clash.append(f"{k} overlaps {k2}")
    for k2, v2 in items[i+1:]:
        if hits(r, rect(v2)):
            clash.append(f"{k} overlaps {k2}")
if clash:
    print("NOT WRITTEN. the plan does not fit:")
    for c in clash:
        print("   ", c)
    sys.exit(1)
print(f"fit check: {len(NEW)} new plots, no overlaps with the {len(standing)} standing.")

# ---- places in
for k, v in NEW.items():
    P[k] = v

# ---- ways between, both directions
def join(a, b):
    for x, y in ((a, b), (b, a)):
        if x in P and y not in P[x].setdefault("exits", []):
            P[x]["exits"].append(y)
for a, b in LINKS:
    join(a, b)
for a, b in UNLINK:
    for x, y in ((a, b), (b, a)):
        if x in P and y in P[x].get("exits", []):
            P[x]["exits"].remove(y)

# ---- the back bank becomes the river walk
if "river_bank" in P:
    P["river_bank"].update(WALK)

# ---- keep what is worth keeping out of the places that go
moved = []
for ob in O:
    tgt = RELOCATE.get(ob["id"])
    if tgt and ob.get("place") in GOES:
        ob["place"] = tgt
        ob["at"] = [0.8, -3.0] if tgt == "wharf" else [2.0, 16.0]
        moved.append(f"{ob['id']} -> {tgt}")

# ---- and the water itself goes with the water
before = len(O)
O[:] = [ob for ob in O if ob.get("place") not in GOES]
dropped_things = before - len(O)

# ---- places out
for k in GOES:
    P.pop(k, None)
for old in MOVES:
    P.pop(old, None)

# ---- new things in
have = {ob["id"] for ob in O}
added = 0
for t in THINGS:
    if t["id"] not in have:
        O.append(t); added += 1

# ---- nothing may point at a place that is not there
bad = []
for k, v in P.items():
    keep = [e for e in v.get("exits", []) if e in P]
    if keep != v.get("exits", []):
        bad += [f"{k} -> {e}" for e in v["exits"] if e not in P]
        v["exits"] = keep
for ob in O:
    if ob.get("place") not in P and ob.get("place") != "_carried":
        bad.append(f"object {ob['id']} was at {ob.get('place')}, put in the tip")
        ob["place"] = "tip"
        ob["at"] = [0, 0]

jsave(WORLD, w)

print()
print(f"places     : {len(P)}  (+{len(NEW)} new, -{len(GOES)} gone, woods moved east)")
print(f"things     : {len(O)}  (+{added} new, -{dropped_things} went with the water)")
print(f"relocated  : {', '.join(moved) or 'none'}")
print(f"river walk : {P['river_bank']['name']}")
if bad:
    print("tidied up  :")
    for b in bad:
        print("   ", b)
print()
print("the wharf is off the bottom of the lane, the town is up past the way out,")
print("and the station is behind the church. all three start undiscovered: he")
print("finds them by looking at the worn path, the milestone and the board.")
