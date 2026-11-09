#!/usr/bin/env python3
"""Check otto's web search works, without spending a model call."""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import engine
q = " ".join(sys.argv[1:]) or "how a beam bridge carries load"
print(f"searching: {q}\n" + "-" * 60)
for name, fn in (("tavily", engine._tavily), ("wikipedia", engine._wikipedia),
                 ("duckduckgo", engine._duckduckgo)):
    try:
        out = fn(q, 3)
        print(f"{name:12} {'OK, ' + str(len(out)) + ' chars' if out else 'empty'}")
    except Exception as e:
        print(f"{name:12} failed: {e.__class__.__name__}: {str(e)[:60]}")
print("-" * 60)
print("what otto would actually get:\n")
print(engine.search_web(q)[:700])
