# domains/ceptre — the Ceptre ports, under their own license

The packages in this directory are one-to-one ports of Ceptre programs from
[chrisamaphone/interactive-lp](https://github.com/chrisamaphone/interactive-lp)
(`examples/*.cep`, checkout 22df9ff) into metis. They keep the original's
rule names and structure; each package's README names the `.cep` it came
from. The recipe and the per-port log are [`CEPTRE-PORTS.md`](CEPTRE-PORTS.md).

| package | ported from |
| --- | --- |
| [`blocks_world/`](blocks_world/) | `examples/blocks-world.cep` |
| [`cellular_automata/`](cellular_automata/) | `examples/cellular-automata.cep` |
| [`fptp/`](fptp/) | `examples/fptp.cep` |
| [`gossip/`](gossip/) | `examples/gossip.cep` |
| [`herstory/`](herstory/) | `examples/herstory.cep` |
| [`ll/`](ll/) | `examples/ll.cep` |
| [`love_triangle/`](love_triangle/) | `examples/love-triangle.cep` (= the Ceptre tutorial's `sol/love-triangle.cep`); `love-triangle.cep.orig` is a verbatim copy |
| [`primes/`](primes/) | `examples/primes.cep` |
| [`talespin/`](talespin/) | `examples/talespin.cep` |
| [`three_pigs/`](three_pigs/) | `examples/3lp.cep` |
| [`three_pigs_connectives/`](three_pigs_connectives/) | `three_pigs/` with `blow_stick` changed (a modified 3lp) |
| [`tower_of_hanoi/`](tower_of_hanoi/) | `examples/tower_of_hanoi.cep` |
| [`tragedy/`](tragedy/) | `examples/tragedy.cep` |

## License

interactive-lp is released under the **Anti-Capitalist Software License
v1.4**, Copyright © 2023 Chris Martens. Its text is [`LICENSE`](LICENSE)
in this directory, verbatim.

- These packages are derived from that software, so they are offered under
  the same license. They are **not** covered by this repository's Apache-2.0
  grant (the root `LICENSE` and `NOTICE`), and they cannot be relicensed
  under it.
- Robofortis is a one-person company. It uses and distributes these packages
  as an individual person laboring for themselves (ACSL condition 2a).
- To use, copy, modify or distribute them, you must meet the license's
  conditions yourself:
  - you are an individual laboring for yourself, a non-profit, an educational
    institution, or a worker-owned organization (condition 2);
  - if you are an organization with owners, all owners are workers and all
    workers are owners, with equal equity or equal vote (condition 3);
  - if you are an organization, you are not law enforcement or military, and
    do not work for or under either (condition 4);
  - you keep the copyright notice and permission notice with every copy or
    modified version (condition 1).
- Their run traces stay in `goldens/traces/<name>.txt`. They are the
  programs' recorded outputs, which CI compares against, not copies of the
  programs.
- Older REPL transcripts under `domains/` (`ports/port-proto/transcripts/`,
  `rddl/tamarisk/` and `rddl/wildfire/` step transcripts) quote metispy's
  former narrate example, four rules of `three_pigs`; those quotes are
  covered by this same notice.

`CEPTRE-PORTS.md` is Robofortis's own text: the porting recipe and the
track. It quotes Ceptre syntax only to explain the recipe, and it stays under
the repository's Apache-2.0 grant, as does `tools/ceptre_lockstep.py`, which
drives the real Ceptre interpreter.
