"""Swappable model backend. Otto does not care who is thinking for him.

Neutral transcript format used everywhere else in the project:
  {"role":"user","text":...}
  {"role":"assistant","text":...,"calls":[{"id","name","input"}]}
  {"role":"tool","results":[{"id","name","output"}]}
"""
import os, json, urllib.request

# per-run token accounting, read by tick.py
USAGE = {"in": 0, "out": 0, "cache_write": 0, "cache_read": 0, "calls": 0}

# how long the unchanging parts of the prompt stay cached. None = the 5 minute
# default. Set OTTO_LONG_TTL=0 to turn the hour long cache off.
LONG_TTL = None if os.environ.get("OTTO_LONG_TTL") == "0" else "1h"

# $ per million tokens: (input, output, cache write, cache read)
# Cache write here is the 5 minute rate, 1.25x input. The 1 hour rate is 2x input,
# so the system and tool blocks (which use 1h) cost a little more to write than
# this reckons and far less overall, because they are written once an hour
# instead of once a tick. Treat spend() as a good guide, not an invoice.
# Cache reads are 0.1x input, except Opus 5.5 and Sonnet 5.5 which are 0.05x.
# Haiku 5.5 jumps to 0.50/2.50 once a prompt goes over 100k tokens. Ours are ~5k.
PRICES = {
    "claude-opus-5-5":   (4.00, 20.00, 5.00,  0.20),
    "claude-opus-5":     (5.00, 25.00, 6.25,  0.50),
    "claude-sonnet-5-5": (2.00, 10.00, 2.50,  0.10),
    "claude-haiku-5-5":  (0.10,  0.50, 0.125, 0.01),
    "claude-haiku-5":    (0.10,  0.50, 0.125, 0.01),
}


def _priced(use, p):
    i, o, cw, cr = p
    return (use["in"] * i + use["out"] * o +
            use["cache_write"] * cw + use["cache_read"] * cr) / 1e6


def spend():
    """Best-effort cost of this run, loop and advisor together.
    Returns None if neither model is priced here."""
    loop = PRICES.get(model())
    adv = PRICES.get(deep_model())
    if not loop and not adv:
        return None
    total = 0.0
    if loop: total += _priced(USAGE, loop)
    if adv:  total += _priced(ADVISOR_USAGE, adv)
    return total

def provider():
    p = os.environ.get("OTTO_PROVIDER")
    if p:
        return p
    if os.environ.get("ANTHROPIC_API_KEY"):
        return "anthropic"
    if os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY"):
        return "gemini"
    if os.environ.get("OPENROUTER_API_KEY"):
        return "openrouter"
    return "none"


# the model for this tick. set by tick.py before it starts thinking.
CURRENT = {"deep": False}

# The advisor. OTTO_ADVISOR=1 turns it on. Off by default so a run can be
# compared against one without it.
ADVISOR = os.environ.get("OTTO_ADVISOR") == "1"
ADVISOR_MAX = int(os.environ.get("OTTO_ADVISOR_MAX", "2"))   # per tick
ADVISOR_USED = {"n": 0}
ADVISOR_USAGE = {"in": 0, "out": 0, "cache_write": 0, "cache_read": 0, "calls": 0}


def _pick(deep):
    p = provider()
    if deep:
        d = {"anthropic": "claude-sonnet-5-5", "gemini": "gemini-2.5-pro",
             "openrouter": "anthropic/claude-sonnet-5-5"}
        return os.environ.get("OTTO_MODEL_DEEP") or os.environ.get("OTTO_MODEL") or d.get(p, "")
    d = {"anthropic": "claude-haiku-5-5", "gemini": "gemini-2.5-flash",
         "openrouter": "anthropic/claude-haiku-5-5"}
    return os.environ.get("OTTO_MODEL_EVERYDAY") or os.environ.get("OTTO_MODEL") or d.get(p, "")


