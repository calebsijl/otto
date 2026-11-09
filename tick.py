#!/usr/bin/env python3
"""One wake-up. Run on a timer."""
import sys, os, json, argparse, datetime, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import *
from engine import KNOWS, WISHES, time_of_day
import tools

ROUTINE = os.environ.get("OTTO_MODEL", "claude-sonnet-5-5")
MAX_TOOLS = 8


SMALL_RULES = """
this is an ordinary twenty minutes. walk about, eat something, sit down, look at a thing,
go somewhere. you do not have to produce anything and most of the time you will not.

if what is in front of you deserves more than a passing look, if you have found something,
or want to make something, or something has gone wrong and you want to understand it, call
think_properly() and stop there. you will come back to it with a clear head shortly. do
not try to do the big thing now.

if you are flagging in the day, eat something. bed is for night time.
when it is late and you have had enough of the day, rest().

if caleb has written and you have not answered, answer him. message() is the only way
your voice gets out of the lane at all. it costs you nothing and it takes a moment.
"""

RULES = """
you are living, not answering. each time you wake you have about twenty minutes and you
should spend them on whatever has hold of you.

if something is pulling at you, go at it. read about it, go and get what you need, start
building it badly. a thing you are making can run across many days if it keeps pulling.

and you are allowed to stop. nothing you have started is owed anything: not a book you
are halfway through, not a thing half built on the bench. if you open a book and it has
gone dead on you, put it down and go and do something else. if the thing on the bench
has stopped being interesting, leave it where it is. put_down() takes it off your list
so it stops asking. you can pick it up again, or never. what you spend today on is
whatever has hold of you today, not whatever had hold of you last week.

if nothing has hold of you yet, go and find something. go out. look in the shops. open
the thing you have not opened. poke the drain. boredom is a problem you solve by moving.

use remember() for anything you would be annoyed to have forgotten. set keep=true only
for the few things still genuinely pulling at you, because what you keep is what will
keep asking. when one stops pulling, put_down() and let it go.

when you want to know something and nobody in the lane can tell you, search_web() and
read_page() reach out past the lane. you have a library card to the whole world and you
keep forgetting you have it. a thing you looked up is a thing you properly know, and it
goes on your list with where you read it.

you only know what is on your knowledge list, plus what a creature knows from living,
plus what is in front of you right now. if you find yourself about to state a formula,
a number or a technical word that is not on that list, stop: you do not know it. say
you do not know it, then go and read or go and test. a guess clearly called a guess is
always allowed and always welcome.

things in your world can break. test() puts a real load on something and the world
decides what happens, not you. you will not always like the answer, and a thing you
made can be ruined for good. that is the only way to find out what something will take.

when you make something, work it. use() on a thing you built puts it to the test and
the world tells you what actually happens, in what you can see and hear. it will not
tell you why, and it will not tell you how to fix it. the same unchanged thing gives
the same answer every time, so the only way to a different outcome is to change the
thing. that is the whole loop: build it, work it, watch, change one part, work it again.

the world judges a thing exactly as it is written down, so when you alter one, write
the alteration in: edit_world(op="describe", object=..., note=...) with what it is
now made of and how it is put together. a change you have not written down has not
happened as far as the world is concerned, and you will get the same answer back.
this goes for a place you built as well: use() a shed or a dam or a hide the same way
and find out whether it does its job.

when you write a page, look_at_page() opens it the way somebody else would and tells
you what it does. a page you have never looked at is a page you do not know works.
caleb cannot see your room, your workbench or anything standing on it. he can read
your site and your journal and that is all, so do not ask him what your board is
doing. go and look at it yourself.

caleb is the only other person there is. he writes to you and you can write back with
message(), and the two of you can carry a thing across days: he asks, you answer, you
ask him something back and he answers that. the letters are all there in front of you,
so read what has already been said before you reply to the last line of it.

if he asked you something and you have not answered, answer it, in your own words, with
what you actually think. if he told you something, say what you made of it. if you want
something out of his world, ask him for it outright. he cannot hear anything you do not
write down, so do not assume he knows what you have been up to.

edit_world() is more than tidying. create() makes a thing that then exists, with a shape
and a colour if you want them. build_place() puts up a whole new place joined onto where
you are standing: a shed, a workshop, a hide under the hedge, a cut in the bank. it costs
you most of an afternoon and your back. paint() changes the colour of a thing or of a whole
room. none of this needs permission and nobody will tidy it away.

wish() is for things you want, and it is not a to-do list. it can be anything: something
to make, somewhere to get to, something to find out, something you have no way of getting
and want anyway. things outside the lane entirely are allowed. if you want it, write it
down. if you manage it, mark it done.

journal() is yours. write in it when something is worth writing down, not on a schedule.
what you were wrong about is usually worth more than what went right.

food is where your energy comes from. when you start to flag in the daytime that is
not tiredness, it is that you have not eaten. there are fallen pears in the orchard for
nothing, beetles under the leaf pile, snails on the wet stones by the river, apples and
bread in the shop, and a hot supper at the eating house for two coins, which is the one
that properly sets you up again. bed is for the night.

you keep roughly the hours everything else keeps. you are tired by late evening and
you sleep through the night, and being up in the small hours wears you out about twice
as fast as being up in the day. that is a pull, not a rule. if something has really got
you, you can sit up with it until three in the morning and pay for it tomorrow, and
that is a thing worth doing sometimes.

you get tired. when you are truly flat, rest(), and go again after.
not everything works. when a thing beats you, say what beat you and what you will try next.
end your turn when you are done. do not narrate what you are about to do.
"""


