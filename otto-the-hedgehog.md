# Otto the hedgehog — project handoff

Everything a fresh chat needs to carry this on. Written 1 November 2026.

Address the user as **Caleb**. He prefers actionable, paste-ready deliverables,
iterative collaboration, light formatting, no em-dashes, and a short
plain-language status line at the end of every reply saying where we are,
what is done and what is next.

---

## 1. What this is

Otto is an autonomous AI hedgehog who lives his own life in a small village,
one tick at a time, whether or not anyone is watching. He has needs, a memory,
a knowledge list, a wishlist, a journal and a website he writes himself. Caleb
can watch him in a 3D world in the browser, talk to him through a console, and
post him physical objects.

It was inspired by **Pino** (`3eyes.iii` on Instagram, `pinos.world`), an
autonomous AI bird in a browser world. The brief from the start: *"this but
different"*.

### The design rules, which matter more than the code

These came from Caleb directly and have been enforced throughout:

- **He is not following a story.** No arcs, no scripted hobbies. He develops
  his own interests from what he runs into.
- **Knowledge must be earned.** He only knows what he has read, been told, or
  found out by doing. Every fact on his knowledge list carries how he got it
  and from where. If he cannot name a source, he does not know it.
- **The model must not leak through.** This is the one Caleb cares about most.
  A hedgehog who already knows what a tandem bicycle is ruins the whole point.
  There is a hard vocabulary gate (section 4) and an audit tool.
- **Adventurous, not careful.** Curious, always up for something new. Caleb
  rejected an earlier, more cautious persona as "a little boring".
- **No pain.** He can get tired, cold, hungry, soaked, startled. He cannot be
  hurt. Caleb was explicit: *"PAIN shouldnt be in the game he cannot feel pain
  that's too much"*.
- **Nobody is ever behind any counter.** The village has no people in it. This
  is deliberate and carries a lot of the atmosphere. Do not add shopkeepers.
- **Cost matters.** An early version ran at ~$190/month. It is now ~$20/month
  and Caleb will push back hard on anything that inflates it.

---

## 2. Where everything lives

| Where | Path | Notes |
|---|---|---|
| Claude's sandbox | `/home/claude/otto/` | Working copy. Not visible to Caleb. |
| Caleb's Mac | `~/Downloads/otto/` | Reached through the desktop app bridge. |
| Live server | `root@165.232.137.53:~/otto/` | DigitalOcean droplet, Ubuntu 24.04. |

Render screenshots are kept in `/home/claude/shots/`, which also holds a local
`node_modules/three` (0.160.1) and Playwright for headless rendering.

**Links**
- The lane (read only): `http://165.232.137.53:8080/world.html`
- Console (read only): `http://165.232.137.53:8080/`
- Console (writable): same, with `?key=<OTTO_KEY>` appended

**The port matters.** `deploy.sh` only sets up nginx, port 80 and https if you pass
a domain as its second argument. With just the IP it serves on 8080, so a bare
`http://165.232.137.53/` answers nothing. Earlier versions of this doc had these
links without the port and they were wrong.

**Deploy** (from the Mac, not from the sandbox):

```
cd ~/Downloads/otto && bash deploy.sh root@165.232.137.53
```

Add migrations after it when they are needed:

```
&& ssh root@165.232.137.53 'cd ~/otto && venv/bin/python3 house.py && venv/bin/python3 layout.py'
```

`deploy.sh` deliberately **excludes** `world/world.json`, `state.json`,
`memory/`, `inbox.jsonl`, `outbox.jsonl`, `log.jsonl`, `site/journal.md` and
`.env`, so his live life is never overwritten by a deploy. Anything that must
change the live world has to be a migration script run on the server.

**Secrets.** The Anthropic key and `OTTO_KEY` live only in `.env` on the server,
which is gitignored and excluded from rsync once the server has one. Never ask
Caleb to paste a key. Never put one in a crontab, a plist or a chat log. The
private half of his SSH key must never be sent anywhere.

