# Elevators: the first RDDL gym domain through the metis loop

> **Packaged (rddl-worlds s-242c7c3f, 2026-10-18):** `elevators_born.llp` is now the program of the package `domains/elevators/` (as `elevators.llp`, byte-equal, with a gym host). This folder is the experiment's record.

**Produced:** no catalog domain file. The experiment was never promoted.
The last accepted world is `iter2-world/` (`base.llp` = catalog
`elevators_observed`, iter1's accepted base, key `b7ad6fca…`; `pack1.llp`
= pack `elevators_riders`, key `55867e89…`). It explains **none** of the
recorded changing steps.
**Source:** rddlrepository `Elevators_MDP_ippc2011`, `domain.rddl` header
lines 1–27 verbatim. That header is the only seed, and it rides as `%`
comments at the top of `elevators_born.llp`. Episodes came from pyRDDLGym
instance 5: 2 elevators, floors f0..f3, horizon 40,
`ARRIVE-PARAM(f1) = 0.06492667`, `ARRIVE-PARAM(f2) = 0.08997825`, f0/f3
unset (domain default 0.0). The data is 5 random-agent episodes, seeds 1–5,
200 transitions in all.
**Subject:** rddl-elevators (s-f26383c1). Step 1 passed the user checkpoint
on 2026-10-09. Step 2 ran on the morning of 2026-10-09. Step 2a (notching)
and the arena step were never run. The subject was closed 2026-10-11 as
superseded by catalog-consolidation (s-8e31674d). The recipe carried on in
rddl-tier1 (`../wildfire/`, `../tamarisk/`), which is where it worked.

## What happened, in one paragraph

**Birth (step 1).** From the header alone, the contained `claude -p` seat
produced `elevators_born.llp`. It has 9 rules (arrivals as an
arrival-vs-none ⊕, move, noop, open_same, open_turn, close, board, alight),
each with a `%%` quote from the header. `revise` passed it green and metisc
was clean. This took a session-only language card (v1) and two mechanical
carry-overs. **Step 2, iter0.** The recorder replayed the 200 gym steps
against it, and every changing step was a surprise: the born world speaks
its own atoms (`at`, `heading`, `waiting`…), never the gym's
(`elevator_at_floor`…). **iter1.** The text mined from the records was
formalized with card v3 into a revised base written in the observed
vocabulary. Unprompted, the seat invented complement atoms and an action
handshake. It still explained nothing, because the records carry none of
those hidden atoms. **iter2.** The records were re-sunk with the `--steps
frame --negatives --tick-token` interface, and the interface was mined into
the text. The seat answered with a note-taking pack, which cannot repair a
base. The experiment stopped there.

## Results vs the gym

The surprise sinks below are from real episodes with exact replay. The sink
files are in `sinks/`.

| world served | readout | surprises / episode | why |
|---|---|---|---|
| born (`elevators_born.llp`) | 1 step | 25.2 (126/200) | vocabulary: no born atom is ever observed |
| iter1 (revise, LLM) | 1 step / frame / frame+neg+tick | 25.2 | its rules need hidden atoms (complements, `ready`/`pending`/`done`) that no record gives |
| iter2 (iter1 + pack, LLM) | frame+neg+tick | 25.2 | a pack of note-taking rules; it cannot repair the base |

- The 1-step and frame-only iter1 rows come from the recorder handoff
  (`.handoff/rddl-recorder-handoff.md`). Only the frame+neg+tick sink is
  kept here.
- **25.2 is the ceiling, not a curve.** The 126 records are exactly the
  126 transitions in which anything changed (`notes-iter0-patterns.txt`).
  The other 74 no-change steps pass trivially. Per episode: 27 / 28 / 26 /
  24 / 21. No world ever priced a changing step above 0.
- The acceptance criterion "surprises/episode falling across ≥3
  iterations" was **not met**.

**Notch target (step 2a, never run).** For whoever retries: the
maximum-likelihood counts below were computed for this README from
`transitions/i5-random-ep1-5.jsonl`. They are not a metis notch.
- An opportunity is a step in which the gym's cpf draws
  `Bernoulli(ARRIVE-PARAM(f))`. That is every (floor, direction) except
  "already waiting and not picked up this step". Up and down share the
  floor's parameter.
- A fire is waiting being true in the next state.

| floor | ARRIVE-PARAM | fires / opportunities | ML rate | 95% Wilson CI |
|---|---|---|---|---|
| f0 | 0 (default) | 0 / 400 | 0 | — |
| f1 | 0.06492667 | 18 / 289 | 0.062 | 0.040–0.096 |
| f2 | 0.08997825 | 15 / 231 | 0.065 | 0.040–0.104 |
| f3 | 0 (default) | 0 / 400 | 0 | — |

