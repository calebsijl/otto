"""Stand the station up, and move it back off the town.

The line runs left to right the whole width of the map, so the station has to
sit well clear of the town or the ballast cuts through the market hall, which
is exactly what it was doing. It now sits twenty paces north of anything else.

The builder draws the platform, the canopy, the building, the tower and the
carriage. The objects here are what otto can look at and talk about, so they
are drawn by the builder and carry no shape of their own.

Idempotent.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import WORLD, jload, jsave

w = jload(WORLD)
P, O = w["places"], w["objects"]
st = P.get("station")
if not st:
    print("there is no station. run town.py first.")
    sys.exit(1)

st["kind"] = "earth"
st["build"] = "station"
st["pos"] = [-13, 0, -92]      # back off the town; the rails are long
st["size"] = [24, 14, 18]
st["scale"] = 0.5              # one number for how grand the whole thing is
st["warmth"] = 0.3
st.pop("style", None)
st["description"] = (
  "a long platform under an iron canopy, tiled in diamonds, with a roof that "
  "curves over and a row of columns holding it up that have ironwork spreading "
  "out of the top of them like fans. there is a clock on a bracket over the "
  "edge and a bigger one up the tower, and both of them are right. standing at "
  "the platform is one wooden carriage, varnished, with its windows still in "
  "it. there is no engine. there has not been an engine for a long time.")

def o(id, name, at, note, **kw):
    d = dict(id=id, name=name, place="station", at=at, shape="nothing",
             face=0, tags=["fixed"], note=note)
    d.update(kw); return d

WANT = {
 "the_carriage": o("the_carriage", "the carriage", [-0.5, -3.2],
   "wooden, and varnished so dark it is nearly red. ten tall windows down the "
   "side with smaller ones above them, a roof that rises in the middle into a "
   "second little roof with its own windows, and an open platform at each end "
   "with a curved rail round it and steps down to the ballast. there is a "
   "wheel on a stand at one end for the brake. nothing is coupled to it and "
   "nothing ever will be."),
 "station_clock": o("station_clock", "the clock on the tower", [-9.8, 5.0],
   "white face, black hands, four of them so it can be read from anywhere. it "
   "has not stopped.", tells_time=True),
 "platform_clock": o("platform_clock", "the clock over the platform edge",
   [3.0, -1.2], "hung off a bracket so it faces both ways down the platform, "
   "for people who are not here.", tells_time=True),
 "platform_bench": o("platform_bench", "a bench on the platform", [-1.2, 3.0],
   "cast ends and wooden slats, looking at the rails. somebody sat here a long "
   "time ago waiting for this.", tags=["sit", "fixed"]),
}

# ---- the road up to it ----------------------------------------------------
# Not a new road off the square. The way out of the village already runs at
# x -17..-11, and the archway through the station building is cut on the
# station's centre line at x -13, dead in line with it. So this is that same
# road carried straight on past the church, same width, same centre line,
# until it stops at the arch.
P["station_road"] = dict(
  name="the station road", kind="street", pos=[-14, 0, -69], size=[6, 0, 28],
  warmth=.25, known=False, exits=["lane_out", "station", "church"],
  description=(
    "the way out of the village, going on. past the church it stops being the "
    "way out of anywhere and becomes the way to one thing only. worn down the "
    "middle, a lamp at each end, and at the far end of it an archway through "
    "the middle of a building, with the platform straight through that."))

# the station is reached through the road, and the road is the thing he has to
# find. the board on the lych gate now tells him about the road, not the
# platform, which is the order you would learn it in.
P["station"]["known"] = True
for ob in O:
    if ob["id"] == "timetable_board":
        ob["reveals"] = "station_road"
        ob["note"] = ("a wooden board with paper under glass, gone brown, listing "
                      "times in two columns. there is a road going on past the "
                      "church, and whatever these times are for is up it.")

# rewire: the road carries everything now, so the links that only existed
# because the station had no road go away.
def unlink(a, b):
    for u, v in ((a, b), (b, a)):
        if u in P and v in P[u].get("exits", []):
            P[u]["exits"].remove(v)
def link(a, b):
    for u, v in ((a, b), (b, a)):
        if u in P and v not in P[u].setdefault("exits", []):
            P[u]["exits"].append(v)
unlink("station", "town_t6")
unlink("station", "church")
unlink("station_road", "town_t6")
unlink("station_road", "town_square")
link("lane_out", "station_road")
link("station", "station_road")
link("church", "station_road")

ROAD = {}
for i, z in enumerate([-11.5, 11.5]):
    ROAD[f"road_lamp_{i}"] = dict(
      id=f"road_lamp_{i}", name="a lamp on the station road", place="station_road",
      at=[2.0, z], shape="lamppost", face=0, tags=["fixed", "warm"],
      note=("the same cast post as the ones on the river walk. somebody still "
            "lights this road, for the people who would be coming up it."))
O[:] = [x for x in O if x["id"] not in ROAD]
O.extend(ROAD.values())

GONE = {"dead_train", "stopped_clock", "station_lamp_a", "station_lamp_b"}
O[:] = [x for x in O if x["id"] not in GONE and x["id"] not in WANT]
O.extend(WANT.values())
jsave(WORLD, w)

sx, sz = st["pos"][0], st["pos"][2]
hw, hd = st["size"][0]/2, st["size"][2]/2
print(f"station at x {sx-hw:.0f}..{sx+hw:.0f}  z {sz-hd:.0f}..{sz+hd:.0f}  scale {st['scale']}")
print(f"the rails run along x at z {sz - 6.5*st['scale']:.1f}")
north = max((p["pos"][2] + p["size"][2]/2) for k, p in P.items()
            if k != "station" and p.get("pos"))
print(f"nothing else reaches past z {north:.0f}")
r = P["station_road"]
print(f"the road: x {r['pos'][0]-3}..{r['pos'][0]+3}  z {r['pos'][2]-14}..{r['pos'][2]+14}, in line with the arch at x -13")
for k, v in list(WANT.items()) + list(ROAD.items()):
    print(f"   {v['name']}" + ("   (tells the time)" if v.get("tells_time") else ""))
