"""This cook's host: the shared-pot kitchen's (../pot_host.py) for this package's cook (cook.json). The module is
loaded once per process (sys.modules), so both cooks' hosts step the ONE kitchen."""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
_PATH = os.path.realpath(os.path.join(HERE, "..", "pot_host.py"))
_NAME = "kitchen_pot_host_%x" % (hash(_PATH) & 0xffffffff)
if _NAME not in sys.modules:
    _spec = importlib.util.spec_from_file_location(_NAME, _PATH)
    _m = importlib.util.module_from_spec(_spec)
    sys.modules[_NAME] = _m
    _spec.loader.exec_module(_m)
_mod = sys.modules[_NAME]


def make(case=None):
    return _mod.make(case, package_dir=HERE)