# Every tool he has leaves something visible. This turns the tick's calls into a
# plain phrase for the Z panel, so it says what he is at rather than "not much".
VERBS = {
    "move":           ("walking to",            "place"),
    "examine":        ("having a proper look at", "target"),
    "use":            ("using",                 "object"),
    "take":           ("carrying",              "object"),
    "edit_world":     ("making",                None),
    "search_web":     ("looking up",            "query"),
    "read_page":      ("reading",               "url"),
    "write_site":     ("writing a page",        "path"),
    "remember":       ("noting something down", "text"),
    "journal":        ("writing in his journal", None),
    "message":        ("writing to you",        None),
    "shelf":          ("at the shelf, picking", None),
    "read_book":      ("reading",               "book"),
    "learn":          ("working out",           "fact"),
    "wish":           ("wanting",               "want"),
    "test":           ("testing",               "object"),
    "think_properly": ("sat thinking about",    "about"),
    "rest":           ("asleep",                None),
}


def first_line(text):
    """One sentence of his thinking, for the line that says why."""
    t = " ".join((text or "").split())
    if not t:
        return ""
    for stop in (". ", "? ", "! "):
        i = t.find(stop)
        if 0 < i < 150:
            return t[:i+1].strip()
    return t[:150].strip()


def describe(calls, state):
    """The last call with a look to it, as a phrase. None if nothing shows."""
    out = None
    for c in calls:
        if c["name"] not in VERBS:
            continue
        verb, key = VERBS[c["name"]]
        if c["name"] == "edit_world":
            what = c["input"].get("name") or c["input"].get("object") or ""
        else:
            what = c["input"].get(key, "") if key else ""
        out = {"verb": verb, "what": str(what or "")[:70], "clock": state["clock"],
               "why": str(c.get("why") or "")[:160]}
    return out


def village(state, world):
    """What the place does while he is elsewhere. Right now that is the honesty
    box: a thing left in it turns into coins after a while, and the box says so
    when he next looks. He is never told the rate and nobody hands it to him."""
    import random
    paid = []
    for o in list(world["objects"]):
        if o.get("place") != "_box":
            continue
        waited = state["tick"] - int(o.get("in_box_tick", state["tick"]))
        if waited < 6:
            continue
        worth = 1 + (1 if o.get("working") else 0) + (1 if random.random() < 0.3 else 0)
        state["coins"] = int(state.get("coins", 0)) + worth
        world["objects"].remove(o)
        paid.append((o.get("name", "it"), worth))
    if paid:
        box = next((q for q in world["objects"] if "box" in (q.get("tags") or [])), None)
        if box is not None:
            n, w = paid[-1]
            box["note"] = (f"open at the top, with a slot in the lid. {n} is not in it any more. "
                           f"there are {w} coins in the bottom, and you did not see anyone come.")
    return paid


