# blocks_world — three blocks and an arm

**License:** derived from interactive-lp's Ceptre examples (Chris Martens) and offered under the Anti-Capitalist Software License v1.4, not under this repository's Apache-2.0 grant: see [`../README.md`](../README.md) and [`../LICENSE`](../LICENSE).

A port of interactive-lp's `blocks-world.cep`, the classic three-block world, one-to-one. It is the textbook case for "no frame axioms" in linear logic: a move consumes exactly the facts it changes, and the multiset is the state. A plan is a derivation from the init to a state holding the goal: c on the table, b on c, a on b.

As in the original, the `win_condition` rule is commented out, so the world never quiesces. The goal is read with `#query` instead.

The world takes no commands from the domain agent: no `intent.yaml`, no host. `#interactive blocks` lets a person pick each step at the REPL.

Run `metisc --run blocks_world.llp </dev/null` to replay its case. Its expected trace is `goldens/traces/blocks_world.txt`.

## Origin

- **Port of**: `interactive-lp/examples/blocks-world.cep`, 2026-10-03 (catalog `blocks-world`).
- **Row**: `domains/ceptre/CEPTRE-PORTS.md`, blocks-world.
- Moved from `domains/planning/blocks_world.llp` (catalog-packages s-a2c529d6), with the program unchanged.