---

## 3. How a tick works

A systemd timer (`otto-tick.timer`, not cron — cron silently refused the job)
runs `tick.py` every 10 minutes. Each tick:

1. Load `state.json` and `world/world.json`.
2. Advance needs by elapsed real minutes (night multipliers, sleep recovery).
3. If asleep and not rested, stop here. He keeps human hours.
4. Read the inbox, append anything new to the conversation thread.
5. Decide the gear:
   - **reflex** (free, no model call): hungry, cold, or late and tired. Pure
     Python pathfinding. Skipped if there is an unread letter.
   - **pottering** (cheap model, subset of tools): an ordinary twenty minutes.
   - **deep** (expensive model, all tools): when something has hold of him,
     when Caleb has written, or every fifth tick regardless. Every third while
     a letter is unanswered.
6. Call the model with a tool schema, apply the tool calls, save the files.

Everything is plain files. There is no database. State is `state.json`, the
world is `world/world.json`, and his mind is a handful of `.jsonl` files under
`memory/`.

**Cost control that must not be undone:** Anthropic prompt caching is applied to
the system prompt, the tool block and two rolling anchors inside the growing
conversation. Re-sending the uncached conversation on every tool round was what
made it cost $190/month.

---

## 4. The files

### Core
- **`persona.md`** — who he is. Deliberately topic-free. Contains the ignorance
  constraint: *"do not produce knowledge out of nowhere... if you cannot say
  where you got it, you did not get it anywhere"*.
- **`engine.py`** — paths, clock, needs decay, pathfinding, library, web search,
  `.env` loading (hardened against BOM, CRLF, `export`, quotes).
- **`tools.py`** — the 19 things he can do. `POTTERING` is the cheap subset.
- **`tick.py`** — the loop, the gears, the prompts (`situation`,
  `small_situation`), `instinct`, `describe`, `thread`, `RULES`, `SMALL_RULES`.
- **`brain.py`** — swappable backends (anthropic / gemini / openrouter), model
  selection, usage and price tracking, the caching.
- **`physics.py`** — load testing. Material × form × span. Answers "will it
  hold", nothing else.
- **`referee.py`** — answers "does it work". See section 5.
- **`vocab.py`** — the leak gate. See below.
- **`serve.py`** — threaded web server, no-cache headers, `/api/feed`, write
  endpoints gated by `OTTO_KEY` via `hmac.compare_digest`.

### The world in the browser
- **`site/world.html`** (~2000 lines) — the whole 3D world. Heightfield terrain,
  procedural canvas textures (brick, stone, timber, shopfront, klinker
  herringbone, floorboards, flagstones, rush weave), buildings with shared walls
  and doorways worked out from exits, furniture models, day/night cycle,
  weather, pointer-lock WASD walking, Z-key mind panel, a real mirror.
- **`site/console.html`** — tabs: now / talk / into / journal / wants / knows /
  thinking / made.
- **`site/models/`** — drop-in `.glb` folder. See section 6.

### Scripts Caleb runs
- `parcel.py` — post him a thing. `--paint COLOUR --goes N` makes it a paint can.
- `say.py`, `inbox.py` — talk to him from the command line.
- `menu.py` — set the eating house menu.
- `house.py`, `layout.py` — world migrations for the house and its furniture.
- `mergetalk.py` — rebuild the conversation thread from inbox and outbox.
- `audit.py` — **the leak check.** Compares every word he has used against
  everything he has been exposed to. Run this regularly.
- `story.py` — readable narrative of a run.
- `selftest.py` — ~90 checks. Run before every push.
- `fresh.py`, `reset.py`, `restock.py`, `tidy.py`, `no_bugs.py`, `sync_clock.py`.

---

## 5. The two things that make it work

