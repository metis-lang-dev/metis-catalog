"""Navigation's host (rddl-worlds s-242c7c3f): the IPPC 2011 Navigation gym,
instance 1, through the catalog's RDDL world host (tools/rddl_host.py).

- The gym's `robot-at___x6__y12` is the program's `at(x6_y12)`. `dead` is
  derived: the robot is nowhere (the gym's robot vanished).
- A fired move rule is the gym's action: mv_north and die_north are both
  `move-north`. The gym, not the program, decides whether the robot arrives;
  the watch scores the program's choice against the gym's answer.
- The weight ports go/die are bound from the instance's own non-fluents, as
  metispy's nav model reads them: go(C,C2) = 1 - P(C2), die(C,C2) = P(C2),
  every direction alike; 0 at the goal, which absorbs. They are the
  instance's parameters, not fitted (no notch)."""
import sys
from pathlib import Path

for _d in Path(__file__).resolve().parents:
    if (_d / "tools" / "rddl_host.py").exists():
        sys.path.insert(0, str(_d / "tools"))
        break
from rddl_host import RddlHost  # noqa: E402

PROBLEM, INSTANCE, SEED = "Navigation_MDP_ippc2011", "1", 1

# a world without intents: no pairs, no words (the domain agent's generic host faces)
PAIRS = ()


def flips(atom):
    return None


def words(atom, names=None):
    return None


def cell(key):
    """`robot-at___x6__y12` -> `x6_y12`."""
    return "_".join(key.split("___")[1].split("__"))


def atom(key):
    return "at(%s)" % cell(key) if key.startswith("robot-at___") else None


def action_of(name, args):
    base = name.split("[")[0]
    for d in ("north", "south", "east", "west"):
        if base in ("mv_" + d, "die_" + d):
            return {"move-" + d: True}
    return None


def dead(host):
    return {"dead": 0 if any(k.startswith("robot-at___") for k in host.obs) else 1}


def _p(host, c):
    x, y = c.split("_")
    return float(host.nonfluents.get("P___%s__%s" % (x, y), 0.0))


def _goal(host, c):
    x, y = c.split("_")
    return bool(host.nonfluents.get("GOAL___%s__%s" % (x, y)))


def go(args, counts, host):
    c, c2 = args
    return 0.0 if _goal(host, c) else 1.0 - _p(host, c2)


def die(args, counts, host):
    c, c2 = args
    return 0.0 if _goal(host, c) else _p(host, c2)


def make(case):
    return RddlHost(case, problem=PROBLEM, instance=INSTANCE, seed=SEED, atom=atom, action_of=action_of,
                    extra=dead, weights={"go": go, "die": die})