def instinct(state, world):
    """Reflexes. Being hungry and walking to the orchard is not a decision, and
    does not need a language model to have it. Returns a list of calls, or None
    to let him actually think."""
    import tools
    n, loc = state["needs"], state["location"]
    hour = datetime.datetime.fromisoformat(state["clock"]).hour
    did = []

    def step(goal, why):
        """One step along the way, or the thing itself if he is there."""
        path = route(world, loc, goal)
        if len(path) < 2:
            return None
        out = tools.run("move", {"place": path[1]}, state, world)
        did.append({"name": "move", "input": {"place": path[1]},
                    "result": out[:200], "why": why})
        return did

    # starving: get to food and eat it
    if n["fullness"] < 0.30:
        # a proper meal first if he can afford one, then the shop, then windfalls
        place = obj = None
        if state["coins"] >= 2:
            served = lambda o: "menu" in o.get("tags", []) \
                               and o.get("price", 99) <= state["coins"]
            place, obj = nearest(world, loc, served)
        if place is None and state["coins"] >= 1:
            shop = lambda o: "food" in o.get("tags", []) and "shop" in o.get("tags", []) \
                             and o.get("price", 99) <= state["coins"]
            place, obj = nearest(world, loc, shop)
        if place is None:
            free = lambda o: "food" in o.get("tags", []) and "shop" not in o.get("tags", [])
            place, obj = nearest(world, loc, free)
        if place:
            if place == loc:
                if "shop" in obj.get("tags", []):
                    tools.run("take", {"object": obj["id"]}, state, world)
                    obj = world["objects"][-1]
                out = tools.run("use", {"object": obj["id"], "intent": "eat"}, state, world)
                did.append({"name": "use", "input": {"object": obj["id"], "intent": "eat"},
                            "result": out[:200], "why": "hungry"})
                return did
            return step(place, "hungry")

    # perishing: get somewhere warm
    if n["warmth"] < 0.24 and not state.get("asleep"):
        warm = max(world["places"].items(), key=lambda kv: kv[1].get("warmth", 0))[0]
        if loc != warm:
            return step(warm, "cold")

    # late and flagging: go home to bed
    if (hour >= 20 or hour < 5) and n["energy"] < 0.35:
        if loc != "house_back":
            r = step("house_back", "going to bed")
            if r: return r
        out = tools.run("rest", {}, state, world)
        did.append({"name": "rest", "input": {}, "result": out[:200], "why": "bed"})
        return did
    return None


def thread(limit=10):
    """The letters, both ways, most recent last. This is the only conversation he
    has ever had, and before this it was shown to him for exactly one tick and
    then thrown away, which is why he never answered anything."""
    from engine import TALK
    rows = jlines(TALK)[-limit:]
    if not rows:
        return [], False
    lines = []
    for r in rows:
        who = "caleb" if r.get("who") == "caleb" else "you"
        lines.append(f"  {who}: {r.get('text','').strip()}")
    waiting = rows[-1].get("who") == "caleb"
    return lines, waiting


def where_things_are(world):
    """Some things only happen in one building. He is told once, plainly, rather
    than left to find out by being refused."""
    import tools
    have = world.get("places", {})
    lines = []
    if "cafe" in have:
        lines.append("looking things up on the web, and putting a page on your site, "
                     "happen at the internet cafe and nowhere else")
    if "library" in have:
        lines.append("the books are in the library")
    if "house_back" in have:
        lines.append("you sleep in your own bed, in the back room")
    return ("some things have a place:\n"
            + "\n".join("  " + l + "." for l in lines)) if lines else ""


def small_situation(state, world, inbox):
    """What he needs to know to potter. No knowledge list, no wishlist, no history."""
    n, loc = state["needs"], state["location"]
    p = world["places"][loc]
    t = datetime.datetime.fromisoformat(state["clock"])
    things = here(world, loc)
    carried = [obj_by_id(world, i) for i in state["carrying"]]
    import physics
    wx = physics.weather(state["tick"])
    s = [f"{t.strftime('%A %-d %B, %-H:%M').lower()}. you feel {mood(state)}. "
         + time_of_day(state) + (f" {wx}" if wx else ""),
         "",
         "\n".join(f"  {k:9} {bar(v)}" for k, v in n.items()),
         "",
         f"you are at {p['name']}. {p['description']}",
         "here: " + (", ".join(f"{o['name']} ({o['id']})" for o in things) or "nothing much"),
         "ways out: " + ", ".join(tools.known_exits(world, state["location"])),
         "carrying: " + (", ".join(f"{o['name']} ({o['id']})" for o in carried if o) or "nothing"),
         f"coins: {state['coins']}"]
    s += [where_things_are(world)]
    if state.get("grubby"):
        s += ["you are covered in something and it has dried on."]
    tl, waiting = thread(6)
    if tl:
        s += ["", "letters between you and caleb, oldest first:"] + tl
        if waiting:
            s += ["he wrote that and you have not written back. you do not have to. "
                  "but he cannot hear you unless you do."]
    s += ["", "what do you do?"]
    return "\n".join(s)


