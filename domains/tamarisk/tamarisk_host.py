"""Tamarisk's host (rddl-worlds s-242c7c3f step 3): the IPPC 2014 Tamarisk gym,
instance 1, through the catalog's RDDL world host (tools/rddl_host.py), as an
OBSERVING world: the program does not act. Each beat is one rddl_recorder
transition: the program at the gym's state (tamarisk_at, native_at and their
not_ negatives), the gym stepped by pyRDDLGym's random agent seeded per episode
(the agent the program was formalized from), the action's eradicate/restore and
a tick handed to the program, whose snap/rouse/act/fate/write cycle then
computes the next state; the watch reads it once the cycle has settled.

The twelve weight ports are bound prior-flat (0.5), as the experiment's
tamarisk_plugin.py binds them; the fitted notch (tamarisk.notch.json, the
program's #notch) rides on top unchanged.

Baseline (rddl-worlds step 3, ruling A): the program's #init step runs; at the
next tick its stage pipeline is not restarted at `snap` (the domain agent does
not do that yet), so the program stays in its last stage and the gym's next
state is a surprise. That is the furthest stage, recorded as such."""
import sys
from pathlib import Path

for _d in Path(__file__).resolve().parents:
    if (_d / "tools" / "rddl_host.py").exists():
        sys.path.insert(0, str(_d / "tools"))
        break
from rddl_host import RddlHost  # noqa: E402

PROBLEM, INSTANCE, SEED = "Tamarisk_MDP_ippc2014", "1", 1
PAIRS = ()
PORTS = ("pdown", "pup", "pcompete", "ptcomp", "pncomp", "perad",
         "ptdie", "pndie", "ptborn", "psib", "prest", "pnborn")
TRANSIENT = ("tick", "eradicate", "restore", "old_t", "old_nt", "old_n", "old_nn", "tdue", "ndue", "open",
             "erad", "noerad", "rest", "norest", "scan", "set_t", "set_nt", "set_n", "set_nn")


def flips(atom):
    return None


def words(atom, names=None):
    return None


def flat(args, counts, host):
    return 0.5                                   # prior-flat: the notch fits it (tamarisk_plugin.py)


def make(case):
    return RddlHost(case, problem=PROBLEM, instance=INSTANCE, seed=SEED, policy="random", negatives=True,
                    tick_token=True, transient=TRANSIENT, weights={p: flat for p in PORTS})
