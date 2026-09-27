# metis-catalog

Behavior catalogs in LLP, with their certified artifacts and the
collected examples that pin them.

| dir | what |
| --- | --- |
| `road/` | the production road catalog (`road_catalog.llp`, served by the runtime) + the certified increment history (`road_handles{,2,3,4}.llp`, `road_zones.llp`) + the exact-filter referee catalog (`road_grid.llp`, opaque RSS ports BY DESIGN — referee, never runtime). |
| `packs/` | admission-gated extension packs (containment-typed: packs constrain, never enable). |
| `demo/` | tutorial catalogs. |
| `scenes/` | generated scene instances (the include-adopts-catalog pattern) + the case manifest — how a domain-generic catalog meets a concrete situation. |
| `goldens/` | committed artifacts + expectations: the product IR artifact the runtime loads (`*_ir_artifact.txt`), per-scene decision/marginal expectations (`*_ir_expect.txt`), canonical keys (`KEYS.txt`). Expectation floats come from the metispy exact referee; keys are cross-toolchain (metisc == metispy, byte-equal). |

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
