"""The RDDL world host (rddl-worlds s-242c7c3f step 1): a catalog host whose
world is a pyRDDLGym environment. The gym is the world, the program is the
formalization, and the domain agent's watch closes the loop on where they
disagree. Each world's `<name>_host.py:make` is a thin configuration over
RddlHost: the problem, the instance, the seed, and how the program's
vocabulary meets the gym's.

The mapping is rddl_recorder's (metispy metis/domains/rddl_recorder.py,
copied, not imported): a grounded fluent `elevator-at-floor___e0__f2` is the
atom `elevator_at_floor(e0,f2)`. A world may map differently (nav's
`robot-at___x6__y12` is `at(x6_y12)`) by giving its own `atom`.

The faces, as the domain agent drives a host:

- on_event(name, args): a fired rule that is an action (the world's
  `action_of`) steps the gym with it, at once, so the watch's reading right
  after the row is the gym's answer to it. Several actions in one beat are
  several gym steps (nav, whose program has no tick).
- tick(counts): one beat. When nothing acted since the last tick, the gym
  steps with no action (the world moves on its own: one beat, one step at
  least). The do-lines then bring the program's state to the gym's on the
  observed atoms: the reading is adopted as the session's state, after the
  watch has scored it (a surprise is recorded before the sync). With
  `tick_token`, `+tick` every beat. None when the gym's episode is over.
- observe(counts): the reading, {atom: 0|1} over every observed atom.
- ports(): what the host reads and drives (the observed atoms, the actions,
  the gym's problem, instance, seed, step and horizon).
- world(lines): driver lines, applied on the next tick:
    `+atom` / `-atom`    the state fluent the atom maps to, set in the gym
    `nonfluent KEY V`    a gym non-fluent (`P___x6__y12 0.9`), until the next open
    `seed N`             the next reset's seed
    `reset [N]`          a new episode now (seed N, else the next seed)
- bind(reg): the world's weight ports, if it binds any (`weights`).
- snapshot()/restore(): the episode as (seed, the actions so far, the
  driver's sets); restore replays them on the gym (deterministic per seed).
- reseed(seed): the domain agent's seed (`{"reset": {"seed": N}}`) is the
  gym's seed too, so an episode is one seed, both sides deterministic.

The gym runs in a child process (tools/rddl_gym.py) under the interpreter
that has pyRDDLGym: $METIS_RDDL_PY, else this one if it imports pyRDDLGym,
else the packages' shared .venv beside the catalog checkout."""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def atom_of(key):
    """`elevator-at-floor___e0__f2` -> `elevator_at_floor(e0,f2)` (rddl_recorder's)."""
    name, _, args = key.partition("___")
    name = name.replace("-", "_")
    if not args:
        return name
    return "%s(%s)" % (name, ",".join(a.replace("-", "_") for a in args.split("__")))


def interpreter():
    py = os.environ.get("METIS_RDDL_PY")
    if py:
        return py
    if importlib.util.find_spec("pyRDDLGym") is not None:
        return sys.executable
    shared = HERE.parent.parent / ".venv" / "bin" / "python"
    if shared.exists():
        return str(shared)
    raise RuntimeError("no interpreter with pyRDDLGym: set METIS_RDDL_PY")


