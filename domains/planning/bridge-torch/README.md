# bridge-torch — bridge and torch, imperative vs declarative

Concluded metis-loop experiment (2026-10-09), copied from
`metis-loop/experiments/bridge-torch/`. Two catalogs formalize the same
statement. Read them side by side: this is the worked example behind
the metis-loop skill's Formalize rule, "declarative over imperative,
model the mechanism, not the ledger".

## 1. What was formalized, from what

Source: the problem statement on en.wikipedia.org/wiki/Bridge_and_torch_problem
(fetched 2026-10-09). It is quoted verbatim in both file headers, and
no solution was consulted. The setup: four people take 1/2/5/8 minutes
to cross, the bridge holds two, a pair walks at the slower pace, and
the torch must be carried. The question: "can they all get across the
bridge if the torch lasts only 15 minutes?" In both files that
question is `P[solved] > 0`.

- `bridge.llp` (catalog `bridge`, imperative, 1 stage, 8 rules). The
  torch is a fuse of 15 `wick` tokens. Each duration is one rule per
  cost class (`solo1/2/5/8`, `pair2/5/8`). Each rule consumes 1, 2, 5
  or 8 wick tokens, and enumerated `max2/max5/max8` pair facts say
  which pair burns at which rate.
- `bridge-declarative.llp` (catalog `bridge_decl`, 3 stages, 7 rules
  plus 3 `qui` links). Time is dynamics and pace is data. The bridge is
  a chain of minute-marks `m0..m8` (`bwd step`). The party advances one
  mark per minute and burns one wick per minute. A walker steps off at
  their own `bwd pace(person, mark)`. The torch lands only when both
  `plank` tokens are back, so "at the slower person's pace" is
  emergent. Capacity two = `#init plank 2`. The tick is
  board → stride → settle → board, which extends the wgc ferry/shore
  tick: in `settle`, enabled `alight`/`land`/`rearm` must fire before
  the stage can quiesce.

## 2. Findings that cost effort

- **The token-multiplicity encoding skews the measure.** At wick 15,
  the opening `events` in `bridge-transcript.md` show `solo1` w=15,
  `pair2`/`solo2` w=210, `pair5`/`solo5` w=360360 and `pair8`/`solo8`
  w=2.59459e+08. Each pair8 opener gets p≈0.2497. The weights are the
  falling factorial 15·14·…·(15−k+1) for consuming k wick tokens. (The
  skill sums this up as C(C,k). The numbers in the transcript are the
  ordered count, which is k! times larger.) Reachability is
  unaffected. The measure is not: "uniform rule weights" are not
  uniform over moves.
- **The imperative file was the mistake, not a language gap.** A
  first summary reported three frictions: no parametric
  multiplicities, the pair-fact blowup and the weight skew. On review
  (session 6f866783, 2026-10-09), all three traced to one authoring
  choice: `max()` and the durations had been worked out by hand when
  the file was written. The declarative redo removes all three. Its
  choice points are uniform: `advance` has w=15 for each walker
  binding (checked with `run 4` + `events`).
- **The `#init` case footgun.** `#init wick 13` from the budget sweep
  persisted in the case, so the next `reset` restored wick 13. The
  first whatif-greedy sweep (transcript 15:09:03–15:09:19) scored
  every opener P=0. It was rerun after `#init wick 15` (15:09:34).
- **Settle-stage forcing.** `alight` must not be skippable: a walker
  cannot miss their exit mark. The fix is to put it in a stage whose
  enabled rules fire before `halt`/`dawn`. `land` needs `plank * plank`,
  so the torch lands only once the last walker is off.
- **Lockstep bookkeeping.** `beat`/`moved`/`rearm` exist only to allow
  exactly one `advance` per visit to `stride`.

## 3. Results against the puzzle

The puzzle's answer for 1/2/5/8 is yes, in 15 minutes
(2+1+8+2+2). The instruments reproduce that answer, and the
14-minute check shows it is the minimum:

| quantity | bridge.llp | bridge-declarative.llp |
|---|---|---|
| `query solved`, wick 15 | 1.162e-08 (@20, exact) | 8.573e-05 (@150, exact) |
| `query solved`, wick 14 | 0 (exact) | 0 (exact) |
| `query solved`, wick 13 | 0 (exact) | not run |

- The declarative mass is about 7000× the imperative mass for the same
  feasibility question. The difference is the multiplicity skew, not
  the dynamics.
- **Whatif-greedy schedule (imperative file).** At each frontier,
  `whatif K do(EV) query solved @20` was run for every enabled event,
  and the session stepped the argmax. #0: only `pair2[a,b]` is
  positive (0.05747). #1: `solo1[a]` back (0.1108) beat `solo2[b]`
  (0.1105). #2: only `pair8[c,d]` is positive (0.3333): "the two
  slowest cross together" emerged as the only positive-mass choice.
  #3: `solo2[b]` back. #4: `pair2[a,b]` gives 1. Final `state` shows
  everyone far, with the wick fully spent.
- **Goal-record replay (declarative file).** `runs/goal-decl.jsonl`
  (observed `solved: 1`, likelihood 8.573e-05) was replayed with
  `explains: true`. The schedule it derived: A+B over (2), B back (2),
  C+D over (C alights at m5 while the torch burns on to m8 with D),
  A back (1), A+B over (2), then `done`. That is 15 minutes, the
  mirror of the greedy schedule's courier order. `fixed: false` is
  expected: this is goal evidence, not a surprise to fix.

## 4. Not solved / do not retry

- Do not go back to the cost-class, `max`-fact or `wick * wick * …`
  encoding. `bridge.llp` is kept only as the counter-example.
- Optimisation is not native. The minimum came from a manual budget
  sweep (15 > 0, 14 = 0). Greedy whatif was complete here only because
  the exact budget prunes all waste. With slack it could wander, and
  that case is untested.
- Once the fuse is out, the three-stage qui cycle spins (`go halt dawn`
  pads to the horizon). It shows in the replay tail after `done` and
  in the seed-1 `trace`/`run` episode, and it bloats traces and cones.
  This is open (it was flagged with the G6 quiescence semantics).
- Whatif-greedy was never run on the declarative file. The replay is
  its only schedule evidence.
- `depart` and `advance` bind X only to read `$aboard(X)`, so they
  produce one identical-effect instance per walker aboard. This is
  harmless at the observed choice points and was not measured further.
- The 1/2/5/10 variant (17 minutes) was not modeled.

## 5. Evidence in this directory

- `bridge.llp`: imperative catalog (wick-token durations).
- `bridge-declarative.llp`: declarative catalog (minute-mark path,
  pace data).
- `bridge-transcript.md`: imperative session. Opening `events`
  weights, the wick 15/14/13 sweep, the all-zero greedy run under the
  footgun, the greedy rerun to `done`.
- `bridge-declarative-transcript.md`: `run 40` smoke run, wick 15/14
  queries, goal record and `replay`.
- `runs/goal-decl.jsonl`: goal-evidence record for the declarative
  catalog.

Both transcripts start with roughly 90 lines of LLM-seat system-prompt
boilerplate; the REPL work follows.

Run, from this directory:

```sh
metis bridge-declarative.llp        # REPL; then: query solved @150
                                    #   #init wick 14 / reset / query ...
                                    #   sink runs/goal-decl.jsonl / record 0 / replay
metis bridge.llp                    # REPL; then: events / query solved @20
../../../../metis-lang/src/metisc --run bridge-declarative.llp
../../../../metis-lang/src/metisc --run bridge.llp
```

`metisc --run` prints the seed-1 case only. For both files that is a
failing random episode, not the solution.
