"""Tower of Hanoi's host (rddl-worlds s-242c7c3f): rddlrepository's
TowerOfHanoi_arcade gym, instance 0 (its only instance), through the
catalog's RDDL world host (tools/rddl_host.py).

- The gym's state is `disk-on-rod___d1__r1` (bool) and `disk-order___d1`
  (int: 0 at the rod's base, higher is higher up). The program's view,
  on(spot,spot) and clear(spot), is derived from both (`extra`): on a rod,
  the disks sorted by order; the lowest rests on the rod, each other on the
  one below it, the highest is clear; a rod with no disk is clear.
  No gym fluent is an observed atom by itself (`atom` is None for all).
- The instance has 4 disks (d1..d4), the program 3 (d1..d3). d4, the
  largest, is not in the program: the host reads it as part of the rod it
  stands on (a disk on d4 is on that rod; d4 clear is the rod clear). No
  program rule moves d4 and nothing else does, so d4 stays on r1, and the
  gym restricted to d1..d3 is the program's 3-disk puzzle. The gym's reward
  (all 4 disks on r3) is therefore out of the program's reach.
- A fired mv(D,P,E) is the gym's `move___D__R`, R the rod E is (a rod) or
  stands on (a disk, read from the gym's state as the move is sent).
  `done` is no action.
- No weight ports: the program declares none (its mv is uniform)."""
import sys
from pathlib import Path

for _d in Path(__file__).resolve().parents:
    if (_d / "tools" / "rddl_host.py").exists():
        sys.path.insert(0, str(_d / "tools"))
        break
from rddl_host import RddlHost  # noqa: E402

PROBLEM, INSTANCE, SEED = "TowerOfHanoi_arcade", "0", 1

DISKS = ("d1", "d2", "d3")          # the program's disks
RODS = ("r1", "r2", "r3")
SPOTS = DISKS + RODS

# a world without intents: no pairs, no words (the domain agent's generic host faces)
PAIRS = ()


def flips(atom):
    return None


def words(atom, names=None):
    return None


def atom(key):
    return None                     # every reading is derived (`view`)


def stacks(host):
    """{rod: [disk, ...] base first}, every gym disk (d4 included)."""
    out = {r: [] for r in RODS}
    for k in host.obs:
        if k.startswith("disk-on-rod___"):
            d, r = k.split("___")[1].split("__")
            out.setdefault(r, []).append(d)
    for r in out:
        out[r].sort(key=lambda d: host.values.get("disk-order___" + d, 0))
    return out


def surface(x, rod):
    """A spot of the program: a disk it has, else the rod (d4 as its rod's base)."""
    return x if x in SPOTS else rod


def view(host):
    """The program's on/clear over its own disks and spots."""
    r = {"on(%s,%s)" % (d, s): 0 for d in DISKS for s in SPOTS if s != d}
    r.update({"clear(%s)" % s: 0 for s in SPOTS})
    for rod, ds in stacks(host).items():
        below = rod
        for d in ds:
            if d in DISKS:
                r["on(%s,%s)" % (d, below)] = 1
            below = surface(d, rod)
        r["clear(%s)" % below] = 1
    return r


def make(case):
    host = None

    def action_of(name, args):
        if not name.startswith("mv["):
            return None
        b = dict(kv.split("=", 1) for kv in name[3:-1].split(","))
        e = b["E"]
        rod = e if e in RODS else next((r for r, ds in stacks(host).items() if e in ds), None)
        return {"move___%s__%s" % (b["D"], rod): True} if rod else None

    host = RddlHost(case, problem=PROBLEM, instance=INSTANCE, seed=SEED, atom=atom, action_of=action_of,
                    extra=view)
    return host