class GymClient:
    """tools/rddl_gym.py as a child: one request, one answer."""

    def __init__(self, problem, instance):
        self.proc = subprocess.Popen([interpreter(), str(HERE / "rddl_gym.py")], stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        self.info = self.call("open", problem=problem, instance=str(instance))

    def call(self, op, **kw):
        self.proc.stdin.write(json.dumps(dict(kw, op=op)) + "\n")
        self.proc.stdin.flush()
        line = self.proc.stdout.readline()
        if not line:
            raise RuntimeError("the gym process ended (%s)" % self.proc.poll())
        out = json.loads(line)
        if not out.pop("ok"):
            raise RuntimeError("gym %s: %s" % (op, out["error"]))
        return out

    def close(self):
        try:
            if self.proc.poll() is None:
                self.proc.stdin.write('{"op": "close"}\n')
                self.proc.stdin.flush()
                self.proc.wait(timeout=10)
        except (OSError, ValueError, subprocess.TimeoutExpired):
            self.proc.kill()

    def __del__(self):
        if getattr(self, "proc", None) is not None:
            self.close()


class RddlHost:
    """A world's gym as a catalog host. A world configures it:

    problem, instance  the rddlrepository problem and instance
    seed               the first episode's seed (the domain agent's reseed overrides)
    atom(key)          a grounded state fluent -> the program's atom, or None (not observed)
    action_of(name, args) -> {action key: value} | None: the fired rule as a gym action
    extra(obs)         -> {atom: n}: readings derived from the gym's state (nav's `dead`)
    weights            {port: fn(args, counts, host)}: the weight ports the host binds
    tick_token         `+tick` every beat (a program that steps by a tick resource)
    """

    def __init__(self, case=None, *, problem, instance="1", seed=1, atom=atom_of, action_of=None,
                 extra=None, weights=None, tick_token=False):
        self.problem, self.instance = problem, str(instance)
        self.atom, self.action_of = atom, action_of or (lambda name, args: None)
        self.extra, self.weights, self.tick_token = extra, dict(weights or {}), tick_token
        self.gym = GymClient(problem, instance)
        info = self.gym.info
        self.horizon, self.nonfluents = info["horizon"], info["nonfluents"]
        self.action_keys = info["actions"]
        self.observed = {}                       # atom -> its state fluent key
        for k in info["state"]:
            a = self.atom(k)
            if a is not None:
                self.observed[a] = k
        # the domain agent's AgentHost reads these of a hosted day
        self.beat, self.due, self.script, self.last = 0, (), {}, None
        self.acted = ()
        self.pending = []                        # driver lines for the next tick
        self.next_seed = seed
        self._reset(seed)

    # ── the episode ──
    def _reset(self, seed):
        self.seed = seed
        self.next_seed = seed + 1
        self.actions = []                        # (step, action) of this episode: the snapshot
        self.sets = []                           # (step, fluents) the driver set
        self.t, self.done, self.reward = 0, False, 0.0
        self._take(self.gym.call("reset", seed=seed))
        self.stepped = False

    def _take(self, out):
        self.obs, self.values = set(out["obs"]), out["values"]

    def _step(self, action):
        out = self.gym.call("step", action=action)
        self._take(out)
        self.actions.append((self.t, action))
        self.t += 1
        self.reward += out["reward"]
        self.done = out["done"]
        self.stepped = True

    def reseed(self, seed):
        """The domain agent's seed is the episode's (a `reset {seed}` rebuilds the agent)."""
        if seed != self.seed:
            self._reset(seed)

    def reading(self):
        r = {a: (1 if k in self.obs else 0) for a, k in self.observed.items()}
        if self.extra:
            r.update(self.extra(self))
        return r

    # ── the host faces ──
    def bind(self, reg):
        for port, fn in self.weights.items():
            reg.weight(port, lambda args, counts, fn=fn: fn(args, counts, self))

    def on_event(self, name, args):
        self.acted += ((self.beat, name, tuple(args)),)
        action = self.action_of(name, args)
        if action is not None and not self.done:
            self._step(action)

    def observe(self, counts):
        return self.reading()

    def tick(self, counts):
        if self.done:
            return None
        self.beat += 1
        dos = []
        for line in self.pending:
            dos += self._driver(line)
        self.pending = []
        if not self.stepped and not self.done:
            self._step({})                       # the world moves on its own: one beat, one step
        self.stepped = False
        for a, n in sorted(self.reading().items()):       # the program's state brought to the gym's
            have = counts.get(a, 0)
            if n > have:
                dos.append("+%s %d" % (a, n - have))
            elif n < have:
                dos.append("-%s %d" % (a, have - n))
        if self.tick_token:
            dos.append("+tick")
        return dos

    def world(self, lines):
        bad = [l for l in lines if not isinstance(l, str) or not (
            (l[:1] in "+-" and len(l) > 1) or l.split()[:1] in (["nonfluent"], ["seed"], ["reset"]))]
        if bad:
            raise ValueError("world lines are +atom, -atom, `nonfluent KEY VALUE`, `seed N` or `reset [N]`, not %r" % bad)
        for l in lines:
            if l[:1] in "+-" and l[1:].split()[0] not in self.observed:
                raise ValueError("%s: not an observed atom of %s (ports lists them)" % (l, self.problem))
            if l.startswith("nonfluent") and (len(l.split()) != 3 or l.split()[1] not in self.nonfluents):
                raise ValueError("%s: `nonfluent KEY VALUE` with a non-fluent of %s" % (l, self.problem))
        self.pending += list(lines)

    def _driver(self, line):
        """A driver line, at the tick: the gym changes; the sync that follows brings the program along."""
        w = line.split()
        if w[0] == "seed":
            self.next_seed = int(w[1])
        elif w[0] == "reset":
            self._reset(int(w[1]) if len(w) > 1 else self.next_seed)
            self.stepped = True                  # the new episode's start is this beat's state
        elif w[0] == "nonfluent":
            v = json.loads(w[2]) if w[2] not in ("true", "false") else w[2] == "true"
            self._set({w[1]: v})
            self.nonfluents[w[1]] = v            # the world's weights read the instance as it is now
        else:
            self._set({self.observed[w[0][1:]]: line[0] == "+"})
        return []

    def _set(self, fluents):
        self._take(self.gym.call("set", fluents=fluents))
        self.sets.append((self.t, fluents))

    def ports(self):
        return {"gym": {"problem": self.problem, "instance": self.instance, "seed": self.seed,
                        "step": self.t, "horizon": self.horizon, "done": self.done, "reward": self.reward},
                "observed": sorted(self.observed), "derived": sorted(self.extra(self)) if self.extra else [],
                "actions": self.action_keys, "weights": sorted(self.weights)}

    def snapshot(self):
        return {"seed": self.seed, "t": self.t, "beat": self.beat, "actions": [[t, a] for t, a in self.actions],
                "sets": [[t, f] for t, f in self.sets], "acted": [list(x) for x in self.acted]}

    def restore(self, snap):
        """The episode replayed on the gym: its seed, then the steps and the sets in order."""
        acts = {t: a for t, a in snap["actions"]}
        sets = {}
        for t, f in snap["sets"]:
            sets.setdefault(t, []).append(f)
        self._reset(snap["seed"])
        for t in range(snap["t"] + 1):
            for f in sets.get(t, []):
                self._set(f)
            if t < snap["t"]:
                self._step(acts.get(t, {}))
        self.beat, self.stepped = snap["beat"], False
        self.acted = tuple((b, n, tuple(a)) for b, n, a in snap["acted"])
