"""Shared bits: files, clock, needs, world mutation, tools."""
import json, os, pathlib, datetime, re, urllib.parse, urllib.request, html as _html

ROOT    = pathlib.Path(__file__).resolve().parent


def _load_env():
    """Read .env next to this file. A real, non-empty shell variable wins; an
    empty or missing one does not block the file."""
    f = ROOT / ".env"
    if not f.exists():
        return
    try:
        raw = f.read_text(encoding="utf-8-sig")        # strips a BOM if present
    except UnicodeDecodeError:
        raw = f.read_text(errors="ignore")
    for line in raw.replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        line = line.strip().strip("\ufeff\u200b")
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        k = k.strip()
        if k.startswith("export "):
            k = k[7:].strip()
        k = "".join(c for c in k if c.isalnum() or c == "_")   # drop anything invisible
        v = v.strip().strip('"').strip("'")
        if k and v and not os.environ.get(k):
            os.environ[k] = v


_load_env()
STATE   = ROOT / "state.json"
WORLD   = ROOT / "world" / "world.json"
NOTES   = ROOT / "memory" / "notes.jsonl"
KEPT    = ROOT / "memory" / "kept.md"
KNOWS   = ROOT / "memory" / "knows.md"
SEEN    = ROOT / "memory" / "seen.jsonl"
WISHES  = ROOT / "memory" / "wishes.jsonl"
INBOX   = ROOT / "inbox.jsonl"
OUTBOX  = ROOT / "outbox.jsonl"
TALK    = ROOT / "memory" / "talk.jsonl"   # the whole correspondence, both ways
LOG     = ROOT / "log.jsonl"
SITE    = ROOT / "site"
PERSONA = ROOT / "persona.md"

TICK_MINUTES = 20

# how fast a need moves in one 20-minute tick
DECAY = {"energy": -0.021, "fullness": -0.016, "calm": 0.0, "wonder": -0.016}
SLEEP_RECOVER = {"energy": 0.030, "fullness": -0.006, "calm": 0.02, "wonder": 0.0}


def jload(p, default=None):
    if not p.exists():
        return default
    return json.loads(p.read_text() or "null")


def jsave(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2))


def jlines(p, limit=None):
    if not p.exists():
        return []
    rows = [json.loads(l) for l in p.read_text().splitlines() if l.strip()]
    return rows[-limit:] if limit else rows


def jappend(p, obj):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a") as f:
        f.write(json.dumps(obj) + "\n")


def clamp(x):
    return max(0.0, min(1.0, x))


def advance(state, world, minutes=None):
    """Move the clock and decay needs. minutes=None means one standard tick.
    In real-time mode we pass the actual minutes elapsed, so a missed tick still
    makes him hungry and a long gap does not leave him frozen."""
    mins = TICK_MINUTES if minutes is None else max(1.0, min(minutes, 240.0))
    scale = mins / TICK_MINUTES
    t = datetime.datetime.fromisoformat(state["clock"]) + datetime.timedelta(minutes=mins)
    state["clock"] = t.isoformat()
    state["tick"] += 1
    n = state["needs"]
    hour = t.hour + t.minute / 60.0
    night = hour >= 21.5 or hour < 6.5            # the small hours
    evening = 19.0 <= hour < 21.5
    table = SLEEP_RECOVER if state.get("asleep") else DECAY
    for k, d in table.items():
        v = d
        if not state.get("asleep") and k == "energy":
            # being up at night costs more than being up in the daytime
            if night:   v = d * 2.4
            elif evening: v = d * 1.4
        if state.get("asleep") and k == "energy":
            # he sleeps better in the dark, as anything does
            v = d * (1.25 if night else 0.65)
        n[k] = clamp(n[k] + v * scale)
    room_warm = world["places"].get(state["location"], {}).get("warmth", 0.5)
    worn = any("clothing" in (o.get("tags") or [])
               for o in world["objects"] if o["id"] in state.get("carrying", []))
    pull = 0.35 if not worn else 0.35 * 0.45      # a coat slows the cold, it does not stop it
    if worn and room_warm < n["warmth"]:
        room_warm = min(n["warmth"], room_warm + 0.25)
    n["warmth"] = clamp(n["warmth"] + (room_warm - n["warmth"]) * pull)
    # calm drifts back toward a baseline, pulled down by other needs being low
    pressure = min(n["energy"], n["fullness"], n["warmth"])
    target = 0.3 + 0.5 * pressure
    if state.get("grubby"):
        target -= 0.10                 # being covered in something wears on you
    n["calm"] = clamp(n["calm"] + (target - n["calm"]) * 0.25)
    return state


