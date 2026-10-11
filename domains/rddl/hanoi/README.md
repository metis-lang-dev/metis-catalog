# hanoi — Tower of Hanoi born from the RDDL header (Tier-2 investigation)

Concluded metis-loop experiment (2026-10-09), copied from
`metis-loop/experiments/hanoi/`. Unlike the Tier-1 gym domains in
`../README.md`, this domain has no stochastics, no ports and no notch
table. It was a hands-on test of one question: is the arcade/enum
RDDL class metis material?

## 1. What was formalized, from what

Source: the header comment of rddlrepository
`arcade/TowerOfHanoi/domain.rddl` (author Mike Gimelfarb), quoted
verbatim in the `hanoi.llp` header. That header is the only RDDL text
kept here. The domain body is in the installed rddlrepository
(`TowerOfHanoi_arcade`).

`hanoi.llp` (catalog `hanoi`) has 1 stage and 2 rules: 3 disks
(d1 < d2 < d3), 3 rods, and the goal rod r3. The doctrine applied:
the RDDL's int fluents (`disk-order`, `disk-count`) are its own ledger,
synchronous-DBN bookkeeping for "on top" and "stack position". The
mechanism is relational:

- `on(spot, spot)`: a disk rests on a surface (a bigger disk or a rod
  base). `clear(spot)`: the surface is uncovered. Both are linear
  resources.
- `mv : $clear(D) * on(D,P) * clear(E) * fits(D,E) -o on(D,E) * clear(P)`
  is the whole dynamics. "Only one disk at a time" means one rule
  firing per move. "Only on a greater disk" is the 12 `bwd fits` data
  facts.
- `done : tally * $on(d1,d2) * $on(d2,d3) * $on(d3,r3) -o solved`.

## 2. Findings that cost effort

- **Metis types do not overlap.** The first draft had both
  `type disk {d1 d2 d3}` and `type spot {d1 d2 d3 r1 r2 r3}`. The REPL
  refused to load it with `line 49: mv: var D typed both spot and disk`
  (session 6f866783, 2026-10-09). The fix was a single supertype `spot`
  plus a `bwd` role relation (`fits`). That is the idiom.
- **The ints dissolved.** Neither `disk-order` nor `disk-count`
  survives in any form: no walked count path was needed, only
  clear/covered resources.
- **Replay pads to the record horizon.** The goal record uses
  `steps 25`. The replayed explanation opens with 8 filler moves
  (d1 shuttling r2↔d2) and ends with 9 more after `done`.

## 3. Results against the puzzle

The known optimum for 3 disks is 2³−1 = 7 moves.

- `query solved @25` = **0.03501**, exact tier.
- **Goal-record replay.** `runs/goal.jsonl` (observed `solved: 1`,
  likelihood 0.035014…) was replayed with `explains: true`. Between
  the filler, the core is exactly the optimal 7 moves: d1→r3, d2→r2,
  d1→d2, d3→r3, d1→r1, d2→d3, d1→d2, then `done`. `fixed: false` is
  expected for goal evidence.

The investigation's verdict (session notes, not artifacts in this
directory): the arcade/enum class is metis material. Eight
(hole-as-token), Sokoban (tokens + adjacency) and PushYourLuck (a
20-face type with a ⊕ notch target) were analysed on paper only. The
genuine limits are real-valued state fluents and heavy cpf arithmetic.

## 4. How this differs from `../../planning/tower_of_hanoi.llp`

That file is an older hand port (2026-10-03) of the Ceptre example
`interactive-lp/examples/tower_of_hanoi.cep`. The two files are a
born-vs-ported pair:

| | `rddl/hanoi/hanoi.llp` (this) | `planning/tower_of_hanoi.llp` |
|---|---|---|
| source | RDDL header prose, formalized blind | Ceptre program, ported rule for rule |
| provenance | `text` | `hand "port:…tower_of_hanoi.cep"` |
| surfaces | one type `spot` = disks ∪ rods | `ring`, `post`, and constructor places `top_r*`/`bottom_p*` via `topof`/`bottomof` graphs |
| size order | 12 enumerated `fits` facts | `succ` + Horn closure `smaller` |
| move | one `mv` rule, single step | arm two-phase: `pickup`, `putdown_on_ring`, `putdown_on_post` (3 rules, `arm_free`/`arm_holding`) |
| goal | `done` rule → `solved`, target r3 | none; `#query on(r3,bottom_p3)`, `#query on(r1,top_r2)` |
| case | `#steps 25`, layer `dyn` | `#steps 14 #seeds 3 #interactive do`, layer `story` |

Neither file replaces the other. The Ceptre port pins the original's
semantics. This file shows what the declarative doctrine produces
from prose alone. Whether the Ceptre port reaches its goal in 7
pick/put pairs was not verified here.

## 5. Not solved / do not retry

- No horizon sweep: a replay at the shortest sufficient `steps`
  (e.g. 7 moves + `done`) should give a clean plan but was not run.
  Optimality comes from reading the replay core, not from a query =
  0 proof at a shorter horizon.
- Only 3 disks were tried. No whatif, necessity or `why` was run.
- Nothing here needs notching: there are no stochastic rules.

## 6. Evidence in this directory

- `hanoi.llp`: the catalog (RDDL header verbatim in its comments).
- `hanoi-transcript.md`: `query solved @25`, `sink`/`record 0`, and
  `replay` with the full explanation sequence. It starts with roughly
  90 lines of LLM-seat system-prompt boilerplate.
- `runs/goal.jsonl`: goal-evidence record.

Run, from this directory:

```sh
metis hanoi.llp          # REPL; then: query solved @25
                         #   sink runs/goal.jsonl / record 0 / replay
../../../../metis-lang/src/metisc --run hanoi.llp
```

`metisc --run` prints the seed-1 random episode. The tower is not
rebuilt in it.
