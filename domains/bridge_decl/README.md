# bridge_decl — bridge and torch, declarative

The bridge-and-torch puzzle formalized declaratively: time is dynamics and pace is data. The bridge is a chain of minute-marks (`m0..m8`). The party advances one mark per minute and burns one wick per minute. Each walker steps off at their own `pace`, and the torch lands only when both planks are back, so the slower person's pace emerges. The tick is board → stride → settle, which extends the wgc ferry/shore tick.

This is the imperative `bridge` package's counterpart, and the worked example of "model the mechanism, not the ledger". The side-by-side account of the two programs, with their results, is `../bridge/README.md`.

The world takes no commands: no `intent.yaml`, no host.

Run `metisc --run bridge_decl.llp` to replay its case. Seed 1 is a failing random episode, not the solution. Its expected trace is `goldens/traces/bridge_decl.txt`.

## Evidence

- `bridge-declarative-transcript.md`: the REPL session (`run 40` smoke run, wick 15/14 queries, the goal record and `replay`). It names the program by its earlier file name, `bridge-declarative.llp`.
- `runs/goal-decl.jsonl`: the goal-evidence record.

## Origin

- **Formalized from**: the problem statement on en.wikipedia.org/wiki/Bridge_and_torch_problem (fetched 2026-10-09), quoted in the header. No solution was consulted. The program's catalog is `bridge_decl` (`provenance text`, 2026-10-09).
- A concluded metis-loop experiment (`metis-loop/experiments/bridge-torch/`). It moved from `domains/planning/bridge-torch/bridge-declarative.llp` (catalog-packages s-a2c529d6); the file was renamed `bridge_decl.llp` after its catalog, and its content is unchanged.
