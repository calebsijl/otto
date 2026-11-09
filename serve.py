#!/usr/bin/env python3
"""Serves otto's site, his world, and the console you talk to him through."""
import http.server, socketserver, pathlib, re, html, sys, json, datetime, os, hmac

HERE = pathlib.Path(__file__).resolve().parent
SITE = HERE / "site"
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else int(os.environ.get("PORT", 8080))
BIND = os.environ.get("OTTO_BIND", "")          # "" = every interface
KEY  = os.environ.get("OTTO_KEY", "")           # set it and only you can write

def jlines(p, limit=None):
    if not p.exists():
        return []
    rows = []
    for line in p.read_text(errors="ignore").splitlines():
        line = line.strip()
        if line:
            try: rows.append(json.loads(line))
            except json.JSONDecodeError: pass
    return rows[-limit:] if limit else rows

SHELL = """<!doctype html><meta charset=utf-8><title>{t}</title>
<meta name=viewport content="width=device-width,initial-scale=1">
<style>
body{{background:#f4f1ea;color:#2b2722;font:16px/1.65 ui-monospace,Menlo,monospace;
max-width:40rem;margin:4rem auto;padding:0 1.5rem}}
a{{color:#2b2722}} h1,h2{{font-weight:600;letter-spacing:-.01em}}
h2{{margin-top:2.6rem;font-size:1rem;color:#8a7f70}}
hr{{border:0;border-top:1px solid #ddd6c9;margin:2.5rem 0}}
nav{{margin-bottom:3rem;color:#8a7f70}}
</style><nav><a href="/">otto</a> · <a href="/console.html">console</a> ·
<a href="/world.html">the lane</a></nav>{b}"""

def md(txt):
    out=[]
    for line in txt.split("\n"):
        if line.startswith("## "): out.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("# "): out.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("- "): out.append(f"<li>{html.escape(line[2:])}</li>")
        elif line.strip(): out.append(f"<p>{html.escape(line)}</p>")
    return "\n".join(out)

def activity(n=70):
    """Flatten the log into a stream of things he did, newest first."""
    rows = jlines(HERE/"log.jsonl", 260)
    out = []
    for r in reversed(rows):
        out.append({"tick": r.get("tick"), "clock": (r.get("clock") or "")[11:16],
                    "mood": r.get("mood",""),
                    "calls": [{"name": c.get("name"), "input": c.get("input", {}),
                               "result": (c.get("result") or "")[:260]}
                              for c in r.get("calls", [])]})
        if len(out) >= n: break
    return out


def interests():
    """What he is actually into, worked out from what he has been doing."""
    log = jlines(HERE/"log.jsonl", 600)
    searches, books, built, tested = [], {}, [], {}
    for r in log:
        for c in r.get("calls", []):
            i = c.get("input") or {}
            if c["name"] == "search_web" and i.get("query"): searches.append(i["query"])
            if c["name"] == "read_book" and i.get("book"):
                books[i["book"]] = books.get(i["book"], 0) + 1
            if c["name"] == "write_site" and i.get("path"): built.append(i["path"])
            if c["name"] == "test" and i.get("object"):
                k = re.sub(r"[_\d]+$", "", str(i["object"]))
                tested[k] = tested.get(k, 0) + 1
    kp = HERE/"memory"/"kept.md"
    chasing = []
    if kp.exists():
        for line in kp.read_text().splitlines():
            m = re.search(r"chasing:?\s*([^.;]+)", line, re.I)
            if m:
                t = m.group(1).strip().lower()
                if t and t not in chasing: chasing.append(t)
    wk = HERE/"memory"/"knows.md"
    sources = {}
    if wk.exists():
        for line in wk.read_text().splitlines():
            m = re.search(r"\[(read|tried|caleb|worked out):", line)
            if m: sources[m.group(1)] = sources.get(m.group(1), 0) + 1
    return {"chasing": chasing[-6:][::-1],
            "searches": list(dict.fromkeys(searches))[::-1][:16],
            "books": sorted(books.items(), key=lambda x:-x[1]),
            "built": list(dict.fromkeys(built))[::-1][:20],
            "tested": sorted(tested.items(), key=lambda x:-x[1])[:14],
            "sources": sources}


def feed():
    state = json.loads((HERE/"state.json").read_text()) if (HERE/"state.json").exists() else {}
    jp = SITE/"journal.md"
    entries=[]
    if jp.exists():
        for block in jp.read_text().split("\n## ")[1:]:
            head, _, body = block.partition("\n")
            entries.append({"when": head.strip(), "text": body.strip()})
    pages = sorted(p.name for p in SITE.iterdir() if p.is_file() and p.name not in
                   ("console.html","world.html")) if SITE.exists() else []
    knows = (HERE/"memory"/"knows.md")
    return {
      "state": state,
      "journal": list(reversed(entries))[:60],
      "from_otto": list(reversed(jlines(HERE/"outbox.jsonl")))[:80],
      "to_otto": list(reversed(jlines(HERE/"inbox.jsonl")))[:80],
      "wishes": jlines(HERE/"memory"/"wishes.jsonl"),
      "thoughts": list(reversed(jlines(HERE/"thoughts.jsonl")))[:60],
      "knows": [l[2:] for l in knows.read_text().splitlines() if l.startswith("- ")][::-1][:60]
                if knows.exists() else [],
      "pages": pages,
      "activity": activity(),
      "interests": interests(),
      "live": _running(),
      "readonly": bool(KEY),
    }


