# gossip — knowledge spreading in a small social network

**License:** derived from interactive-lp's Ceptre examples (Chris Martens) and offered under the Anti-Capitalist Software License v1.4, not under this repository's Apache-2.0 grant: see [`../README.md`](../README.md) and [`../LICENSE`](../LICENSE).

A port of interactive-lp's `gossip.cep`, a game of social-network knowledge propagation. People post messages, followers read them, and a reader with something new reposts it. Stage `say` posts and stage `read` reads, with links between them. Once nobody has heard anything new, the world is done.

The port's departures are each noted in the header:
- the unbounded `says` constructor is flattened;
- once-tokens stand in for Ceptre's latching `!` heads;
- the read→say link is guarded, so the saturated network quiesces instead of flipping to the step bound.

The world takes no commands: no `intent.yaml`, no host.

Run `metisc --run gossip.llp` to replay its case. Its expected trace is `goldens/traces/gossip.txt`.

## Origin

- **Port of**: `interactive-lp/examples/gossip.cep`, 2026-10-03.
- **Row**: `domains/ceptre/CEPTRE-PORTS.md`, gossip.
- Moved from `domains/social/gossip.llp` (catalog-packages s-a2c529d6), with the program unchanged.
