#!/usr/bin/env python3
"""Tell otto something. He sees it next time he wakes, and may ignore it."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import jappend, jload, INBOX, STATE
text = " ".join(sys.argv[1:]).strip()
if not text:
    sys.exit("usage: ./say.py there is a thing called a lathe, it spins metal")
jappend(INBOX, {"t": jload(STATE)["clock"], "text": text, "read": False})
print("he'll see it when he wakes.")
