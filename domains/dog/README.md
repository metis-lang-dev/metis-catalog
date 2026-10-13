# dog — the quadruped robot dog as a metis domain

**What:** `dog.llp` formalizes what the executive's dog (metis-agent `go/`)
already does: the eleven intents of `go/grammar/dog-corpus.tsv` and the
outcomes of the E10 corpus (done · refused with a reason · expired ·
progress). `dog_host.py` is its host, a PortPlugin with no weight ports: the
TIME face carries the person's commands (as the domain agent would type them)
and the world's answers; the OUTPUT face actuates and schedules what the world
says back. `dog-transcript.md` is one hosted day.

**Why it exists:** metis-agent DESIGN.md "The direction of the intent schema"
(2026-10-13). The dog was the example everyone imprinted on, and it was the one
domain with no catalog: its intent went from the model to a dispatcher and out
to the robot, with no runtime between. With a catalog the chain is the designed
one: words → the domain agent's typed intent → one command token asserted by
the host → a rule that fires only when the body's state allows → the outcome
token the narrator reads → the port that actuates.

## The shape

| the executive's intent | the command token | accepted by | refused by (the reason is the rule's `%%` line) |
|---|---|---|---|
| LOCAL_ACTION stand/sit/lie | `cmd_stand`, `cmd_sit`, `cmd_lie` | `stand`, `sit`, `lie` (the posture changes) | `*_already`; `stand_low` (battery), `sit_wet` (floor) |
| LOCAL_ACTION turn/move | `cmd_turn(side)`, `cmd_move(way)` | `turn`, `move` | `turn_obstacle`, `move_wall`; `*_must_stand` (has to stand first) |
| LOCAL_ACTION shake | `cmd_paw` | `paw` | `paw_hot` |
| NAVIGATE | `cmd_go(place)` | `go` → `moving(P)` + `progress(go)`; ends by `arrive` / `go_blocked` / `go_expire` | `go_unmapped`, `go_closed`, `go_must_stand`, `go_busy*` |
| FIND | `cmd_find(thing)` | `find` → `searching(T)`; ends by `found` / `find_locked` / `find_expire` | `find_low`, `find_busy*` |
| FOLLOW | `cmd_follow` | `follow` → `following`; ends by `follow_lost` | `follow_nobody`, `follow_must_stand`, `follow_busy*`, `follow_already` |
| STOP, CANCEL | `cmd_stop`, `cmd_cancel` | `stop_*`, `cancel_*` (the task token goes, `cancelled(ACT)`) | `stop_still` ("I am already stopped"); cancel with nothing to drop is `done` |
| QUERY about a thing | `cmd_query(thing)` | `query_seen` | `query_unseen` |
| QUERY about a place ("what do you see near the window") | `cmd_look(place)` | `look` | `look_unmapped` |
| TIME, DATE, CHITCHAT | `cmd_time`, `cmd_date`, `cmd_chat` | `time`, `date`, `chat` | — |
| UNKNOWN | `cmd_unknown` | — | `unknown` |

- **The body's facts are complementary pairs the host keeps current**
  (`battery_ok | battery_low`, `clear(W) | wall(W)`, `mapped(P) | unmapped(P)`,
  `open(P) | closed(P)`, `seen(T) | unseen(T)`, …): LL has no negation, so the
  accept rule reads one side with `$` and each refusal reads the other. Exactly
  one of a pair holds, so one rule is enabled per command: the run's likelihood
  is 1, the dog's choices are the state's, never the sampler's.
- **One task at a time:** `idle` is the slot; `moving`, `searching`,
  `following` hold it; a second long command is refused as busy.
- **Outcomes are tokens** (`done(ACT)`, `refused(ACT)`, `progress(ACT)`,
  `expired(ACT)`, `cancelled(ACT)`); the host narrates them at its next tick
  and retracts them. `why refused(go)` names the rule and the blocker it rested
  on; the event's bindings (`arrive[P=tag3,Q=door]`) carry the command's
  identity that E10 read 4 found missing from the executive's outcome cue.
- **Commands are exogenous input** (`[env]` rows): excluded from the
  likelihood, first-class in `why`, `graph`, `fork`. Asserting them by hand
  (`+ cmd_sit`) works for a quick look but rebases the causal graph at every
  assert; the host plugin is the faithful driver.

## Run

```
cd domains/dog
metis dog.llp                              # hand-driven: + cmd_sit · events · step · why refused(go)
metis --plugin dog_host:make dog.llp       # the scripted day: run 60 · log · why done(go)
```
(`metis` is metispy's REPL; on taycann it is in metis-agent `py/.venv/bin`.)

## Found while formalizing

1. A constant on the right of `<>` (`P<>standing`) is not supported by the
   toolchain (`cannot serve: 'standing'`); spec §2 allows `VARIDENT "<>" ident`.
   Written with a `bwd other(posture, posture)` guard instead. Filed as a
   question to the metis line: spec wording or implementation.
2. `on_event` receives the canonical name with bindings (`go[P=tag3]`) and the
   ground args as a tuple; a host keys on `name.split("[")[0]`.
3. Open vocabulary ("the red chair near the window") does not enter the
   catalog: `place` and `thing` are handles the host's table resolves. The
   places and things here are the E10 corpus's plus two standing handles,
   `tag_near` (the nearest tag, "go to the tag") and `elsewhere` (a place the
   host cannot resolve, so every "not on my map" refusal has an atom); a real
   host maps perception targets to handles at the intent → atom step.
4. Quantities (`angle_deg`, `distance_m`, `duration`) never enter the catalog
   either: they ride with the command in the host's queue, keyed by the
   command's id, and the port actuates with them (domain-agent step 1).

## Not yet

- Progress notes ("halfway there") are the host's words; a `progress(ACT)`
  token says only that the task is running.
- `expired` fires on a host `timeout` token; the 90 s / 30 s windows of the
  wire are the host's clock, not the catalog's.
- The executive still dispatches the dog intent directly (go/internal/wire);
  putting this catalog between the intent and the robot is the "move under the
  line" of DESIGN.md, a later subject.
