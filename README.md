# otto

a hedgehog who lives in a lane, on a timer.

## what this is

a folder of files plus a script that wakes up every twenty minutes. the script loads his
state, his world, his recent notes and anything you have told him, hands it all to a model,
and applies whatever he decides to do. interests are not configured anywhere. they form
because a note survives in memory/kept.md and he keeps running into it.

## where to put the key

copy .env.example to .env, in this folder, and put your key in it:

    cp .env.example .env
    open -e .env            # or nano .env

    ANTHROPIC_API_KEY=sk-ant-...
    OTTO_MODEL=claude-sonnet-5-5

.env is gitignored and nothing else reads it. a real shell variable, if you set one,
wins over the file. never paste a key into crontab or the plist.

## where it runs

anywhere with python3 and an internet connection. no server, no database, no account.
the whole thing is this folder, and otto is whatever is in these files.

on your mac, for the test:

    ./install-mac.sh        # sets up a launchd timer, every 20 minutes
    tail -f cron.log        # watch him live

your mac must be awake for him to live. plug it in and turn sleep off, or run
`caffeinate -dimsu &`. if the mac does sleep, nothing breaks: his clock only moves when
he wakes, so he does not lose days, his life just runs slower in real time than yours.

for the long run, put the folder on a cheap always-on box, because a creature whose
world stops every time you shut your laptop is a worse creature. any $5 vps works:

    scp -r otto you@box:~/ && ssh you@box
    cd otto && pip3 install anthropic
    crontab -e
    */20 * * * * cd ~/otto && ./run.sh

## the two-hour test, start to finish

1. unpack, and check nothing needs a key:

       cd otto
       ./selftest.py
       ./tick.py --show

2. put three or four books in library/ as .txt, .md, .epub or .pdf. delete
   bridges-sample.txt, it was only there to test the reader. mix them: something
   technical, something opinionated, something irrelevant.

3. key:

       cp .env.example .env
       open -e .env

   ANTHROPIC_API_KEY=sk-ant-...
   OTTO_MODEL=claude-sonnet-5-5

       pip3 install anthropic

4. one tick, on its own. do not launch a batch at an untested config:

       ./tick.py

   you should see one line: the tick number, the time, his mood, and the tools he
   used. it prints the cost of that tick at the end.

5. if that worked, run a day. no timer. ticks run back to back as fast as the api
   answers, so about 15 minutes of real time:

       ./tick.py --ticks 45

   it stops itself at $2 spent. raise that with --budget if you want more.

6. read him:

       ./story.py              what he did, looked up, read, made and kept
       ./story.py --full       every single move, for debugging
       ./serve.py              his website on :8080

7. a second day, to see whether anything carried over:

       ./tick.py --ticks 45
       ./story.py

do not use the timer for testing. it exists so he lives alongside you in real time,
which is the right mode later and the wrong mode now. do not shorten his day either:
his needs and his reading speed are tuned to a 20-minute tick, and compressing it
distorts the thing you are testing.

## what you are judging

after two in-world days, look at exactly three things.

memory/kept.md. has he decided anything is his? an empty file after two days means
nothing is sticking and the fix is the memory window or the persona.

his searches in ./story.py. are they following each other, or is every one unrelated?
a thread means taste is forming. scattered one-offs mean he is reacting, not wanting.

site/journal.md. is it worth reading? this is the actual product. if it is boring,
nothing downstream saves it.

## the plan

phase 1, free. run him on gemini for a few hours. you are testing the machinery, not
the character: does he move, buy things, read, write pages, stay alive overnight.

    ./selftest.py        every check that does not need a model
    ./tick.py --show     the exact prompt, no key, changes nothing
    ./tick.py --fake     scripted creature through the real machinery
    export GEMINI_API_KEY=... OTTO_MODEL=gemini-2.5-flash
    ./tick.py --ticks 10

phase 2, wipe. the free run leaves notes, kept interests and a journal behind, and
those would become the foundation of the real otto. do not build him on a cheap
model's taste.

    ./reset.py --archive gemini-test

phase 3, the real one. anthropic, two days, books on the shelf, left alone.

    export ANTHROPIC_API_KEY=sk-... OTTO_MODEL=claude-sonnet-5-5
    ./tick.py                                 # once, check it works
    */20 * * * * cd /path/to/otto && ./tick.py >> cron.log 2>&1