def deep_model():     return _pick(True)
def everyday_model(): return _pick(False)


def model():
    """The model running the tick loop.

    With the advisor on, the loop is always the cheap model and the expensive
    one is only ever reached through advise(). That is the whole saving: he
    keeps every tool and every round, and the frontier model is spent on the
    handful of moments that deserve it instead of on walking to the orchard.
    """
    if ADVISOR:
        return everyday_model()
    return _pick(CURRENT["deep"])


# ------------------------------------------------------------------ anthropic
def _anthropic(system, turns, schema):
    global LONG_TTL
    from anthropic import Anthropic
    msgs = []
    for t in turns:
        if t["role"] == "user":
            msgs.append({"role": "user",
                         "content": [{"type": "text", "text": t["text"]}]})
        elif t["role"] == "assistant":
            c = ([{"type": "text", "text": t["text"]}] if t.get("text") else []) + \
                [{"type": "tool_use", "id": c["id"], "name": c["name"], "input": c["input"]}
                 for c in t.get("calls", [])]
            msgs.append({"role": "assistant", "content": c})
        else:
            msgs.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": r["id"], "content": r["output"]}
                for r in t["results"]]})

    # The whole point: a tick is many rounds and each one resends everything said
    # so far. Marking the end of the conversation means the next round reads all
    # of it back at a tenth of the price instead of paying full freight again.
    if msgs:
        tail = msgs[-1]["content"]
        if isinstance(tail, list) and tail:
            tail[-1]["cache_control"] = {"type": "ephemeral"}
    if len(msgs) > 2:
        mid = msgs[-3]["content"]      # a second, older anchor, so a miss is partial
        if isinstance(mid, list) and mid:
            mid[-1]["cache_control"] = {"type": "ephemeral"}

    # The persona, the rules and the tool block are byte for byte the same on
    # every tick, but ticks are 20 minutes apart and the default cache only
    # lives 5, so every tick used to pay to write them again. An hour long
    # cache outlives the gap: written once, read by the next two or three ticks.
    # The conversation anchors above stay on 5 minutes, because they are
    # different every tick and a 1h write costs more.
    tools = [dict(s) for s in schema]
    tools[-1]["cache_control"] = {"type": "ephemeral"}
    MAXTOK = int(os.environ.get("OTTO_MAX_TOKENS", "4000"))

    def _send(ttl):
        sysblock = [{"type": "text", "text": system,
                     "cache_control": {"type": "ephemeral", **({"ttl": ttl} if ttl else {})}}]
        tl = [dict(t) for t in tools]
        if tl:
            cc = dict(tl[-1].get("cache_control") or {"type": "ephemeral"})
            if ttl: cc["ttl"] = ttl
            else: cc.pop("ttl", None)
            tl[-1]["cache_control"] = cc
        return Anthropic().messages.create(
            model=model(), max_tokens=MAXTOK,
            system=sysblock, tools=tl, messages=msgs)

    try:
        r = _send(LONG_TTL)
    except Exception as e:
        # if this build of the API will not take a 1h cache, fall back for good
        # rather than failing a tick over a saving
        if LONG_TTL and ("ttl" in str(e).lower() or "cache" in str(e).lower()):
            print("    1h cache refused, falling back to the 5 minute default")
            LONG_TTL = None
            r = _send(None)
        else:
            raise
    u = getattr(r, "usage", None)
    if u:
        USAGE["in"] += getattr(u, "input_tokens", 0) or 0
        USAGE["out"] += getattr(u, "output_tokens", 0) or 0
        USAGE["cache_write"] += getattr(u, "cache_creation_input_tokens", 0) or 0
        USAGE["cache_read"] += getattr(u, "cache_read_input_tokens", 0) or 0
    USAGE["calls"] += 1
    text = " ".join(b.text for b in r.content if b.type == "text").strip()
    calls = [{"id": b.id, "name": b.name, "input": b.input}
             for b in r.content if b.type == "tool_use"]
    return text, calls


