# otto, handoff

Written 2026-11-13. Everything below was checked against the running server,
not against this folder, because the two differ in ways that matter.

## What this is

A hedgehog who lives in a small Dutch village and runs his own life. A tick
loop asks a model what he wants to do, applies it to a world file, and a
three.js page renders the result. He is autonomous: nobody drives him, and he
is not told what things are.

- live at **http://165.232.137.53:8080**
- server **root@165.232.137.53**, project at `~/otto` there
- working copy on the mac at `~/Downloads/otto`
- github: private repo, pushed **from the server only**

## The three-way split, which is where most mistakes come from

There are three copies of this project and they are not the same thing.

| | code | world.json, state.json, memory | pushes to github |
|---|---|---|---|
| mac `~/Downloads/otto` | edited here | **stale, ignore it** | no, no remote, no commits |
| server `~/otto` | deployed here | **the real ones** | yes, hourly |
| github | backup of the server | backup of the server | n/a |

`deploy.sh` rsyncs code up and **deliberately excludes** `world/world.json`,
`state.json`, `memory/`, the jsonl logs and `.env`. That is correct: it stops a
deploy from overwriting his life. The consequence people keep tripping over is
that **anything you change in the world on the mac never reaches him.** World
changes have to be a migration script that runs on the server.

The mac copy of `world/world.json` is from before the wipe and is misleading.
At the time of writing it claims 144 objects and 7 things he made; the server
has 129 objects and 0 made by him. Do not reason from the mac copy. Read the
server, see below.

## Reading the live world without ssh

The site serves the real files. `serve.py` maps `/world.json` to
`world/world.json` and `/state.json` to the root one. So from any browser
console on the page:

```js
const w = await fetch('/world.json?'+Date.now()).then(r=>r.json());
const s = await fetch('/state.json?'+Date.now()).then(r=>r.json());
```

That is the fastest way to find out what is actually true. Use it before
changing anything.

## Deploying

```
cd ~/Downloads/otto && ./deploy.sh root@165.232.137.53
```

It installs and restarts `otto-web.service`, writes `otto-tick.service` and
`otto-tick.timer`, and leaves the timer in whatever state it found it, so a
deploy does not silently restart a paused hedgehog. Optional second argument is
a domain, which switches it to caddy and https.

Code only. For anything in the world, deploy and then run the migration:

```
ssh root@165.232.137.53 'cd ~/otto && python3 <migration>.py && ./gitsave.sh'
```

`gitsave.sh` runs on the server, commits everything, scans for leaked api keys
and refuses to push if it finds one, then pushes `origin main`. A timer runs it
hourly, so the explicit call is only to make it immediate.

Pause and start him:

```
ssh root@165.232.137.53 'systemctl stop otto-tick.timer'
ssh root@165.232.137.53 'systemctl start otto-tick.timer'
```

`./pull.sh root@165.232.137.53` brings his life back down to the mac to look at.

## Hard-won facts

**Otto's real size.** `otto.glb` is scaled by its longest side, not its height:
`scale = 1.0 / max(size.x, size.z)`. In world units he ends up **1.00 long,
0.62 tall, 0.80 wide**. He is long and low, not a small upright creature. Any
object built to his scale has to start from those numbers.

**He cannot be posed.** The glb has four clips (idle, walk, sleep, eat) and no
bones the renderer can drive. He can be moved and played, not bent. Anything
that needs him in a new posture has to be built in code, the way the placeholder
hedgehog is before the glb loads.

**`buildRig(kind)` starts with `if (MODELCACHE[kind]) return ...clone(true)`.**
A kind listed in `MODELS` is loaded from a glb and the code below is never
reached. Check `MODELS` before writing a rig by hand.

**Object placement.** In `buildObjects`, `o.at` is an offset from the place
centre and `o.face` is the yaw. With no `at` the object walks a fallback ring;
with no `face` it is rotated by a default of 1.2 radians, which is the 69 degree
slew that has bitten benches, flowers and the tandem. **Places overlap.** Giving
an object an `at` without checking the other places' footprints can bury it
inside a building, which is exactly what happened to the tandem: `lane_top`
spans x -4 to 4, `house_main` spans x -9.5 to -2.5, and an `at` of x -3 put the
bike inside his front room where nothing could see it. `tandem.py` now works the
spot out by reading every other place's box. Copy that approach.

**Wheels turn about X.** Spokes therefore belong in the YZ plane
(`rotation.x`), and crank arms swing fore and aft, not side to side. The
original tandem rig had both wrong.

**Street and earth places lay a pad.** `padTop` is 0.20, or 0.30 if paved with
flagstones. Objects dropped at land height sink into their own floor.

**The renderer skips `place === '_carried'`.** That is how a thing he is holding,
or riding, is kept from being drawn twice.

## Where the tandem work stands

Otto found something leaning at the top of the lane. He has never been told what
it is and nothing in the world names it. It is a tandem bicycle.

Done and deployed:

- `site/world.html`, `buildRig('tandem')` rewritten as a twin-lateral open frame
  from a reference photograph: red, chrome guards and rims, gum-wall tyres,
  leather saddles, cream grips, timing chain on the left, drive chain on the
  right, band brake, mudguards, rack, bell, centre stand. Hands `userData.wheels`
  and `userData.cranks` out so the ridden copy can turn them.
- `site/world.html`, `rideUpdate()` plus a call in the frame loop. When
  `STATE.riding` is set it builds one upright copy, keeps it under him, turns the
  wheels by the distance he has actually covered and both cranksets with them,
  and lifts him onto the front saddle. `RIDE_LIFT = 0.88` is the tunable.
- `tools.py`, a `ride` tag handled in `use`. It only fires when his intent is
  about getting on (sit, climb, ride, on top, mount, stand on), so pushing the
  rings or looking underneath still goes to `referee.py` and is judged properly.
  Getting on moves the object to `_carried`; getting off puts it back.

Pending, as of writing:

- `tandem.py` has been rewritten to place the bike at a spot it has checked. It
  has **not** been deployed or run since that rewrite. Run the two commands under
  Deploying. Until then the bike is still inside his house.

Deliberately left out, as too complex for now: the repair (oil, spanner, pump,
patch, rag, about nine coins against a two coin supper), condition and wear on
the machine, and a travel cost for riding it. The design for all of that exists
in the artifact mockup.

Backups before the tandem change: `site/world.html.pretandem.bak`,
`tools.py.pretandem.bak`.

## Open items, not urgent

- The site is plain http, so the owner key travels in clear. A domain passed as
  the second argument to `deploy.sh` switches it to https.
- The visitor chat quota is per ip, so a household shares it and a determined
  person can get round it.
- The old anthropic key in `.env.before-model-fix` should be rotated.
- `~/Downloads/otto/.git` is half initialised: everything staged, no commits, no
  remote, on `master` while the real repo is on `main`. It does nothing and is a
  trap for a future `git` command. Either delete it or wire it up properly.
- Caleb has asked about monetisation: a livestream with paid gifts that appear in
  the world. The design conclusion was that gifts should arrive anonymously, the
  giver's name goes on the site and never in Otto's mouth, and the free version
  should be tested before any payment work. Nothing built.

## House rules

Address him as Caleb. No em-dashes. End replies with a short plain status line.
Light formatting. Weigh options and send them before building. Mock designs up
outside the world before putting them in it. Never tell Otto what something is.
