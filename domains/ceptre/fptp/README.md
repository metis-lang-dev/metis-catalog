# fptp — first-past-the-post voting

**License:** derived from interactive-lp's Ceptre examples (Chris Martens) and offered under the Anti-Capitalist Software License v1.4, not under this repository's Apache-2.0 grant: see [`../README.md`](../README.md) and [`../LICENSE`](../LICENSE).

A port of interactive-lp's `fptp.cep`. It has three stages:
- `count` tallies the ballots;
- `pick` finds the maximum, eliminating every lower candidate;
- `done` elects the one left.

It exercises state-carrying quiescence links (`count -o pick * max(n0)`) and Ceptre's persistent `!elected`/`!defeated` heads, written as atoms produced once. With alice 3, bob 2 and charlie 1, alice is elected with probability 1. A tie would be broken uniformly, as in the original.

The world takes no commands: no `intent.yaml`, no host.

Run `metisc --run fptp.llp` to replay its case. Its expected trace is `goldens/traces/fptp.txt`.

## Origin

- **Port of**: `interactive-lp/examples/fptp.cep`, 2026-10-03.
- **Row**: `domains/ceptre/CEPTRE-PORTS.md`, fptp.
- Moved from `domains/votes/fptp.llp` (catalog-packages s-a2c529d6), with the program unchanged.
