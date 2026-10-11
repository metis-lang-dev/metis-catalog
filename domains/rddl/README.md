# rddl — RDDL gym domains formalized through the metis loop

These come from subject rddl-tier1 (closed 2026-10-11). Wildfire and
Tamarisk are SYNTHETIC IPPC2014 benchmark domains (rddlrepository,
played in pyRDDLGym). The exercise was not to reproduce the gym. It
tested **the split between LL and runtime**:

- **In LL (the `.llp`):** structure and the step's timeline. Lockstep
  stages walk one gym step. Quantities are walked `bwd` chains, not
  unrolled rules: Wildfire's burning-neighbor count k0..k8 is a tally
  path, and Tamarisk's noisy-or is a scan over source positions. Every
  stochastic law is ONE rule with a complement pair `@w p | @w ~p`.
- **At runtime:** the numbers. Each rate is a weight port (`weight
  p(...) reads {}`) bound when the world is served: a plugin's
  prior-flat base (0.5) plus a notch table fitted from recorded gym
  episodes. The catalogs contain no rate literal.

Serve: `metis --plugin <plugin>:make domains/rddl/<domain>.llp`. The
plugins and fitting scripts live in metis-loop `experiments/<domain>/`.
The fitted tables are here (`<domain>.notch.json`, the overlay format of
`rddl_recorder --overlay`).

## Last result against the gym (instance 1, random agent)

### wildfire.llp — 1 port, pign(K)

The fit uses 2400 transitions; the scores are 10 held-out episodes.

| k | gym law 1/(1+e^(4.5−k)) | fitted pign(k) | n |
|---|---|---|---|
| 0 | 0.0110 | 0.0094 | 3194 |
| 1 | 0.0293 | 0.0258 | 3366 |
| 2 | 0.0759 | 0.0837 | 1040 |
| 3 | 0.1824 | 0.1464 | 280 |
| 4 | 0.3775 | 0.4000 | 25 |
| 5 | 0.6225 | 0.6000 | 5 |

All six lie within their 95% CI of the gym's law. Held-out surprises
per episode: born catalog 11.5; ports prior-flat 12.3; ports fitted 1.3.
The gym's own generator scores 1.4.

### tamarisk.llp — 11 ports

The fit uses 2400 transitions, 8 stochastic-EM rounds; the scores are
10 held-out episodes.

| port | gym non-fluent | gym | fitted | n |
|---|---|---|---|---|
| perad | ERADICATION-RATE | 0.9 | 0.894 | 614 |
| prest | RESTORATION-RATE | 0.9 | 0.918 | 183 |
| pdown | DOWNSTREAM-SPREAD-RATE | 0.6 | 0.602 | 1068 |
| psib | DOWNSTREAM-SPREAD-RATE (within reach) | 0.6 | 0.576 | 465 |
| pup | UPSTREAM-SPREAD-RATE | 0.15 | 0.098 | 889 |
| ptdie | DEATH-RATE-TAMARISK | 0.05 | 0.046 | 10148 |
| pndie | DEATH-RATE-NATIVE | 0.05 | 0.049 | 4955 |
| ptborn | EXOGENOUS-PROD-RATE-TAMARISK | 0.1 | 0.134 | 2662 |
| pnborn | EXOGENOUS-PROD-RATE-NATIVE | 0.1 | 0.094 | 2669 |
| ptcomp | COMPETITION-WIN-RATE-TAMARISK | 0.8 | 0.787 | 305 |
| pncomp | COMPETITION-WIN-RATE-NATIVE | 0.2 | 0.200 | 305 |

Held-out log-loss per step over the 16 observed fluents: born 10.87;
ports prior-flat 6.40; ports fitted 2.72. The gym's own generator
scores 2.65.

- 8 of 11 ports contain the gym value in their 95% CI.
- pup and ptborn share credit for the same arrivals (noisy-or), and the
  EM had not separated them after 8 rounds.
- Per-reach rows agree with the global ports: 2 of 36 fall outside
  their CI.

Full reports: metis-loop `experiments/wildfire/RESULTS-step2.md` and
`experiments/tamarisk/RESULTS-step2.md`.
