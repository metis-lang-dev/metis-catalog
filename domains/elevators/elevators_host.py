"""Elevators' host (rddl-worlds s-242c7c3f step 3): the IPPC 2011 Elevators
gym, instance 8, through the catalog's RDDL world host (tools/rddl_host.py),
in nav mode: the program's rules choose the moves.

- Instance 8 is the one whose objects are the program's: elevators e0 e1,
  floors f0..f4 (instance 9 has the same objects, other ARRIVE-PARAMs).
- The gym's fluents are the program's atoms: elevator-at-floor(e,f) is
  at(e,f), elevator-closed(e) is closed(e), elevator-dir-up(e) is
  heading(e,up), person-waiting-up(f) / -down(f) are waiting(f,top) /
  waiting(f,bottom), person-in-elevator-going-up(e) / -down(e) are
  riding(e,top) / riding(e,bottom). Derived (the complements the gym keeps
  as one boolean): open(e) = not closed, heading(e,down) = not dir-up, and
  free(f,x) = not waiting(f,x) for the eight arrival slots the program
  declares (#init: f0 top, f1..f3 both, f4 bottom). `delivered` has no gym
  fluent: not observed.
- A fired rule that is an elevator's action is the gym's action: move is
  move-current-dir(e), open_same/open_turn are open-door-going-up/-down(e)
  by the heading they leave, close is close-door(e). noop, the arrivals,
  board and alight are not actions: the gym does them in its own step.
- No weight ports: the program declares none (its weights are literals), so
  none is bound."""
import sys
from pathlib import Path

for _d in Path(__file__).resolve().parents:
    if (_d / "tools" / "rddl_host.py").exists():
        sys.path.insert(0, str(_d / "tools"))
        break
from rddl_host import RddlHost  # noqa: E402

PROBLEM, INSTANCE, SEED = "Elevators_MDP_ippc2011", "8", 1

# a world without intents: no pairs, no words (the domain agent's generic host faces)
PAIRS = ()

ELEVATORS = ("e0", "e1")
SLOTS = (("f0", "top"), ("f1", "top"), ("f1", "bottom"), ("f2", "top"), ("f2", "bottom"),
         ("f3", "top"), ("f3", "bottom"), ("f4", "bottom"))       # the program's free(F,X) at #init


def flips(atom):
    return None


def words(atom, names=None):
    return None


def atom(key):
    name, _, rest = key.partition("___")
    args = rest.split("__") if rest else []
    if name == "elevator-at-floor":
        return "at(%s,%s)" % tuple(args)
    if name == "elevator-closed":
        return "closed(%s)" % args[0]
    if name == "elevator-dir-up":
        return "heading(%s,up)" % args[0]
    if name == "person-waiting-up":
        return "waiting(%s,top)" % args[0]
    if name == "person-waiting-down":
        return "waiting(%s,bottom)" % args[0]
    if name == "person-in-elevator-going-up":
        return "riding(%s,top)" % args[0]
    if name == "person-in-elevator-going-down":
        return "riding(%s,bottom)" % args[0]
    return None


def derived(host):
    obs = host.obs
    r = {}
    for e in ELEVATORS:
        r["open(%s)" % e] = 0 if "elevator-closed___" + e in obs else 1
        r["heading(%s,down)" % e] = 0 if "elevator-dir-up___" + e in obs else 1
    for f, x in SLOTS:
        key = ("person-waiting-up___" if x == "top" else "person-waiting-down___") + f
        r["free(%s,%s)" % (f, x)] = 0 if key in obs else 1
    return r


def _binding(name):
    """`move[E=e0,F=f0,D=up,G=f1]` -> {"E": "e0", ...}."""
    if "[" not in name:
        return {}
    return dict(kv.split("=", 1) for kv in name.split("[", 1)[1].rstrip("]").split(",") if "=" in kv)


def action_of(name, args):
    rule, b = name.split("[")[0], _binding(name)
    e = b.get("E")
    if rule == "move":
        return {"move-current-dir___" + e: True}
    if rule == "open_same":
        return {"open-door-going-%s___%s" % (b["D"], e): True}
    if rule == "open_turn":
        return {"open-door-going-%s___%s" % (b["R"], e): True}
    if rule == "close":
        return {"close-door___" + e: True}
    return None


def make(case):
    return RddlHost(case, problem=PROBLEM, instance=INSTANCE, seed=SEED, atom=atom, action_of=action_of,
                    extra=derived)
