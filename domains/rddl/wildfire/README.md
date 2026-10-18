# Wildfire: an RDDL gym domain through the metis loop

> **Moved (rddl-worlds s-242c7c3f, 2026-10-18):** the program, its notch and the manifest are now the package `domains/wildfire/` (`wildfire.llp`, `wildfire.notch.json`, `domain.yaml`, a gym host `wildfire_host.py`). This folder is the experiment's record; its `../wildfire.llp` paths below are as they were.

**Produced:** `../wildfire.llp` (catalog 5), served with
`wildfire_plugin.py` plus the fitted table `../wildfire.notch.json`.
**Source:** rddlrepository `Wildfire_MDP_ippc2014` (IPPC2014), with its
header as the only seed; pyRDDLGym instance 1 (3×3 grid, random agent)
for episodes. **Subject:** rddl-tier1 (s-8f820524), steps 1–2, closed
2026-10-11. This was the first domain of the RDDL shelf
(`../EXPERIMENT-RDDL.md`), rerunning the elevators recipe
(`../elevators/`).

Wildfire is a synthetic benchmark. The point was not gym fidelity but
**the LL/runtime split**:
- the step's timeline and counting live in LL (lockstep stages, the
  neighbor count walked as a `bwd` chain);
- the numbers live at runtime (one weight port, fitted from episodes).

## What happened, in one paragraph

**Birth (step 1).** From the header alone, the formalize seat (contained
`claude -p`, `seat-claude.sh`, card `step1-language-card.txt`) went green
in 1 round. It invented its own lockstep stages and walked k as a tally
path. It declined to fake the logistic, leaving ignition flat
"to be attached as data".

**iter1.** The loop mined 400 recorded steps. The mined text quoted
per-k counts, and the seat **unrolled ignition per k with the counts as
literal weights**, turning a "1 of 1" into certainty.

**iter2.** The text was re-mined as "rate = data, one law", with a
weight-ports section in the card (`step2-language-card-v2.txt`). That
produced ONE rule, `catch … @w pign(K) | @w ~pign(K)`, in 1 round.

**Notch.** Fitting pign from 2400 transitions recovered the header's
logistic within its 95% CI at every observed k.

## Results vs the gym

| world served | held-out surprises / episode |
|---|---|
| born | 11.5 |
| iter1 (per-k literals) | 1.3 |
| iter2, port prior-flat 0.5 | 12.3 |
| **iter2, port notched** | **1.3** |
| the gym's own cpfs (the floor) | 1.4 |

| k | gym 1/(1+e^(4.5−k)) | notched pign(k) | 95% CI | n |
|---|---|---|---|---|
| 0 | 0.0110 | 0.0094 | [0.007, 0.013] | 3194 |
| 1 | 0.0293 | 0.0258 | [0.021, 0.032] | 3366 |
| 2 | 0.0759 | 0.0837 | [0.068, 0.102] | 1040 |
| 3 | 0.1824 | 0.1464 | [0.110, 0.193] | 280 |
| 4 | 0.3775 | 0.4000 | [0.234, 0.593] | 25 |
| 5 | 0.6225 | 0.6000 | [0.231, 0.882] | 5 |

k ≥ 6 never occurs in instance 1 under random play.

## Intelligence: what cost effort

1. **Counts in the mined text get unrolled.** Numbers in the approved
   text became per-value rules plus literal weights, even though the
   card's doctrine paragraph forbade it, and no gate measures it. Keep
   counts out of the text; they are evidence for the notch. With "rate
   = data, one law" plus port syntax in the card, the seat wrote the
   port in 1 round. (Suggested and not built: a gate warning for ≥3
   rules differing only in one ground constant.)
2. **The surprise metric needs a floor.** A joint likelihood < 0.05
   flags the TRUE generator 1.4–2.1 times per episode on 9 cells.
   `true_likelihood.py` evaluates the cpfs directly. Report against it,
   never raw counts.
3. **The exact filter cannot price grid-lockstep catalogs.** Per-cell
   scans interleave within a stage (more than 2M intermediate states at
   step 26). `replay`, gate scenarios and the revise diff all hit it.
   The recorder's sampled tier (`--tier sampled`, Wilson CI) carried
   every number here. The catalog scene's revise still warns (500k
   states).
