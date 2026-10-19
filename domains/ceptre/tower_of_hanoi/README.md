# tower_of_hanoi — three rings, three posts, one arm (the Ceptre port)

**License:** derived from interactive-lp's Ceptre examples (Chris Martens) and offered under the Anti-Capitalist Software License v1.4, not under this repository's Apache-2.0 grant: see [`../README.md`](../README.md) and [`../LICENSE`](../LICENSE).

A port of interactive-lp's `tower_of_hanoi.cep`. Constructed places (`top_of ring`, `bottom post`) become named constants with bwd graph relations (`topof`, `bottomof`). `smaller` is the original's Horn closure. The optimal solve is 7 moves, which is 14 steps.

This is not the RDDL `hanoi` package. That one is the IPPC TowerOfHanoi world with a gym host; this is the Ceptre example.

The world takes no commands from the domain agent: no `intent.yaml`, no host. `#interactive do` lets a person pick each step at the REPL.

Run `metisc --run tower_of_hanoi.llp </dev/null` to replay its case. Its expected trace is `goldens/traces/tower_of_hanoi.txt`.

## Origin

- **Port of**: `interactive-lp/examples/tower_of_hanoi.cep`, 2026-10-03 (catalog `tower-of-hanoi`).
- **Row**: `domains/ceptre/CEPTRE-PORTS.md`, tower_of_hanoi.
- Moved from `domains/planning/tower_of_hanoi.llp` (catalog-packages s-a2c529d6), with the program unchanged.
