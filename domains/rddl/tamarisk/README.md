# Tamarisk: an RDDL gym domain through the metis loop

> **Moved (rddl-worlds s-242c7c3f, 2026-10-18):** the program, its notch and the manifest are now the package `domains/tamarisk/` (`tamarisk.llp`, `tamarisk.notch.json`, `domain.yaml`, a gym host `tamarisk_host.py`). This folder is the experiment's record; its `../tamarisk.llp` paths below are as they were.

**Produced:** `../tamarisk.llp` (catalog 2), served with
`tamarisk_plugin.py` plus the fitted table `../tamarisk.notch.json`.
**Source:** rddlrepository `Tamarisk_MDP_ippc2014` (IPPC2014, the RL
Competition 2014 invasive-species domain), with its header as the only
seed. The header is **latin-1**: byte 0x96 becomes U+0096. Episodes come
from pyRDDLGym instance 1 (4 reaches × 2 slots, random agent, horizon
40). **Subject:** rddl-tier1 (s-8f820524), steps 3–4, closed 2026-10-11.

As with Wildfire, the test was **the LL/runtime split**: structure and
timeline in LL, rates at runtime. It was also a 17-non-fluent notch
stress test.

## What happened

**Birth.** From the header alone, card v2 (`step1-language-card.txt` =
Wildfire's v2) put the rates in **weight ports at birth** (`pdown(R)`,
`pup(R)`, `pcompete(R)`), the first born catalog to do so. Green in 1
formalize round. Fidelity gaps vs the cpfs were recorded, not fixed:
- interventions modelled as spontaneous events;
- no deaths and no exogenous production;
- the wrong competition shape;
- reward modelled as state.

**Loop, one iteration.** The born vocabulary explained nothing: 289 of
400 steps were unmodeled. Mined text: the interface, the instance as
data, five qualitative laws, and **no counts**. The laws were read off
an iter0 contingency table that stayed out of the text. formalize went
green in 1 round. The world:
- lockstep `snap → rouse → act → fate → write`;
- a start-of-step snapshot, so nothing seeds within its own step;
- 11 global one-law ports;
- tamarisk arrival as a **walked noisy-or**: a scan over source
  positions, each live source its own draw.

**Notch.** The per-slot episode notch ran over 2400 transitions with
stochastic EM, 8 rounds (`notch_slots.py`).

## Results vs the gym

Held-out (10 episodes, seed 101) per-step log-loss over the 16 observed
fluents:

| world | log-loss/step | excess over floor |
|---|---|---|
| born | 10.874 | 8.226 |
| iter1, ports prior-flat 0.5 | 6.395 | 3.747 |
| **iter1, ports notched** | **2.717** | **0.069** |
| the gym's cpfs (floor) | 2.648 | 0 |

| port | gym non-fluent | gym | notched | 95% CI | n |
|---|---|---|---|---|---|
| perad | ERADICATION-RATE | 0.9 | 0.894 | [0.867, 0.916] | 614 |
| prest | RESTORATION-RATE | 0.9 | 0.918 | [0.869, 0.950] | 183 |
| pdown | DOWNSTREAM-SPREAD-RATE | 0.6 | 0.602 | [0.572, 0.631] | 1068 |
| psib | (same, within a reach) | 0.6 | 0.576 | [0.531, 0.620] | 465 |
| pup | UPSTREAM-SPREAD-RATE | 0.15 | 0.098 | [0.080, 0.119] | 889 |
| ptdie | DEATH-RATE-TAMARISK | 0.05 | 0.046 | [0.042, 0.050] | 10148 |
| pndie | DEATH-RATE-NATIVE | 0.05 | 0.049 | [0.044, 0.056] | 4955 |
| ptborn | EXOGENOUS-PROD-RATE-TAMARISK | 0.1 | 0.134 | [0.122, 0.148] | 2662 |
| pnborn | EXOGENOUS-PROD-RATE-NATIVE | 0.1 | 0.094 | [0.084, 0.106] | 2669 |
| ptcomp | COMPETITION-WIN-RATE-TAMARISK | 0.8 | 0.787 | [0.738, 0.829] | 305 |
| pncomp | COMPETITION-WIN-RATE-NATIVE | 0.2 | 0.200 | [0.159, 0.248] | 305 |

8 of 11 contain the gym value. Per-reach structure check (`--split R`):
2 of 36 rows fall outside the global value's CI, about chance.

## Intelligence: what cost effort

1. **Wide observations break the surprise count.** At 16 independent
   fluents per step, the gym's OWN joint likelihood is ~1e-3..1e-5. The
   0.05 "rare" threshold flags the true generator 15–18 times per
   episode, and a sampled joint below 1/samples reads 0. Score
   per-fluent log-loss against an exact floor instead
   (`score_episodes.py`, `true_likelihood.py`).