4. **Kernel defect, not patched:** the factored tier returns likelihood
   0 for a reachable observation. Repro: `iter1-world/base.llp`,
   transition 0 of `transitions/iter0-i1-random-s1-n10.jsonl`
   (negatives + tick). Every reference run reaches it. It is filed on
   the exact-instruments backlog.
5. **Policy index spaces** (fixed in metispy). `run_trace` indexes
   policies by `canonical_events`, the filter by `program.events()`.
   `PortPricer.policy(prog, canonical=True)` exists for traces.
6. **Notch targets: dynamics, not reward.** The shelf listed Wildfire's
   "4 real" non-fluents as targets, but they are reward costs. The
   dynamics ground truth is the header's logistic per k. Audit this
   per domain.
7. **The recorder maps state fluents and actions, not non-fluents.**
   NEIGHBOR/TARGET entered as observed instance data in the mined text
   (`nonfluents-i1.json`).
8. **A `%%` before a `weight` declaration attaches to the next rule**
   (docs belong to rules). So the header's logistic rides as the `%%`
   doc on `catch`, the rule pign prices.
9. **The interface that works** is the elevators-converged one:
   - every observed fluent as `atom` or `not_atom` (negatives);
   - the action atoms;
   - one `tick`;
   - the next state read at the settle (frame) readout.

## Not solved / do not retry

- Do not mine counts into text (finding 1). Do not trust a surprise
  count without its floor (finding 2). Do not wait for the exact tier
  on lockstep grids (finding 3); use `--tier sampled`.
- Not run: instances 2–10 (4×4, 5×5 grids). They would test
  topology-as-data and the sampled tier's cost.
- The factored-tier zero (finding 4) is open in the kernel.

## Evidence in this directory

| file | shows |
|---|---|
| `header.txt` | the seed (header verbatim, 1559 chars) |
| `step1-language-card.txt`, `step2-language-card-v2.txt` | the cards: v3-elevators + doctrine; + WEIGHT PORTS |
| `seat-claude.sh` | the contained formalize seat |
| `step1-transcript.md`, `step2-iter1-transcript.md`, `step2-iter2-transcript.md` | the REPL lab notebooks (instruments quoted) |
| `step2-iter1-mined-text.txt`, `step2-iter2-mined-text.txt` | the approved texts: counted (unrolled) vs "rate = data" (port) |
| `wildfire_born.llp`, `step1-candidate-from-formalize.llp` | the born catalog |
| `iter1-world/`, `iter2-world/` | the accepted worlds (iter1 = the unrolled counterexample) |
| `wildfire_plugin.py` | prior-flat base binding of pign |
| `notch_episodes.py`, `notch_table.py`, `notch/pign-overlay.json` | the episode notch, the acceptance table, the fitted overlay |
| `true_likelihood.py`, `nonfluents-i1.json` | the floor, the instance topology |
| `transitions/` | iter0 (seed 1), held-out (seed 101), training (seed 1001) episodes |
| `sinks/` | the surprise sinks behind the tables (+ `.summary.json`) |
| `RESULTS-step1.md`, `RESULTS-step2.md` | the full step reports (gaps vs cpfs, the loop iteration by iteration) |

Reproduce, from this directory with the metispy venv:

```
python -m metis.domains.rddl_recorder record --problem Wildfire_MDP_ippc2014 --instance 1 --episodes 10 --seed 101 --agent random --out transitions/heldout-i1-random-s101-n10.jsonl
python -m metis.domains.rddl_recorder sink --catalog iter2-world/base.llp --transitions transitions/heldout-i1-random-s101-n10.jsonl --out /tmp/h.jsonl --steps frame --negatives --tick-token --tier sampled --samples 2000 --frame-cap 256 --plugin wildfire_plugin:make --overlay notch/pign-overlay.json
python true_likelihood.py nonfluents-i1.json transitions/heldout-i1-random-s101-n10.jsonl
metis --plugin wildfire_plugin:make ../wildfire.llp
```