# ------------------------------------------------------------------ gemini
def _gemini_schema(s):
    """JSON Schema -> Gemini function declaration. Drops what it will not accept."""
    def clean(node):
        if not isinstance(node, dict):
            return node
        out = {k: v for k, v in node.items() if k in
               ("type", "description", "properties", "required", "items", "enum")}
        if "properties" in out:
            out["properties"] = {k: clean(v) for k, v in out["properties"].items()}
        if "items" in out:
            out["items"] = clean(out["items"])
        return out
    d = {"name": s["name"], "description": s["description"]}
    p = clean(s["input_schema"])
    if p.get("properties"):
        d["parameters"] = p
    return d


def _gemini(system, turns, schema):
    key = os.environ.get("GEMINI_API_KEY") or os.environ["GOOGLE_API_KEY"]
    contents = []
    for t in turns:
        if t["role"] == "user":
            contents.append({"role": "user", "parts": [{"text": t["text"]}]})
        elif t["role"] == "assistant":
            parts = ([{"text": t["text"]}] if t.get("text") else []) + \
                    [{"functionCall": {"name": c["name"], "args": c["input"]}}
                     for c in t.get("calls", [])]
            contents.append({"role": "model", "parts": parts})
        else:
            contents.append({"role": "user", "parts": [
                {"functionResponse": {"name": r["name"], "response": {"result": r["output"]}}}
                for r in t["results"]]})
    body = {"contents": contents,
            "systemInstruction": {"parts": [{"text": system}]},
            "tools": [{"functionDeclarations": [_gemini_schema(s) for s in schema]}],
            "generationConfig": {"maxOutputTokens": 4000}}
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{model()}:generateContent?key={key}")
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.load(r)
    um = data.get("usageMetadata") or {}
    USAGE["in"] += um.get("promptTokenCount", 0)
    USAGE["out"] += um.get("candidatesTokenCount", 0)
    USAGE["calls"] += 1
    cands = data.get("candidates") or []
    if not cands:
        return "", []
    parts = cands[0].get("content", {}).get("parts", []) or []
    text = " ".join(p["text"] for p in parts if "text" in p).strip()
    calls = []
    for i, p in enumerate(parts):
        if "functionCall" in p:
            fc = p["functionCall"]
            calls.append({"id": f"g{i}", "name": fc["name"], "input": fc.get("args", {})})
    return text, calls


# ------------------------------------------------------------------ openrouter
def _openai_tools(schema):
    return [{"type": "function", "function": {
        "name": s["name"], "description": s["description"],
        "parameters": s["input_schema"]}} for s in schema]


def _openrouter(system, turns, schema):
    msgs = [{"role": "system", "content": system}]
    for t in turns:
        if t["role"] == "user":
            msgs.append({"role": "user", "content": t["text"]})
        elif t["role"] == "assistant":
            m = {"role": "assistant", "content": t.get("text") or None}
            if t.get("calls"):
                m["tool_calls"] = [{"id": c["id"], "type": "function",
                                    "function": {"name": c["name"],
                                                 "arguments": json.dumps(c["input"])}}
                                   for c in t["calls"]]
            msgs.append(m)
        else:
            for r in t["results"]:
                msgs.append({"role": "tool", "tool_call_id": r["id"], "content": r["output"]})
    body = {"model": model(), "messages": msgs,
            "tools": _openai_tools(schema), "max_tokens": 4000}
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + os.environ["OPENROUTER_API_KEY"]})
    with urllib.request.urlopen(req, timeout=120) as r:
        data = json.load(r)
    un = data.get("usage") or {}
    USAGE["in"] += un.get("prompt_tokens", 0)
    USAGE["out"] += un.get("completion_tokens", 0)
    USAGE["calls"] += 1
    if not data.get("choices"):
        return "", []
    m = data["choices"][0]["message"]
    calls = []
    for c in (m.get("tool_calls") or []):
        try:
            args = json.loads(c["function"].get("arguments") or "{}")
        except json.JSONDecodeError:
            args = {}
        calls.append({"id": c["id"], "name": c["function"]["name"], "input": args})
    return (m.get("content") or "").strip(), calls


