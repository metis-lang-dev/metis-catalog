# road — parked until the SUMO subject (next release)

The road domain in one package, as the user ruled (road-collapse s-2a2cbea3,
2026-10-19): "packs, road, scenes all belong to the road domain. We'll work
on it next release with SUMO as the runtime. For now just collapse the 3 dirs
into a road domain package, but do not try to fix it."

**Parked.** The files are moved, not fixed: no program changed, no
diagnostic fixed, no `#` case added. SUMO runtime and the real port: next
release, a separate subject. The catalog packages job exempts the package by
name (`ci/packages.py`, "parked"); roundtrip, diagnose (with its exemptions,
`ci/diag-exempt.txt`) and the canonical-key gate (`ci/check.sh` gate 2:
`scenes/manifest.txt` → `goldens/KEYS.txt`) run on its files as before.

## Provenance

Chariot's road catalog: the source of truth for chariot's road-behavior
catalog, metisc catalogs compiled and certified python-side and grounded per
scene by metispy's semantic compiler (`metis.domains.road.gridcat`). The
upstream README is kept verbatim as `UPSTREAM-README.md` (its `packs/`
mentions are this package's `packs/`).

## What is here (moved from)

| file | what | was |
| --- | --- | --- |
| `road_catalog.llp` | the production road catalog (the runtime's); the package's program — an include fragment, typed by `scenes/prodcat_instance.llp` | `road/` |
| `road_handles{,2,3,4}.llp`, `road_zones.llp` | the certified increment history (templates: their types come from metispy's instantiators) | `road/` |
| `road_grid.llp`, `grid_domain.llp` | the exact-filter referee catalog (opaque RSS ports by design: referee, never runtime) and its grid domain | `road/` |
| `handles_domain.llp`, `mini.llp` | the handle-encoding domain (fragment, typed by `scenes/road_close_instance.llp`) and the mini road the pack case runs on | `road/` |
| `wheelchair.llp` | the pack overlay, the catalog-side copy (`extends road`) | `road/` |
| `packs/wheelchair.llp` | the admission-gated pack (metispy's scene/loop vocabulary; containment-typed: it constrains, never enables) | `packs/` |
| `scenes/prodcat_instance.llp`, `scenes/road_close_instance.llp`, `scenes/nav4_instance.llp` | generated scene instances (the include-adopts-catalog pattern); `nav4_instance` is the 2×2 navigation corpus instance (it includes `../../nav/nav_domain.llp`) | `scenes/` |
| `scenes/manifest.txt` | the scene cases the canonical-key gate grounds (metisc `--keys`) | `scenes/` |
| `UPSTREAM-README.md` | chariot's README | `road/` |

The layout is the user's (the package root, `packs/` and `scenes/` beneath
it). Every `.llp` is byte-equal to the file it was, except that the three scene
instances' include lines moved with them, and nothing else did:
`../road/road_catalog.llp` → `../road_catalog.llp`,
`../road/handles_domain.llp` → `../handles_domain.llp`, and
`../domains/nav/nav_domain.llp` → `../../nav/nav_domain.llp`. The manifest's
`../road/mini.llp` is now `../mini.llp`. Their keys in `goldens/KEYS.txt` are
unchanged.