def time_of_day(state):
    """What the hour feels like, in his words."""
    t = datetime.datetime.fromisoformat(state["clock"])
    h = t.hour + t.minute / 60.0
    if 5.0 <= h < 7.0:   return "it is barely light."
    if 7.0 <= h < 11.0:  return "morning."
    if 11.0 <= h < 14.0: return "the middle of the day."
    if 14.0 <= h < 17.5: return "afternoon."
    if 17.5 <= h < 19.5: return "the light is going."
    if 19.5 <= h < 21.5: return "evening. dark outside now."
    if 21.5 <= h < 24.0: return "late. everyone sensible is asleep."
    return "the middle of the night. properly dark and properly quiet."


def mood(state):
    n = state["needs"]
    if state.get("asleep"):
        return "asleep"
    if n["energy"] < 0.2:
        return "worn out"
    if n["fullness"] < 0.25:
        return "hungry"
    if n["warmth"] < 0.3:
        return "cold"
    if n["calm"] < 0.3:
        return "unsettled"
    if n["wonder"] > 0.72:
        return "onto something"
    if n["wonder"] < 0.25:
        return "restless"
    if n["calm"] > 0.7 and n["energy"] > 0.6:
        return "contented"
    return "settled"


def bar(v):
    f = int(round(v * 10))
    return "#" * f + "." * (10 - f)


def obj_by_id(world, oid):
    for o in world["objects"]:
        if o["id"] == oid:
            return o
    return None


def here(world, place):
    return [o for o in world["objects"] if o.get("place") == place]


# ---------------------------------------------------------------- web
UA = {"User-Agent": "Mozilla/5.0 (otto, a hedgehog, learning things)"}


def _get(url, timeout=25):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "ignore")


