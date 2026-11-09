#!/usr/bin/env python3
"""Catch the model leaking through the creature.

Compares every word otto has USED against everything he has been EXPOSED to
(books read, searches returned, pages fetched, things caleb told him). Words he
used but never met are suspicious: either the model leaked, or he coined it.
"""
import sys, re, json, pathlib, argparse
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import jlines, SEEN, KNOWS, KEPT, NOTES, SITE, OUTBOX, LIBRARY, book_text

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


def words(text):
    return set(w for w in re.findall(r"[a-z][a-z\-']{4,}", text.lower()))


ap = argparse.ArgumentParser()
ap.add_argument("--list", action="store_true", help="show every flagged word, not the top 40")
a = ap.parse_args()

# everything he has met
exposure = []
for row in jlines(SEEN):
    exposure.append(row.get("text", ""))
# books count fully only as far as he actually read, but be generous: whole book
# The shelf, plus library/.finished, which is where a book goes when it is
# taken away. He still read it, so the words in it are still words he has met.
# Dropping them from exposure would flag every one of them as a leak.
SHELVES = [LIBRARY, LIBRARY / ".finished"]
for d in SHELVES:
    for p in (d.iterdir() if d.exists() else []):
        if p.is_file() and p.suffix.lower() in (".txt", ".md", ".epub", ".pdf"):
            try:
                exposure.append(book_text(p))
            except Exception:
                pass
met = words(" ".join(exposure))

# everything he has produced
produced_parts = {}
if KNOWS.exists():
    produced_parts["knows.md"] = KNOWS.read_text()
if KEPT.exists():
    produced_parts["kept.md"] = KEPT.read_text()
produced_parts["notes"] = " ".join(r.get("text", "") for r in jlines(NOTES))
produced_parts["messages"] = " ".join(r.get("text", "") for r in jlines(OUTBOX))
# Only the pages HE wrote. site/ also holds the viewer we wrote: world.html,
# console.html, look.js. Scanning those counts our CSS and JavaScript as his
# vocabulary, which buries any real leak under a thousand border-radiuses.
OURS = {"world.html", "console.html", "look.js", "index.md"}
if SITE.exists():
    for p in SITE.rglob("*"):
        if not p.is_file() or p.name in OURS:
            continue
        if p.suffix != ".md":              # he writes pages, not markup
            continue
        produced_parts[f"site/{p.name}"] = re.sub(r"<[^>]+>", " ", p.read_text(errors="ignore"))

print("=" * 66)
print("LEAK AUDIT")
print("=" * 66)
print(f"exposure: {len(jlines(SEEN))} items logged, {len(met):,} distinct words he has met")

flagged = {}
for where, text in produced_parts.items():
    for w in words(text) - met - COMMON:
        flagged.setdefault(w, set()).add(where)

if not flagged:
    print("\nnothing flagged. every word he used, he met first.")
    sys.exit(0)

order = sorted(flagged.items(), key=lambda x: (-len(x[1]), x[0]))
shown = order if a.list else order[:40]
print(f"\n{len(flagged)} words used but never encountered"
      + ("" if a.list else f" (showing {len(shown)}, --list for all)") + ":\n")
for w, where in shown:
    print(f"  {w:24} {', '.join(sorted(where))[:60]}")

print("""
how to read this. some will be ordinary words my stoplist does not have, ignore those.
what matters is technical vocabulary: if a word like 'catenary' or 'cantilever' is here,
he produced it without ever reading it, and that is the model talking, not the hedgehog.
the fix is tightening persona.md, or putting a book on the shelf that actually teaches it.""")
