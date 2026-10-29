"""metis-catalog package gates (catalog-packages s-a2c529d6): every domain
package is run and built, by both toolchains.

  run    `metisc --run` of the package's program (its `#` case; stdin closed,
         so an `#interactive` choice is the sampler's) equals the committed
         goldens/traces/<name>.txt byte for byte. A package without a program
         of its own (kitchen_shared) runs the first file it serves. The CI
         cases in goldens/cases/<name>.llp (the program included, with a start
         that fires, where the program's own #init is its live start and
         stays as it is) run against goldens/traces/<name>.case.txt. A program
         with no `#` case whose package has cases/ (kitchen_pot's cooks and
         director: their cases are cases/*.yaml) runs those through metispy's
         interface stub instead (python -m metis.catalog cases NAME); one with
         neither (cook_b, pot_director) has the wire gate only, and says so.
  twin   metispy's replay of the same case (render_run, the REPL's `trace`)
         gives the same I/T/F lines: both samplers seeded alike.
  wire   `metisc --wire` of the served program (the program and its
         extensions) equals metispy's bundle ground.wire (served_doc +
         emit_artifact) byte for byte.
  golden a package with goldens/ (its day.jsonl and intents.jsonl in,
         their .out.jsonl out; dagent-fixtures s-86bbd1e7 step 2): metispy
         writes the same goldens again (metis.domain.day), byte for byte. A
         commit that changes what the package says without writing them
         again (`python -m metis.catalog golden NAME`) fails here; --update
         writes them. The domain agents (metis-agent's Go and py) are held to
         the same files in their own CI.

Every tracked package needs a trace, and every trace a package or a case. Each
metisc call is its own process (in the environment as it is: metisc finds its own
standard units, metis-lang spec/17 amendment 5), at most --jobs at once (talespin grounds 105k
events in about 2 minutes, for its run and for its wire alike).

  python ci/packages.py [--jobs N] [--only NAME...] [--no-py]
  python ci/packages.py --update [--only NAME...]     write the traces and the goldens

METISC as in check.sh. --no-py: the run gate only (no metispy)."""
import argparse
import os
import subprocess
import sys
import time

import yaml
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import metis_catalog as mc  # noqa: E402

METISC = os.environ.get("METISC") or str(ROOT.parent / "metis-lang/src/metisc")
TRACES = ROOT / "goldens/traces"
CASES = ROOT / "goldens/cases"


