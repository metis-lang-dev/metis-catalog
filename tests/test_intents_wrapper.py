"""tools/intents.py is a wrapper over metispy's metis.intents for one release (metis-packages
s-65778b98): the generator and its tests live in metispy (tests/catalog/test_intents_gen.py);
here, that the old path still runs the same CLI on this checkout."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_the_old_path_runs_metis_intents_on_this_checkout():
    old = subprocess.run([sys.executable, str(ROOT / "tools/intents.py"), "check", "dog"], cwd="/", capture_output=True, text=True)
    new = subprocess.run([sys.executable, "-m", "metis.intents", "check", "dog"], cwd=ROOT, capture_output=True, text=True,
                         env=dict(os.environ, METIS_CATALOG=str(ROOT)))
    assert (old.returncode, old.stdout) == (new.returncode, new.stdout) == (0, ""), old.stdout + old.stderr + new.stderr