def _tavily(query, n):
    key = os.environ.get("TAVILY_API_KEY")
    if not key:
        return ""
    req = urllib.request.Request(
        "https://api.tavily.com/search",
        data=json.dumps({"api_key": key, "query": query,
                         "max_results": n, "search_depth": "basic"}).encode(),
        headers={"Content-Type": "application/json", **UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)
    return "\n\n".join(f"{x['title']}\n{x['url']}\n{x.get('content','')[:600]}"
                        for x in data.get("results", [])[:n])


def _wikipedia(query, n):
    """No key, reliable, and well suited to a creature learning how things work."""
    api = "https://en.wikipedia.org/w/api.php"
    hits = json.loads(_get(
        f"{api}?action=query&list=search&srsearch={urllib.parse.quote(query)}"
        f"&format=json&srlimit={n}"))["query"]["search"]
    if not hits:
        return ""
    titles = "|".join(h["title"] for h in hits)
    ex = json.loads(_get(
        f"{api}?action=query&prop=extracts&exintro=1&explaintext=1"
        f"&titles={urllib.parse.quote(titles)}&format=json"))["query"]["pages"]
    out = []
    for page in ex.values():
        t = page.get("title", "")
        body = re.sub(r"\s+", " ", page.get("extract", "")).strip()
        if not body:
            continue
        url = "https://en.wikipedia.org/wiki/" + urllib.parse.quote(t.replace(" ", "_"))
        out.append(f"{t}\n{url}\n{body[:900]}")
    return "\n\n".join(out)


def _duckduckgo(query, n):
    body = _get("https://html.duckduckgo.com/html/?q=" + urllib.parse.quote(query))
    pats = [r'<a[^>]+class="result__a"[^>]*href="([^"]+)"[^>]*>(.*?)</a>',
            r'<a rel="nofollow" href="(http[^"]+)"[^>]*>(.*?)</a>',
            r'<a[^>]+href="(https?://[^"]+)"[^>]*>(.*?)</a>']
    for pat in pats:
        hits = re.findall(pat, body, re.S)
        rows = []
        for href, title in hits:
            title = _html.unescape(re.sub("<[^>]+>", "", title)).strip()
            href = _html.unescape(href)
            if not title or "duckduckgo.com" in href:
                continue
            if href.startswith("//duckduckgo.com/l/?uddg="):
                href = urllib.parse.unquote(href.split("uddg=")[1].split("&")[0])
            rows.append(f"{title}\n{href}")
            if len(rows) >= n:
                break
        if rows:
            return "\n\n".join(rows)
    return ""


def search_web(query, n=5):
    """Try each source in turn. Returns text, or says plainly that nothing came back."""
    errors = []
    for name, fn in (("tavily", _tavily), ("wikipedia", _wikipedia), ("duckduckgo", _duckduckgo)):
        try:
            out = fn(query, n)
            if out and out.strip():
                return out
        except Exception as e:
            errors.append(f"{name}: {e.__class__.__name__}")
    return ("nothing came back for that. "
            + ("tried " + ", ".join(errors) + ". " if errors else "")
            + "try different words, or ask caleb.")


def read_page(url, limit=6000):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode("utf-8", "ignore")
    body = re.sub(r"(?is)<(script|style|nav|footer|header)[^>]*>.*?</\1>", " ", body)
    text = _html.unescape(re.sub(r"<[^>]+>", " ", body))
    return re.sub(r"\s+", " ", text).strip()[:limit]


# ---------------------------------------------------------------- library
LIBRARY = ROOT / "library"
BOOKMARKS = ROOT / "memory" / "bookmarks.json"
ASIDE     = ROOT / "memory" / "aside.json"   # books he has put down on purpose
PAGE = 3800          # characters in one sitting
CACHE = LIBRARY / ".text"


def _extract(path):
    s = path.suffix.lower()
    if s in (".txt", ".md"):
        return path.read_text(errors="ignore")
    if s == ".epub":
        import zipfile
        parts = []
        with zipfile.ZipFile(path) as z:
            for n in sorted(z.namelist()):
                if n.lower().endswith((".xhtml", ".html", ".htm")):
                    parts.append(z.read(n).decode("utf-8", "ignore"))
        body = " ".join(parts)
        body = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", body)
        return re.sub(r"\s+", " ", _html.unescape(re.sub(r"<[^>]+>", " ", body)))
    if s == ".pdf":
        import subprocess, shutil
        if shutil.which("pdftotext"):
            return subprocess.run(["pdftotext", "-q", str(path), "-"],
                                  capture_output=True, text=True).stdout
        try:
            import pypdf
            return "\n".join(p.extract_text() or "" for p in pypdf.PdfReader(str(path)).pages)
        except Exception:
            return ""
    return ""


def book_text(path):
    """Extract once, cache as plain text."""
    CACHE.mkdir(parents=True, exist_ok=True)
    c = CACHE / (path.stem + ".txt")
    if not c.exists() or c.stat().st_mtime < path.stat().st_mtime:
        t = re.sub(r"[ \t]+", " ", _extract(path)).strip()
        c.write_text(t or "(this one would not open)")
    return c.read_text()


def books():
    if not LIBRARY.exists():
        return []
    return sorted(p for p in LIBRARY.iterdir()
                  if p.is_file() and p.suffix.lower() in (".txt", ".md", ".epub", ".pdf"))


def shelf():
    """What he sees on the shelf, with how far through each he is."""
    marks = jload(BOOKMARKS, {}) or {}
    aside = jload(ASIDE, []) or []
    out = []
    for p in books():
        total = max(1, len(book_text(p)))
        pos = marks.get(p.stem, 0)
        pct = int(100 * pos / total)
        if p.stem in aside:
            tag = f"  (you put this one down at {pct}%, and that is allowed)"
        elif pos >= total:
            tag = "  (finished)"
        elif pos:
            tag = f"  ({pct}% in)"
        else:
            tag = "  (unopened)"
        out.append(f"{p.stem}{tag}")
    return out


def read_book(stem, sittings=1):
    marks = jload(BOOKMARKS, {}) or {}
    match = [p for p in books() if stem.lower() in p.stem.lower()]
    if not match:
        return None, "no such book on the shelf."
    p = match[0]
    aside = jload(ASIDE, []) or []
    if p.stem in aside:
        jsave(ASIDE, [s for s in aside if s != p.stem])
    text = book_text(p)
    pos = marks.get(p.stem, 0)
    if pos >= len(text):
        return p.stem, f"you have finished {p.stem}."
    chunk = text[pos:pos + PAGE * sittings]
    marks[p.stem] = pos + len(chunk)
    jsave(BOOKMARKS, marks)
    left = int(100 * marks[p.stem] / max(1, len(text)))
    return p.stem, f"[{p.stem}, {left}% in]\n\n{chunk}"


# ---------------------------------------------------------------- getting about
def route(world, start, goal):
    """Shortest way through the exits. Returns the list of places, start first."""
    if start == goal:
        return [start]
    seen = {start: None}
    q = [start]
    while q:
        cur = q.pop(0)
        if cur == goal:
            break
        for e in world["places"].get(cur, {}).get("exits", []):
            if e not in seen:
                seen[e] = cur
                q.append(e)
    if goal not in seen:
        return []
    path, c = [], goal
    while c is not None:
        path.append(c); c = seen[c]
    return path[::-1]


def nearest(world, start, want):
    """The closest place holding an object that want() likes. Returns (place, object)."""
    best = None
    for o in world["objects"]:
        p = o.get("place")
        if not p or p not in world["places"] or not want(o):
            continue
        r = route(world, start, p)
        if not r:
            continue
        if best is None or len(r) < best[0]:
            best = (len(r), p, o)
    return (best[1], best[2]) if best else (None, None)
