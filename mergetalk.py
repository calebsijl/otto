#!/usr/bin/env python3
"""Fold the letters already sent, both ways, into one thread.

Safe to run twice: it rebuilds talk.jsonl from inbox and outbox rather than
appending, so nothing is doubled.
"""
import sys, pathlib, json
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import INBOX, OUTBOX, TALK, jlines

rows = []
for r in jlines(INBOX):
    rows.append({"who": "caleb", "t": r.get("t") or r.get("sent") or "",
                 "tick": r.get("tick", 0), "text": r.get("text", "")})
for r in jlines(OUTBOX):
    rows.append({"who": "otto", "t": r.get("t", ""),
                 "tick": r.get("tick", 0), "text": r.get("text", "")})
rows = [r for r in rows if r["text"].strip()]
rows.sort(key=lambda r: (str(r["t"]), r["tick"]))

TALK.parent.mkdir(parents=True, exist_ok=True)
TALK.write_text("".join(json.dumps(r) + "\n" for r in rows))
print(f"the thread now has {len(rows)} letters: "
      f"{sum(1 for r in rows if r['who']=='caleb')} from caleb, "
      f"{sum(1 for r in rows if r['who']=='otto')} from otto.")
for r in rows[-6:]:
    print(f"  {r['who']:5} {r['text'][:70]}")
