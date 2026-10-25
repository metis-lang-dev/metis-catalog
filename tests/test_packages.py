"""The one CI check over every domain package (catalog-entry step 2): every
manifest carries only the package's keys (the loader refuses any other),
its files are there, and its generated intent files are what its
intent.yaml makes (python -m metis.intents check), and its own cases pass
through the interface stub (cases/*.yaml: the package's program alone, its
manifest's interface closed by the cases' facts; metis-lang spec/15 §10.4)."""
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from metis.catalog import manifests as mc  # noqa: E402  (the loader: metispy's since metis-packages)

PACKAGES = mc.domains(ROOT)          # raises ManifestError on a key a package does not carry


def test_every_package_loads():
    assert {"dog", "plant", "kitchen", "kitchen_shared"} <= {d.name for d in PACKAGES}


@pytest.mark.parametrize("d", [d for d in PACKAGES if d.intent.get("spec")], ids=lambda d: d.name)
def test_the_generated_intent_files_are_current(d):
    r = subprocess.run([sys.executable, "-m", "metis.intents", "check", d.name], cwd=ROOT,
                       capture_output=True, text=True, env=dict(os.environ, METIS_CATALOG=str(ROOT)))
    assert r.returncode == 0, r.stdout + r.stderr
    assert {"grammar", "prompt", "examples"} <= set(d.intent), d.name


@pytest.mark.parametrize("d", PACKAGES, ids=lambda d: d.name)
def test_the_packages_files_are_there(d):
    # a pkg.mod:path whose top-level package is not installed here (the
    # kitchen pair's scenes live in metispy): skipped; any other serves
    # error — a typo'd module with the package installed — fails
    tops = {str(x).partition(":")[0].split(".")[0] for x in d.manifest.get("serves") or []
            if ":" in str(x) and not str(x).partition(":")[0].endswith(".llp")}
    missing = sorted(t for t in tops if importlib.util.find_spec(t) is None)
    if missing:
        pytest.skip(f"{d.name} serves from {', '.join(missing)}, not installed here")
    for p in ([d.program] if d.manifest.get("program") else []) + d.extensions() + d.serves():
        assert p.is_file(), (d.name, p)


@pytest.mark.parametrize("d", [d for d in PACKAGES if (d.dir / "cases").is_dir()], ids=lambda d: d.name)
def test_the_packages_own_cases_pass_through_the_interface_stub(d):
    # the specialist alone (no director, no world): metispy's one generic stub, driven by the manifest
    from metis.catalog import stub
    rs = stub.run_package(d)
    assert rs, "%s: cases/ holds no case" % d.name
    assert all(r.passed for r in rs), stub.render(rs)
