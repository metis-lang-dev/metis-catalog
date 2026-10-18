# sysadmin — SysAdmin (IPPC 2011) as an RDDL world

Computers on a network fail and recover: a running computer stays up with a
probability that rises with its running in-neighbours, a down one comes back
on its own with the reboot probability, and a reboot brings it up for sure.
The program is the formalization, and the gym is the world:
`sysadmin_host.py` steps rddlrepository's `SysAdmin_MDP_ippc2011`,
instance 1, through the catalog's RDDL world host (`tools/rddl_host.py`,
which runs `tools/rddl_gym.py` under an interpreter with pyRDDLGym:
`$METIS_RDDL_PY`, else the packages' shared `.venv`).

- `sysadmin2.llp` is the 2-computer fixture (computers `a`, `b`, `adj(a,b)`,
  `adj(b,a)`), unchanged: one gym tick compiled into an interleaved
  mark / update / sweep cycle of nine program steps (snapshot `run`/`down`
  into `prev`/`pdown`, draw each computer's next state by the weight ports,
  commit it), chained by the `m`/`u`/`s` index tokens.
- No gym instance has 2 computers (instances 1–2: 10, 3–4: 20, … 9–10: 50).
  The program's `a` and `b` are instance 1's `c6` and `c8`, the one pair
  connected both ways there, as the program's adjacency is. Only they are
  observed: `running___c6` is `run(a)`, `running___c8` is `run(b)`;
  `down(a)`/`down(b)` are derived (not running). Their other in-neighbours,
  `c9` (into `c6`) and `c2` (into `c8`), are outside the program.
- No rule is an action. `rb(C)` (the reboot) is read by the weight ports and
  produced by no rule, so the gym always steps with no action (`reboot` is
  never sent). A beat with no action is one gym step; the gym's horizon
  (40 steps) ends the episode.
- The weight ports are the binding metispy already has for this program
  (its tests' `sys_registry`, the recode of `model.py`'s `sysadmin_p_on`):
  `cpt(C)` = 1 under `rb(C)`, else .45 + .5·(1 + r)/(1 + |adj C|), r the
  snapshot's running neighbours over the program's own `adj`; `rp(C)` = 1
  under `rb(C)`, else the instance's `REBOOT-PROB` (0.05), as `model.py`
  takes it from the instance. Not fitted.
- No intents. `{"reset": {"seed": N}}` is episode N on both sides. World
  lines: `+run(a)`/`-run(a)` set `running___c6` in the gym, `nonfluent KEY V`
  a non-fluent (`REBOOT-PROB 0.1`), `seed N`, `reset [N]`.

What it does today: the program file carries no `#init`, so its chain token
`m(i0)` is never present and no rule fires; the host keeps `run`/`down` in
step with the gym every beat, and the program says nothing about it (every
beat scores 1.0, vacuously). With an `#init m(i0) 1` added, the first
snapshot rule consumes `run(a)` while the gym still reads it, and the watch
opens an unmodeled surprise on the first row of every episode. See the
work notes for why.

Through the domain agent: `python -m metis_agent.domain_agent --domain
sysadmin --case replay`.
