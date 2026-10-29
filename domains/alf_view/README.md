# alf_view — a belief level the toolchain declares

The place level of the loop's ALFWorld view (metis-loop policy-tuning-2, step 2f: the first level a brain declared),
as a package: `alf_view.llp` has the rules that read the level atom `$place_level(high, O, R)` and nothing that
declares it. The manifest's `levels:` block fully determines the rest (metis-lang spec/16 amendment 1), so the
toolchain generates it at build:

```
type level {low mid high}.
weight where(O,R) reads {inrecep(O,R)}.
pred place_level(level,object,receptacle) : alf.
```

(`metisc --levels domains/alf_view/domain.yaml` prints them; metispy's `metis.lang.levels` makes the same lines.)
`fetch_risk` is an evaluate level: its pred and its type `risk` are the program's own, and agree with the manifest.

The package is the catalog's parity case for the generation: `ci/packages.py` builds its wire with both toolchains,
each with the manifest, and compares them and the generated lines byte for byte. It has no `#` case: the program alone
does not compile, by design.
