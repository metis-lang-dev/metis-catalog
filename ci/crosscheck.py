"""metis-catalog cross-toolchain gate (CI.md): every non-exempt .llp
must compile under metispy too — metisc (ci/diagnose.sh) and the
python referee must AGREE that it is clean. Needs metispy importable."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _manifest(p):
    """The package's domain.yaml when it has a levels: block and P is its program or an extension of it — the rule
    ci/diagnose.sh gives metisc as --manifest: the level declarations are generated from it (metis-lang spec/16
    amendment 1). Anything else: None."""
    import re
    rel = p.relative_to(ROOT).parts
    if len(rel) == 4 and rel[0] == "domains" and rel[2] == "extensions":
        pkg = p.parent.parent
    elif len(rel) == 3 and rel[0] == "domains":
        pkg = p.parent
        m = re.search(r"^program:[ \t]*([^\s#]+)", (pkg / "domain.yaml").read_text(), re.M) \
            if (pkg / "domain.yaml").is_file() else None
        if not m or m.group(1) != p.name:
            return None
    else:
        return None
    man = pkg / "domain.yaml"
    return man if man.is_file() and re.search(r"^levels:", man.read_text(), re.M) else None


def _program(p, manifest=None):
    """P's AST, includes resolved, with its manifest's generated level declarations."""
    from metis.lang import parse, resolve_includes
    cat = resolve_includes(parse(p.read_text(), file=str(p)), p.parent)
    if manifest is not None:
        from metis.lang.levels import with_levels
        cat = with_levels(cat, manifest)
    return cat


def _compile(p, manifest=None):
    from metis.lang import compile_catalog
    return compile_catalog(_program(p, manifest))


def _base(p):
    """A domain package's extension (domains/*/extensions/*.llp) compiles
    with the program it extends, the manifest's program: — the rule
    ci/diagnose.sh gives metisc as --base. Anything else: None."""
    rel = p.relative_to(ROOT).parts
    if not (len(rel) == 4 and rel[0] == "domains" and rel[2] == "extensions"):
        return None
    import re                       # the manifest's program: line, as diagnose.sh's sed
    pkg = p.parent.parent           # reads it (this step's python has no pyyaml)
    m = re.search(r"^program:[ \t]*([^\s#]+)", (pkg / "domain.yaml").read_text(), re.M)
    prog = m and m.group(1)
    if not prog or not (pkg / prog).is_file():
        raise ValueError(f"an extension of {pkg.name}, whose manifest names "
                         "no program to compile it with")
    return pkg / prog


def main() -> int:
    from metis.lang import compile_catalog
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
            man = _manifest(p)              # levels: the program's (the base's, for an extension)
            compile_catalog(_program(p, None if base else man),
                            base and _compile(base, man))
            print(f"ok   {f}" + (f" (with {base.relative_to(ROOT)})"
                                 if base else "") + (f" (levels from {man.relative_to(ROOT)})" if man else ""))
        except Exception as e:                      # noqa: BLE001
            bad += 1
            print(f"FAIL {f}: metispy disagrees with metisc's clean "
                  f"verdict — {type(e).__name__}: {str(e)[:300]}")
    print("CROSS-CHECK GREEN" if not bad else f"{bad} disagreement(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
