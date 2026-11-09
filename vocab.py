#!/usr/bin/env python3
"""What words he has actually met.

The persona asks him not to produce knowledge out of nowhere, but a request in a
prompt is not a constraint: the model behind him recognises things and names
them. This is the constraint. A word he has never read or been told is a word he
cannot type into a search box, so the only way to look a thing up is to describe
it in words he does have, and the word comes back to him off the page.
"""
import re, pathlib, sys
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import jlines, jload, SEEN, KNOWS, KEPT, NOTES, WISHES, WORLD, LIBRARY, book_text

WORD = re.compile(r"[a-z][a-z\-']{4,}")

# plain english he is taken to have, so the gate catches names and jargon, not grammar
COMMON = set("""
a about above across after again against all almost alone along already also although always am
among an and another any anything are around as at away back bad be because been before behind
being below beside best better between big both bring but by came can cannot come comes coming
could did do does doing done down drink each early easy eat either else end enough even ever
every everything far fast feel feels felt few find fine first five floor for found four from
front full gave get gets getting give given go goes going gone good got great green ground had
half hand hands happen happens hard has have having he head hear heard heavy held help her here
high him his hold holding home house how however if in inside into is it its itself just keep
keeps kept kind know known large last late later least leave left less let light like little
live long look looked looking looks lot made make makes making many may maybe me mean might mind
more morning most move moved moving much must my near need needs never new next night no nor not
nothing now of off often old on once one only onto open or other our out outside over own paper
part people perhaps piece place put rain ran reach read ready real really rest right room round
run said same saw say says see seem seems seen set several shall she short should side since sit
sitting six small so some something sometimes soon stand start started still stop such sure take
taken takes than that the their them then there these they thing things think this those though
three through time to today together told too took top toward turn turned two under until up
upon us use used using very walk walked want wanted warm was watch water way we well went were
what when where whether which while white who whole why wide will wind with within without
work worked working would write writing written wrong year yes yet you your
day days drain lane shop shops shelf library book books page pages post office house window
stove chair table bed coin coins string pencil apple apples bread wood stone street cobble
otto hedgehog caleb morning afternoon evening night tick ticks world
""".split())


def _words(text):
    return set(WORD.findall((text or "").lower()))


def met(world=None):
    """Every word he could honestly have read, heard or written."""
    seen = set()
    for row in jlines(SEEN):                       # searches, pages, books, caleb
        seen |= _words(row.get("text", ""))
    for f in (KNOWS, KEPT):                        # his own list and his own notes
        if f.exists():
            seen |= _words(f.read_text())
    for row in jlines(NOTES):
        seen |= _words(row.get("text", ""))
    for row in jlines(WISHES):
        seen |= _words(row.get("want", "") + " " + row.get("why", ""))
    w = world if world is not None else jload(WORLD)
    for o in w.get("objects", []):                 # anything standing in front of him
        seen |= _words(o.get("name", "") + " " + o.get("note", ""))
    for p in w.get("places", {}).values():
        seen |= _words(p.get("name", "") + " " + p.get("description", ""))
    for p in (LIBRARY.iterdir() if LIBRARY.exists() else []):
        if p.is_file() and p.suffix.lower() in (".txt", ".md", ".epub", ".pdf"):
            try:
                seen |= _words(book_text(p))
            except Exception:
                pass
    return seen | COMMON


def unknown(text, world=None, known=None):
    """The words in `text` he has no business knowing. Empty list means fine."""
    have = known if known is not None else met(world)
    return [w for w in sorted(_words(text)) if w not in have]


if __name__ == "__main__":
    q = " ".join(sys.argv[1:])
    if not q:
        v = met()
        print(f"{len(v):,} words he has met")
    else:
        u = unknown(q)
        print("he could search that." if not u else "he could not: " + ", ".join(u))
