#!/usr/bin/env python3
"""His shelf: what is on it, what goes on it, what comes off it.

A sitting is 3,800 characters. That number is the whole story of why he got
stuck on one book: The Boy Mechanic is 1.36 million characters, which is 357
sittings. At a sitting or two a day he would have finished it in about a year,
and meanwhile it sat on the shelf saying "1% in" forever.

Everything else was just as bad: walden 176 sittings, selborne 137, poetics 69,
alice 46. Nothing he owned could be finished, so nothing could be put down.

Aim for things he can finish. Twenty sittings is a fortnight. Five is an
afternoon. A long book is better split into parts that each end somewhere.

    python3 books.py                      what is on the shelf, and how long each is
    python3 books.py add FILE             put a book on the shelf
    python3 books.py add FILE --as name   ...under a different name
    python3 books.py add FILE --split     ...cut into finishable parts
    python3 books.py remove NAME          take it off the shelf (keeps the text)
    python3 books.py restore NAME         put it back
"""
import sys, json, shutil, pathlib, argparse, re

HERE = pathlib.Path(__file__).resolve().parent
LIB = HERE / "library"
DONE = LIB / ".finished"
MARKS = HERE / "memory" / "bookmarks.json"
PAGE = 3800                      # must match engine.PAGE
TARGET_SITTINGS = 10             # what one part of a split book aims for
EXT = (".txt", ".md", ".epub", ".pdf")


def marks():
    try:
        return json.loads(MARKS.read_text() or "{}")
    except Exception:
        return {}


def save_marks(m):
    MARKS.parent.mkdir(parents=True, exist_ok=True)
    MARKS.write_text(json.dumps(m, indent=1))


def sittings(path):
    try:
        return max(1, round(len(path.read_text(errors="ignore")) / PAGE))
    except Exception:
        return None


def verdict(n):
    if n is None:      return "cannot measure (not plain text)"
    if n <= 6:         return "an afternoon"
    if n <= 20:        return "a fortnight"
    if n <= 60:        return "months. consider --split"
    return "he will never finish this. split it."


def show():
    m = marks()
    rows = sorted(p for p in LIB.iterdir() if p.is_file() and p.suffix.lower() in EXT)
    if not rows:
        print("the shelf is empty.")
        return
    print(f"{'book':28}{'sittings':>9}   {'read':>5}   how long that is")
    for p in rows:
        n = sittings(p)
        pos = m.get(p.stem, 0)
        pct = f"{int(100*pos/max(1,len(p.read_text(errors='ignore'))))}%" if pos else "-"
        print(f"{p.stem:28}{str(n):>9}   {pct:>5}   {verdict(n)}")
    off = sorted(p.stem for p in DONE.iterdir()) if DONE.exists() else []
    if off:
        print("\noff the shelf (still counted as things he has read): " + ", ".join(off))


def split_text(text, want):
    """Cut on blank lines so a part ends between paragraphs, not mid-sentence."""
    size = PAGE * want
    paras, out, cur = re.split(r"\n\s*\n", text), [], ""
    for para in paras:
        if cur and len(cur) + len(para) > size:
            out.append(cur.strip()); cur = ""
        cur += para + "\n\n"
    if cur.strip():
        out.append(cur.strip())
    return out


def add(src, name=None, do_split=False):
    src = pathlib.Path(src).expanduser()
    if not src.exists():
        print(f"no such file: {src}"); return 1
    LIB.mkdir(parents=True, exist_ok=True)
    stem = name or re.sub(r"[^a-z0-9]+", "-", src.stem.lower()).strip("-")
    if src.suffix.lower() not in (".txt", ".md") or not do_split:
        dst = LIB / (stem + src.suffix.lower())
        shutil.copy2(src, dst)
        n = sittings(dst)
        print(f"on the shelf: {dst.stem}  ({n} sittings, {verdict(n)})")
        if n and n > 40:
            print("  that is a long one. `--split` would cut it into parts he can finish.")
        return 0
    parts = split_text(src.read_text(errors="ignore"), TARGET_SITTINGS)
    for i, part in enumerate(parts, 1):
        dst = LIB / f"{stem}-{i}{src.suffix.lower()}"
        dst.write_text(part)
    print(f"on the shelf: {stem}-1 .. {stem}-{len(parts)}  "
          f"({len(parts)} parts, about {TARGET_SITTINGS} sittings each)")
    return 0


def remove(name):
    hits = [p for p in LIB.iterdir() if p.is_file() and name.lower() in p.stem.lower()]
    if not hits:
        print(f"nothing on the shelf matching '{name}'"); return 1
    DONE.mkdir(parents=True, exist_ok=True)
    m = marks()
    for p in hits:
        shutil.move(str(p), str(DONE / p.name))
        m.pop(p.stem, None)
        print(f"off the shelf: {p.stem}")
    save_marks(m)
    print("  the text stays in library/.finished, so what he read still counts as read.")
    return 0


def restore(name):
    if not DONE.exists():
        print("nothing has been taken off the shelf"); return 1
    hits = [p for p in DONE.iterdir() if p.is_file() and name.lower() in p.stem.lower()]
    if not hits:
        print(f"nothing archived matching '{name}'"); return 1
    for p in hits:
        shutil.move(str(p), str(LIB / p.name))
        print(f"back on the shelf: {p.stem}")
    return 0


ap = argparse.ArgumentParser(add_help=True)
sub = ap.add_subparsers(dest="cmd")
a1 = sub.add_parser("add");    a1.add_argument("file"); a1.add_argument("--as", dest="name")
a1.add_argument("--split", action="store_true")
a2 = sub.add_parser("remove"); a2.add_argument("name")
a3 = sub.add_parser("restore"); a3.add_argument("name")
g = ap.parse_args()

if g.cmd == "add":        sys.exit(add(g.file, g.name, g.split))
elif g.cmd == "remove":   sys.exit(remove(g.name))
elif g.cmd == "restore":  sys.exit(restore(g.name))
else:                     show()
