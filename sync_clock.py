#!/usr/bin/env python3
"""Set otto's clock to right now, so his day lines up with yours from here on."""
import sys, pathlib, datetime
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import STATE, jload, jsave
now = datetime.datetime.now()
s = jload(STATE)
was = s.get("clock", "?")
s["clock"] = now.isoformat(timespec="seconds")
s["real"]  = now.isoformat(timespec="seconds")
jsave(STATE, s)
print(f"his clock was {was[11:16]}, it is now {now.strftime('%H:%M')} on {now.strftime('%A %d %B')}.")
print("from here his day runs with yours.")