then read memory/kept.md and site/journal.md. that is the whole test of whether this
works.

## look before you pay

    ./tick.py --show     prints the exact system prompt, exactly what he sees this tick,
                         every tool he can call, and the token count. no key, no API call,
                         changes nothing. read this first.
    ./tick.py --fake     runs a scripted creature through the real machinery so you can
                         watch state.json, the journal and the world actually change.

## run it

he does not care which model thinks for him. pick one.

free, for testing:

    GEMINI_API_KEY=...                       # aistudio.google.com
    OTTO_MODEL=gemini-2.5-flash

or openrouter, one key for everything, free models to test on and claude later:

    OPENROUTER_API_KEY=sk-or-...             # openrouter.ai
    OTTO_MODEL=meta-llama/llama-3.3-70b-instruct:free

the real thing:

    pip install anthropic
    ANTHROPIC_API_KEY=sk-ant-...             # console.anthropic.com
    OTTO_MODEL=claude-sonnet-5-5             # his everyday brain
    # OTTO_MODEL=claude-opus-5-5             # when he is building something

a note on subscriptions: cursor, copilot and the like cannot drive this. they are
editors, not model endpoints, and they do not give you a key you can call from a
script. otto needs a metered api. gemini free or an openrouter free model costs
nothing to test with.

optional, better web search than the free fallback:

    TAVILY_API_KEY=...

then:

    ./tick.py                # one wake-up
    ./tick.py --ticks 20     # a chunk of his day

prompt caching is on for anthropic. his persona and tool list are identical every tick,
so most of each prompt is cached and the bill drops by roughly a third.

on a timer, every 20 minutes:

    */20 * * * * cd /path/to/otto && ./tick.py >> cron.log 2>&1

## your side

    ./say.py there is a thing called a lathe, it spins metal and you cut it
    ./parcel.py a small brass telescope      # turns up at the post office
    ./inbox.py                               # read what he has sent you
    ./serve.py                               # his website on :8080
    ./searchtest.py how arches work          # check his web search works, no model call

## upgrading without killing him

the archive contains a fresh state.json and world.json, so extracting it over a
living otto wipes his life. unpack somewhere else and copy only the code:

    mkdir -p /tmp/ottonew && tar -xzf ~/Downloads/otto.tar.gz -C /tmp/ottonew
    cd ~/Downloads/otto
    cp /tmp/ottonew/otto/{engine,tools,tick,brain,physics}.py .
    cp /tmp/ottonew/otto/{selftest,story,searchtest,reset,audit}.py .
    cp /tmp/ottonew/otto/persona.md .
    chmod +x *.py
    ./selftest.py

his state, world, site, memory and library are untouched by that.

## what he costs, and the two models

He has three gears.

**Reflex.** Free. No model is called at all. Being hungry and walking to the
orchard is not a decision, so he just does it: he paths to the nearest food and
eats it, heads for the warmest room when he is perishing, and walks home to bed
when it is late and he is flagging. These still appear in the log and in the
world, marked `free`. They do not fire if you have said something to him, if
wonder is above 0.80, or if he asked to think last tick.

Then two more, because most of his moments are small and a philosophy seminar
to decide whether to have lunch is a waste of everyone's money.

**Pottering.** The cheap model, nine tools, three rounds, and a short prompt with
no knowledge list, no wishlist and no history: the time, how he feels, where he is,
what is there, and the ways out. About 2,300 tokens a round and 0.06 cents a tick.
If something in front of him deserves more, he calls think_properly() and stops;
the next tick picks it up with a clear head.

**Properly.** The good model, every tool, eight rounds, his full situation. About
5,700 tokens a round and 5 cents a tick. He gets this when any of these is true:

- wonder is 0.62 or above, meaning something has hold of him
- you have said something to him since he last woke
- it has been five ticks since the last good one

Asleep ticks cost nothing at all, because no model is called.
Everyday ticks also get five tool rounds instead of eight, which stops a dull
tick from sprawling.

- he asked for it last tick with think_properly()