Both nonzero parameters fall inside their intervals. 200 steps cannot
separate f1 from f2: their intervals overlap almost entirely. A real notch
needs the 2400-transition scale that wildfire and tamarisk used.

## Findings that cost effort

1. **Cold start, three cards.**
   - **v1** (`step1-language-card.txt`): on a blank world the formalize
     prompt is two lines, and the only syntax reference is the empty base.
     Without a card the model invented a language: dotted names, `const`,
     a `rule` keyword, `extends scratch 1.`. Four rounds stuck on parse
     errors. v1 is the generic grammar plus a toy bakery, with no domain
     content.
   - **v2** (`step2-language-card-v2.txt`): once a base exists the seat had
     no *pack* syntax either (`type elevator.`, no `extends`), and it was
     stuck for 4 rounds. v2 adds a generic pack section and a toy pack;
     after that, 1 round.
   - **v3** (`step2-language-card-v3.txt`): adds one method line: observed
     atoms that are not the base's vocabulary call for a revised
     standalone base. Only then did iter1 come back base-shaped, after 2
     rounds, gated as revise.
   - v3 plus one doctrine paragraph became the tier-1 card. With it,
     wildfire was green in 1 round.
2. **Gate-green ≠ explains.** The v2 pack gated green with no findings. It
   mapped the observed actions onto base atoms that a pack may not produce,
   so it explained nothing; it was not accepted. iter2's pack was accepted
   and explains 0 records. The post-accept replay catches this only after
   the world has changed. A shadow replay before accept (merge the
   candidate, re-score the records) is the missing check; it was filed but
   is not built here.
3. **A born catalog never speaks the observed vocabulary.** Prose names no
   fluents, so step 2's first iteration is necessarily a base rewrite, and
   packs cannot do it. Expect it, and seed the observed vocabulary (and
   the interface, finding 4) into the first mined text.
4. **The observation interface: settle readout + negatives + tick.**
   - This came out of iter1, and wildfire calls it "the elevators-converged
     interface". Linear logic cannot test absence, so a false fluent is
     observed as `not_<atom>`. One gym step is several metis events, so the
     next state is read when the catalog settles (`--steps frame`, capped
     at 64 here). One `tick` atom per transition lets a catalog structure
     the step.
   - iter1 discovered both problems unprompted, but in its *own* names
     (`elevator_open`, `elevator_dir_down`, `slot_up/down`, plus a
     `ready → action*pending → done` handshake). The recorder gives
     `not_elevator_closed(e0)`, `tick`, and nothing else. Under the new
     interface the served iter1+pack world is **quiescent at reset**: no
     event is enabled (end of `step2-exploratory.md`).
   - Lesson: the catalog must be written *in the recorder's interface*.
     Mine the interface first, as `step2-iter2-mined-text.txt` does. iter2
     did that only after iter1's base was accepted, so the seat could only
     add a pack.
5. **Synchrony gap: pre-registered, observed, never formalized.**
   - In the born world each Bernoulli draw is an ordinary event that
     competes with moves. At the initial state, 16 of 24 enabled events are
     arrival draws, carrying about 0.49 of the choice mass (`events` in
     `step2-exploratory.md`). In the architect's `run 15`, 11 of 15 events
     were arrivals and `move` never fired (`metis-transcript-20261009-110529.md`).
   - The gym data shows many changes per step. Record 58: move and door-open
     on e1 in one step. Record 3: close + open_up ends closed. Record 25: a
     boarding and a new arrival at the same floor. Records 1 and 37: three
     changes each. 17 of 200 steps change ≥3 atoms.
   - The design note that fits all five: a phase-staged tick (board →
     arrive → move → doors → shut, with quiescence links) and one paired
     arrival site per floor×direction per tick, `@w arrive(F) | @w
     ~arrive(F)`. That pair is exactly the notchable shape. It was never
     written into a catalog. Wildfire's seat later produced a lockstep
     cycle unprompted.
6. **The seat fabricates numbers and instances.** The born catalog asserts
   5 floors (the gym instance has 4), "busy"/"quiet" floors, arrival
   weights 0.4/0.1, `move @w 2`, `board/alight @w 3` and `noop @w 0.2`.
   None of these is in the header. This is the origin of the
   "no invented rates" doctrine and of weight ports.
7. **Seat hang, root-caused.** `claude -p` hangs to the 600 s backend
   timeout when it has a controlling tty *and* runs from the experiment's
   git checkout; `setsid` does not help. The fix is `seat-claude.sh` (cd to
   a neutral dir, then exec the contained `claude -p`). With it a call
   takes 20–28 s.
