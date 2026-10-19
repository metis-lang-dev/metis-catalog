"""metis-catalog package gates (catalog-packages s-a2c529d6): every domain
package is run and built, by both toolchains.

  run    `metisc --run` of the package's program (its `#` case; stdin closed,
         so an `#interactive` choice is the sampler's) equals the committed
         goldens/traces/<name>.txt byte for byte. A package without a program
         of its own (kitchen_shared) runs the first file it serves. The CI
         cases in goldens/cases/<name>.llp (the program included, with a start
         that fires, where the program's own #init is its live start and
         stays as it is) run against goldens/traces/<name>.case.txt.
  twin   metispy's replay of the same case (render_run, the REPL's `trace`)
         gives the same I/T/F lines: both samplers seeded alike.
  wire   `metisc --wire` of the served program (the program and its
         extensions) equals metispy's bundle ground.wire (served_doc +
         emit_artifact) byte for byte.

Every tracked package needs a trace, and every trace a package or a case. Each
metisc call is its own process, at most --jobs at once (talespin grounds 105k
events in about 2 minutes, for its run and for its wire alike).

  python ci/packages.py [--jobs N] [--only NAME...] [--no-py]
  python ci/packages.py --update [--only NAME...]     write the traces

METISC as in check.sh. --no-py: the run gate only (no metispy)."""
import argparse
import os
import subprocess
import sys
import time
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


def py_wire(served):
    from metis.kernel.artifact import served_doc
    from metis.kernel.wire import emit_artifact
    doc, case, _ = served_doc(served[0], served[1:])
    return emit_artifact(doc, doc.catalog.ground(dict(case["init"])), case["steps"])


def itf(text):
    return [l for l in text.splitlines() if l[:2] in ("I ", "T ", "F ")]


def check_run(unit, py, update):
    """[(gate, ok, note)]: the unit's run against its trace, and its twin."""
    name, path, _ = unit
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
    """[(gate, ok, note)]: the served program's wire, metisc against metispy."""
    _, _, served = unit
    args = ["--wire", str(served[0])]
    for e in served[1:]:
        args += ["--extension", str(e)]
    try:
        w, dt = metisc(args)
    except RuntimeError as e:
        return [("wire", False, str(e))]
    if not py:
        return [("wire", True, f"{dt:.1f}s (metisc only)")]
    try:
        ok = py_wire(served) == w
        return [("wire", ok, f"{dt:.1f}s" if ok else "metisc --wire differs from metispy's ground.wire")]
    except Exception as e:                              # noqa: BLE001
        return [("wire", False, f"{type(e).__name__}: {str(e)[:200]}")]


# the units whose metisc ground takes minutes start first, so their run and
# wire overlap the rest instead of trailing it (talespin: ~2 min each)
HEAVY = ("talespin", "tragedy")


def one(task):
    """One gate of one unit, in a worker process of its own (metispy's work is
    pure Python: threads would serialize it)."""
    u, gate, py, update = task
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
