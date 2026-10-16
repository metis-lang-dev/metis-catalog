"""metis-catalog cross-toolchain gate (CI.md): every non-exempt .llp
must compile under metispy too — metisc (ci/diagnose.sh) and the
python referee must AGREE that it is clean. Needs metispy importable."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _compile(p):
    from metis.lang import compile_catalog, parse, resolve_includes
    return compile_catalog(resolve_includes(parse(p.read_text(), file=str(p)),
                                            p.parent))


def _base(p):
    """A domain package's extension (domains/*/extensions/*.llp) compiles
    with the program it extends, the manifest's program: — the rule
    ci/diagnose.sh gives metisc as --base. Anything else: None."""
    rel = p.relative_to(ROOT).parts
    if not (len(rel) == 4 and rel[0] == "domains" and rel[2] == "extensions"):
        return None
    import yaml
    pkg = p.parent.parent
    prog = (yaml.safe_load((pkg / "domain.yaml").read_text()) or {}).get("program")
    if not prog or not (pkg / prog).is_file():
        raise ValueError(f"an extension of {pkg.name}, whose manifest names "
                         "no program to compile it with")
    return pkg / prog


def main() -> int:
    from metis.lang import compile_catalog, parse, resolve_includes
    exempt = {l.split()[0] for l in (ROOT / "ci/diag-exempt.txt")
              .read_text().splitlines() if l.strip() and not l.startswith("#")}
    files = subprocess.run(["git", "ls-files", "*.llp"], cwd=ROOT,
                           capture_output=True, text=True,
                           check=True).stdout.split()
    bad = 0
    for f in files:
        if f in exempt:
            continue
        p = ROOT / f
        try:
            base = _base(p)                 # an extension: with its program
            compile_catalog(resolve_includes(parse(p.read_text(), file=f),
                                             p.parent),
                            base and _compile(base))
            print(f"ok   {f}" + (f" (with {base.relative_to(ROOT)})"
                                 if base else ""))
        except Exception as e:                      # noqa: BLE001
            bad += 1
            print(f"FAIL {f}: metispy disagrees with metisc's clean "
                  f"verdict — {type(e).__name__}: {str(e)[:300]}")
    print("CROSS-CHECK GREEN" if not bad else f"{bad} disagreement(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
