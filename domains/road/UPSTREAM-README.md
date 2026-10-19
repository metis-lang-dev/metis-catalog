# Chariot road catalog — canonical `.llp` sources

This directory is the **source of truth** for chariot's road-behavior
catalog (see chariot_ws `docs/catalog-reconciliation.md`). The files are
metisc (`metis.lang`) catalogs: compiled and certified python-side,
grounded per scene by the semantic compiler
(`metis.domains.road.gridcat`, transitional home), destined for the C++
runtime via the grounded-program loader.

- `road_grid.llp` — the production kernel catalog (lolli window kernel,
  lifted: relations-only rules, compiler-generated Horn tables, policy
  as weight ports).
- `road_handles.llp` — the handle-encoding catalog
  (docs/road-encoding.md): geometry behind ports, RSS gap classes.
- `packs/wheelchair.llp` — pack overlay (`extends`, containment by
  construction).

Rules of the road:

1. **New behavior clauses land here** — through the admission gate
   (lint + containment + model checks), with catalog-level provenance.
   The surprise channel (docs/surprise-catalog.md) feeds candidates.
2. **Metis keeps frozen fixtures** of these catalogs for kernel parity
   (`metis/domains/road/catalogs/`). `py/tests/test_catalog_parity.py`
   pins this copy program_key-identical to the fixture; a divergence is
   either a deliberate chariot behavior change (update the pin: the
   fixture stays behind) or an accident (fix it).
3. The flat-LLP files under `packs/` at the package root (loaded by the
   legacy lolli pack path) are a different, older format — do not
   confuse them with these catalogs.
