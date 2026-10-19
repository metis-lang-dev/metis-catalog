"""Game of Life's host (rddl-worlds s-242c7c3f): the IPPC 2011 Game of Life
gym, instance 1, through the catalog's RDDL world host (tools/rddl_host.py).

- The gym's `alive___x1__y2` is the program's `a(x1__y2)`. `d(x1__y2)` is
  derived: the cell is not alive (the program holds one of a/d per cell).
- No rule of the program is a gym action: its `force(C)` (the gym's
  `set___x1__y2`) is an input atom no rule produces; metispy chose it code-side
  (rddl_adapter.agent_metis, greedy_set). So every gym step is the noop, and
  the host takes it as an observing world does (`policy="noop"`, rddl-watch
  s-cfe94dca): each beat the program is brought to the gym's state, the gym
  steps, and the program's mark/update/sweep pass computes the step; the
  manifest's clock {lockstep: true} has the watch read once per pass, at
  its wrap (step 3 read every row, and the mark pass's first row surprised).
- The weight port life(C) is metispy's own binding, model.life_bindings, as it
  is, over the instance's own non-fluents (as rddl_adapter.load reads them):
  the neighbors from NEIGHBOR, the noise from NOISE-PROB. Not fitted (no notch)."""
import sys
from pathlib import Path

for _d in Path(__file__).resolve().parents:
    if (_d / "tools" / "rddl_host.py").exists():
        sys.path.insert(0, str(_d / "tools"))
        break
from rddl_host import RddlHost  # noqa: E402

PROBLEM, INSTANCE, SEED = "GameOfLife_MDP_ippc2011", "1", 1

# a world without intents: no pairs, no words (the domain agent's generic host faces)
PAIRS = ()


def flips(atom):
    return None


def words(atom, names=None):
    return None


def cell(key):
    """`alive___x1__y2` -> `x1__y2` (rddl_adapter's cell name)."""
    return key.split("___")[1]


def atom(key):
    return "a(%s)" % cell(key) if key.startswith("alive___") else None


def action_of(name, args):
    return None


def dead(host):
    return {"d(%s)" % c: 0 if "alive___" + c in host.obs else 1 for c in _cells(host)}


def _cells(host):
    return sorted(cell(k) for k in host.observed.values())


def _instance(host):
    """rddl_adapter.load's reading of the instance: neighbors and noise per cell."""
    nf = host.nonfluents
    nbrs = {c: [] for c in _cells(host)}
    for k, v in nf.items():
        if k.startswith("NEIGHBOR___") and v:
            x1, y1, x2, y2 = k.split("___")[1].split("__")
            nbrs["%s__%s" % (x1, y1)].append("%s__%s" % (x2, y2))
    noise = {c: float(nf.get("NOISE-PROB___" + c, nf.get("NOISE-PROB", 0.1))) for c in nbrs}
    return nbrs, noise


def life(args, counts, host):
    """metispy's life_bindings over the instance as it is now (rebuilt when a
    `nonfluent` world line changes a NEIGHBOR or NOISE-PROB value)."""
    nf = host.nonfluents
    if not hasattr(host, "_life_keys"):
        host._life_keys = sorted(k for k in nf if k.startswith(("NEIGHBOR", "NOISE-PROB")))
    key = tuple(nf[k] for k in host._life_keys)
    if getattr(host, "_life", (None,))[0] != key:
        from metis.domains.gol.model import life_bindings
        host._life = (key, life_bindings(*_instance(host))["life"])
    return host._life[1](args, counts)


def make(case):
    return RddlHost(case, problem=PROBLEM, instance=INSTANCE, seed=SEED, atom=atom, action_of=action_of,
                    extra=dead, weights={"life": life}, policy="noop")
