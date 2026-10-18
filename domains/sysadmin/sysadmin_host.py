"""SysAdmin's host (rddl-worlds s-242c7c3f): the IPPC 2011 SysAdmin gym,
instance 1, through the catalog's RDDL world host (tools/rddl_host.py).

- The program is the 2-computer fixture sysadmin.llp (catalog sysadmin2; computers a, b,
  adj(a,b), adj(b,a)); every gym instance has 10 computers or more. The
  program's a and b are the gym's c6 and c8: in instance 1 they are the one
  pair connected both ways (CONNECTED(c6,c8) and CONNECTED(c8,c6)), the
  program's adjacency. Only they are observed: `running___c6` is `run(a)`,
  `running___c8` is `run(b)`; `down(a)`/`down(b)` are derived (not running).
  Their other in-neighbours (c9 into c6, c2 into c8) are outside the
  program: the mismatch the baseline records.
- No rule is an action: rb(C) (the reboot) is read by the weight ports,
  never produced by a rule, so the gym always steps with no action.
- The weight ports are the binding metispy already has for this program
  (tests' sys_registry, the recode of model.py's sysadmin_p_on): cpt(C) = 1
  under rb(C), else .45 + .5 (1 + r)/(1 + |adj C|), r the snapshot's
  prev(D) over the program's adj; rp(C) = 1 under rb(C), else the reboot
  probability, which model.py takes from the instance (REBOOT-PROB, 0.05 in
  instance 1). Not fitted (no notch)."""
import sys
from pathlib import Path

for _d in Path(__file__).resolve().parents:
    if (_d / "tools" / "rddl_host.py").exists():
        sys.path.insert(0, str(_d / "tools"))
        break
from rddl_host import RddlHost  # noqa: E402

PROBLEM, INSTANCE, SEED = "SysAdmin_MDP_ippc2011", "1", 1

# the program's computers as the gym's (instance 1's mutually connected pair)
GYM = {"a": "c6", "b": "c8"}
PROG = {v: k for k, v in GYM.items()}
# the program's adjacency (adj(a,b). adj(b,a).): the registry's ADJ
ADJ = {"a": ["b"], "b": ["a"]}

# a world without intents: no pairs, no words (the domain agent's generic host faces)
PAIRS = ()


def flips(atom):
    return None


def words(atom, names=None):
    return None


def atom(key):
    """`running___c6` -> `run(a)`; the other computers are not observed."""
    if key.startswith("running___"):
        c = PROG.get(key.split("___")[1])
        return "run(%s)" % c if c else None
    return None


def action_of(name, args):
    return None                     # no rule of the program is a reboot (rb is only read)


def down(host):
    return {"down(%s)" % c: 0 if "running___" + g in host.obs else 1 for c, g in sorted(GYM.items())}


def _reboot_prob(host):
    return float(host.nonfluents.get("REBOOT-PROB", 0.04))


def cpt(args, counts, host):
    c = args[0]
    if "rb(%s)" % c in counts:
        return 1.0
    ins = ADJ[c]
    r = sum(1 for y in ins if "prev(%s)" % y in counts)
    return 0.45 + 0.5 * (1 + r) / (1 + len(ins))


def rp(args, counts, host):
    return 1.0 if "rb(%s)" % args[0] in counts else _reboot_prob(host)


def make(case):
    return RddlHost(case, problem=PROBLEM, instance=INSTANCE, seed=SEED, atom=atom, action_of=action_of,
                    extra=down, weights={"cpt": cpt, "rp": rp})