def tracked():
    """The package directories git knows (an untracked domain is the user's)."""
    out = subprocess.run(["git", "ls-files", "domains/*/domain.yaml"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout.split()
    return {(ROOT / p).parent.resolve() for p in out}


def units(only):
    """[(unit name, file to run, served files or None)] — a package's run and
    wire, then the CI cases (run only)."""
    dirs = tracked()
    out = []
    for d in mc.domains(ROOT):
        if (only and d.name not in only) or (not only and d.dir not in dirs):   # --only: named, tracked or not
            continue
        served = d.serves()
        out.append((d.name, d.program or served[0], served))
    for c in sorted(CASES.glob("*.llp")):
        if not only or c.stem in only:
            out.append((c.stem + ".case", c, None))
    return out


def stub_cases(name):
    """(ok, note): the package's cases/*.yaml through the interface stub (metis.catalog.stub)."""
    from metis import catalog
    from metis.catalog import stub
    res = stub.run_package(catalog.get(name, ROOT))
    bad = [c.as_dict().get("name") for c in res if not c.passed]
    return (bool(res) and not bad), (f"{len(res)} cases/*.yaml through the stub (no # case)" if not bad
                                     else f"cases failing through the stub: {bad}")


def metisc(args):
    """(stdout, seconds). stdout goes to a file, not a pipe: talespin's wire is
    56 MB, and a pipe's reader starved by other work stalls the writer."""
    import tempfile
    t = time.time()
    with tempfile.TemporaryFile("w+") as out:
        r = subprocess.run([METISC, *args], stdin=subprocess.DEVNULL, stdout=out,
                           stderr=subprocess.PIPE, text=True)
        out.seek(0)
        text = out.read()
    if r.returncode:
        raise RuntimeError(f"metisc {' '.join(args)}: exit {r.returncode}: "
                           f"{r.stderr.strip().splitlines()[-1:]}")
    return text, time.time() - t


def py_run(path):
    """metispy's replay of the file's case, wire mode (= metisc --run)."""
    from metis.kernel.artifact import served_doc
    from metis.lang.directives import render_run
    doc, case, _ = served_doc(Path(path), [])
    prog = doc.catalog.ground(dict(case["init"]))
    return render_run(Path(path).stem, case, prog) + "\n"


def py_wire(served, manifest=None):
    from metis.kernel.artifact import served_doc
    from metis.kernel.wire import emit_artifact
    doc, case, _ = served_doc(served[0], served[1:], manifest)
    return emit_artifact(doc, doc.catalog.ground(dict(case["init"])), case["steps"])


def check_golden(unit, update):
    """[(gate, ok, note)]: the package's goldens/ against what metispy makes of it now."""
    from metis import catalog
    from metis.domain import day
    d = catalog.get(unit[0], ROOT)
    if update:
        files = day.golden(d)
        for f, text in files.items():
            (d.dir / day.GOLDENS / f).write_text(text)
        return [("golden", bool(files), f"wrote {', '.join(sorted(files))}" if files else "no day.jsonl or intents.jsonl")]
    bad = day.check(d)
    return [("golden", not bad, "\n".join(f"goldens/{f}: {w}" for f, w in bad))]


def has_goldens(unit):
    """A package (not a CI case) whose directory has goldens/."""
    if unit[2] is None:
        return False
    from metis import catalog
    return (catalog.get(unit[0], ROOT).dir / "goldens").is_dir()


def itf(text):
    return [l for l in text.splitlines() if l[:2] in ("I ", "T ", "F ")]


def check_run(unit, py, update):
    """[(gate, ok, note)]: the unit's run against its trace, and its twin."""
    name, path, _ = unit
    if "#steps" not in Path(path).read_text():          # no # case: its #init is its live start
        if (Path(path).parent / "cases").is_dir():
            return [("run", *stub_cases(name))]
        return [("run", True, "no # case and no cases/: the wire gate only")]
    res = []
    gold = TRACES / f"{name}.txt"
    try:
        run, dt = metisc(["--run", str(path)])
    except RuntimeError as e:
        return [("run", False, str(e))]
    if update:
        gold.write_text(run)
        res.append(("run", True, f"wrote {gold.relative_to(ROOT)} ({dt:.1f}s)"))
    elif not gold.is_file():
        res.append(("run", False, f"no trace {gold.relative_to(ROOT)} (--update writes it)"))
    elif gold.read_text() != run:
        import difflib
        d = "".join(list(difflib.unified_diff(gold.read_text().splitlines(True), run.splitlines(True),
                                              str(gold.relative_to(ROOT)), "metisc --run"))[:12])
        res.append(("run", False, "the trace differs:\n" + d))
    else:
        res.append(("run", True, f"{dt:.1f}s"))
    if py:
        try:
            ok = itf(py_run(path)) == itf(run)
            res.append(("twin", ok, "" if ok else "metispy's I/T/F lines differ from metisc's"))
        except Exception as e:                          # noqa: BLE001
            res.append(("twin", False, f"{type(e).__name__}: {str(e)[:200]}"))
    return res


def check_wire(unit, py):
    """[(gate, ok, note)]: the served program's wire, metisc against metispy, with the package's manifest (its
    levels' generated declarations, metis-lang spec/16 amendment 1); a package with a levels: block adds the
    levels gate: metisc --levels == metispy's metis.lang.levels, byte for byte."""
    name, _, served = unit
    manifest = mc.get(name, ROOT).dir / "domain.yaml"
    args = ["--wire", str(served[0])]
    for e in served[1:]:
        args += ["--extension", str(e)]
    args += ["--manifest", str(manifest)]
    lv = []
    if "levels" in (yaml.safe_load(manifest.read_text()) or {}):
        try:
            gen, _ = metisc(["--levels", str(manifest)])
            if py:
                from metis.lang.levels import lines
                ok = "".join(l + "\n" for l in lines(manifest)) == gen
                lv = [("levels", ok, f"{len(gen.splitlines())} generated" if ok else "metisc --levels differs from metispy's")]
            else:
                lv = [("levels", True, f"{len(gen.splitlines())} generated (metisc only)")]
        except RuntimeError as e:
            lv = [("levels", False, str(e))]
    try:
        w, dt = metisc(args)
    except RuntimeError as e:
        return [("wire", False, str(e))] + lv
    if not py:
        return [("wire", True, f"{dt:.1f}s (metisc only)")] + lv
    try:
        ok = py_wire(served, manifest) == w
        return [("wire", ok, f"{dt:.1f}s" if ok else "metisc --wire differs from metispy's ground.wire")] + lv
    except Exception as e:                              # noqa: BLE001
        return [("wire", False, f"{type(e).__name__}: {str(e)[:200]}")] + lv


# the units whose metisc ground takes minutes start first, so their run and
# wire overlap the rest instead of trailing it (talespin: ~2 min each)
HEAVY = ("talespin", "tragedy")


def one(task):
    """One gate of one unit, in a worker process of its own (metispy's work is
    pure Python: threads would serialize it)."""
    u, gate, py, update = task
    if gate == "golden":
        return u, check_golden(u, update)
    return u, (check_run(u, py, update) if gate == "run" else check_wire(u, py))


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--jobs", type=int, default=2)
    ap.add_argument("--only", nargs="+", default=[])
    ap.add_argument("--update", action="store_true")
    ap.add_argument("--no-py", action="store_true")
    a = ap.parse_args(argv)
    us = units(set(a.only))
    t0 = time.time()
    py = not a.no_py
    tasks = [(u, "run", py, a.update) for u in us] + [(u, "wire", py, False) for u in us
                                                      if u[2] is not None and not a.update]
    tasks += [(u, "golden", py, a.update) for u in us if py and has_goldens(u)]
    tasks.sort(key=lambda t: t[0][0] not in HEAVY)     # stable: otherwise in order
    with ProcessPoolExecutor(max(1, a.jobs)) as ex:
        results = sorted(ex.map(one, tasks), key=lambda r: r[0][0])
    bad = 0
    for (name, _, _), res in results:
        for gate, ok, note in res:
            bad += not ok
            print(f"{'ok  ' if ok else 'FAIL'} {gate:4} {name}{'  ' + note if note else ''}")
    if not a.only:                                      # a trace with no package or case is stale
        names = {u[0] for u in us}
        for t in sorted(TRACES.glob("*.txt")):
            if t.stem not in names:
                bad += 1
                print(f"FAIL {t.relative_to(ROOT)}: no package or case of that name")
    print(f"{len(us)} units in {time.time() - t0:.0f}s, --jobs {a.jobs}")
    print("PACKAGES GREEN" if not bad else f"{bad} failure(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
