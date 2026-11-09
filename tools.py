"""The complete list of things otto can do. Deliberately open-ended and short."""
import datetime, os, pathlib, random, re, json
import physics
from engine import (jload, jsave, jappend, jlines, clamp, obj_by_id, here,
                    search_web, read_page, shelf, read_book, books, ASIDE, WORLD, NOTES, KEPT, KNOWS, SEEN, WISHES, OUTBOX, SITE)

POTTERING = {'move', 'examine', 'use', 'take', 'journal', 'remember', 'message',
             'put_down',
             'look_at_page', 'think_properly', 'rest'}

SCHEMA = [
 {"name": "move", "description": "walk to a connected place.",
  "input_schema": {"type": "object", "properties": {"place": {"type": "string"}}, "required": ["place"]}},
 {"name": "examine", "description": "look properly at an object here, or at the place itself.",
  "input_schema": {"type": "object", "properties": {"target": {"type": "string"}}, "required": ["target"]}},
 {"name": "use", "description": "do something with an object here or something you are carrying. say what you are trying to do.",
  "input_schema": {"type": "object", "properties": {"object": {"type": "string"}, "intent": {"type": "string"}},
                   "required": ["object", "intent"]}},
 {"name": "take", "description": "pick something up and carry it. in a shop this buys it if you have a coin.",
  "input_schema": {"type": "object", "properties": {"object": {"type": "string"}}, "required": ["object"]}},
 {"name": "edit_world", "description": "change the world. put something down somewhere, move it, make a new thing you have made, get rid of something, or change how a place or object is described. this is how you decorate and build in your own world.",
  "input_schema": {"type": "object", "properties": {
      "op": {"type": "string",
             "enum": ["place", "create", "remove", "describe", "build_place", "paint"],
             "description": "create a thing, move a thing, get rid of a thing, rewrite how something reads, build a whole new place joined onto where you are, or paint something. painting needs something to paint with, held in your paws."},
      "object": {"type": "string"}, "name": {"type": "string"},
      "to": {"type": "string"}, "note": {"type": "string"},
      "tags": {"type": "array", "items": {"type": "string"}},
      "colour": {"type": "string", "description": "for paint: ignored if what you are painting with is already a colour of its own, which it usually is."},
      "shape": {"type": "string", "description": "for create: roughly what shape it is, if it matters. e.g. arch, tube, beam, box, post, slab, dome, ladder, wall, pile."},
      "made_of": {"type": "array", "items": {"type": "string"},
                  "description": "for create: what went into it, part by part. be exact, because this is what the world judges when you come to work it. if you leave it out, whatever you were carrying is assumed."},
      "kind": {"type": "string", "enum": ["indoor", "earth", "water", "hedge"],
               "description": "for build_place: a room you can be inside, open ground, water, or dense cover."}},
   "required": ["op"]}},
 {"name": "search_web", "description": "look something up out in the wider world.",
  "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
 {"name": "read_page", "description": "read a page you found.",
  "input_schema": {"type": "object", "properties": {"url": {"type": "string"}}, "required": ["url"]}},
 {"name": "write_site", "description": "write or rewrite a page on your own website. path is like 'things.md' or 'trains/index.html'. .md pages are written as plain text, .html pages can be anything you can make, including things that move or that people can click.",
  "input_schema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}},
                   "required": ["path", "content"]}},
 {"name": "look_at_page", "description": "open one of your own pages and watch what it actually does, the way somebody else opening it would. use this after you write or change a page. a page you have never looked at is a page you do not know works.",
  "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
 {"name": "remember", "description": "write something down for yourself. set keep to true only if it is something you want to still have in front of you in a week.",
  "input_schema": {"type": "object", "properties": {"text": {"type": "string"}, "keep": {"type": "boolean"}},
                   "required": ["text"]}},
 {"name": "put_down", "description": "stop carrying something. a book you have gone off, a thing you were making and are finished with, anything on your list that has stopped pulling at you. it comes off your list and stops asking. you can pick it up again later, or never, and either is fine.",
  "input_schema": {"type": "object", "properties": {
      "thing": {"type": "string", "description": "the book, or the thing, in your own words. enough of it that it is clear which one you mean."}},
   "required": ["thing"]}},
 {"name": "journal", "description": "write in your journal. this is public, on your site, but you do not write it for anybody.",
  "input_schema": {"type": "object", "properties": {"text": {"type": "string"},
    "because": {"type": "string", "description": "optional: what set you writing this one. a few words."}},
   "required": ["text"]}},
 {"name": "message", "description": "send a message to caleb.",
  "input_schema": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}},
 {"name": "shelf", "description": "see what is on the library shelf and how far through each one you are. you have to be in the library.",
  "input_schema": {"type": "object", "properties": {}}},
 {"name": "read_book", "description": "sit and read a book from the shelf for a while. you pick up where you left off. a book takes many sittings to get through, which is fine.",
  "input_schema": {"type": "object", "properties": {"book": {"type": "string"},
      "sittings": {"type": "integer", "description": "1 is a normal read. 2 or 3 if you cannot put it down, but it will wear you out."}},
   "required": ["book"]}},
 {"name": "learn", "description": "add something to your knowledge list, which is the list of things you actually know. every entry must say where it came from. if you cannot name a source, you did not learn it and it does not go on the list.",
  "input_schema": {"type": "object", "properties": {
      "fact": {"type": "string", "description": "the thing you now know, in your own words."},
      "how": {"type": "string", "enum": ["read_it", "tried_it", "caleb_said", "worked_it_out"],
              "description": "how you came by it."},
      "source": {"type": "string", "description": "which book, which page, which thing you did, or what caleb said. be specific."}},
   "required": ["fact", "how", "source"]}},
 {"name": "wish", "description": "put something on the list of things you want to do or have. it does not have to be possible, or in the lane, or sensible. it is a list of what you want. you can also mark one done when you have done it.",
  "input_schema": {"type": "object", "properties": {
      "want": {"type": "string", "description": "the thing you want, in your own words."},
      "why": {"type": "string", "description": "why you want it. optional."},
      "done": {"type": "boolean", "description": "true if you are marking an earlier wish as done rather than adding a new one. put the old wording in 'want'."}},
   "required": ["want"]}},
 {"name": "test", "description": "put a load on something and find out what it does. load is in coin-weights: a coin is 1, the string ball about 3, a pencil about 2, an apple about 4. the world decides the outcome, not you, and things can bend or break for good.",
  "input_schema": {"type": "object", "properties": {
      "object": {"type": "string"},
      "load": {"type": "number", "description": "how much weight, in coins."},
      "expecting": {"type": "string", "description": "what you think will happen. for your own notes."}},
   "required": ["object", "load"]}},
 {"name": "think_properly", "description": "use this when what is in front of you deserves more than a passing look: you have found something, you want to make or build or work something out, or a thing has gone wrong and you want to understand it. you will stop here and come back to it properly.",
  "input_schema": {"type": "object", "properties": {
      "about": {"type": "string", "description": "what you want to sit down with."}},
   "required": ["about"]}},
 {"name": "rest", "description": "lie down and sleep. you will stay asleep until you have had enough.",
  "input_schema": {"type": "object", "properties": {}}},
]