Two other things keep the bill down. The conversation inside a tick is cached as
it grows, so round eight is not paying full price to resend rounds one to seven.
And his knowledge list is capped at the most recent 22 entries in the prompt;
nothing is deleted, he simply is not re-reading his whole life every quarter hour.

    where it started, every 20 min       about $190 a month
    two gears + caching, every 20 min    about  $15 a month
    two gears + caching, every 15 min    about  $20 a month
    two gears + caching, every 10 min    about  $30 a month

A `*` next to the tick number in the log means that one ran on the good model.
Set `OTTO_MODEL` to force a single model for everything.

## what he knows

the model behind him knows everything. the creature must not. so knowledge is a ledger:
memory/knows.md, where every line carries its source.

    - a folded strip holds the string ball, a flat one sags  [tried: laid both across
      the drain at lane_top, tick 23]

learn() refuses any fact without a real source. his prompt shows him the ledger and
tells him that everything not on it is guessing. guesses are encouraged, as long as he
calls them guesses and then goes and tests them.

this will not be airtight. the model's knowledge leaks, especially under pressure. but
the ledger makes leaks visible: read knows.md and if a formula appears there with
[tried: ...] against an experiment that could not have produced it, you have caught one.
tighten the persona wording when that happens.

when he predicts an outcome in test(), the world tells him plainly if he was wrong.

## catching the leak

the model behind him knows everything, and under pressure that leaks. two defences.

prevention: persona.md forbids producing facts from nowhere, and learn() refuses any
entry without a real source.

detection, which is the one you can rely on: everything he is exposed to is logged to
memory/seen.jsonl, every book chunk, search result, page and message from you. then:

    ./audit.py            words he used but never encountered
    ./audit.py --list     all of them

technical vocabulary in that list is a leak. if 'catenary' appears and he never read
it, the hedgehog did not come up with that. run it after every day. the fix is either
tightening persona.md or putting a book on the shelf that genuinely teaches the thing.

## things can break

objects have a capacity, worked out from what they are made of, what shape he gave
them and how far they span, times a hidden flaw unique to each object. test() puts a
load on and the world answers: holds, sags, creaks, bends for good, or fails. a
rolled tube carries about three times a flat strip, an arch slightly more, because
the geometry words in the object's own name and note are what the model reads.

he cannot predict outcomes and cannot undo them. a thing he spent a day on can be
destroyed in one test. that is the point.

## the library

drop books into library/ as .txt, .md, .epub or .pdf. they appear on the shelf in the
library, which is a real place he has to walk to.

he cannot swallow a book. he reads roughly 3,800 characters a sitting and keeps a
bookmark in memory/bookmarks.json, so a full-length book runs to about forty sittings,
spread over days. reading pushes wonder up hard and energy down, so a long session
costs him.

what you put on that shelf is the strongest lever you have over what he becomes. web
search gives him facts; a book gives him a voice and an argument to argue with. choose
accordingly, and mix: something technical, something with a strong opinion, something
with nothing to do with anything.

## the files

    .env              your keys. gitignored. the only place they go.
    run.sh            one wake-up, what the timer calls
    install-mac.sh    sets up the mac timer
    selftest.py       every check that needs no model. run it after any change.
    reset.py          wipe him to tick 0, optionally archiving the old life to runs/
    brain.py          the model backend. anthropic and gemini. swap freely.
    persona.md        his temperament. no topics in it, on purpose.
    state.json        needs, mood, where he is, what he owns
    world/world.json  every place and object. he edits this himself.
    memory/notes.jsonl   everything he has written down
    memory/kept.md       the few things he decided are his. this is where obsessions live.
    memory/knows.md      what he knows, each line with where it came from
    site/             his website. whatever he writes goes live.
    library/          books you put there. .text/ is the extracted cache, ignore it.
    memory/bookmarks.json  how far through each book he is
    log.jsonl         every tool call he has ever made
    thoughts.jsonl    what he was thinking between actions

## the knobs that matter

- DECAY in engine.py sets how fast he gets tired and hungry. slower decay means more
  free afternoons and more making.
- the number of recent notes in tick.py (currently 14) sets how long a passing interest
  survives before it falls off the edge.
- RULES in tick.py is the only place that tells him a quiet tick is allowed. keep it.
