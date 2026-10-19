"""Wildfire's host (rddl-worlds s-242c7c3f step 3): the IPPC 2014 Wildfire gym,
instance 1, through the catalog's RDDL world host (tools/rddl_host.py), as an
OBSERVING world: the program does not act. Each beat is one rddl_recorder
transition: the program at the gym's state (burning, out_of_fuel and their
not_ negatives), the gym stepped by pyRDDLGym's random agent seeded per episode
(the agent the program was formalized from), the action's put_out/cut_out and
a tick handed to the program, whose open/count/act/screen/ignite cycle then
computes the next state; the watch reads it once the cycle has settled.

The manifest's clock {lockstep: true} (rddl-watch s-cfe94dca): the watch
reads once per pass, when it ends quiet in `ignite`, and the beat's input
restarts the pipeline at `open` (step 3 stopped there: the second step
stalled in `ignite`). A pass is past the exact filter's state budget, so it
is priced on the declared sampled tier.

The weight port pign is bound prior-flat (0.5 for every neighbor count), as
the experiment's wildfire_plugin.py binds it; the fitted notch
(wildfire.notch.json, the program's #notch) rides on top unchanged."""
import sys
from pathlib import Path

for _d in Path(__file__).resolve().parents:
    if (_d / "tools" / "rddl_host.py").exists():
        sys.path.insert(0, str(_d / "tools"))
        break
from rddl_host import RddlHost  # noqa: E402

PROBLEM, INSTANCE, SEED = "Wildfire_MDP_ippc2014", "1", 1
PAIRS = ()
TRANSIENT = ("tick", "walk", "cell", "fresh", "held", "tally", "scan", "put_out", "cut_out")


def flips(atom):
    return None


def words(atom, names=None):
    return None


def pign(args, counts, host):
    return 0.5                                   # prior-flat: the notch fits it (wildfire_plugin.py)


def make(case):
    return RddlHost(case, problem=PROBLEM, instance=INSTANCE, seed=SEED, policy="random", negatives=True,
                    tick_token=True, transient=TRANSIENT, weights={"pign": pign})