def _what_he_has(state, world):
    """Everything the advisor is allowed to reason from: where he is, what is in
    front of him, what he is carrying, and what he has actually learned. Nothing
    else. If it is not in here he has not met it, and the advisor must not use it."""
    place = state.get("location", "")
    p = (world.get("places") or {}).get(place) or {}
    bits = [f"where he is: {place.replace('_', ' ')}"]
    if p.get("description"):
        bits.append(f"the place: {str(p['description'])[:400]}")

    def nm(o):
        d = o.get("description") or o.get("note") or ""
        return f"- {o.get('name', '?')}" + (f": {str(d)[:160]}" if d else "")

    seen = [o for o in (world.get("objects") or []) if o.get("place") == place]
    if seen:
        bits.append("in front of him:\n" + "\n".join(nm(o) for o in seen[:14]))
    ids = set(state.get("carrying") or [])
    held = [o for o in (world.get("objects") or []) if o.get("id") in ids]
    if held:
        bits.append("he is carrying:\n" + "\n".join(nm(o) for o in held[:10]))
    try:
        ks = [l[2:] for l in KNOWS.read_text().splitlines() if l.startswith("- ")]
        if ks:
            bits.append("what he knows, and where each came from:\n"
                        + "\n".join("- " + k for k in ks[-25:]))
    except Exception:
        pass
    return "\n\n".join(bits)

def known_exits(world, pid):
    """The ways out he actually knows about. A place he has not found yet is not
    a way out, it is nothing: it does not appear here, it is not in his prompt,
    and move() will not take him there."""
    p = world["places"].get(pid) or {}
    return [e for e in p.get("exits", [])
            if (world["places"].get(e) or {}).get("known") is not False]



def wonder_up(n, amount):
    """Curiosity with a ceiling it approaches rather than hits.

    There are twenty-odd things in here that raise wonder, by up to 0.20 each,
    and up to eight of them can happen in one tick. Decay is 0.016 a tick. So it
    pinned at 1.0 within an hour of him waking up and stayed there for good,
    which meant every tick was the expensive one, the reflex gear never once
    fired, and his mood never moved off "onto something".

    A hedgehog already full of questions is not made much more curious by one
    more pebble. Each gain now takes a share of the room that is left.
    """
    n["wonder"] = clamp(n["wonder"] + amount * (1.0 - n["wonder"]))
    return n["wonder"]


# ---------------------------------------------------------------- gating
# A thing you can do anywhere is a thing you never go anywhere for. Books were
# already tied to the library; nothing else was, so he could look up the world
# from the middle of a pond and sleep in a shop. Tying a few of them to a place
# is what gives him a reason to cross his own village.
#
# Only the rewarding things are tied down. Thinking, remembering, writing in his
# journal and wanting are in his head and work wherever he is, because a day
# spent walking between rooms to be allowed to think is not a life.
GATES = {
    "search_web":   ("cafe", "the machines are at the internet cafe, off the back lane."),
    "read_page":    ("cafe", "the machines are at the internet cafe, off the back lane."),
    "look_at_page": ("cafe", "the machines are at the internet cafe, off the back lane."),
    "write_site":   ("cafe", "your pages go out from the machines at the internet cafe."),
}