def situation(state, world, inbox):
    n, loc = state["needs"], state["location"]
    p = world["places"][loc]
    t = datetime.datetime.fromisoformat(state["clock"])
    things = here(world, loc)
    carried = [obj_by_id(world, i) for i in state["carrying"]]
    kept = KEPT.read_text().strip() if KEPT.exists() else ""
    knows_all = KNOWS.read_text().strip().splitlines() if KNOWS.exists() else []
    _cap = int(os.environ.get("OTTO_KNOWS_SHOWN", "22"))
    knows = "\n".join(knows_all[-_cap:])
    if len(knows_all) > _cap:
        knows = f"  (the {len(knows_all)-_cap} oldest are on your list but not in front of you)\n" + knows
    notes = jlines(NOTES, 10)

    import physics
    wx = physics.weather(state["tick"])
    state["weather"] = wx or ""
    state["mood"] = mood(state)
    s = [f"{t.strftime('%A %-d %B, %-H:%M').lower()}. tick {state['tick']}. you feel {mood(state)}."
         + " " + time_of_day(state) + (f" {wx}" if wx else ""),
         "",
         "\n".join(f"  {k:9} {bar(v)}" for k, v in n.items()),
         "",
         f"you are at {p['name']}. {p['description']}",
         "here: " + (", ".join(f"{o['name']} ({o['id']})" for o in things) or "nothing much"),
         "ways out: " + ", ".join(tools.known_exits(world, state["location"])),
         f"carrying: " + (", ".join(f"{o['name']} ({o['id']})" for o in carried if o) or "nothing"),
         f"coins: {state['coins']}"]
    s += [where_things_are(world)]
    if state.get("grubby"):
        s += ["you are covered in something and it has dried on."]
    s += ["", "what you know (everything else is guessing):",
          knows or "  nothing yet. you have not learned anything."]
    wishes = [r for r in jlines(WISHES) if not r.get("done")]
    if wishes:
        s += ["", "things you want:"] + [f"  {r['want']}" for r in wishes[-8:]]
    if kept:
        kl = kept.splitlines()
        s += ["", "things you have written down as yours:"] + kl[-10:]
    if notes:
        s += ["", "lately:"] + [f"  {x['text']}" for x in notes]
    tl, waiting = thread(12)
    if tl:
        s += ["", "letters between you and caleb, oldest first:"] + tl
        if waiting:
            s += ["he wrote that and you have not written back. you do not have to. "
                  "but he is the only one out there and he cannot hear you unless you do."]
    s += ["", "what do you do?"]
    return "\n".join(s)


