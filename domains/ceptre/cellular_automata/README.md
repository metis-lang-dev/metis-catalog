# cellular_automata — a 3×3 grid with no rules yet

**License:** derived from interactive-lp's Ceptre examples (Chris Martens) and offered under the Anti-Capitalist Software License v1.4, not under this repository's Apache-2.0 grant: see [`../README.md`](../README.md) and [`../LICENSE`](../LICENSE).

A port of interactive-lp's `cellular-automata.cep`. The original is a **skeleton**: its header says the predicates were set up but no code was written. The port is one-to-one with that. It has the grid (cells `c<x><y>`, `pos`), the neighbour relation (`nbr`, 6 of 8 Moore neighbours, as in the original) and two empty stages. No update rule is invented. The run starts and ends at once.

Writing the automaton's rules is left to the user: one generation would be one `main`/`compute` lap.

The world takes no commands: no `intent.yaml`, no host.

Run `metisc --run cellular_automata.llp` to replay its case (`#steps 1`, no `#init`: the empty trace). Its expected trace is `goldens/traces/cellular_automata.txt`.

## Origin

- **Port of**: `interactive-lp/examples/cellular-automata.cep`, 2026-10-03 (catalog `cellular-automata`).
- **Row**: `domains/ceptre/CEPTRE-PORTS.md`, cellular-automata.
- Moved from `domains/automata/cellular_automata.llp` (catalog-packages s-a2c529d6), with the program unchanged.
