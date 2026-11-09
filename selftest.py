#!/usr/bin/env python3
"""Checks everything that can be checked without a model. No key needed."""
import sys, json, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import engine, tools, brain

ok = True
def check(label, cond, detail=""):
    global ok
    ok = ok and cond
    print(f"  {'pass' if cond else 'FAIL'}  {label}" + (f"  {detail}" if detail and not cond else ""))

print("files")
for f in ("persona.md", "state.json", "world/world.json", "world/seed.json"):
    check(f, (engine.ROOT / f).exists())

print("world")
w = engine.jload(engine.WORLD); s = engine.jload(engine.STATE)
check("state location exists", s["location"] in w["places"])
for pid, p in w["places"].items():
    for e in p["exits"]:
        check(f"{pid} -> {e}", e in w["places"])
        check(f"{e} -> {pid} (two-way)", pid in w["places"][e]["exits"])
for o in w["objects"]:
    check(f"object {o['id']} placed", o["place"] in w["places"] or o["place"] == "_carried")

print("tools")
names = [t["name"] for t in tools.SCHEMA]
check("no duplicate names", len(names) == len(set(names)))
for t in tools.SCHEMA:
    check(f"{t['name']} has a description", bool(t.get("description")))
    check(f"{t['name']} schema is an object", t["input_schema"].get("type") == "object")

print("gemini conversion")
for t in tools.SCHEMA:
    g = brain._gemini_schema(t)
    check(f"{t['name']} converts", "name" in g and "description" in g)
    if "parameters" in g:
        check(f"{t['name']} params have properties", bool(g["parameters"].get("properties")))
        for k, v in g["parameters"]["properties"].items():
            check(f"{t['name']}.{k} has a type", "type" in v)
body = {"tools": [{"functionDeclarations": [brain._gemini_schema(t) for t in tools.SCHEMA]}]}
check("whole tool block serialises", bool(json.dumps(body)))

print("openrouter conversion")
ot = brain._openai_tools(tools.SCHEMA)
check("all tools convert", len(ot) == len(tools.SCHEMA))
for t in ot:
    f = t["function"]
    check(f"{f['name']} has parameters object", f["parameters"].get("type") == "object")
check("whole tool block serialises", bool(json.dumps(ot)))

print("library")
check("library folder exists", engine.LIBRARY.exists())
print(f"  books on the shelf: {len(engine.books())}")

print("provider")
print(f"  provider: {brain.provider()}   model: {brain.model() or '(none set)'}")

print()
print("all good." if ok else "something above needs fixing.")
sys.exit(0 if ok else 1)
