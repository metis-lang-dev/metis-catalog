"""The RDDL gym as a child process (rddl-worlds s-242c7c3f step 1): one
pyRDDLGym environment behind JSON lines on stdin/stdout, so a catalog
host (tools/rddl_host.py) steps the gym from the domain agent's process
without pyRDDLGym in that process's environment. Run by the host under an
interpreter that has pyRDDLGym and rddlrepository; nothing here knows a
catalog.

One request per line, one answer per line ({"ok": false, "error": ...}
on a failure; the process stays up):

  {"op": "open", "problem": P, "instance": I}
      -> {"horizon", "state": [fluent keys], "actions": [...], "nonfluents": {key: value}}
  {"op": "reset", "seed": S}           -> {"obs": [true boolean keys], "values": {key: number}}
  {"op": "step", "action": {key: v}}   -> {"obs", "values", "reward", "done", "action"}
  {"op": "step", "policy": "random"}   the action drawn by pyRDDLGym's RandomAgent, seeded
                                       with the episode's seed at reset (rddl_recorder's agent)
  {"op": "set", "fluents": {key: v}}   -> {"obs", "values"}   a state fluent or a non-fluent,
                                                              grounded (`robot-at___x6__y12`);
                                                              a non-fluent holds until the next open
  {"op": "close"}

The state's grounded keys are pyRDDLGym's (`robot-at___x6__y12`); the
host maps them to atoms (rddl_recorder's mapping)."""
import json
import sys


def jsonable(v):
    t = type(v).__name__
    if t in ("bool", "bool_"):
        return bool(v)
    if hasattr(v, "item"):
        return v.item()
    return v


class Gym:
    def __init__(self):
        self.env = None
        self.override = {}       # non-fluents set by the driver: applied after every reset

    def open(self, problem, instance):
        import pyRDDLGym
        from rddlrepository.core.manager import RDDLRepoManager
        prob = RDDLRepoManager().get_problem(problem)
        self.env = pyRDDLGym.make(prob.get_domain(), prob.get_instance(str(instance)))
        self.override = {}
        m = self.env.model
        nf = m.ground_vars_with_values(m.non_fluents)
        return {"horizon": int(self.env.horizon), "state": sorted(m.ground_vars_with_values(m.state_fluents)),
                "actions": sorted(m.action_fluents), "nonfluents": {k: jsonable(v) for k, v in nf.items()}}

    def _obs(self, obs):
        out, vals = [], {}
        for k, v in obs.items():
            v = jsonable(v)
            if isinstance(v, bool):
                if v:
                    out.append(k)
            else:
                vals[k] = v
        return {"obs": sorted(out), "values": vals}

    def _set(self, fluents):
        m, subs = self.env.model, self.env.sampler.subs
        for key, v in fluents.items():
            name = key.split("___")[0]
            g = m.variable_groundings.get(name)
            if g is None or name not in subs:
                raise KeyError("no fluent %r" % key)
            arr = subs[name]
            if hasattr(arr, "flat"):
                arr = arr.copy()                  # never the model's own array: a reset starts from it
                arr.flat[g.index(key)] = v
            else:
                arr = v
            subs[name] = arr
            if name in m.non_fluents:
                self.override[key] = v
            elif self.env.state is not None and key in self.env.state:
                self.env.state[key] = v

    def reset(self, seed):
        from pyRDDLGym.core.policy import RandomAgent
        self.agent = RandomAgent(action_space=self.env.action_space,
                                 num_actions=self.env.max_allowed_actions, seed=int(seed))
        obs, _ = self.env.reset(seed=int(seed))
        self.last = obs
        if self.override:
            self._set(dict(self.override))
        return self._obs(obs)

    def step(self, action, policy=None):
        if policy == "random":
            action = {k: jsonable(v) for k, v in self.agent.sample_action(self.last).items()}
        elif policy not in (None, "noop"):
            raise ValueError("policy: random | noop, not %r" % policy)
        obs, r, term, trunc, _ = self.env.step(dict(action))
        self.last = obs
        return dict(self._obs(obs), reward=float(r), done=bool(term or trunc), action=dict(action))

    def set(self, fluents):
        self._set(fluents)
        return self._obs(self.env.state or {})


def main():
    out_stream, sys.stdout = sys.stdout, sys.stderr   # the answers only: the gym's prints go to stderr
    g = Gym()
    for line in sys.stdin:
        if not line.strip():
            continue
        try:
            req = json.loads(line)
            op = req.get("op")
            if op == "close":
                break
            if op == "open":
                out = g.open(req["problem"], req.get("instance", "1"))
            elif g.env is None:
                raise RuntimeError("open first")
            elif op == "reset":
                out = g.reset(req.get("seed", 1))
            elif op == "step":
                out = g.step(req.get("action") or {}, req.get("policy"))
            elif op == "set":
                out = g.set(req.get("fluents") or {})
            else:
                raise ValueError("no op %r" % op)
            out["ok"] = True
        except Exception as e:  # noqa: BLE001 — the answer says it; the gym stays up
            out = {"ok": False, "error": "%s: %s" % (type(e).__name__, e)}
        out_stream.write(json.dumps(out) + "\n")
        out_stream.flush()


if __name__ == "__main__":
    main()
