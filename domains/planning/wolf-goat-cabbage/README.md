# wolf-goat-cabbage — ferry/shore tick, whatif-solved

Concluded metis-loop experiment (2026-10-09), copied from
`metis-loop/experiments/wolf-goat-cabbage/`. This experiment
introduced the settle-stage idiom ("deterministic consequences fire
before quiescence") that `bridge-torch/bridge-declarative.llp` later
extended.

## 1. What was formalized, from what

Source: the problem statement on
en.wikipedia.org/wiki/Wolf,_goat_and_cabbage_problem (fetched
2026-10-09), four sentences quoted verbatim in the `wgc.llp` header.
It was formalized from the statement alone. The session notes that a
web-search summary leaked the solution outline, so the catalog was
kept to the statement only.

`wgc.llp` (catalog `wgc`) has 2 stages, 5 rules and 2 `qui` links, and
every rule weight is 1:

- `on(item, bank)` and `farmer(bank)` are linear position tokens.
  `boat` is a resource that is consumed and then rearmed. Its shape
  alone enforces "only the farmer and a single item": `carry` moves
  the farmer plus one item, and `row` moves the farmer alone.
- One generic `eat` rule over `bwd eats(wolf,goat)`,
  `eats(goat,cabbage)` covers both hazards. It applies when the
  predator is present (`$on(X,A)`) and the farmer is on the other bank.
- The tick: `ferry` (one boat move) → `qui tide` → `shore` → `qui ebb`
  → `ferry`. "Would eat" is deterministic, so no weight was invented.
  `eat` sits in `shore`, where an enabled rule must fire before the
  stage can quiesce. `turn` rearms the boat, and `done` (consuming
  `tally`) marks the goal.

## 2. Findings that cost effort

- **Deterministic consequences come from stage structure, not
  weights.** That is the ferry/shore qui-tick. It was reused as
  board/stride/settle in bridge-declarative.
- **The wrong opener is fatal and the instruments prove it.** The
  first experiment was `step 4` (`carry[A=near,X=wolf,B=far]`) then
  `run 4`. The shore stage fired `eat[Y=cabbage,A=near,X=goat,B=far]`,
  after which `query solved @40` = **0 exact**. `why gone(cabbage)`
  names the chain: wolf carry → `tide` → `eat`, with `turn`/`ebb`
  pruned as irrelevant.
- **REPL quirk seen in `wgc-whatif-transcript.md`.** After `reset` at
  15:00:42 the state rewinds, but `log` still lists the five earlier
  wolf-first events. New events are numbered from #5 onward, so the
  whatif indices continue at #5, #9, #13 and so on.

## 3. Results against the puzzle

The puzzle's known answer is seven crossings, with the goat brought
back once. The instruments reproduce it:

- `query solved @40` = **0.003108**, exact tier, from the initial
  state. A safe crossing exists even for a uniformly random farmer.
- **Goal-record replay.** `runs/goal.jsonl` (observed `solved: 1`,
  likelihood 0.003107853…) was replayed with `explains: true`. The
  derived plan: goat over, row back, wolf over, **goat back**, cabbage
  over, row back, goat over, then `done`. Seven crossings and zero
  `eat` events. Filler moves follow `done` up to the 40-step horizon.
  `fixed: false` is expected for goal evidence.
- **Whatif repair and greedy auto-solve** (`wgc-whatif-transcript.md`).
  The first step swept `whatif 0 do(EV) query solved @40` over the four
  openers. Goat gives **0.01243**. Wolf, cabbage and row give
  **exactly 0**, so the instrument alone picks the only viable first
  move. The session then stepped the argmax at each frontier, and
  P(solved) climbed at every step:
  0.003108 → 0.01243 → 0.03101 (row back) → 0.04029 (wolf; cabbage
  ties at 0.04029, the symmetric second solution) → 0.1052 (goat back)
  → 0.2752 (cabbage) → 0.6376 (row back) → **1** (goat). `done`
  fired, and the final `state` is all three items and the farmer far,
  with `solved`.

## 4. Not solved / do not retry

- The plan's minimality is not an instrument verdict. The replay and
  greedy paths happen to be seven crossings, but neither shows that
  no shorter plan exists. A horizon sweep in the style of the bridge
  wick sweep was not run.
- Replay pads to the record's fixed `steps` (40). Expect post-`done`
  shuttling in its explanation. A shorter record horizon gives a
  cleaner plan (the same lesson as hanoi).
- `metisc --run wgc.llp` prints the seed-1 random episode, in which
  the cabbage is eaten. That is not a bug.
- This file needs no re-encoding. It is the reference for the
  "declarative" side of the doctrine.

## 5. Evidence in this directory

- `wgc.llp`: the catalog.
- `wgc-transcript.md`: `ctx`, `query solved @40`, goal record +
  `replay` (derived plan), the wolf-first negative control (`step 4`,
  `run 4`, `query` = 0, `why gone(cabbage)`). The two `help` dumps can
  be skipped.
- `wgc-whatif-transcript.md`: whatif opener sweep, `reset`, and the
  whatif-greedy auto-solve to `done`.
- `runs/goal.jsonl`: goal-evidence record.

Both transcripts start with roughly 90 lines of LLM-seat system-prompt
boilerplate.

Run, from this directory:

```sh
metis wgc.llp            # REPL; then: query solved @40
                         #   sink runs/goal.jsonl / record 0 / replay
                         #   whatif 0 do(carry[A=near,X=goat,B=far]) query solved @40
../../../../metis-lang/src/metisc --run wgc.llp
```