def think(system, turns, schema):
    p = provider()
    if p == "anthropic":
        return _anthropic(system, turns, schema)
    if p == "gemini":
        return _gemini(system, turns, schema)
    if p == "openrouter":
        return _openrouter(system, turns, schema)
    import pathlib as _pl
    env = _pl.Path(__file__).resolve().parent / ".env"
    found = [k for k in ("ANTHROPIC_API_KEY", "GEMINI_API_KEY", "OPENROUTER_API_KEY")
             if os.environ.get(k)]
    raise SystemExit(
        "no model configured.\n"
        f"  .env file:        {'found' if env.exists() else 'NOT FOUND'} at {env}\n"
        f"  keys in the env:  {found or 'none'}\n"
        "  put one of ANTHROPIC_API_KEY, GEMINI_API_KEY or OPENROUTER_API_KEY in .env,\n"
        "  or export it in this shell, then run again.")


# ------------------------------------------------------------------ advisor
ADVISOR_RULES = """you are the slow part of otto's mind. he is a hedgehog who lives
alone in a village and works things out for himself. he has stopped in front of
something and wants to think about it properly before going on.

you are him thinking, not someone explaining things to him. write as his own
thought: plain, first person, short.

what you must not do, and this matters more than being useful:

do not produce knowledge out of nowhere. if a number, a rule, a formula, a
material property or a technical word comes into your head and he cannot say
where he got it, he did not get it anywhere, and you must not use it. you know
only what is written below under what he knows and what is in front of him.

do not name a thing he has not met. if he has not met the word, describe the
thing instead: what it looks like, what it does, how it behaves.

do not give him facts about the real world, history, science or how anything is
normally done. he has a library, a shop and the web, and finding out is his to
do. if the answer needs something he has not got, say what he would need to go
and look at or try, not what the answer is.

guessing is good, and a guess is his. say it is a guess and say what would show
whether it is right. the best thing you can give him is the next thing to try.

four or five sentences. no lists, no headings."""


def advise(question, context):
    """One careful thought from the deep model. Returns None when the advisor is
    off, used up for this tick, or unavailable, and the caller falls back to the
    old behaviour of sleeping on it."""
    if not ADVISOR or not question:
        return None
    if ADVISOR_USED["n"] >= ADVISOR_MAX:
        return None
    if provider() != "anthropic":
        return None                       # only wired for anthropic so far
    try:
        from anthropic import Anthropic
        r = Anthropic().messages.create(
            model=deep_model(),
            max_tokens=int(os.environ.get("OTTO_ADVISOR_TOKENS", "400")),
            system=[{"type": "text", "text": ADVISOR_RULES,
                     "cache_control": {"type": "ephemeral",
                                       **({"ttl": LONG_TTL} if LONG_TTL else {})}}],
            messages=[{"role": "user", "content":
                       f"{context}\n\nwhat he has stopped to think about:\n{question}"}])
    except Exception as e:
        print(f"    advisor call failed, sleeping on it instead: {e}")
        return None
    ADVISOR_USED["n"] += 1
    u = getattr(r, "usage", None)
    if u:
        ADVISOR_USAGE["in"] += getattr(u, "input_tokens", 0) or 0
        ADVISOR_USAGE["out"] += getattr(u, "output_tokens", 0) or 0
        ADVISOR_USAGE["cache_write"] += getattr(u, "cache_creation_input_tokens", 0) or 0
        ADVISOR_USAGE["cache_read"] += getattr(u, "cache_read_input_tokens", 0) or 0
    ADVISOR_USAGE["calls"] += 1
    return " ".join(b.text for b in r.content if b.type == "text").strip() or None