2. **Whole-step rejection notching does not scale.** Wildfire's
   `notch_episodes.py` waits for a run matching the entire step, which
   is hopeless at 1e-4. **The per-unit factorisation** in
   `notch_slots.py`: condition on each slot's own atoms and attribute
   only events whose first binding is that slot (`rule-k[S=slot,…]`).
   This is an exact posterior sample when units are conditionally
   independent given the start state, as here. It is worth lifting into
   metispy's notch with a declared unit variable.
3. **Single-sample stochastic EM is slow on shared credit.** When an
   empty slot gains tamarisk with several live sources, the observation
   does not say which draw seeded it.
   - Round 0, priced at 0.5, gave ptborn 0.31; after 8 rounds it was
     0.134 and still falling.
   - pup moved away from the truth.
   - The 7 rates the observation pins down converged by round 1.
   - Use several imputed samples per transition, or an exact per-slot
     E-step, before calling such a rate fitted.
4. **The domain's eradication guard is dead code.** `~(forall_{?s2}
   [SLOT-AT-REACH(?s2,?r) ^ tamarisk-at(?s2)])` quantifies over every
   slot of the instance, so eradication is never blocked. The episodes
   agree: on a full reach it cleared 64 of 78 slots. A floor written
   from the comment instead of the code is wrong.
5. **The cpfs comment and code disagree on within-reach spread.** The
   comment says UPSTREAM, the code uses DOWNSTREAM. The mined text gave
   within-reach its own port (psib), and the notch found it ≈ pdown: a
   structure discovered, not told.
6. **Loop defects found here, fixed in metispy with tests:**
   - `accept` was not atomic on unbound ports (it now re-serves first
     and refuses cleanly);
   - `load` stored `pretty()`, losing the `%` header and directives and
     expanding ⊕ (it now keeps the candidate verbatim:
     `step1b-export-after-load-LOSSY.llp` is the evidence).
   Open: `formalize` gates prior-only while `revise` is strict about
   unbound ports.
7. **Heredoc paste hangs the terminal REPL.** readline vs
   `sys.stdin.readline`: a whole paste lands in readline's buffer.
   Workaround: send `text <<EOF`, then the body, then `EOF` separately.
   Not fixed.
8. **Run batch jobs at ≤4 workers under `nice`.** The machine is shared.

## Not solved / do not retry

- pup/ptborn are not separated (finding 3). More single-sample EM rounds
  are the slow path; change the E-step instead.
- Do not judge this domain by surprises per episode (finding 1).
- Instances 2–10 were not run.

## Evidence in this directory

| file | shows |
|---|---|
| `header.txt` | the seed (latin-1, 1884 chars) |
| `step1-language-card.txt`, `seat-claude.sh` | card v2, the contained seat |
| `step1-transcript.md`, `step1b-accept-transcript.md` | the birth session; the accept that refused, then passed |
| `tamarisk_born.llp`, `step1-candidate-from-formalize.llp` | the born catalog |
| `step1b-export-after-load-LOSSY.llp` | the `load`/`pretty()` defect (finding 6) |
| `step2-iter1-mined-text.txt`, `step2-iter1-transcript.md`, `step2-iter1-candidate.llp`, `iter1-world/` | the loop iteration and the accepted world |
| `tamarisk_plugin.py` | prior-flat base bindings (born + iter1 ports) |
| `true_likelihood.py`, `score_episodes.py` | the floor, the per-fluent scorer |
| `notch_slots.py`, `notch/` | the per-slot EM notch: rounds r0–r7, the log, the split-by-reach check |
| `transitions/`, `sinks/`, `scores/` | the episodes; the iter0 sink; the held-out scores |
| `RESULTS-step1.md`, `RESULTS-step2.md` | the full step reports |

Reproduce, from this directory with the metispy venv (CPU: `--jobs 4`,
`nice`):

```
python -m metis.domains.rddl_recorder record --problem Tamarisk_MDP_ippc2014 --instance 1 --episodes 10 --seed 101 --agent random --out transitions/heldout-i1-random-s101-n10.jsonl
python true_likelihood.py transitions/heldout-i1-random-s101-n10.jsonl
nice python notch_slots.py iter1-world/base.llp transitions/iter0-i1-random-s1-n10.jsonl transitions/train-i1-random-s1001-n50.jsonl --rounds 8 --jobs 4 --out notch/iter1-overlay.json
nice python score_episodes.py iter1-world/base.llp transitions/heldout-i1-random-s101-n10.jsonl --overlay notch/iter1-overlay.json
metis --plugin tamarisk_plugin:make ../tamarisk.llp
```
