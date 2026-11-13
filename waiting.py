#!/usr/bin/env python3
"""What is waiting in his inbox, and a way to throw it out.

    python3 waiting.py            show what he has not read yet
    python3 waiting.py --all      show everything, read or not
    python3 waiting.py --drop 3   throw out message 3
    python3 waiting.py --clear    throw out everything unread
"""
import sys, json, pathlib, argparse
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import INBOX, jlines

ap = argparse.ArgumentParser()
ap.add_argument("--all", action="store_true")
ap.add_argument("--drop", type=int)
ap.add_argument("--clear", action="store_true")
a = ap.parse_args()

rows = jlines(INBOX)
if a.drop is not None or a.clear:
    keep = []
    for i, m in enumerate(rows, 1):
        if a.clear and not m.get("read"):
            continue
        if a.drop == i:
            print(f"thrown out: {m.get('who','caleb')}: {str(m.get('text'))[:70]}")
            continue
        keep.append(m)
    INBOX.write_text("".join(json.dumps(m) + "\n" for m in keep))
    print(f"{len(rows) - len(keep)} gone, {len(keep)} left.")
    sys.exit()

shown = 0
for i, m in enumerate(rows, 1):
    if not a.all and m.get("read"):
        continue
    shown += 1
    who = m.get("who", "caleb")
    mark = " " if m.get("trusted") or who == "caleb" else "?"
    print(f"{i:3} {mark} {who:<20} {str(m.get('text'))[:90]}")
print(f"\n{shown} waiting." if shown else "\nnothing waiting.")
print("a ? means the name is only claimed. --drop N throws one out.")
