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
- world(lines): driver lines, applied to the gym at once; sync(counts) then
  gives the do-lines the domain agent applies before the program moves:
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
import json
from pathlib import Path

from metis.host import GymChild, find_interpreter

HERE = Path(__file__).resolve().parent


def atom_of(key):
    """`elevator-at-floor___e0__f2` -> `elevator_at_floor(e0,f2)` (rddl_recorder's)."""
    name, _, args = key.partition("___")
    name = name.replace("-", "_")
    if not args:
        return name
    return "%s(%s)" % (name, ",".join(a.replace("-", "_") for a in args.split("__")))


def interpreter():
    """$METIS_RDDL_PY, else this interpreter when it imports pyRDDLGym, else the packages'
    shared .venv beside the catalog checkout (metis.host.find_interpreter)."""
    return find_interpreter("METIS_RDDL_PY", "pyRDDLGym", [HERE.parent.parent / ".venv" / "bin" / "python"], default=False)


class GymClient(GymChild):
    """tools/rddl_gym.py as a child: one request, one answer (metis.host.GymChild, metis-packages)."""

    def __init__(self, problem, instance):
        super().__init__(HERE / "rddl_gym.py", interpreter(), "gym", problem=problem, instance=str(instance))


class RddlHost:
    """A world's gym as a catalog host. A world configures it:

    problem, instance  the rddlrepository problem and instance
    seed               the first episode's seed (the domain agent's reseed overrides)
    atom(key)          a grounded state fluent -> the program's atom, or None (not observed)
    action_of(name, args) -> {action key: value} | None: the fired rule as a gym action
    extra(obs)         -> {atom: n}: readings derived from the gym's state (nav's `dead`)
    weights            {port: fn(args, counts, host)}: the weight ports the host binds
    tick_token         `+tick` every beat (a program that steps by a tick resource)

    A world whose program does not act but OBSERVES (rddl_recorder's
    transitions: the state, the action taken and a tick in, the next state
    out; wildfire, tamarisk) sets `policy`:
    policy             "random" (pyRDDLGym's RandomAgent, seeded per episode, the
                       recorder's agent: wildfire, tamarisk) | "noop" (gol and
                       sysadmin, whose programs never act): the host acts. Each tick: the
                       program brought to the gym's state, the action and tick
                       atoms of the last step taken off, the gym stepped by the
                       policy, its action's true fluents and `+tick` given to the
                       program, whose cycle then computes the next state.
    negatives          a false fluent is also `not_<atom>` (the recorder's --negatives)
    transient          the program's in-cycle predicates: while any is held the
                       reading waits (observe gives nothing), so the watch scores
                       the settled cycle (the recorder's frame readout); taken off
                       at each tick, as the step's action atoms are
    tokens             atoms handed to the program with each step's input besides
                       `tick`, when it does not hold them (a cycle's start token:
                       sysadmin's `m(i0)`, which its wrapping pipeline then carries)
    action_atom(key)   a true action fluent -> the program's atom, or None
                       (default rddl_recorder's mapping)

    read_steps         the reading is news only after a row that stepped the gym
                       (or a beat's step): between gym steps the world has not
                       moved, and the program's rows are its own step in progress
                       (elevators' arrivals, drawn row by row where the gym draws
                       them inside its step), so observe gives nothing and the
                       watch's window runs from one gym step to the next
                       (rddl-watch s-cfe94dca)
    """

    def __init__(self, case=None, *, problem, instance="1", seed=1, atom=atom_of, action_of=None,
                 extra=None, weights=None, tick_token=False, policy=None, negatives=False, transient=(),
                 tokens=(), action_atom=atom_of, read_steps=False):
        self.problem, self.instance = problem, str(instance)
        self.atom, self.action_of = atom, action_of or (lambda name, args: None)
        self.extra, self.weights, self.tick_token = extra, dict(weights or {}), tick_token
        if policy not in (None, "random", "noop"):
            raise ValueError("policy: random | noop | None, not %r" % policy)
        self.policy, self.negatives, self.transient = policy, negatives, set(transient)
        self.tokens, self.action_atom = tuple(tokens), action_atom
        self.read_steps = read_steps
        self.gym = GymClient(problem, instance)
        info = self.gym.info
        self.horizon, self.nonfluents = info["horizon"], info["nonfluents"]
        self.action_keys = info["actions"]
        self.observed = {}                       # atom -> its state fluent key
        for k in info["state"]:
            a = self.atom(k)
            if a is not None:
                self.observed[a] = k
        self.action_preds = {k.replace("-", "_") for k in self.action_keys}     # put-out -> put_out(…)
        # the domain agent's AgentHost reads these of a hosted day
        self.beat, self.due, self.script, self.last = 0, (), {}, None
        self.next_seed = seed
        self._reset(seed)

    # ── the episode ──
    def _reset(self, seed):
        self.seed = seed
        self.next_seed = seed + 1
        self.actions = []                        # (step, action, drawn by the policy) of this episode: the snapshot
        self.sets = []                           # (step, fluents) the driver set
        self.t, self.done, self.reward = 0, False, 0.0
        self.stalled = False                     # an observing program that stopped taking its steps
        self.fresh = False                       # read_steps: the last row (or beat) stepped the gym
        self._take(self.gym.call("reset", seed=seed))
        self.stepped = False

    def _take(self, out):
        self.obs, self.values = set(out["obs"]), out["values"]

    def _step(self, action, policy=None):
        out = self.gym.call("step", action=action, policy=policy) if policy else self.gym.call("step", action=action)
        self._take(out)
        action = out.get("action", action)       # the policy's draw: a restore draws it again
        self.last_action = action
        self.actions.append((self.t, action, bool(policy)))
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
        if self.negatives:
            r.update({"not_" + a: (0 if k in self.obs else 1) for a, k in self.observed.items()})
        if self.extra:
            r.update(self.extra(self))
        return r

    def settled(self, counts):
        return not any(n > 0 and a.split("(")[0] in self.transient for a, n in counts.items())

    # ── the host faces ──
    def bind(self, reg):
        for port, fn in self.weights.items():
            reg.weight(port, lambda args, counts, fn=fn: fn(args, counts, self))

    def on_event(self, name, args):
        action = self.action_of(name, args)
        self.fresh = False
        if action is not None and not self.done:
            self._step(action)
            self.fresh = True

    def observe(self, counts):
        if self.done:
            return {}                            # the episode is over: the world answers nothing more
        if self.policy and self.t == 0:
            return {}                            # an observing world before its first step: no outcome to read
                                                 # (a program whose #init holds a step's input runs it uncompared)
        if self.transient and not self.settled(counts) and not self.stalled:
            return {}                            # the program's cycle is in flight: nothing to read yet
        if self.read_steps and not self.fresh:
            return {}                            # the gym has not moved since its last step's reading
        return self.reading()

    def tick(self, counts):
        if self.done:
            return None
        self.beat += 1
        if self.policy:
            return self._observer_tick(counts)
        if not self.stepped and not self.done:
            self._step({})                       # the world moves on its own: one beat, one step
            self.fresh = True
        self.stepped = False
        dos = self.sync(counts)                  # the program's state brought to the gym's
        if self.tick_token:
            dos.append("+tick")
        return dos

    def _observer_tick(self, counts):
        """The recorder's transition as one beat: the program at the gym's state
        (its leftover action and tick atoms taken off), the gym stepped by the
        policy, the action's true fluents and the tick handed to the program."""
        off = self.action_preds | self.transient | {"tick"}
        left = [(a, n) for a, n in sorted(counts.items()) if n > 0 and a.split("(")[0] in off]
        if self.t > 0 and left and not self.stalled:
            # the last step's input was never taken: the program's cycle did not run.
            # The reading is not deferred from here on, so the stall shows as the
            # program's state against the gym's (not as a silence)
            self.stalled = True
            return []
        if self.stalled:
            self._step({}, policy=self.policy)   # the world goes on; the program does not
            self.stepped = False
            return []
        dos = self.sync(counts)
        for a, n in left:
            dos.append("-%s %d" % (a, n))
        self._step({}, policy=self.policy)
        self.stepped = False
        acts = [self.action_atom(k) for k, v in sorted(self.last_action.items()) if v is True or v == 1]
        dos += ["+" + a for a in acts if a]
        dos += ["+" + a for a in self.tokens if not counts.get(a)]   # a pipeline that wraps carries its own
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
        for l in lines:                          # the gym changes now: the program's next move starts from it
            self._driver(l)

    def sync(self, counts):
        """The do-lines that bring the program's state to the gym's, with no
        gym step and no beat: the domain agent applies them right after
        world lines (rddl-worlds review R1), so the scenario holds before
        the program's next move."""
        dos = []
        for a, n in sorted(self.reading().items()):
            have = counts.get(a, 0)
            if n > have:
                dos.append("+%s %d" % (a, n - have))
            elif n < have:
                dos.append("-%s %d" % (a, have - n))
        return dos

    def _driver(self, line):
        """A driver line: the gym changes; sync() brings the program along."""
        w = line.split()
        if w[0] == "seed":
            self.next_seed = int(w[1])
        elif w[0] == "reset":
            self._reset(int(w[1]) if len(w) > 1 else self.next_seed)
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
        # the episode only, bounded by the horizon: the repl stores a snapshot after
        # every fired row, so nothing here may grow per fired event (`acted` did:
        # quadratic, a 23.7 GB xtraffic run — rddl-worlds step 3)
        snap = {"seed": self.seed, "t": self.t, "beat": self.beat, "stalled": self.stalled,
                "actions": [[t, a, drawn] for t, a, drawn in self.actions],
                "sets": [[t, f] for t, f in self.sets]}
        if self.read_steps:
            snap["fresh"] = self.fresh
        return snap

    def restore(self, snap):
        """The episode replayed on the gym: its seed, then the steps and the sets in order."""
        # a step the policy drew is drawn again (the agent, seeded at reset, then
        # draws on from the same place: nina's step-3 review N1); a sent action is sent
        acts = {t: (a, drawn) for t, a, drawn in snap["actions"]}
        sets = {}
        for t, f in snap["sets"]:
            sets.setdefault(t, []).append(f)
        self._reset(snap["seed"])
        for t in range(snap["t"] + 1):
            for f in sets.get(t, []):
                self._set(f)
            if t < snap["t"]:
                a, drawn = acts.get(t, ({}, False))
                self._step({}, policy=self.policy) if drawn else self._step(a)
        self.beat, self.stepped, self.stalled = snap["beat"], False, snap.get("stalled", False)
        self.fresh = snap.get("fresh", False)
