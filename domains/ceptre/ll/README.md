# ll — a toy linear-logic theorem prover

**License:** derived from interactive-lp's Ceptre examples (Chris Martens) and offered under the Anti-Capitalist Software License v1.4, not under this repository's Apache-2.0 grant: see [`../README.md`](../README.md) and [`../LICENSE`](../LICENSE).

A port of interactive-lp's `ll.cep`, a "toy lin log interactive thm prover". Sequent rules are written as linear-logic rules. `goal F` is the right of the sequent and `ctx F` a hypothesis. Each rule decomposes one connective, and a proof is a run that consumes every goal and every ctx. The test theorem is proved on every run.

`prop` is recursive, so the port enumerates the subformulas of the original's test context as constants. A new theorem needs its own enumeration. The original's open question (oneR needs an absence test) is kept open in the header.

The world takes no commands from the domain agent: no `intent.yaml`, no host. `#interactive prove` lets a person pick each step at the REPL (`metis ll.llp`). With stdin closed, `metisc --run` takes the sampler's choice.

Run `metisc --run ll.llp </dev/null` to replay its case. Its expected trace is `goldens/traces/ll.txt`.

## Origin

- **Port of**: `interactive-lp/examples/ll.cep`, 2026-10-03.
- **Row**: `domains/ceptre/CEPTRE-PORTS.md`, ll.
- Moved from `domains/logic/ll.llp` (catalog-packages s-a2c529d6), with the program unchanged.
