#!/usr/bin/env python3
"""What he is actually costing. Reads log.jsonl, which records a spend figure
per tick since the cost-logging change.

    python3 cost.py              today, and what that is per month
    python3 cost.py --days 7     a day-by-day breakdown
    ssh <server> 'cd ~/otto && python3 cost.py'
"""
import json, sys, collections, datetime, pathlib

HERE = pathlib.Path(__file__).resolve().parent
rows = []
for line in (HERE / "log.jsonl").read_text().splitlines():
    line = line.strip()
    if line:
        try: rows.append(json.loads(line))
        except Exception: pass

days = 1
if "--days" in sys.argv:
    days = int(sys.argv[sys.argv.index("--days") + 1])

priced = [r for r in rows if "spend" in r]
if not priced:
    print("no cost data in log.jsonl yet. it starts recording from the next tick.")
    sys.exit(0)

by_day = collections.defaultdict(lambda: {"spend": 0.0, "ticks": 0, "deep": 0,
                                          "free": 0, "models": collections.Counter(),
                                          "cr": 0, "cw": 0, "in": 0, "out": 0,
                                          "adv": 0, "advout": 0,
                                          "spend_by": {}, "times": [], "on": False})
for r in priced:
    day = (r.get("clock") or "")[:10] or "?"
    d = by_day[day]
    d["spend"] += r.get("spend") or 0.0
    d["ticks"] += 1
    if r.get("deep"): d["deep"] += 1
    if not r.get("model"): d["free"] += 1
    elif r.get("model"): d["models"][r["model"]] += 1
    t = r.get("tok") or {}
    d["cr"] += t.get("cache_read", 0); d["cw"] += t.get("cache_write", 0)
    d["in"] += t.get("in", 0);         d["out"] += t.get("out", 0)
    d["adv"] += r.get("advisor", 0)
    d["advout"] += (r.get("advisor_tok") or {}).get("out", 0)
    d["on"] = d.get("on") or bool(r.get("advisor_on"))
    d["spend_by"][r.get("model") or "free"] = \
        d["spend_by"].get(r.get("model") or "free", 0.0) + (r.get("spend") or 0.0)
    d["times"].append(r.get("clock") or "")

order = sorted(by_day)[-days:]
print(f"{'day':12} {'ticks':>6} {'deep':>5} {'free':>5} {'spend':>9}   models")
for day in order:
    d = by_day[day]
    models = ", ".join(f"{m.split('claude-')[-1]}x{n}" for m, n in d["models"].most_common())
    print(f"{day:12} {d['ticks']:6} {d['deep']:5} {d['free']:5} ${d['spend']:8.4f}   {models}")

last = by_day[order[-1]]
print()
print(f"most recent day so far: ${last['spend']:.4f} over {last['ticks']} ticks")

# How often does he actually wake? Measured, not assumed, because the day is
# usually part-finished and multiplying a partial day by 30 is how you talk
# yourself into a number that is nine times too low.
mins = []
ts = sorted(t for t in last["times"] if len(t) >= 16)
for i in range(1, len(ts)):
    try:
        a0 = datetime.datetime.fromisoformat(ts[i-1])
        b0 = datetime.datetime.fromisoformat(ts[i])
        m = (b0 - a0).total_seconds() / 60
        if 0 < m < 240: mins.append(m)
    except Exception: pass
gap = sorted(mins)[len(mins)//2] if mins else None

if last["ticks"]:
    per = last["spend"] / last["ticks"]
    print(f"average per tick:     ${per:.5f}")
    if gap:
        perday = 1440.0 / gap
        print(f"he wakes every {gap:.0f} min, so about {perday:.0f} ticks a day")
        print(f"  -> ${per*perday:.2f} a day, ${per*perday*30:.2f} a month")
    else:
        print("  not enough ticks yet to measure how often he wakes")

if len(last["spend_by"]) > 1:
    print("\nwhere it went, by model:")
    for m, v in sorted(last["spend_by"].items(), key=lambda kv: -kv[1]):
        print(f"  {m or 'free':22} ${v:.4f}")

cached = last["cr"] + last["cw"]
if cached:
    hit = 100.0 * last["cr"] / cached
    print(f"\ncache: {last['cr']:,} read vs {last['cw']:,} written  ({hit:.0f}% read)")
    print("  the 1h cache is working if that read share keeps climbing over the day.")
    print("  if writes roughly equal reads, the cache is expiring between ticks.")
print(f"tokens: {last['in']:,} fresh in, {last['out']:,} out")
if last["adv"]:
    print(f"advisor: {last['adv']} calls to the deep model, {last['advout']:,} tokens out")
    print(f"  that is {last['adv'] / max(1, last['ticks']):.2f} per tick")
elif last["on"]:
    print("advisor: switched on, but he never called think_properly. that is him,")
    print("  not a fault: the deep model only runs when he asks for it.")
else:
    print("advisor: switched off (set OTTO_ADVISOR=1 in .env on the server)")
