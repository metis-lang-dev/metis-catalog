# metis-catalog

[![ci](https://github.com/metis-lang-dev/metis-catalog/actions/workflows/ci.yml/badge.svg)](https://github.com/metis-lang-dev/metis-catalog/actions/workflows/ci.yml)

Behavior catalogs in LLP, with their certified artifacts and the
collected examples that pin them. Road is ONE world model here, not
the point: `domains/` is the playground of logical problems gathered
across benchmarks, each a full LLP world model.

| dir | what |
| --- | --- |
| `domains/ceptre/` | the Ceptre lineage, under interactive-lp's license: one-to-one ports of interactive-lp's examples (Chris Martens), each a package (domain.yaml, the program, a README of where it came from), offered under the Anti-Capitalist Software License v1.4 and NOT under this repository's Apache-2.0 grant (`domains/ceptre/README.md`, `domains/ceptre/LICENSE`). The story worlds `love_triangle/`, `tragedy/`, `herstory/`, `talespin/`, `three_pigs/`, `three_pigs_connectives/`: Martens' love triangle (A Midsummer Night's Dream), with the ORIGINAL `love-triangle.cep` beside it, and the interactive-lp story worlds — samples become an exact measure, `#interactive` becomes a policy hook, the trace becomes a MAP plot summary. They take no commands: no intent.yaml, so the domain agent opens each with no verbs. The formal worlds `primes/`, `cellular_automata/`, `ll/`, `blocks_world/`, `tower_of_hanoi/`, `gossip/`, `fptp/`: packages with no host and no intents; `tower_of_hanoi` is the Ceptre example, not the RDDL `hanoi`. `CEPTRE-PORTS.md` (Robofortis's own text, Apache-2.0) tracks the ports: the recipe and the per-port log. The wider origin corpus (79 `.cep`: vampire, civ, sokoban, cocktails…) lives in the `if` archive. |
| `domains/bridge/`, `bridge_decl/`, `wgc/` | puzzles formalized from their statements in the metis loop (bridge and torch twice, wolf-goat-cabbage); wgc is the specialist's domain. |
| `domains/gol/` | Game of Life (IPPC) — exact live play via the factored one-step agent; an RDDL world package (the program written out by metispy's generator, a gym host). |
| `domains/kitchen/` | Overcooked-AI — partner-posterior overlay, intent choice on the measure. |
| `domains/nav/` | IPPC Navigation — provably optimal; the reference RDDL world: a package whose host steps the IPPC 2011 gym (`tools/rddl_host.py`, `tools/rddl_gym.py`), no intents. |
| `domains/sysadmin/` | IPPC SysAdmin — the genericity proof domain; an RDDL world package (the 2-computer program on two of the gym's computers). |
| `domains/xtraffic/` | CrossingTraffic — lifted includes, sampling evaluator; an RDDL world package (instance 1 over the lifted domain, a gym host). |
| `domains/wildfire/`, `tamarisk/`, `elevators/`, `hanoi/` | the RDDL gym domains formalized through the metis loop, as RDDL world packages (a gym host each; wildfire and tamarisk with their fitted notch). |
| `domains/rddl/` | the records of those formalization experiments: structure in LL, rates as runtime weight ports fitted from gym episodes. |
| `domains/ports/` | the port-plugin conformance fixtures (sensor, reservoir, clock): rates and exogenous input from a live environment. |
| --- | --- |
| `domains/road/` | moved: the road domains live beside their world, metis-worlds `road/domains` (road-move, 2026-10-26); the parked road catalog before them is removed (its road-close scene stays pinned in metis-lang `corpus/road-close`). |
| `demo/` | tutorial catalogs. |
| `goldens/` | committed expectations: `demo_patrol_v*_goldens.txt` (the C++ runtime's acceptance demo). `traces/<name>.txt`: each package's `metisc --run` trace, and `cases/<name>.llp` + `traces/<name>.case.txt`: CI cases, not domains — the program included unchanged with a start that fires, where the program's own `#init` is its live start (dog, plant, kitchen, sysadmin). |

## Install

```sh
pip install metis-catalog          # the loader and the domain packages; Python 3.10+
pip install metispy metis-catalog  # with the referee: a domain NAME builds and runs
```

The wheel carries the loader (`metis_catalog`, `python -m metis_catalog list`)
and the domain packages under `domains/` (`metis_catalog/domains/` once
installed: the packages `ci/packages.py` runs), with the hosts' tools; not
`domains/ceptre/` (its own license, below), the experiment records
(`domains/rddl/`), the port fixtures, `goldens/` or `demo/`. Installed,
`metis_catalog.root()` is the wheel's catalog, read-only: a loop that writes a
domain sets `METIS_CATALOG` to a checkout or a scratch copy. A checkout reads
its own `domains/`:

```sh
pip install -e .                   # development: root() is this checkout
```

## Releasing

metis-catalog goes to PyPI from GitHub by trusted publishing
(`.github/workflows/publish.yml`, metispy's flow; no token anywhere): bump
`version` in `pyproject.toml` and `metis_catalog.__version__`, commit,
`gh release create vX.Y.Z` (the tag must be `v` + that version: the workflow
refuses any other); the tag's push publishes straight through (the `pypi`
environment has no required reviewer). The run builds the sdist and the wheel,
smoke-installs the wheel in a fresh venv outside the checkout with metispy
from PyPI (`tools/smoke_wheel.sh`: every package there, every domain's bundle
built by name; ci.yml runs it on every push too) and uploads.
`workflow_dispatch` is the dry run: everything but the upload.

## Experiments: the formalization record

The metis-loop experiments, concluded and moved here on 2026-10-11, each
live next to the domain they produced. Each experiment's `README.md`
carries what formalization taught: findings, numbers vs the reference,
and what not to retry. The rest of the directory is the evidence it
cites. metis-loop keeps only the loop machinery.

| experiment | what it formalized |
| --- | --- |
| `domains/rddl/wildfire/` | IPPC2014 Wildfire from its header; one ignition port notched to the gym's logistic |
| `domains/rddl/tamarisk/` | IPPC2014 Tamarisk; 11 one-law ports, the per-slot EM notch |
| `domains/rddl/elevators/` | IPPC elevators — the first RDDL run; the recipe, cards and interface the shelf reused |
| `domains/rddl/hanoi/` | rddlrepository arcade Tower of Hanoi (Tier-2 probe) |
| `domains/bridge/`, `domains/bridge_decl/` | bridge and torch — imperative vs declarative; the "mechanism, not ledger" doctrine (the account in bridge's README) |
| `domains/wgc/` | wolf, goat and cabbage — the ferry/shore settle tick |
| `domains/ports/port-proto/` | the PortPlugin conformance fixtures |
| `demo/surprise-demo/` | the pantry world: a planted gap, the surprise walkthrough |
| `demo/synthetic-meadow/` | the first end-to-end surprise cycle in the REPL |

## Check

```sh
sh ci/check.sh         # METISC=<path> to override the sibling metis-lang build
sh ci/diagnose.sh      # no error diagnostics (reasoned exemptions in ci/diag-exempt.txt)
python ci/packages.py  # every package: --run against its trace, metispy's twin, --wire against metispy's bundle
python ci/packages.py --update --only NAME   # rewrite a package's trace after a deliberate change
```

**Every live program is a package** (`domains/<name>/`: domain.yaml,
`<name>.llp`, a README). The loader finds a package by its `domain.yaml`
anywhere under the root, so a part of the catalog is a catalog too:
`cd domains/ceptre && metis-loop` serves the Ceptre ports, with their
README as the catalog's context. What stays outside packages, and why:

| where | why it is not a package |
| --- | --- |
| `domains/rddl/` | the record of the RDDL formalization experiments (born, candidate, iteration worlds): evidence for their READMEs, not served worlds. The worlds they produced are packages. |
| `domains/ports/port-proto/` | the PortPlugin conformance fixtures (clock, reservoir, sensor): protocol tests with their own drivers and transcripts, not worlds a person opens. |
| `demo/` | the C++ runtime's acceptance demo (`patrol.llp`, `patrol_v2.llp`: pinned by `goldens/demo_patrol_v*_goldens.txt`, wires regenerated by roadcat) and two concluded REPL walkthroughs (`surprise-demo/`, `synthetic-meadow/`, kept as their READMEs and transcripts cite them): fixtures and teaching records. |
| `goldens/cases/` | CI cases (see goldens/), not domains. |

These keep their roundtrip (check.sh) and diagnose gates only.

check.sh roundtrips every `.llp` (`parse (pretty a) = a`). The canonical-key gate over the parked road scenes went
with them (road-move); metis-lang's corpus keeps its own key pins.

## Provenance

Extracted from `chariot_ws/packages/wayplan/catalog` (R1 closure of
the catalog-runtime rebase). Decode/binding code (geometry → semantic
atoms, port registries) stays with the consuming runtime; this repo
is sources + certified data only.

## License

Apache License 2.0 (see `LICENSE`, `NOTICE`) — the loader, the packages
under `domains/` except `domains/ceptre/`, the tools, CI, goldens and
docs. Copyright 2026 Robofortis.

Exceptions:

- `domains/ceptre/` holds ports of Ceptre programs from
  [interactive-lp](https://github.com/chrisamaphone/interactive-lp)
  (Copyright © 2023 Chris Martens). They are offered under its
  Anti-Capitalist Software License v1.4 (`domains/ceptre/LICENSE`), not
  under the Apache-2.0 grant. A User must meet that license's conditions;
  see `domains/ceptre/README.md`. Its `CEPTRE-PORTS.md` is Robofortis's own
  text, under Apache-2.0.
- The paper under `paper/` is copyright its authors, all rights reserved
  (it is licensed by its publication venue, not by this repository).
