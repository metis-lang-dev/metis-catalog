> **Archived 2026-10-26** (road-world s-e812715d step 2, the user's go): this parked package is replaced by
> `domains/road/` — the road domains over roles (responder, planner, the tree director; metis-worlds road/ the
> exerciser and the hosts). Its files are kept here unchanged, with their provenance below; the metis-lang corpus
> pin `corpus/road-close.llp` stays as a frozen fixture. The keys gate (ci/check.sh gate 2) and the diagnostics'
> exemptions (ci/diag-exempt.txt) now name these paths; its trace golden is goldens/road.txt beside them; the one
> edit: scenes/nav4_instance.llp includes domains/nav by its new relative path (the grounded program, and its key,
> unchanged).

# road — parked until the SUMO subject (next release)

The road domain in one package, as the user ruled (road-collapse s-2a2cbea3,
2026-10-19): "packs, road, scenes all belong to the road domain. We'll work
on it next release with SUMO as the runtime. For now just collapse the 3 dirs
into a road domain package, but do not try to fix it."

**Parked.** The files are moved, not fixed: no moved program changed, no
diagnostic fixed. SUMO runtime and the real port: next release, a separate
subject. So that the package runs and builds nominally (the user, 2026-10-19:
"you can simplify road main script that it pass nominally"), its program is a
new, simple `road.llp`: the production catalog `road_catalog.llp` included
unchanged on the production scene (`scenes/prodcat_instance.llp`'s types and
lane facts), with that scene's start from `scenes/manifest.txt` as its `#`
case, one tick of 17 rows through the catalog's nine stages. Its weight ports
(brk, cls, rss, zadv) have no host and price at their prior. It passes every
package gate as any other package does: `metisc --run` against
`goldens/traces/road.txt`, metispy's twin, the wire byte-equal to metispy's.
Roundtrip, diagnose (with its exemptions, `ci/diag-exempt.txt`) and the
canonical-key gate (`ci/check.sh` gate 2: `scenes/manifest.txt` →
`goldens/KEYS.txt`) run on the other files as before.

## Provenance

Chariot's road catalog: the source of truth for chariot's road-behavior
catalog, metisc catalogs compiled and certified python-side and grounded per
scene by metispy's semantic compiler (`metis.domains.road.gridcat`). The
upstream README is kept verbatim as `UPSTREAM-README.md` (its `packs/`
mentions are this package's `packs/`).

## What is here (moved from)

| file | what | was |
| --- | --- | --- |
| `road.llp` | the package's program: `road_catalog.llp` on the production scene, one tick (new) | — |
| `road_catalog.llp` | the production road catalog (the runtime's) — an include fragment, typed by `road.llp` and `scenes/prodcat_instance.llp` | `road/` |
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
