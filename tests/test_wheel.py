"""The wheel's package list (pi-release s-8e13f6a8): pyproject.toml's
package-data for metis_catalog.domains names every tracked package outside
domains/ceptre/ (ACSL, not this grant) and nothing else, and
tools/smoke_wheel.sh's PACKAGES is the same set; root() is the checkout
here, the package directory once installed."""
import re
import subprocess
import tomllib
from pathlib import Path

import metis_catalog as mc

ROOT = Path(__file__).resolve().parents[1]


def tracked():
    out = subprocess.run(["git", "ls-files", "domains/*/domain.yaml"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout.split()
    return {p.split("/")[1] for p in out if not p.startswith("domains/ceptre/")}


def test_package_data_is_the_tracked_packages():
    pp = tomllib.loads((ROOT / "pyproject.toml").read_text())
    globs = pp["tool"]["setuptools"]["package-data"]["metis_catalog.domains"]
    assert all(g.endswith("/**/*") for g in globs), globs
    assert {g.split("/")[0] for g in globs} == tracked()


def test_smoke_lists_the_same_packages():
    text = (ROOT / "tools" / "smoke_wheel.sh").read_text()
    block = re.search(r"PACKAGES = \{(.*?)\}", text, re.S).group(1)
    assert set(re.findall(r'"(\w+)"', block)) == tracked()


def test_root_is_the_checkout(monkeypatch):
    monkeypatch.delenv("METIS_CATALOG", raising=False)
    assert mc.root() == ROOT
