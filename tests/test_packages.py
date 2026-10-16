"""The one CI check over every domain package (catalog-entry step 2): every
manifest carries only the package's keys (the loader refuses any other),
its files are there, and its generated intent files are what its
intent.yaml makes (tools/intents.py check)."""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import metis_catalog as mc  # noqa: E402

PACKAGES = mc.domains(ROOT)          # raises ManifestError on a key a package does not carry


def test_every_package_loads():
    assert {"dog", "plant", "kitchen", "kitchen_shared"} <= {d.name for d in PACKAGES}


@pytest.mark.parametrize("d", [d for d in PACKAGES if d.intent.get("spec")], ids=lambda d: d.name)
def test_the_generated_intent_files_are_current(d):
    r = subprocess.run([sys.executable, str(ROOT / "tools/intents.py"), "check", d.name], cwd=ROOT,
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert {"grammar", "prompt", "examples"} <= set(d.intent), d.name


@pytest.mark.parametrize("d", PACKAGES, ids=lambda d: d.name)
def test_the_packages_files_are_there(d):
    try:
        served = d.serves()
    except ValueError as e:         # a pkg.mod:path whose package is not installed
        pytest.skip(f"{d.name} serves from a package not installed here: {e}")
    for p in ([d.program] if d.manifest.get("program") else []) + d.extensions() + served:
        assert p.is_file(), (d.name, p)