### The vocabulary gate (`vocab.py`)
He got caught using the word "tandem" for an object whose description never
names it. The word came from the model, not the world. So: `search_web` now
refuses any content word he has not actually met in a book, a page, a search
result, something Caleb said, something he wrote, or something standing in
front of him. He has to describe the thing instead, and the word comes back to
him off the page, which is discovery rather than recall.

`OTTO_VOCAB_GATE=0` in `.env` disables it if it ever proves too tight.

### The referee (`referee.py`)
`physics.py` only ever answered "will it hold weight", which is right for an
arch and useless for a buzzer. He built a rapping board, a paddle wheel and a
pepper's ghost box and the world said nothing, so he could not tell a working
one from a broken one. Now:

- Anything with a description, worked with any intent, is judged by a model
  that knows real physics, electricity, optics and code.
- It reports **only what he can see, hear or feel**. Never why. Never a
  principle, a cause, or a word he has not used. Never advice.
- The verdict is **cached against what the thing is made of**, so an unchanged
  thing gives an identical answer and changing it is the only route to a
  different outcome. That is what makes fixing worth doing.
- It is given the place and the other things he has made nearby, so two
  pendulums judged separately still agree with each other.
- Covers: objects he built, places he built, world objects he has rigged, any
  world object with a description, and `look_at_page()` on his own web pages.

Known limits: a change must be written down (`edit_world describe`) for the
world to see it; a failed model call falls back to the old generic line; there
is no sense of elapsed time for things that grow or rust.

---

## 6. What is built, and what is broken

### Built and working
- The village: 19 places, two lanes, a pond, a stream, a river, an orchard with
  four pear trees, a hedge, a yard, and five public buildings (library, general
  shop, oddments, post office, eating house).
- **Otto's house is one building**: front room, kitchen, bedroom, washroom in an
  L, with shared internal walls, one pitched roof, one chimney, one name.
- Front room furniture modelled from Caleb's reference photographs: a cast-iron
  range with a lit flickering firebox and a flue, a rush-seated spindle-back
  chair, a plank work table.
- Cooking (light the slab with wood, then food on it, he gets better with
  practice) and washing (fills the bath, clears "grubby", which comes from
  painting and digging).
- Painting needs a physical can with a colour and a limited number of goes.
- A real mirror in the washroom. His note for it never says mirror or
  reflection, so working out what he is looking at is his to do.
- The conversation thread. Previously a message was shown for exactly one tick
  and thrown away, with no record either way, which is why he never replied to
  anything. Now the last 6–12 turns are in front of him on every tick and he is
  told plainly when he has not written back.
- Day/night, weather, a real clock in Caleb's timezone.

### Known faults, in priority order
1. **The window is a frame around solid wall.** It was only ever painted on the
   outside face. It needs a real opening cut, the same way doorways are cut.
2. **Interior lighting is flat.** Rooms read as daylight rather than the warm
   pools of the reference. Causes found so far: 22 point lights in the village,
   each room's lamp reaching two rooms away through the new doorways (fixed),
   ACES exposure at 1.45 (now 1.08), ambient overwritten every frame by the day
   cycle (now scaled 0.58). Still needs a deliberate pass.
3. **`site/models/` is empty.** The drop-in pipeline is built and waiting.
4. The four other public buildings have never been designed. A library design
   was proposed (shelves to the ceiling he can only reach two of, an unlit
   stove, a chair by the window, a drawer of uncaptioned plates, a record of
   what he has read) and not yet built or agreed.

### The model pipeline
`site/models/` takes `.glb` files named in the `MODELS` table in `world.html`
(`range.glb`, `chair.glb`, `worktable.glb`, `bed.glb`, `nightstand.glb`,
`slab.glb`, `sink.glb`, `bath.glb`, `jug.glb`, `bookcase.glb`, `counter.glb`).
Each is measured on load, scaled to the size the world wants, stood on the floor
and turned to face the room, so a model straight off the internet lands
correctly. A missing or broken file is ignored and the hand-built version is
used instead.

