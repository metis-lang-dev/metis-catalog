# metis-catalog

[![ci](https://github.com/metis-lang-dev/metis-catalog/actions/workflows/ci.yml/badge.svg)](https://github.com/metis-lang-dev/metis-catalog/actions/workflows/ci.yml)

Behavior catalogs in LLP, with their certified artifacts and the
collected examples that pin them. Road is ONE world model here, not
the point: `domains/` is the playground of logical problems gathered
across benchmarks, each a full LLP world model.

| dir | what |
| --- | --- |
| `domains/love_triangle/`, `tragedy/`, `herstory/`, `talespin/`, `three_pigs/`, `three_pigs_connectives/` | the Ceptre lineage, each a catalog domain (domain.yaml, the program, a README of where it came from): Martens' love triangle (A Midsummer Night's Dream), with the ORIGINAL `love-triangle.cep` beside it, and the interactive-lp story worlds — samples become an exact measure, `#interactive` becomes a policy hook, the trace becomes a MAP plot summary. They take no commands: no intent.yaml, so the domain agent opens each with no verbs. `domains/CEPTRE-PORTS.md` tracks the ports; the wider origin corpus (79 `.cep`: vampire, civ, sokoban, cocktails…) lives in the `if` archive, ports welcome. |
| `domains/gol/` | Game of Life (IPPC) — exact live play via the factored one-step agent. |
| `domains/kitchen/` | Overcooked-AI — partner-posterior overlay, intent choice on the measure. |
| `domains/nav/` | IPPC Navigation — provably optimal. |
| `domains/sysadmin/` | IPPC SysAdmin — the genericity proof domain. |
| `domains/xtraffic/` | CrossingTraffic — lifted includes, sampling evaluator. |
| `domains/rddl/` | RDDL gym domains formalized through the metis loop (Wildfire, Tamarisk; the elevators and hanoi experiments): structure in LL, rates as runtime weight ports fitted from gym episodes. |
| `domains/ports/` | the port-plugin conformance fixtures (sensor, reservoir, clock): rates and exogenous input from a live environment. |
| `domains/CEPTRE-PORTS.md` | the Ceptre → metis porting track: the recipe and the per-port log. |
| --- | --- |
| `road/` | the production road catalog (`road_catalog.llp`, served by the runtime) + the certified increment history (`road_handles{,2,3,4}.llp`, `road_zones.llp`) + the exact-filter referee catalog (`road_grid.llp`, opaque RSS ports BY DESIGN — referee, never runtime). |
| `packs/` | the road catalog's admission-gated packs (metispy's scene/loop vocabulary; containment-typed: they constrain, never enable). A domain package's are its `extensions/` (CATALOG.md). |
| `demo/` | tutorial catalogs. |
| `scenes/` | generated scene instances (the include-adopts-catalog pattern) + the case manifest — how a domain-generic catalog meets a concrete situation. |
| `goldens/` | committed artifacts + expectations: the product IR artifact the runtime loads (`*_ir_artifact.txt`), per-scene decision/marginal expectations (`*_ir_expect.txt`), canonical keys (`KEYS.txt`). Expectation floats come from the metispy exact referee; keys are cross-toolchain (metisc == metispy, byte-equal). |

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
| `domains/planning/bridge-torch/` | bridge and torch — imperative vs declarative; the "mechanism, not ledger" doctrine |
| `domains/planning/wgc/` | wolf, goat and cabbage — the ferry/shore settle tick |
| `domains/ports/port-proto/` | the PortPlugin conformance fixtures |
| `demo/surprise-demo/` | the pantry world: a planted gap, the surprise walkthrough |
| `demo/synthetic-meadow/` | the first end-to-end surprise cycle in the REPL |

## Check

```sh
sh ci/check.sh    # METISC=<path> to override the sibling metis-lang build
```

Gate 1 roundtrips every `.llp` (`parse (pretty a) = a`); gate 2
grounds the committed scene through metisc and pins the canonical
`program_key` against `goldens/KEYS.txt` — the same key metispy
asserts, so the artifact cache is shared across toolchains.

## Provenance

Extracted from `chariot_ws/packages/wayplan/catalog` (R1 closure of
the catalog-runtime rebase). Decode/binding code (geometry → semantic
atoms, port registries) stays with the consuming runtime; this repo
is sources + certified data only.
