#!/usr/bin/env python3
"""Wipe otto back to his first morning. Books on the shelf are kept."""
import sys, json, shutil, pathlib, argparse
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import ROOT, STATE, WORLD, NOTES, KEPT, INBOX, OUTBOX, LOG, SITE, BOOKMARKS

ap = argparse.ArgumentParser()
ap.add_argument("--keep-site", action="store_true", help="leave what he built on his site")
ap.add_argument("--archive", metavar="NAME", help="save this life into runs/NAME first")
a = ap.parse_args()

if a.archive:
    dest = ROOT / "runs" / a.archive
    dest.mkdir(parents=True, exist_ok=True)
    for p in (STATE, NOTES, KEPT, LOG, OUTBOX, INBOX, BOOKMARKS, ROOT / "thoughts.jsonl"):
        if p.exists():
            shutil.copy(p, dest / p.name)
    if SITE.exists():
        shutil.copytree(SITE, dest / "site", dirs_exist_ok=True)
    print(f"archived that life to runs/{a.archive}")

STATE.write_text(json.dumps({
    "name": "otto", "species": "hedgehog", "tick": 0,
    "clock": "2026-10-31T07:00:00", "asleep": False,
    "needs": {"energy": 0.82, "fullness": 0.65, "warmth": 0.70, "calm": 0.60, "wonder": 0.45},
    "location": "house_main", "carrying": [], "coins": 12}, indent=2))
WORLD.write_text((WORLD.parent / "seed.json").read_text())
for p in (NOTES, KEPT, INBOX, OUTBOX, LOG, BOOKMARKS, ROOT / "thoughts.jsonl"):
    p.unlink(missing_ok=True)
if not a.keep_site:
    for p in SITE.glob("**/*"):
        if p.is_file():
            p.unlink()
print("otto is back at tick 0. the library is untouched.")