def _running():
    """Is a run happening right now? True if the log moved in the last 90 seconds."""
    lp = HERE/"log.jsonl"
    if not lp.exists(): return False
    import time
    return (time.time() - lp.stat().st_mtime) < 90

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self,*a,**k): super().__init__(*a, directory=str(SITE), **k)
    def log_message(self, *a): pass

    def end_headers(self):
        # never let the browser cache anything here, or you edit a file and see the old one
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        super().end_headers()

    def send_header(self, k, v):
        if k == "Cache-Control" and getattr(self, "_cc", False): return
        if k == "Cache-Control": self._cc = True
        super().send_header(k, v)

    def send_response(self, *a, **k):
        self._cc = False
        super().send_response(*a, **k)

    def _send(self, body, ctype="application/json"):
        if isinstance(body,(dict,list)): body=json.dumps(body).encode()
        elif isinstance(body,str): body=body.encode()
        self.send_response(200); self.send_header("Content-Type",ctype)
        self.send_header("Cache-Control","no-store")
        self.send_header("Content-Length",str(len(body))); self.end_headers()
        self.wfile.write(body)

    def _may_write(self, data):
        if not KEY: return True
        given = (self.headers.get("X-Otto-Key") or data.get("key") or "")
        return hmac.compare_digest(str(given), KEY)

    def do_POST(self):
        n=int(self.headers.get("Content-Length",0))
        try: data=json.loads(self.rfile.read(n) or b"{}")
        except json.JSONDecodeError: data={}
        clock=json.loads((HERE/"state.json").read_text()).get("clock","") \
              if (HERE/"state.json").exists() else ""
        if not self._may_write(data):
            return self._send({"ok":False,"error":"read only. only caleb can send him things."})
        if self.path=="/api/say":
            text=(data.get("text") or "").strip()
            if not text: return self._send({"ok":False,"error":"nothing to say"})
            with (HERE/"inbox.jsonl").open("a") as f:
                f.write(json.dumps({"t":clock,"text":text,"read":False,
                                    "sent":datetime.datetime.now().isoformat(timespec="seconds")})+"\n")
            return self._send({"ok":True})
        if self.path=="/api/parcel":
            name=(data.get("name") or "").strip()
            if not name: return self._send({"ok":False,"error":"no name"})
            wp=HERE/"world"/"world.json"; w=json.loads(wp.read_text())
            oid=re.sub(r"[^a-z0-9]+","_",name.lower())[:28]+f"_{len(w['objects'])}"
            w["objects"].append({"id":oid,"name":name,"place":"post_office",
                                 "tags":["gift"],"note":"came in the post.","from":"caleb"})
            wp.write_text(json.dumps(w,indent=2))
            with (HERE/"inbox.jsonl").open("a") as f:
                f.write(json.dumps({"t":clock,"text":"there is a parcel for you at the post office.",
                                    "read":False})+"\n")
            return self._send({"ok":True})
        self.send_error(404)

    def do_GET(self):
        rel=self.path.lstrip("/").split("?")[0]
        if rel=="api/feed": return self._send(feed())
        if rel in ("world.json","state.json"):
            src=(HERE/"world"/"world.json") if rel=="world.json" else (HERE/"state.json")
            if src.exists(): return self._send(src.read_bytes())
        if rel=="": rel="console.html"
        p=SITE/rel
        if p.is_dir(): p=p/"index.md"
        if not p.exists() and (SITE/(rel+".md")).exists(): p=SITE/(rel+".md")
        if p.suffix==".md" and p.exists():
            return self._send(SHELL.format(t=p.stem,b=md(p.read_text())),"text/html; charset=utf-8")
        if not p.exists() and rel=="console.html":
            return self._send("<p>console.html is missing from site/</p>","text/html")
        return super().do_GET()

SITE.mkdir(exist_ok=True)
socketserver.TCPServer.allow_reuse_address=True
class Threaded(socketserver.ThreadingMixIn, socketserver.TCPServer):
    daemon_threads = True

print(f"otto's console  http://localhost:{PORT}")
print(f"the lane        http://localhost:{PORT}/world.html")
if KEY:
    print(f"\nwriting is locked. your own link:  http://localhost:{PORT}/?key={KEY}")
    print("anyone without that can watch but not send him anything.")
else:
    print("\nOTTO_KEY is not set, so anyone who can reach this can message him.")
    print("set OTTO_KEY before putting it on the internet.")
Threaded.allow_reuse_address = True
Threaded((BIND,PORT),H).serve_forever()
