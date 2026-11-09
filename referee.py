#!/usr/bin/env python3
"""The world's own opinion of whether a thing he made actually works.

physics.py answers one question well: will it hold weight. That is the right
question for an arch and the wrong one for a buzzer, a lens, a water wheel or a
web page, and when he started building those he got nothing back at all. He would
push the switch and the world would say "you push the switch", so he could not
tell a working circuit from a broken one and had no way to improve either.

This asks a model that knows real physics, electricity and code what would
actually happen, and then tells him ONLY what he could see, hear or feel. No
explanation, no principle, no component he has not already named. The verdict is
cached against what the thing is made of, so trying the same unchanged thing
twice gives the same answer, and changing it is the only way to change the
outcome. That is what makes it worth fixing.
"""
import hashlib, json, os, re

SYSTEM = """you are the world, not otto.

otto is a hedgehog who builds things out of what he can get hold of. he has just
tried to work one of them. you know real physics, electricity, optics, chemistry
and code perfectly. decide what would actually happen, honestly, including that
most first attempts do not work.

then report ONLY what he could see, hear, smell or feel standing there. this part
matters more than anything else:

- never explain why. no principle, no law, no cause, no "because".
- never name a part, a material or a word he has not used himself.
- never give advice, never suggest a fix, never ask a question.
- never mention electricity, circuits, current, voltage, magnetism, refraction,
  frequency or any other technical idea, even to say it is absent.
- be specific enough that he could tell the difference after changing something.
  "nothing happens" is a bad report. "the iron sits dead still, and the wire by
  your paw is faintly warm" is a good one.
- two or three sentences at most. plain, flat, observational.

if what he built would genuinely work, say what it does, and let it be good.
"""

SCHEMA = [{
    "name": "verdict",
    "description": "what happens, and what he observes.",
    "input_schema": {"type": "object", "properties": {
        "works": {"type": "string", "enum": ["yes", "partly", "no"],
                  "description": "does it do the thing he is trying to make it do."},
        "observed": {"type": "string",
                     "description": "what he sees, hears or feels. observation only."}},
     "required": ["works", "observed"]}}]


def _fingerprint(desc, attempt):
    return hashlib.sha1((desc + "|" + attempt).encode("utf-8")).hexdigest()[:12]


def judge(desc, attempt, extra=""):
    """desc: what the thing is and what it is made of. attempt: what he is doing
    with it. Returns (works, observed) or (None, None) if there is no model."""
    if os.environ.get("OTTO_REFEREE", "1") == "0":
        return None, None
    try:
        import brain
        was = brain.CURRENT.get("deep")
        brain.CURRENT["deep"] = False          # the cheap model is plenty for this
        prompt = f"the thing:\n{desc}\n\nwhat he is doing:\n{attempt}"
        if extra:
            prompt += f"\n\nwhat has changed since last time:\n{extra}"
        try:
            _text, calls = brain.think(SYSTEM, [{"role": "user", "content": prompt}], SCHEMA)
        finally:
            brain.CURRENT["deep"] = was
        for c in calls:
            if c["name"] == "verdict":
                a = c["input"]
                return a.get("works", "no"), (a.get("observed") or "").strip()
    except Exception:
        pass                                   # the world stays quiet rather than breaking
    return None, None


def describe(obj):
    """Everything the world knows about a thing he made."""
    bits = [obj.get("name", "a thing")]
    if obj.get("note"):   bits.append(obj["note"])
    if obj.get("shape"):  bits.append(f"shape: {obj['shape']}")
    if obj.get("colour"): bits.append(f"colour: {obj['colour']}")
    if obj.get("made_of"): bits.append("made out of: " + ", ".join(obj["made_of"]))
    if obj.get("tags"):   bits.append("tags: " + ", ".join(obj["tags"]))
    cond = obj.get("condition", 1.0)
    if cond < 0.95:       bits.append(f"condition: {cond:.2f} of new")
    return ". ".join(bits)


def context(obj, state, world):
    """Where the thing is standing, and what else he has built nearby.

    A water wheel in a stream and a water wheel on a table are not the same
    object, and two pendulums judged with no knowledge of each other will come
    back with numbers that do not agree. Both of those matter to him, because
    comparing one against another is how he works anything out.
    """
    bits = []
    place = world.get("places", {}).get(obj.get("place") or state.get("location"), {})
    if place:
        bits.append(f"it is at {place.get('name','somewhere')}. {place.get('description','')}")
    here_made = [o for o in world.get("objects", [])
                 if o.get("made_by") == "otto" and o.get("id") != obj.get("id")
                 and o.get("place") == obj.get("place")]
    for o in here_made[:4]:
        v = (o.get("verdict") or {}).get("observed")
        line = f"also here, made by him: {describe(o)}"
        if v:
            line += f" | when he last worked it: {v}"
        bits.append(line)
    return "\n".join(bits)


def ask(obj, attempt, changed="", where=""):
    """Judge an object, reusing the last answer while nothing about it has changed."""
    desc = describe(obj)
    if where:
        desc += "\n\n" + where
    fp = _fingerprint(desc, attempt)
    old = obj.get("verdict") or {}
    if old.get("fp") == fp and old.get("observed"):
        return old["works"], old["observed"], True
    works, observed = judge(desc, attempt, changed)
    if observed:
        obj["verdict"] = {"fp": fp, "works": works, "observed": observed}
        return works, observed, False
    return None, None, False
