"""Consequence. Things in otto's world can now fail, and he does not get to decide when.

The point is not accuracy. It is that an outcome arrives from outside him, carries a
number he can calibrate against, and sometimes ruins what he built.
"""
import random, re

# what a thing is made of, guessed from what he called it and wrote about it
MATERIAL = {
    "paper": 1.0, "card": 1.8, "string": 2.5, "twine": 2.5, "wood": 6.0,
    "stick": 5.0, "pencil": 4.0, "metal": 20.0, "wire": 12.0, "stone": 15.0,
    "leaf": 0.4, "straw": 0.8, "cloth": 1.2, "bark": 3.0,
}

# geometry he chose. this is where real engineering gets rewarded.
FORM = {
    "tube": 3.2, "rolled": 3.0, "cylinder": 3.0,
    "accordion": 2.8, "folded": 2.6, "corrugated": 3.0, "pleated": 2.6,
    "truss": 3.5, "triangle": 3.4, "triangular": 3.4, "lattice": 3.2,
    "arch": 3.8, "arched": 3.8, "vault": 3.6,
    "suspension": 2.2, "cable": 2.4, "hung": 2.0,
    "box": 2.9, "i-beam": 3.3, "ribbed": 2.4, "layered": 1.9, "doubled": 1.7,
    "flat": 1.0, "strip": 0.9, "sheet": 0.85, "single": 0.9,
}

SPAN = {"long": 0.45, "wide": 0.55, "short": 1.8, "narrow": 1.6, "tiny": 2.2}


def _score(table, text, default=1.0):
    best = None
    for k, v in table.items():
        if re.search(rf"\b{re.escape(k)}", text):
            if best is None or v > best:
                best = v
    return default if best is None else best


def capacity(obj):
    """How much this thing takes before it complains, in coin-weights."""
    text = f"{obj.get('name','')} {obj.get('note','')} {' '.join(obj.get('tags',[]))}".lower()
    base = _score(MATERIAL, text, 1.0)
    form = _score(FORM, text, 1.0)
    span = _score(SPAN, text, 1.0)
    wear = obj.get("condition", 1.0)
    cap = base * form * span * 3.0 * wear
    # every object has its own quiet flaw, fixed for its lifetime
    seed = sum(ord(c) for c in obj.get("id", "x"))
    cap *= 0.75 + (seed % 50) / 100.0
    return round(cap, 1)


def test(obj, load, note=""):
    """Put a load on it. Returns (what happened, how its condition changed)."""
    cap = capacity(obj)
    try:
        load = float(load)
    except (TypeError, ValueError):
        load = 1.0
    ratio = load / max(0.1, cap)
    roll = random.uniform(0.88, 1.14)          # the day, the damp, the luck
    r = ratio * roll
    name = obj.get("name", "it")

    if r < 0.45:
        return (f"{name} takes {load:g} without a sound. nothing moves. "
                f"it is nowhere near its limit.", 0.0)
    if r < 0.75:
        return (f"{name} takes {load:g}. a small sag, maybe two millimetres, "
                f"and it holds there.", -0.01)
    if r < 0.95:
        return (f"{name} takes {load:g} but it is working for it. visible bend, "
                f"a dry creak when you touch it. it would not take much more.", -0.06)
    if r < 1.15:
        return (f"{name} bends under {load:g} and stays bent. it did not break, "
                f"but it is not straight any more and it will not come back.", -0.30)
    if r < 1.6:
        return (f"{name} fails at {load:g}. it goes slowly, a crease that runs across "
                f"and then gives. the load comes down.", -1.0)
    return (f"{name} fails at {load:g} immediately and completely. it did not even "
            f"bend first. whatever was on it is on the floor.", -1.0)


MISHAPS = [
    ("the load goes into the drain. you hear it hit something a long way down, "
     "and that is the last of it.", "lose_load"),
    ("a corner tears as it comes apart. the piece that is left is smaller than it was.", None),
    ("it goes while you are holding it and the whole lot comes apart in your hands. "
     "you sit back on the cobbles, cross about it.", "startle"),
    ("it comes down with a clatter that carries the length of the lane. you look "
     "around to see whether anyone heard.", "startle"),
    ("the whole lot slides sideways into the wet and you spend a while picking it "
     "out of the gutter.", "wet"),
    ("it drops clean through and takes your string with it.", "lose_load"),
]


def mishap(seed):
    """Sometimes a failure costs more than the thing that failed. Returns (text, kind)."""
    random.seed(seed)
    if random.random() < 0.35:
        return random.choice(MISHAPS)
    return (None, None)


def weather(tick):
    """Occasional outside events, so the world is not only reacting to him."""
    random.seed(tick * 7919)
    r = random.random()
    if r < 0.04:
        return "rain. heavy enough to hear it on the roof and run in the drain."
    if r < 0.08:
        return "wind, the kind that gets under things and moves them."
    if r < 0.11:
        return "cold. everything metal is colder than it should be."
    if r < 0.14:
        return "fog in the lane. you cannot see the bottom of it."
    return None