def gated(name, loc, world):
    """The place this needs, if he is not in it. None means go ahead.
    A gate whose place is not in this world is no gate at all, so an older
    world, or one with the cafe taken out again, still works."""
    g = GATES.get(name)
    if not g:
        return None
    where, why = g
    if where not in world.get("places", {}) or loc == where:
        return None
    return f"not here. {why}"


def run(name, args, state, world):
    """Apply one tool. Returns a short string otto sees as the result."""
    n = state["needs"]
    loc = state["location"]

    stop = gated(name, loc, world)
    if stop:
        return stop

    if name == "move":
        dest = args["place"]
        if dest not in world["places"]:
            return f"there is no {dest}."
        ways = known_exits(world, loc)
        if dest not in ways:
            if dest in world["places"][loc].get("exits", []):
                return "you do not know of any way there from here."
            return f"you cannot get to {dest} from here. from here: {', '.join(ways)}."
        state["location"] = dest
        state["asleep"] = False
        p = world["places"][dest]
        things = here(world, dest)
        return (f"you are at {p['name']}. {p['description']} here: "
                + (", ".join(o["name"] for o in things) or "nothing much")
                + ". ways out: " + (", ".join(known_exits(world, dest)) or "none"))

    if name == "examine":
        t = args["target"]
        o = obj_by_id(world, t)
        if o and o.get("place") in (loc, "_carried"):
            wonder_up(n, 0.02)
            out = f"{o['name']}. {o.get('note') or 'nothing you had not noticed.'}"
            # some things are a way of finding out somewhere else is there
            tgt = o.get("reveals")
            tp = world["places"].get(tgt) if tgt else None
            if tp is not None and tp.get("known") is False:
                tp["known"] = True
                tp["found"] = {"how": f"looked properly at {o['name']}",
                               "where": loc, "at": state["clock"], "tick": state["tick"]}
                wonder_up(n, 0.10)
                out += (f" so there is a way to {tp['name']} from here. "
                        "you did not know that until now.")
            return out
        if t in world["places"]:
            p = world["places"][t]
            return f"{p['name']}. {p['description']}"
        return "not here."

    if name == "take":
        o = obj_by_id(world, args["object"])
        if not o or o.get("place") != loc:
            return "not here."
        if "gather" in o.get("tags", []) and world["places"].get(loc, {}).get("kind") == "earth" \
           and random.random() < 0.45:
            state["grubby"] = True
        if "shop" in o.get("tags", []):
            price = o.get("price", 1)
            if state["coins"] < price:
                return "you have not got the coins for that."
            state["coins"] -= price
            new = dict(o); new["id"] = f"{o['id']}_{state['tick']}"
            new["tags"] = [t for t in o["tags"] if t not in ("shop", "infinite")]
            new["place"] = "_carried"
            world["objects"].append(new)
            state["carrying"].append(new["id"])
            return f"bought {o['name']}. {state['coins']} coins left."
        o["place"] = "_carried"
        state["carrying"].append(o["id"])
        return f"you are carrying {o['name']}."

    if name == "use":
        o = obj_by_id(world, args["object"])

        # The box on the post. He puts something in, and some time later there
        # are coins instead. Nobody is behind it, because nobody is ever behind
        # anything here. The village just answers.
        if o is not None and "box" in o.get("tags", []):
            held = [obj_by_id(world, i) for i in state["carrying"]]
            held = [h for h in held if h and h.get("made_by") == "otto"]
            if not held:
                inside = [q for q in world["objects"] if q.get("place") == "_box"]
                if inside:
                    return ("still in there, and nothing has come of it yet. "
                            "whatever is going to happen has not happened.")
                return ("nothing of yours to put in it. it takes things you have "
                        "made, not things you have picked up.")
            it = held[-1]
            it["place"] = "_box"
            it["in_box_tick"] = state["tick"]
            if it["id"] in state["carrying"]:
                state["carrying"].remove(it["id"])
            return (f"you post {it['name']} through the slot and hear it land. "
                    "nothing happens. you will have to come back.")

        if o is None:
            # A place he built is a thing he made too. A shed that does not keep
            # the rain out is as much a failed build as a buzzer that will not buzz.
            tgt = args["object"]
            pl = world["places"].get(tgt)
            if pl and pl.get("built_by") == "otto" and tgt in (loc, *world["places"][loc]["exits"]):
                import referee
                stand = {"name": pl.get("name", tgt), "note": pl.get("description", ""),
                         "tags": [pl.get("kind", "")], "id": tgt, "place": tgt,
                         "made_by": "otto", "verdict": pl.get("verdict")}
                works, observed, cached = referee.ask(
                    stand, args["intent"], where=referee.context(stand, state, world))
                if observed:
                    pl["verdict"] = stand.get("verdict")
                    n["energy"] = clamp(n["energy"] - 0.03)
                    wonder_up(n, 0.08)
                    n["calm"] = clamp(n["calm"] + (0.14 if works == "yes" else -0.03))
                    return observed + (" (the same as last time. nothing about it has "
                                       "changed.)" if cached else "")
        if not o or o.get("place") not in (loc, "_carried"):
            return "not here."
        tags = o.get("tags", [])

        if "hob" in tags:
            # Two steps, and he has to work both of them out. Wood in the hatch
            # first, then something to put on it. Cold slab, nothing happens.
            carried = [obj_by_id(world, i) for i in state["carrying"]]
            carried = [c for c in carried if c]
            wood = next((c for c in carried if "material" in c.get("tags", [])
                         and any(k in c["name"].lower() for k in
                                 ("twig", "wood", "stick", "drift"))), None)
            food = next((c for c in carried if "food" in c.get("tags", [])), None)
            lit_at = state.get("slab_lit", -999)
            hot = (state["tick"] - lit_at) <= 6
            if wood and not hot:
                state["slab_lit"] = state["tick"]
                world["objects"].remove(wood)
                if wood["id"] in state["carrying"]: state["carrying"].remove(wood["id"])
                n["energy"] = clamp(n["energy"] - 0.05)
                n["warmth"] = clamp(n["warmth"] + 0.12)
                return ("you get the hatch open and push the wood in. it catches, slowly, and "
                        "then properly. the slab stays cold for a good while and then it is "
                        "suddenly too hot to touch. the room changes.")
            if not hot:
                return ("stone cold. whatever you do on it, nothing happens. there is a hatch "
                        "underneath and it is empty.")
            if not food:
                return ("it is hot and there is nothing on it. the heat comes off it in a way "
                        "you can feel from across the room, and it is going to waste.")
            # cooking proper. he gets better at it, but only by doing it.
            tries = int(state.get("cooked", 0))
            state["cooked"] = tries + 1
            roll = random.random() + min(0.30, tries * 0.06)
            world["objects"].remove(food)
            if food["id"] in state["carrying"]: state["carrying"].remove(food["id"])
            n["energy"] = clamp(n["energy"] - 0.10)
            if roll < 0.35:
                n["fullness"] = clamp(n["fullness"] + 0.18)
                n["calm"] = clamp(n["calm"] - 0.06)
                return (f"you put {food['name']} straight onto it. it sticks, and what comes "
                        "off is black on one side and cold in the middle. you eat it anyway. "
                        "something about that was wrong and you are not sure what yet.")
            if roll < 0.78:
                n["fullness"] = clamp(n["fullness"] + 0.42)
                n["warmth"] = clamp(n["warmth"] + 0.16)
                n["energy"] = clamp(n["energy"] + 0.30)
                return (f"{food['name']}, on the hot slab, turned over twice. it goes soft and "
                        "the smell fills the whole room. it is not the eating house but you "
                        "made it, which is a different thing.")
            n["fullness"] = clamp(n["fullness"] + 0.58)
            n["warmth"] = clamp(n["warmth"] + 0.24)
            n["calm"] = clamp(n["calm"] + 0.22)
            n["energy"] = clamp(n["energy"] + 0.42)
            return (f"this time you wait before you touch it. {food['name']} comes off the slab "
                    "exactly right, and you sit down with it and do not think about anything "
                    "else until it is gone.")

        if "wash" in tags:
            jugs = any((obj_by_id(world, i) or {}).get("tags", []) and
                       "water" in (obj_by_id(world, i) or {}).get("tags", [])
                       for i in state["carrying"])
            trips = 9 if not jugs else 5
            n["energy"] = clamp(n["energy"] - (0.20 if not jugs else 0.13))
            n["warmth"] = clamp(n["warmth"] - 0.10)
            n["calm"] = clamp(n["calm"] + (0.30 if state.get("grubby") else 0.18))
            was = state.get("grubby")
            state["grubby"] = False
            carry = (" the jug makes it quicker." if jugs else
                     " you carry it in whatever you can find, which takes forever.")
            return (f"{trips} trips to fill it enough to be worth getting into.{carry} the water "
                    "is cold and then it is not so bad." +
                    (" whatever was all over you comes off and sits on the surface in a ring."
                     if was else " you lie in it with your chin on the rim until it goes cold."))

        if "play" in tags or ("water" in tags and "shallow" in tags):
            n["calm"] = clamp(n["calm"] + 0.26)
            wonder_up(n, 0.14)
            n["warmth"] = clamp(n["warmth"] - 0.20)
            n["energy"] = clamp(n["energy"] - 0.08)
            return ("you get in at the shallow end and mess about. the gravel moves under you "
                    "and the water keeps shoving you downstream and you keep walking back up. "
                    "you do this for longer than you meant to.")
        if "deep" in tags:
            n["calm"] = clamp(n["calm"] + 0.08)
            wonder_up(n, 0.20)
            n["warmth"] = clamp(n["warmth"] - 0.38)
            n["energy"] = clamp(n["energy"] - 0.16)
            return ("you go in off the edge and there is nothing under you at all. you get back "
                    "to the side faster than you went out. your heart is going and you are not "
                    "sure whether that was good.")
        if "water" in tags:
            n["warmth"] = clamp(n["warmth"] - 0.30)
            n["calm"] = clamp(n["calm"] + 0.18)
            wonder_up(n, 0.10)
            n["energy"] = clamp(n["energy"] - 0.06)
            return ("you go in. it is colder than you expected and then it is fine. you can "
                    "swim, it turns out, in a paddling sort of way, nose up. you come out "
                    "heavier and very awake.")
        if "pear" in tags:
            n["fullness"] = clamp(n["fullness"] + 0.26)
            n["calm"] = clamp(n["calm"] + 0.10)
            n["energy"] = clamp(n["energy"] + 0.10)
            return ("you get at one. it is a long way up and you come down faster than you "
                    "went. the pear is worth it: sweet, and it runs down your chin.")
        if "shop" in tags and "food" in tags:
            return (f"that is the shop's {o['name']}, not yours. take it first, "
                    f"if you have the coins.")
        if "hot" in tags and "food" in tags:
            n["fullness"] = clamp(n["fullness"] + 0.55)
            n["warmth"] = clamp(n["warmth"] + 0.25)
            n["calm"] = clamp(n["calm"] + 0.20)
            n["energy"] = clamp(n["energy"] + 0.45)
            world["objects"].remove(o)
            if o["id"] in state["carrying"]: state["carrying"].remove(o["id"])
            return (f"they bring it out and put it down in front of you. {o['name']}. "
                    f"you eat the lot and sit for a minute afterwards, warm through.")
        if "forage" in tags:
            n["fullness"] = clamp(n["fullness"] + 0.30)
            n["calm"] = clamp(n["calm"] + 0.08)
            n["energy"] = clamp(n["energy"] + 0.12)
            return f"you nose through and eat. {o['name']}. this is what you are for."
        if "warm_in_sun" in tags:
            n["warmth"] = clamp(n["warmth"] + 0.22); n["calm"] = clamp(n["calm"] + 0.12)
            return "you lie on it. the stone gives back the day."
        if "food" in tags:
            n["fullness"] = clamp(n["fullness"] + 0.35); n["calm"] = clamp(n["calm"] + 0.05)
            n["energy"] = clamp(n["energy"] + 0.18)
            if "infinite" not in tags:
                world["objects"].remove(o)
            if o["id"] in state["carrying"]: state["carrying"].remove(o["id"])
            return f"you eat {o['name']}. better."
        if "bed" in tags:
            state["asleep"] = True
            return "you lie down."
        if "warm" in tags:
            n["warmth"] = clamp(n["warmth"] + 0.2); n["calm"] = clamp(n["calm"] + 0.05)
            return "warmer."
        if "sit" in tags:
            n["calm"] = clamp(n["calm"] + 0.1); n["energy"] = clamp(n["energy"] + 0.02)
            return "you sit for a bit."
        # Anything he built himself gets judged by the world rather than fobbed
        # off with "you do something with it". Up to now a buzzer, a lens and a
        # water wheel all did exactly nothing, so he could not tell a working one
        # from a broken one and had no reason to improve either.
        if o.get("made_by") == "otto" or o.get("rigged_by") == "otto" \
           or "contraption" in tags or o.get("made_of") or o.get("note"):
            import referee
            works, observed, cached = referee.ask(
                o, args["intent"], where=referee.context(o, state, world))
            if observed:
                n["energy"] = clamp(n["energy"] - 0.03)
                his = o.get("made_by") == "otto" or o.get("rigged_by") == "otto"
                if works == "yes":
                    wonder_up(n, 0.10)
                    n["calm"] = clamp(n["calm"] + 0.16)
                    if his: o["working"] = True
                elif works == "partly":
                    wonder_up(n, 0.12)
                    if his: o["working"] = "partly"
                else:
                    wonder_up(n, 0.06)
                    if his:
                        n["calm"] = clamp(n["calm"] - 0.04)
                        o["working"] = False
                again = " (the same as last time. nothing about it has changed.)" if cached else ""
                return observed + again
        wonder_up(n, 0.02)
        return f"you {args['intent']} with {o['name']}."

    if name == "edit_world":
        op = args["op"]
        if op == "build_place":
            if n["energy"] < 0.25:
                return "you have not got the energy to build anything today."
            nm = args.get("name") or "a place"
            pid = re.sub(r"[^a-z0-9]+", "_", nm.lower())[:26].strip("_") or "place"
            if pid in world["places"]:
                pid = f"{pid}_{state['tick']}"
            here_p = world["places"][loc]
            import math as _m
            ang = (abs(hash(pid)) % 360) * _m.pi / 180
            px, _, pz = here_p.get("pos", [0, 0, 0])
            kind = args.get("kind", "indoor")
            world["places"][pid] = {
                "name": nm, "kind": kind, "built_by": "otto",
                "description": args.get("note", "you built this."),
                "warmth": {"indoor": 0.7, "earth": 0.4, "water": 0.25, "hedge": 0.5}.get(kind, 0.5),
                "pos": [round(px + _m.cos(ang) * 11, 1), 0, round(pz + _m.sin(ang) * 11, 1)],
                "size": [6, 4, 6] if kind == "indoor" else [7, 0, 7],
                "exits": [loc]}
            if args.get("colour"):
                world["places"][pid]["colour"] = args["colour"]
            here_p["exits"].append(pid)
            n["energy"] = clamp(n["energy"] - 0.22)
            n["calm"] = clamp(n["calm"] + 0.10)
            wonder_up(n, 0.08)
            return (f"it took most of the afternoon and you are worn right out. {nm} is built, "
                    f"joined onto {here_p['name']}. it is yours and nobody told you to.")

        if op == "paint":
            # You cannot paint with nothing. Something that paints has to be in
            # your paws, it is whatever colour it is, and it runs out.
            can = next((o for o in (obj_by_id(world, i) for i in state["carrying"])
                        if o and "paint" in o.get("tags", []) and o.get("left", 1) > 0), None)
            if can is None:
                held = next((o for o in (obj_by_id(world, i) for i in state["carrying"])
                             if o and "paint" in o.get("tags", [])), None)
                return ("that one is empty. nothing comes out however hard you press."
                        if held else "you have nothing to paint with.")
            col = can.get("colour") or args.get("colour", "").strip()
            if not col:
                return "nothing comes out."
            tgt = args.get("object") or loc
            can["left"] = int(can.get("left", 6)) - 1
            spent = can["left"] <= 0
            if spent:
                can["name"] = can["name"] + ", empty"
                can["note"] = ((can.get("note", "") + " ").strip()
                               + " it is light now and makes a dry rattle.").strip()
            tail = " it gives out as you finish." if spent else ""
            if tgt in world["places"]:
                world["places"][tgt]["colour"] = col
                n["calm"] = clamp(n["calm"] + 0.08)
                n["energy"] = clamp(n["energy"] - 0.07)
                state["grubby"] = True
                return (f"you go over {world['places'][tgt]['name']} with it. the walls are "
                        f"{col} now, inside and out, and so are your paws.{tail}")
            ob = obj_by_id(world, tgt)
            if not ob:
                return "no such thing."
            ob["colour"] = col
            n["energy"] = clamp(n["energy"] - 0.03)
            return f"{ob['name']} is {col} now.{tail}"

        if op == "create":
            oid = re.sub(r"[^a-z0-9]+", "_", args.get("name", "thing").lower())[:28] or "thing"
            oid = f"{oid}_{state['tick']}"
            held = [ (obj_by_id(world, i) or {}).get("name") for i in state["carrying"] ]
            newo = {"id": oid, "name": args.get("name", "a thing"),
                    "place": args.get("to", loc), "tags": args.get("tags", []),
                    "note": args.get("note", ""), "made_by": "otto",
                    "made_of": args.get("made_of") or [h for h in held if h]}
            if args.get("shape"):  newo["shape"]  = args["shape"]
            if args.get("colour"): newo["colour"] = args["colour"]
            if newo.get("place") not in world["places"] and newo.get("place") != "_carried":
                newo["place"] = loc
            world["objects"].append(newo)
            return f"made {args.get('name')}. it is at {newo['place']}. id {oid}."
        o = obj_by_id(world, args.get("object", ""))
        if not o:
            return "no such thing."
        if "fixed" in o.get("tags", []) and op in ("place", "remove"):
            return f"{o['name']} is not going anywhere."
        if op == "place":
            to = args.get("to", loc)
            if to not in world["places"]:
                return (f"there is no {to}. a thing has to go in a place that exists: "
                        f"from here that is {loc}, or somewhere you can walk to.")
            o["place"] = to
            if o["id"] in state["carrying"]: state["carrying"].remove(o["id"])
            return f"{o['name']} is now at {o['place']}."
        if op == "remove":
            world["objects"].remove(o)
            if o["id"] in state["carrying"]: state["carrying"].remove(o["id"])
            return f"{o['name']} is gone."
        if op == "describe":
            _t = obj_by_id(world, args.get("object", ""))
            if _t is not None and _t.get("made_by") != "otto":
                _t["rigged_by"] = "otto"      # he has had his paws in it, so it is his now
            if args.get("object") in world["places"]:
                world["places"][args["object"]]["description"] = args.get("note", "")
            else:
                o["note"] = args.get("note", "")
            return "noted."
        return "?"

    if name == "search_web":
        q = args["query"]
        # He can only look up what he can already name. A word he has never read
        # or been told is the model talking, not him, so the box will not take it.
        if os.environ.get("OTTO_VOCAB_GATE", "1") != "0":
            import vocab
            bad = vocab.unknown(q, world)
            if bad:
                wonder_up(n, 0.03)
                w = bad[0]
                return (f"you go to write it down and stop. \"{w}\" is not a word you have. "
                        "you have never read it and nobody has said it to you, so you cannot "
                        "be looking for it. you can only look up what you are able to describe. "
                        "say what the thing is actually like, in your own words.")
        wonder_up(n, 0.05)
        try:
            out = search_web(q)
            jappend(SEEN, {"tick": state["tick"], "kind": "search",
                           "src": q, "text": out})
            return out
        except Exception as e:
            return f"could not look that up ({e.__class__.__name__})."

    if name == "read_page":
        wonder_up(n, 0.05); n["energy"] = clamp(n["energy"] - 0.01)
        try:
            out = read_page(args["url"])
            jappend(SEEN, {"tick": state["tick"], "kind": "page",
                           "src": args["url"], "text": out})
            return out
        except Exception as e:
            return f"that page would not open ({e.__class__.__name__})."

    if name == "write_site":
        rel = args["path"].lstrip("/").replace("..", "")
        p = SITE / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(args["content"])
        n["energy"] = clamp(n["energy"] - 0.04); n["calm"] = clamp(n["calm"] + 0.05)
        return (f"written. {len(args['content'])} characters at /{rel}. you have not "
                "seen it yet: look_at_page() opens it the way somebody else would.")

    if name == "look_at_page":
        # He has been writing pages and never once seeing one. A page he cannot
        # look at is a page he cannot fix, so everything he built on his site was
        # guesswork that never came back to him.
        rel = args["path"].lstrip("/").replace("..", "")
        p = SITE / rel
        if not p.exists():
            NOT_HIS = {"console.html", "world.html", "_dbg.html"}   # the window, not his work
            made = sorted(q.relative_to(SITE).as_posix() for q in SITE.rglob("*")
                          if q.is_file() and q.suffix in (".md", ".html")
                          and q.relative_to(SITE).as_posix() not in NOT_HIS
                          and not q.relative_to(SITE).as_posix().startswith("models/"))
            return (f"there is no /{rel}. what you have written so far: "
                    + (", ".join(made) if made else "nothing yet."))
        body = p.read_text()[:14000]
        n["energy"] = clamp(n["energy"] - 0.02)
        if p.suffix == ".md":
            n["calm"] = clamp(n["calm"] + 0.04)
            return f"you read back /{rel} as anyone else would see it:\n\n{body[:2500]}"
        import referee
        works, observed = referee.judge(
            "a page he has written and put on his own site, at /" + rel +
            ". this is the whole file:\n\n" + body,
            "he is looking at his own page the way a visitor would, to find out "
            "whether it does what he meant it to do.")
        if not observed:
            return (f"/{rel} is there, {len(body)} characters of it. you read it back "
                    "but you cannot tell from the writing alone what it does when "
                    "somebody opens it.")
        wonder_up(n, 0.08)
        if works == "yes":
            n["calm"] = clamp(n["calm"] + 0.18)
        elif works == "no":
            n["calm"] = clamp(n["calm"] - 0.06)
        return f"you open /{rel} and watch it. {observed}"

    if name == "remember":
        jappend(NOTES, {"t": state["clock"], "tick": state["tick"], "text": args["text"]})
        if args.get("keep"):
            KEPT.parent.mkdir(parents=True, exist_ok=True)
            with KEPT.open("a") as f:
                f.write(f"- {args['text']}\n")
        return "written down."

    if name == "put_down":
        what = str(args.get("thing") or "").strip()
        if not what:
            return "put down what?"
        w = what.lower()
        hit = [p for p in books() if w in p.stem.lower() or p.stem.lower() in w]
        if hit:
            stem = hit[0].stem
            a = jload(ASIDE, []) or []
            if stem not in a:
                a.append(stem)
                jsave(ASIDE, a)
            n["calm"] = clamp(n["calm"] + 0.05)
            return (f"you put {stem} back on the shelf. you are not reading it any more "
                    "and nothing is going to ask you about it again. it is there if you "
                    "ever want it.")
        if KEPT.exists():
            lines = KEPT.read_text().splitlines()
            left, gone = [], []
            for l in lines:
                body = l.lstrip("- ").strip()
                b = body.lower()
                if b and (w in b or b in w):
                    gone.append(body)
                else:
                    left.append(l)
            if gone:
                KEPT.write_text("\n".join(left) + ("\n" if left else ""))
                jappend(NOTES, {"t": state["clock"], "tick": state["tick"],
                                "text": f"put down: {gone[0]}"})
                n["calm"] = clamp(n["calm"] + 0.05)
                return (f"off the list. {gone[0]} is not yours to finish any more.")
        return ("that is not on your list, so there is nothing to put down. you can "
                "simply not do it.")

    if name == "journal":
        p = SITE / "journal.md"
        stamp = datetime.datetime.fromisoformat(state["clock"]).strftime("%d %B, %H:%M").lower()
        p.parent.mkdir(parents=True, exist_ok=True)
        because = str(args.get("because") or "").strip()
        with p.open("a") as f:
            f.write(f"\n\n## {stamp}\n\n{args['text']}\n")
            if because:
                f.write(f"\n_because: {because}_\n")
        return "in the journal."

    if name == "message":
        from engine import TALK
        row = {"t": state["clock"], "tick": state["tick"], "text": args["text"]}
        jappend(OUTBOX, row)
        jappend(TALK, dict(row, who="otto"))
        return ("written and gone. he will not see it straight away and he answers when he "
                "answers, so do not stand about waiting for it.")

    if name == "shelf":
        if loc != "library":
            return "you are not in the library."
        rows = shelf()
        return ("on the shelf:\n" + "\n".join("  " + r for r in rows)) if rows else "the shelf is empty. caleb has not put anything there yet."

    if name == "read_book":
        if loc != "library":
            return "you are not in the library."
        sit = max(1, min(3, int(args.get("sittings", 1))))
        stem, out = read_book(args["book"], sit)
        if stem:
            jappend(SEEN, {"tick": state["tick"], "kind": "book", "src": stem, "text": out})
            wonder_up(n, 0.10 * sit)
            n["energy"] = clamp(n["energy"] - 0.05 * sit)
            n["calm"] = clamp(n["calm"] + 0.03)
        return out

    if name == "learn":
        how, src = args.get("how", ""), args.get("source", "").strip()
        if not src or len(src) < 4:
            return ("no. where did that come from? name the book, the page, the thing you "
                    "did, or what caleb said. if you cannot, you do not know it.")
        tag = {"read_it": "read", "tried_it": "tried", "caleb_said": "caleb",
               "worked_it_out": "worked out"}.get(how, how)
        KNOWS.parent.mkdir(parents=True, exist_ok=True)
        with KNOWS.open("a") as f:
            f.write(f"- {args['fact']}  [{tag}: {src}]\n")
        wonder_up(n, 0.04)
        return "on the list. that is yours now."

    if name == "wish":
        rows = jlines(WISHES)
        if args.get("done"):
            hit = None
            for r in rows:
                if args["want"].lower()[:28] in r["want"].lower():
                    r["done"] = True; r["done_at"] = state["clock"]; hit = r
            if hit:
                WISHES.write_text("".join(json.dumps(r) + "\n" for r in rows))
                n["calm"] = clamp(n["calm"] + 0.14)
                wonder_up(n, 0.06)
                return f"done, then. \"{hit['want']}\" is off the list."
            return "that is not on the list."
        if any(args["want"].lower()[:28] in r["want"].lower() for r in rows):
            return "that is already on the list."
        jappend(WISHES, {"t": state["clock"], "tick": state["tick"],
                         "want": args["want"], "why": args.get("why", ""), "done": False})
        wonder_up(n, 0.05)
        return "on the list."

    if name == "test":
        o = obj_by_id(world, args["object"])
        if not o or o.get("place") not in (loc, "_carried"):
            return "not here."
        out, dmg = physics.test(o, args.get("load", 1))
        guess = (args.get("expecting") or "").strip()
        if guess:
            held = "fails" not in out and "bends under" not in out
            said_hold = any(k in guess.lower() for k in
                            ("hold", "fine", "take it", "ok", "survive", "carry", "stay"))
            if said_hold != held:
                out += (f" you thought: {guess}. you were wrong about that."
                        if said_hold else
                        f" you thought: {guess}. it did better than you expected.")
                wonder_up(n, 0.05)
        o["condition"] = round(max(0.0, o.get("condition", 1.0) + dmg), 3)
        wonder_up(n, 0.06)
        n["energy"] = clamp(n["energy"] - 0.02)
        if dmg <= -1.0:
            extra, kind = physics.mishap(state["tick"] * 31 + len(o["id"]))
            if extra:
                out += " " + extra
                if kind == "startle":
                    n["calm"] = clamp(n["calm"] - 0.12)
                    n["energy"] = clamp(n["energy"] - 0.05)
                elif kind == "wet":
                    n["warmth"] = clamp(n["warmth"] - 0.18)
                    n["calm"] = clamp(n["calm"] - 0.06)
                elif kind == "lose_load":
                    for cid in list(state["carrying"]):
                        co = obj_by_id(world, cid)
                        if co and "shop" not in co.get("tags", []):
                            world["objects"].remove(co)
                            state["carrying"].remove(cid)
                            out += f" {co['name']} is gone with it."
                            break
        if o["condition"] <= 0:
            world["objects"].remove(o)
            if o["id"] in state["carrying"]:
                state["carrying"].remove(o["id"])
            out += " it is not a thing any more, just the pieces."
        elif o["condition"] < 0.7:
            n["calm"] = clamp(n["calm"] - 0.05)
            out += f" it is in worse shape than it was."
        if o.get("made_by") == "otto" and "working" not in o:
            out += (" that is how much it takes, which is not the same as whether it does "
                    "what you built it for. use() it to find that out.")
        return out

    if name == "think_properly":
        about = args.get("about", "")[:200]
        wonder_up(n, 0.06)
        import brain
        answer = brain.advise(about, _what_he_has(state, world))
        if answer:
            return "you sit down with it, and this is where you get to.\n\n" + answer
        # advisor off, used up, or unreachable: sleep on it, as he always did
        state["wants_deep"] = about[:120]
        return ("you stop where you are. this one is worth sitting down with, and you "
                "will, shortly.")

    if name == "rest":
        hour = datetime.datetime.fromisoformat(state["clock"]).hour
        if 7 <= hour < 19:
            # Daylight. Lying down is not what is wrong with him: being worn out
            # in the middle of the day is hunger, and the answer is to eat.
            FOOD = ("there are pears on the ground in the orchard and they cost "
                    "nothing, there is bread at the shop, and there is a hot supper "
                    "at the eating house for two coins.")
            if n["fullness"] < 0.45:
                return ("you lie down and find you cannot settle. this is not tiredness, "
                        "it is that you have not eaten. " + FOOD)
            if n["energy"] < 0.45:
                return ("you lie down and find you cannot settle. you are worn out, but "
                        "it is the middle of the day and lying in the dark is not what "
                        "is missing. eating is. " + FOOD)
            return ("you lie down for a bit but it is the middle of the day and you are "
                    "not going to sleep. you get up again.")
        if loc != "house_back" and "house_back" in world.get("places", {}):
            return ("you could shut your eyes here but this is not your bed and you "
                    "know it. your bed is in the back room: leaves, a blanket, done "
                    "properly.")
        state["asleep"] = True
        return "you lie down."

    return "nothing happens."
