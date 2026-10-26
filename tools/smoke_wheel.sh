#!/usr/bin/env bash
# smoke_wheel.sh DIST — the built wheel in DIST installed into a fresh venv
# outside any checkout, with metispy from PyPI, and run there (pi-release
# s-8e13f6a8): the loader imports from site-packages and its root() is the
# wheel's own catalog, every package of the packages job's set is in it (and
# domains/ceptre/ is not), each served file is there, `python -m metis_catalog
# list` answers, the intent generator and the RDDL host are found from a
# package, no file holds `/home/` or the host's name, and every domain builds
# its bundle BY NAME through metispy.
# CI (ci.yml) and the release (publish.yml) run it.
set -euo pipefail
DIST=$(cd "$1" && pwd)
W=$(mktemp -d)
trap 'rm -r "$W"' EXIT
"${PYTHON:-python3}" -m venv "$W/venv"
"$W/venv/bin/pip" install -q "$DIST"/*.whl "${METISPY:-metispy}"
cd "$W"                                   # no checkout on the path
env -u METIS_CATALOG -u PYTHONPATH "$W/venv/bin/python" - <<'PY'
import os
import subprocess
import sys
from pathlib import Path

import metis_catalog as mc

PACKAGES = {"bridge", "bridge_decl", "dog", "elevators", "gol", "hanoi", "kitchen", "kitchen_pot", "kitchen_shared",
            "nav", "plant", "sysadmin", "tamarisk", "wgc", "wildfire", "xtraffic"}
r = mc.root()
assert "site-packages" in mc.__file__ and r == Path(mc.__file__).resolve().parent, (mc.__file__, r)
names = {d.dir.relative_to(r / "domains").parts[0] for d in mc.domains()}   # the packages' top directories (kitchen_pot holds three domains)
assert names == PACKAGES, sorted(names ^ PACKAGES)
assert not (r / "domains" / "ceptre").exists(), "domains/ceptre/ (ACSL) is in the wheel"
assert not list((r / "domains").rglob("records")), "a package's records/ is in the wheel"
for d in mc.domains():
    for f in d.serves():
        assert f.is_file(), (d.name, f)
assert (r / "tools" / "intents.py").is_file() and (r / "tools" / "rddl_host.py").is_file()
host = os.uname().nodename                             # no path or name of the host that built it
for f in r.rglob("*"):
    if f.is_file() and "__pycache__" not in f.parts:
        t = f.read_bytes()
        assert b"/home/" not in t and (len(host) < 4 or host.encode() not in t), ("a host path or name in", f.relative_to(r))
out = Path.cwd() / "bundles"                          # the venv's scratch dir, removed on exit
built = sorted(d.name for d in mc.domains() if not d.partner_of)   # each domain (kitchen_pot: its three); a partner never alone
for name in built:
    subprocess.run([sys.executable, "-m", "metis.kernel.artifact", name, "-o", str(out / name)],
                   check=True, stdout=subprocess.DEVNULL)
    assert (out / name / "ground.wire").is_file(), name
print("smoke: metis_catalog %s from %s, %d packages, %d bundles"
      % (mc.__version__, r, len(names), len(built)))
PY
env -u METIS_CATALOG "$W/venv/bin/python" -m metis_catalog list --domains > /dev/null
echo "SMOKE GREEN"
