"""CrossingTraffic's host (rddl-worlds s-242c7c3f): the IPPC 2011
CrossingTraffic gym, instance 1, through the catalog's RDDL world host
(tools/rddl_host.py).

- The gym's `robot-at___x3__y1` is the program's `rob(x3_y1)`, its
  `obstacle-at___x2__y2` the program's `o(x2_y2)`. Derived: `e(C)` on the
  obstacle rows (the cell is free: the program's complement of o, which the
  gym does not have), and `dead` (the robot is nowhere: the gym's robot
  vanished).
- One move-stage rule fires per epoch, and it is the epoch's gym step: a
  move rule (fmv_north, fst_north, mv_north alike) is `move-north` (against
  the edge the gym leaves the robot where it is, as fst_ does); the epoch's
  other rules (str the stay, dier the death, atgoal, deadtick) are the step
  with no action. The program's tick never quiesces (its `sm` link opens the
  next epoch), so the host's tick would never come to step the gym: the
  epoch's rule steps it.
- The weight ports obs, go, stayw, fgo, fstayw are metispy's binding of
  this program (metis.domains.xtraffic.model.XTrafficModel.bindings) as it
  is, over the instance's topology read from the gym's own non-fluents
  (EAST, NORTH, MIN/MAX-YPOS, GOAL; obs's edge rate is INPUT-RATE, read
  live). Its policy table is empty: the base policy (uniform over the
  goal-ward moves, stay where none is). Not fitted (no notch)."""
import sys
from pathlib import Path

for _d in Path(__file__).resolve().parents:
    if (_d / "tools" / "rddl_host.py").exists():
        sys.path.insert(0, str(_d / "tools"))
        break
from rddl_host import RddlHost  # noqa: E402

PROBLEM, INSTANCE, SEED = "CrossingTraffic_MDP_ippc2011", "1", 1
DIRS = ("north", "south", "east", "west")

# a world without intents: no pairs, no words (the domain agent's generic host faces)
PAIRS = ()


def flips(atom):
    return None


def words(atom, names=None):
    return None


def cell(key):
    """`robot-at___x3__y1` -> `x3_y1`."""
    return "_".join(key.split("___")[1].split("__"))


def atom(key):
    if key.startswith("robot-at___"):
        return "rob(%s)" % cell(key)
    if key.startswith("obstacle-at___"):
        return "o(%s)" % cell(key)
    return None


def action_of(name, args):
    base = name.split("[")[0]
    for d in DIRS:
        if base in ("fmv_" + d, "fst_" + d, "mv_" + d):
            return {"move-" + d: True}
    if base in ("str", "dier", "atgoal", "deadtick"):
        return {}                                # the epoch's step with no action
    return None


def _chain(host, name):
    """The gym's EAST / NORTH successor pairs as an ordered chain."""
    nxt = dict(tuple(k.split("___")[1].split("__")) for k, v in host.nonfluents.items()
               if k.startswith(name + "___") and v)
    out = [(set(nxt) - set(nxt.values())).pop()]
    while out[-1] in nxt:
        out.append(nxt[out[-1]])
    return out


def topology(host):
    """metispy's Topology of the gym's instance, as its rddl_adapter.load reads it."""
    from metis.domains.xtraffic.model import Topology
    xs, ys = _chain(host, "EAST"), _chain(host, "NORTH")
    nf = host.nonfluents
    cells = ["%s_%s" % (x, y) for x in xs for y in ys]
    adj = {}
    for xi, x in enumerate(xs):
        for yi, y in enumerate(ys):
            c = "%s_%s" % (x, y)
            if yi + 1 < len(ys):
                adj[(c, "north")] = "%s_%s" % (x, ys[yi + 1])
            if yi > 0:
                adj[(c, "south")] = "%s_%s" % (x, ys[yi - 1])
            if xi + 1 < len(xs):
                adj[(c, "east")] = "%s_%s" % (xs[xi + 1], y)
            if xi > 0:
                adj[(c, "west")] = "%s_%s" % (xs[xi - 1], y)
    rows = [y for y in ys if not nf.get("MIN-YPOS___" + y) and not nf.get("MAX-YPOS___" + y)]
    ocells, east_of = [], {}
    for y in rows:
        row = ["%s_%s" % (x, y) for x in xs]
        ocells += row
        east_of.update(zip(row, row[1:]))
    goal = next(cell(k) for k, v in nf.items() if k.startswith("GOAL___") and v)
    return Topology(cells, adj, ocells, east_of, goal=goal, input_rate=float(nf["INPUT-RATE"]),
                    horizon=host.horizon)


def _bindings(host):
    """metispy's bindings of the program, once per host (an empty policy table: the base policy)."""
    b = host.__dict__.get("_xt")
    if b is None:
        from metis.domains.xtraffic.model import XTrafficModel
        m = XTrafficModel.__new__(XTrafficModel)        # the bindings need only the topology and the table
        m.topo, m.policy = topology(host), {}
        b = host._xt = (m, m.bindings())
    return b


def extra(host):
    m, _ = _bindings(host)
    r = {"dead": 0 if any(k.startswith("robot-at___") for k in host.obs) else 1}
    for c in m.topo.ocells:
        x, y = c.split("_")
        r["e(%s)" % c] = 0 if "obstacle-at___%s__%s" % (x, y) in host.obs else 1
    return r


def port(name):
    def fn(args, counts, host):
        m, b = _bindings(host)
        m.topo.input_rate = float(host.nonfluents["INPUT-RATE"])   # a `nonfluent` world line holds
        return b[name](tuple(args), {a: n for a, n in counts.items() if n})
    return fn


def make(case):
    return RddlHost(case, problem=PROBLEM, instance=INSTANCE, seed=SEED, atom=atom, action_of=action_of,
                    extra=extra, weights={p: port(p) for p in ("obs", "go", "stayw", "fgo", "fstayw")})