8. **REPL footguns hit here.**
   - `record N` sets the scene, but not the session state: run `reset`
     before using the instruments.
   - `save` writes the case's current state as `#init`. The
     saved `elevators_iter1.llp` (dropped in the consolidation; same body
     as `iter2-world/base.llp`) carried record 4's scene with `#steps 1`,
     not the candidate's directives. Use `export`.
   - Loop fixes F3, F5, F6, F7 and F1b landed on 2026-10-09 (they appear
     in `RESULTS-step1.md` as findings 3, 5–7 and 2). Wildfire reports they
     held.
   - Filed from the architect session and not verified here: `necessity`
     refuses inside a `fork`; the `log` likelihood footer does not name
     active masks; a zero-event cone prints a bare `P = 0`.

## Not solved / do not retry

- **Nothing explains a changing gym step.** Notching against ARRIVE-PARAM
  (2a) and the arena comparison against NoOp/Random were never run.
- **Do not retry:**
  - iterating with packs on top of a prose-born or self-named base;
  - the 1-step readout;
  - letting the seat name its own complements;
  - mining counts into the text. The iter2 text quotes 8/8/5/9 arrival
    counts, and wildfire showed that counts get unrolled into literal
    weights.
- **Retry path.** Re-birth with the tier-1 card (v3 + doctrine + weight
  ports):
  - the observed vocabulary and the frame/negatives/tick interface go in
    the first mined text;
  - a lockstep tick with one paired arrival port per floor, priced by a
    prior-flat plugin;
  - notch against the table above, at ≥2400 transitions;
  - `--tier auto|sampled` if the lockstep world blows the exact filter's
    budget (a wildfire finding);
  - score against the gym's own generator as the floor (wildfire finding
    2). No floor was computed here.
- **Never observed in 200 random steps:** a passenger leaving an elevator.
  Delivery and alighting need a non-random agent or longer episodes.
- **Not reached here,** because no world priced a step: token-multiplicity
  weight skew, the `#init`-persists-on-reset footgun, and exact-filter
  blowups (see `../../bridge/` and `../wildfire/`).

## Evidence in this directory

| file | shows |
|---|---|
| `RESULTS-step1.md` | the step-1 report: the session step by step, findings 1–8 |
| `step1-transcript.txt` | the step-1 terminal session, verbatim (pty-driven `metis`) |
| `step1-language-card.txt`, `step2-language-card-v2.txt`, `step2-language-card-v3.txt` | cards v1 / v2 (+ pack section) / v3 (+ revise-the-base line) |
| `seat-claude.sh` | the contained formalize seat (neutral cwd; needs `/tmp/claude-1000/metis-seat`) |
| `elevators_born.llp`, `step1-candidate-from-formalize.llp` | the born catalog (header verbatim) and the raw candidate (`#init` atoms with spaces, finding 6) |
| `transitions/i5-random-ep1-5.jsonl` | the 200 raw gym transitions (also the notch dataset) |
| `notes-iter0-patterns.txt` | 126 changing steps, the 61 (lost → gained) signatures |
| `sinks/iter0-born.jsonl`, `sinks/iter1-frame-neg-tick.jsonl` | the surprise sinks behind the results table |
| `step2-exploratory.md` | the step-2 lab notebook: sink, replays, the three cards in use, iter1/iter2 formalize + accept, quiescence under the new interface |
| `step2-iter1-mined-text.txt`, `step2-iter2-mined-text.txt` | the approved texts: observed vocabulary; + the interface and the synchrony evidence |
| `iter2-world/` | the last accepted world (`base.llp` = iter1, `pack1.llp`, `text.md`) |
| `metis-transcript-20261009-110529.md` | architect hands-on on the born world: arrivals hog the event clock; fork + mask + `query` |

Reproduce, from this directory with a metispy env that has the `sysadmin`
extra (pyRDDLGym + rddlrepository). The recorder refuses to overwrite an
existing output, so write to a new path:

```
python -m metis.domains.rddl_recorder record --problem Elevators_MDP_ippc2011 --instance 5 --episodes 5 --seed 1 --agent random --out /tmp/i5.jsonl
python -m metis.domains.rddl_recorder sink --catalog elevators_born.llp --transitions transitions/i5-random-ep1-5.jsonl --out /tmp/iter0.jsonl
python -m metis.domains.rddl_recorder sink --catalog iter2-world/base.llp --transitions transitions/i5-random-ep1-5.jsonl --out /tmp/iter1.jsonl --steps frame --negatives --tick-token
metis elevators_born.llp      # then: sink sinks/iter0-born.jsonl / record 4 / reset / replay
```

No elevators catalog declares a weight port, so `metis --plugin` does not
apply. `iter2-world/pack1.llp` extends `elevators_observed` and does not
compile standalone (`extends-no-base`).