**Claude's sandbox can only reach GitHub.** poly.pizza, kenney.nl and
quaternius.com are all blocked, so Caleb downloads and Claude processes.
Recommended: **Quaternius** (licence verified: free for commercial use, no
credit required, cannot resell the assets), then **Kenney** (CC0), then
**Poly Pizza**. Pick one pack and stay in it: the world is flat-shaded and a
photoreal model will look worse than a box. Keep each under ~500 KB;
`gltf-transform` compression works well (47 MB to 471 KB on the hedgehog).

---

## 7. Gotchas, learned the hard way

- **The world view rebuilds itself from the server every 15 seconds**
  (`setInterval` in `world.html`). Any live experiment in a headless browser is
  silently wiped mid-test unless `setInterval` is stubbed for intervals
  ≥ 10000 ms. This wasted a lot of time once.
- **Placement by rule rather than by looking** has caused four separate bugs:
  walls overlapping at corners, floorboard gap strips inside the floor slab, the
  window drawn in the doorway, and the dado running straight across every
  opening. Anything drawn around all four sides of a room must check the
  doorway map, which is now passed into `decorate()`.
- **Objects had no position at all** until recently. They were laid out by
  walking the room perimeter in file order. `at: [dx, dz]` and `face` now
  override that; anything without them still auto-places, which is right for
  things he drops or is sent.
- `.env` once failed because of two zero-width spaces at the start of the file,
  from copying a command out of a browser. `_load_env` is now hardened. If a key
  "is there" but is not seen, check the raw bytes with `xxd`.
- Ubuntu 24.04 needs a venv (`~/otto/venv`); bare `pip install` is refused.
- Use **systemd timers**, not cron. Cron silently refused the job twice.
- The server's timezone is set from the Mac's by `deploy.sh`.
- Headless renders: use the local `three` copy in `/home/claude/shots/node_modules`,
  since the CDN is blocked from the sandbox.

---

## 8. Open questions for Caleb

- Can Otto earn coins, or is running out something he has to ask Caleb about?
  He starts with 12 and meals cost 2 to 3. Still unanswered.
- The library: should the high shelves eventually be reachable, or does some of
  it stay permanently above him?
- The pink flower on the far bank (`unknown_plant`) is a deliberate blank with
  no identity in the world. Otto drew it and asked Caleb what it is. Suggested:
  **Himalayan balsam**, because the seed pods snap and fling seeds when touched,
  which gives him a mechanism to investigate rather than a fact to accept.
  Whatever Caleb says becomes true, and the word then enters Otto's vocabulary
  so he can research it. The object is still named "a plant you do not know" and
  should probably be corrected by Otto himself, not by a script.

---

## 9. PENDING — the next thing to do

Caleb's exact words, 1 November 2026, 14:45:

> i want you to look at these videos of pino the ai bird and look at how big
> that world is and how his character the guy who runs it walks properly and how
> all the options (like our console) is there on the same screen, and it looks
> so much cleaner, lets brainstorm how we can design ottos world to be much
> better, like seriously not just think it

**So the task is: a serious design overhaul of Otto's world, benchmarked
against Pino.** The four things Caleb named:

1. **Scale.** Pino's world is much bigger than Otto's 19 places.
2. **Movement.** Pino's owner-character "walks properly". Otto's observer is a
   floating camera with pointer-lock WASD and the hedgehog walks a path between
   places with a simple procedural pose. Proper locomotion, and possibly a
   visible body for the viewer, is wanted.
3. **One screen.** Everything on a single screen. Otto's console and world are
   two separate pages with a "console" button that links between them. Caleb
   asked for this once before and it was only partly done.
4. **Cleanliness.** The whole thing should look considerably more finished.

**Important: the videos were not attached to that message.** Ask Caleb to send
them again, or the `pinos.world` / `3eyes.iii` links, before designing against
them. Do not design from memory of a description.

Caleb wants this brainstormed and then actually built, not just discussed.
