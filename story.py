#!/usr/bin/env python3
"""Read his life back. This is the thing you actually judge him on."""
import sys, json, pathlib, argparse
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import jlines, jload, LOG, KEPT, NOTES, OUTBOX, SITE, STATE, ROOT

ap = argparse.ArgumentParser()
ap.add_argument("--full", action="store_true", help="every tool call, not just a summary")
a = ap.parse_args()

log = jlines(LOG)
s = jload(STATE)

print("=" * 68)
print(f"otto, tick {s['tick']}, {s['clock'][:10]} {s['clock'][11:16]}, {s['location']}")
print("=" * 68)

if not log:
    sys.exit("he has not lived yet.")

# what he spent his life doing
counts = {}
for row in log:
    for c in row["calls"]:
        counts[c["name"]] = counts.get(c["name"], 0) + 1
print("\nwhat he did, by count:")
for k, v in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {v:4}  {k}")

# the searches and books are where interests show
print("\nwhat he went looking for:")
seen = set()
for row in log:
    for c in row["calls"]:
        if c["name"] == "search_web":
            q = c["input"].get("query", "")
            if q not in seen:
                seen.add(q); print(f"  {q}")
if not seen:
    print("  nothing. that is a red flag.")

print("\nwhat he read:")
books = {}
for row in log:
    for c in row["calls"]:
        if c["name"] == "read_book":
            b = c["input"].get("book", "?")
            books[b] = books.get(b, 0) + 1
for b, n in books.items():
    print(f"  {b}  ({n} sittings)")
if not books:
    print("  nothing.")

print("\nwhat he made:")
if SITE.exists():
    for p in sorted(SITE.rglob("*")):
        if p.is_file():
            print(f"  /{p.relative_to(SITE)}  ({p.stat().st_size:,} bytes)")

print("\nwhat he kept (this is the obsession list):")
print((KEPT.read_text().rstrip() if KEPT.exists() else "  nothing yet.") or "  nothing yet.")

msgs = jlines(OUTBOX)
if msgs:
    print("\nwhat he said to you:")
    for m in msgs:
        print(f"  [{m['t'][11:16]}] {m['text']}")

jp = SITE / "journal.md"
if jp.exists():
    print("\n" + "=" * 68); print("HIS JOURNAL"); print("=" * 68)
    print(jp.read_text().strip())

if a.full:
    print("\n" + "=" * 68); print("EVERY MOVE"); print("=" * 68)
    for row in log:
        print(f"\n-- tick {row['tick']}  {row['clock'][11:16]}  {row['mood']}")
        for c in row["calls"]:
            arg = json.dumps(c["input"])[:90]
            print(f"   {c['name']:11} {arg}")
            print(f"   {'':11} -> {c['result'][:90]}")
