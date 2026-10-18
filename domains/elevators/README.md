# elevators — Elevators (IPPC 2011) as an RDDL world

Two elevators carry passengers to the top or bottom floor. The program is the
formalization, and the gym is the world: `elevators_host.py` steps
rddlrepository's `Elevators_MDP_ippc2011`, instance 8, through the catalog's
RDDL world host (`tools/rddl_host.py`, which runs `tools/rddl_gym.py` under an
interpreter with pyRDDLGym: `$METIS_RDDL_PY`, else the packages' shared
`.venv`).

- `elevators.llp` is the RDDL experiment's born program
  (`domains/rddl/elevators/elevators_born.llp`, byte-equal). It was born
  from the domain header's prose alone, so it carries its own `#init` and
  literal weights. Instance 8 is the gym instance with the same objects:
  elevators e0 e1 and floors f0..f4. Instance 9 has the same objects with
  other arrival rates.
- The host maps the gym's fluents to the program's atoms:

  | gym fluent | program atom |
  |---|---|
  | `elevator-at-floor(e,f)` | `at(e,f)` |
  | `elevator-closed(e)` | `closed(e)`; derived `open(e)` = not closed |
  | `elevator-dir-up(e)` | `heading(e,up)`; derived `heading(e,down)` = not dir-up |
  | `person-waiting-up(f)` / `-down(f)` | `waiting(f,top)` / `waiting(f,bottom)`; derived `free(f,x)` = not waiting, for the program's 8 slots |
  | `person-in-elevator-going-up(e)` / `-down(e)` | `riding(e,top)` / `riding(e,bottom)` |
  | (none) | `delivered`: not observed |

- The program's rules choose the moves, so the host runs in nav mode. A
  fired `move` is `move-current-dir(e)`. `open_same` and `open_turn` are
  `open-door-going-up(e)` or `-down(e)`, by the heading they leave. `close`
  is `close-door(e)`. `noop`, the arrivals, `board` and `alight` are not
  actions: the gym does them in its own step. A beat with no action is one
  gym step with no action, and the gym's horizon (40 steps) ends the
  episode.
- No weight ports: the program declares none (its weights are literals), so
  the host binds none.
- No intents: the domain agent opens the world with no verbs.
  `{"reset": {"seed": N}}` is episode N on both sides. World lines are
  `+atom`/`-atom` on an observed atom (`-at(e1,f0)`, `+at(e1,f4)`,
  `-heading(e1,up)`), `nonfluent KEY V` (`ARRIVE-PARAM___f1 0.1`),
  `seed N` and `reset [N]`.
- **The baseline surprises at the first fired row of every episode.** The
  program's `#init` puts e1 at f4 heading down. The gym starts both
  elevators at f0 heading up. See the step's NOTES.

Run the case without the gym: `metisc --run elevators.llp` (its `#init` and
`#steps`). Through the domain agent: `python -m metis_agent.domain_agent
--domain elevators --case replay`.