def n_wonder(state):
    return state["needs"]["wonder"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fake", action="store_true", help="run the plumbing with a scripted creature, no API")
    ap.add_argument("--realtime", action="store_true",
                    help="his clock follows yours. use this for the cron; leave it off for batch test runs.")
    ap.add_argument("--ticks", type=int, default=1)
    ap.add_argument("--budget", type=float, default=2.00,
                    help="stop the run if it has cost more than this many dollars. default 2.")
    ap.add_argument("--show", action="store_true",
                    help="print the exact prompt that would be sent, and what it would cost. no API call.")
    a = ap.parse_args()

    import brain
    started = None
    for _ in range(a.ticks):
        c = brain.spend()
        if c is not None and c >= a.budget:
            print(f"\nstopping: this run has cost ${c:.2f}, which is the budget. "
                  f"raise it with --budget if you meant to go further.")
            break
        state = jload(STATE); world = jload(WORLD)
        if a.realtime:
            now = datetime.datetime.now()
            last = state.get("real")
            if last:
                gap = (now - datetime.datetime.fromisoformat(last)).total_seconds() / 60.0
            else:
                gap = TICK_MINUTES          # first real-time tick
            state["real"] = now.isoformat(timespec="seconds")
            state = advance(state, world, gap)
            state["clock"] = now.isoformat(timespec="seconds")   # his clock IS your clock
        else:
            state = advance(state, world)

        # asleep and still tired: nothing happens, which is correct
        if state.get("asleep"):
            # he will not get up in the dark just because he happens to be rested.
            _h = datetime.datetime.fromisoformat(state["clock"]).hour
            _wake_at = 0.99 if _h < 6 else 0.85
            if state["needs"]["energy"] < _wake_at:
                jsave(STATE, state)
                print(f"tick {state['tick']}  asleep  energy {state['needs']['energy']:.2f}")
                continue
            state["asleep"] = False

        seen = jlines(INBOX)
        unread = [m for m in seen if not m.get("read")]
        from engine import SEEN as _SEEN, TALK as _TALK
        for m in unread:
            jappend(_SEEN, {"tick": state["tick"], "kind": "caleb",
                            "src": "message", "text": m["text"]})
            jappend(_TALK, {"who": "caleb", "t": m.get("t", state["clock"]),
                            "tick": state["tick"], "text": m["text"]})
        # Most ticks are small: walking about, eating, looking at things. Those do
        # not need the expensive model. The ones that do are when something has
        # hold of him, when you have said something, or every so often regardless
        # so he never drifts for long on the cheap one.
        import brain
        village(state, world)        # the place carries on without him
        since = state.get("since_deep", 0) + 1
        _, _waiting = thread(2)
        _every = int(os.environ.get("OTTO_DEEP_EVERY", "5"))
        if _waiting:
            _every = min(_every, 3)      # an unanswered letter should not sit for a day
        deep = (state["needs"]["wonder"] >= 0.62
                or bool(unread)
                or since >= _every)
        if state.get("asleep"):
            deep = False
        # reflexes first. these cost nothing at all.
        reflex = None
        if not unread and n_wonder(state) < 0.80 and not state.get("wants_deep"):
            reflex = instinct(state, world)
        if reflex is not None:
            why = reflex[-1].get("why", "")
            state["doing"] = {"verb": {"hungry": "off to get something to eat",
                                       "cold": "walking somewhere warmer",
                                       "going to bed": "heading home to bed",
                                       "bed": "asleep"}.get(why, "walking"),
                              "what": "", "clock": state["clock"]}
            state["since_deep"] = since
            jsave(STATE, state); jsave(WORLD, world)
            jappend(LOG, {"tick": state["tick"], "clock": state["clock"],
                          "mood": mood(state), "calls": reflex,
                          "deep": False, "model": "", "spend": 0.0})
            print(f"tick {state['tick']}. {state['clock'][11:16]}  {mood(state):22} "
                  + ", ".join(c["name"] for c in reflex) + f"   ({why}, free)")
            continue

        if state.pop("wants_deep", None):
            deep = True                       # he asked for it last time
        brain.CURRENT["deep"] = deep
        brain.ADVISOR_USED["n"] = 0        # a fresh advisor budget each tick
        state["since_deep"] = 0 if deep else since

        if deep:
            prompt = situation(state, world, unread)
            system = PERSONA.read_text() + "\n\n" + RULES
            kit = tools.SCHEMA
        else:
            prompt = small_situation(state, world, unread)
            system = PERSONA.read_text() + "\n\n" + SMALL_RULES
            kit = [x for x in tools.SCHEMA if x["name"] in tools.POTTERING]
        system = PERSONA.read_text() + "\n\n" + RULES

        if a.show:
            import brain
            sysmsg = PERSONA.read_text() + "\n\n" + RULES
            tl = json.dumps(tools.SCHEMA)
            print("=" * 72); print("SYSTEM PROMPT"); print("=" * 72); print(sysmsg)
            print("=" * 72); print("WHAT HE SEES THIS TICK"); print("=" * 72); print(prompt)
            print("=" * 72); print("TOOLS HE CAN CALL"); print("=" * 72)
            for t in tools.SCHEMA:
                print(f"  {t['name']:12} {t['description'][:84]}")
            tok = (len(sysmsg) + len(tl) + len(prompt)) / 3
            print("=" * 72)
            print(f"provider: {brain.provider()}   model: {brain.model() or '(none set)'}")
            print(f"one round of this tick is about {tok:,.0f} input tokens")
            print(f"  on sonnet 5.5 that is ${tok*2/1e6:.4f} in, a whole tick usually 3-6 rounds")
            print(f"  on gemini free tier that is $0.00 and counts as one request")
            return

        if a.fake:
            calls = fake_brain(state, world)
        else:
            calls = real_brain(system, prompt, state, world, kit)

        # Sitting down with something properly settles some of it. Without this
        # wonder only ever goes up, he never comes off the expensive gear, and
        # the two cheap ones might as well not exist. Now it builds while he
        # potters, tips him into a deep tick, and that deep tick spends it.
        if deep and not a.fake:
            spend = float(os.environ.get("OTTO_WONDER_SPEND", "0.25"))
            state["needs"]["wonder"] = clamp(state["needs"]["wonder"] - spend)

        for m in seen:
            m["read"] = True
        INBOX.write_text("".join(json.dumps(m) + "\n" for m in seen))
        if seen:                       # these were unread until this tick
            state["because_of"] = {"who": "caleb",
                                   "text": str(seen[-1].get("text") or "")[:160],
                                   "at": state["clock"]}

        state["doing"] = describe(calls, state) or state.get("doing") \
                         or {"verb": "idle", "what": "", "clock": state["clock"]}

        jsave(STATE, state); jsave(WORLD, world)
        # what this tick actually cost, so a runaway bill shows up in the log
        # instead of in an invoice. USAGE is per process, and the timer runs one
        # tick per process, so this is this tick.
        jappend(LOG, {"tick": state["tick"], "clock": state["clock"],
                      "mood": mood(state), "calls": calls,
                      "deep": bool(deep), "model": brain.model(),
                      "spend": round(brain.spend() or 0.0, 6),
                      "tok": dict(brain.USAGE),
                      "advisor": brain.ADVISOR_USAGE["calls"],
                      "advisor_on": bool(brain.ADVISOR),
                      "advisor_tok": dict(brain.ADVISOR_USAGE)})
        tag = "*" if deep else " "
        print(f"tick {state['tick']}{tag} {state['clock'][11:16]}  {mood(state):22} " +
              ", ".join(c["name"] for c in calls))


def real_brain(system, prompt, state, world, kit=None):
    import brain
    kit = kit if kit is not None else tools.SCHEMA
    MAX = int(os.environ.get("OTTO_MAX_TOOLS", "8" if brain.CURRENT["deep"] else "3"))
    turns = [{"role": "user", "text": prompt}]
    calls = []
    for _ in range(MAX):
        text, wants = brain.think(system, turns, kit)
        if text:
            jappend(ROOT / "thoughts.jsonl", {"tick": state["tick"], "text": text})
        if not wants:
            break
        turns.append({"role": "assistant", "text": text, "calls": wants})
        results = []
        # The text he wrote in the same round as the call IS his reason for it.
        # It was going to thoughts.jsonl and nowhere else, so nothing downstream
        # could ever say why he did anything.
        why = first_line(text)
        for u in wants:
            out = tools.run(u["name"], u["input"], state, world)
            calls.append({"name": u["name"], "input": u["input"],
                          "result": out[:400], "why": why})
            results.append({"id": u["id"], "name": u["name"], "output": out})
            if u["name"] in ("test", "examine", "use", "move"):
                jappend(ROOT / "memory" / "seen.jsonl",
                        {"tick": state["tick"], "kind": "world",
                         "src": u["name"], "text": out})
        turns.append({"role": "tool", "results": results})
        if state.get("asleep"):
            break
    return calls


def fake_brain(state, world):
    """No API. Proves the plumbing moves real files."""
    script = [("examine", {"target": "stove"}), ("move", {"place": "lane_top"}),
              ("move", {"place": "shop_general"}), ("take", {"object": "apples"}),
              ("use", {"object": f"apples_{state['tick']}", "intent": "eat it"}),
              ("remember", {"text": "the drain at the top of the lane makes a noise when it rains.", "keep": False}),
              ("journal", {"text": "bought an apple. ate it on the way back. the drain was doing its noise."})]
    calls = []
    for name, args in script:
        out = tools.run(name, args, state, world)
        calls.append({"name": name, "input": args, "result": out[:400]})
    return calls


def summary():
    import brain
    u = brain.USAGE
    if not u["calls"]:
        return
    c = brain.spend()
    print()
    import brain as _b
    print(f"{u['calls']} model calls   "
          f"{u['in']:,} in / {u['out']:,} out tokens"
          + (f"   {u['cache_read']:,} read from cache" if u["cache_read"] else ""))
    if c is not None:
        print(f"this run cost ${c:.3f}")
    else:
        print(f"model {brain.model()} is not in the price table, no cost shown.")


if __name__ == "__main__":
    try:
        main()
    finally:
        summary()
