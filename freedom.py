"""Give otto permission to put things down, and the means to actually do it.

Three parts:
  1. the rules stop telling him a project "should" run across many days
  2. put_down() takes a book or a kept thing off his list for good
  3. the shelf shows a book he put down as a choice, not an unpaid debt

Idempotent. Safe to run twice.
"""
import pathlib, sys, re

ROOT = pathlib.Path(__file__).resolve().parent

PLAN = {}   # file -> list of (label, old, new)

# ----------------------------------------------------------------- engine.py
PLAN["engine.py"] = [
 ("aside path",
  'BOOKMARKS = ROOT / "memory" / "bookmarks.json"',
  'BOOKMARKS = ROOT / "memory" / "bookmarks.json"\n'
  'ASIDE     = ROOT / "memory" / "aside.json"   # books he has put down on purpose'),

 ("shelf shows put-down books",
  '''    marks = jload(BOOKMARKS, {}) or {}
    out = []
    for p in books():
        total = max(1, len(book_text(p)))
        pos = marks.get(p.stem, 0)
        pct = int(100 * pos / total)
        out.append(f"{p.stem}" + (f"  ({pct}% in)" if pos else "  (unopened)"))
    return out''',
  '''    marks = jload(BOOKMARKS, {}) or {}
    aside = jload(ASIDE, []) or []
    out = []
    for p in books():
        total = max(1, len(book_text(p)))
        pos = marks.get(p.stem, 0)
        pct = int(100 * pos / total)
        if p.stem in aside:
            tag = f"  (you put this one down at {pct}%, and that is allowed)"
        elif pos >= total:
            tag = "  (finished)"
        elif pos:
            tag = f"  ({pct}% in)"
        else:
            tag = "  (unopened)"
        out.append(f"{p.stem}{tag}")
    return out'''),

 ("opening a book picks it back up",
  '''    p = match[0]
    text = book_text(p)''',
  '''    p = match[0]
    aside = jload(ASIDE, []) or []
    if p.stem in aside:
        jsave(ASIDE, [s for s in aside if s != p.stem])
    text = book_text(p)'''),
]

# ------------------------------------------------------------------ tools.py
PLAN["tools.py"] = [
 ("import aside + books",
  '                    search_web, read_page, shelf, read_book, WORLD, NOTES, KEPT,',
  '                    search_web, read_page, shelf, read_book, books, ASIDE, WORLD, NOTES, KEPT,'),

 ("put_down is pottering",
  "POTTERING = {'move', 'examine', 'use', 'take', 'journal', 'remember', 'message',",
  "POTTERING = {'move', 'examine', 'use', 'take', 'journal', 'remember', 'message',\n"
  "             'put_down',"),

 ("put_down tool",
  ''' {"name": "journal", "description": "write in your journal.''',
  ''' {"name": "put_down", "description": "stop carrying something. a book you have gone off, a thing you were making and are finished with, anything on your list that has stopped pulling at you. it comes off your list and stops asking. you can pick it up again later, or never, and either is fine.",
  "input_schema": {"type": "object", "properties": {
      "thing": {"type": "string", "description": "the book, or the thing, in your own words. enough of it that it is clear which one you mean."}},
   "required": ["thing"]}},
 {"name": "journal", "description": "write in your journal.'''),

 ("put_down handler",
  '''    if name == "journal":''',
  '''    if name == "put_down":
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
                KEPT.write_text("\\n".join(left) + ("\\n" if left else ""))
                jappend(NOTES, {"t": state["clock"], "tick": state["tick"],
                                "text": f"put down: {gone[0]}"})
                n["calm"] = clamp(n["calm"] + 0.05)
                return (f"off the list. {gone[0]} is not yours to finish any more.")
        return ("that is not on your list, so there is nothing to put down. you can "
                "simply not do it.")

    if name == "journal":'''),
]

# ------------------------------------------------------------------- tick.py
PLAN["tick.py"] = [
 ("no more should",
  '''if something is pulling at you, go at it. read about it, go and get what you need, start
building it badly. a thing you are making can run across many days and it should.''',
  '''if something is pulling at you, go at it. read about it, go and get what you need, start
building it badly. a thing you are making can run across many days if it keeps pulling.

and you are allowed to stop. nothing you have started is owed anything: not a book you
are halfway through, not a thing half built on the bench. if you open a book and it has
gone dead on you, put it down and go and do something else. if the thing on the bench
has stopped being interesting, leave it where it is. put_down() takes it off your list
so it stops asking. you can pick it up again, or never. what you spend today on is
whatever has hold of you today, not whatever had hold of you last week.'''),

 ("keep is for what still pulls",
  '''use remember() for anything you would be annoyed to have forgotten. set keep=true for
the things you are not putting down, because what you keep is what you will still be
chasing next week.''',
  '''use remember() for anything you would be annoyed to have forgotten. set keep=true only
for the few things still genuinely pulling at you, because what you keep is what will
keep asking. when one stops pulling, put_down() and let it go.'''),
]

# ------------------------------------------------------------------ fresh.py
PLAN["fresh.py"] = [
 ("wipe aside too",
  '''ROOT / "thoughts.jsonl", ROOT / "memory" / "bookmarks.json"]''',
  '''ROOT / "thoughts.jsonl", ROOT / "memory" / "bookmarks.json",
        ROOT / "memory" / "aside.json"]'''),
]

MARKER = {"engine.py": "ASIDE     = ROOT",
          "tools.py": '"name": "put_down"',
          "tick.py": "put_down() takes it off your list",
          "fresh.py": 'ROOT / "memory" / "aside.json"]'}

bad = 0
for fname, edits in PLAN.items():
    p = ROOT / fname
    if not p.exists():
        print(f"  !! {fname} missing"); bad += 1; continue
    txt = p.read_text()
    if MARKER[fname] in txt:
        print(f"  -- {fname}: already done"); continue
    done, miss = [], []
    for label, old, new in edits:
        if txt.count(old) == 1:
            txt = txt.replace(old, new, 1)
            done.append(label)
        else:
            miss.append(f"{label} (found {txt.count(old)}x)")
    if miss:
        print(f"  !! {fname}: NOT WRITTEN, these anchors failed:")
        for m in miss:
            print(f"       {m}")
        bad += 1
        continue
    # compile check before committing anything
    try:
        compile(txt, fname, "exec")
    except SyntaxError as e:
        print(f"  !! {fname}: NOT WRITTEN, syntax error at line {e.lineno}: {e.msg}")
        bad += 1
        continue
    p.write_text(txt)
    print(f"  ok {fname}: {', '.join(done)}")

print()
print("he can put things down now." if not bad else f"{bad} file(s) untouched. nothing half-applied.")
sys.exit(1 if bad else 0)
