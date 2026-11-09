#!/usr/bin/env python3
"""Read what otto has sent you."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from engine import jlines, OUTBOX
for m in jlines(OUTBOX):
    print(f"[{m['t'][5:16].replace('T',' ')}] {m['text']}\n")
