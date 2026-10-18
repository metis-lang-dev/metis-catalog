# nav — Navigation (IPPC 2011) as an RDDL world

The robot crosses a grid to its goal; every cell may claim it on arrival. The
program is the formalization, and the gym is the world: `nav_host.py` steps
rddlrepository's `Navigation_MDP_ippc2011`, instance 1, through the catalog's
RDDL world host (`tools/rddl_host.py`, which runs `tools/rddl_gym.py` under an
interpreter with pyRDDLGym: `$METIS_RDDL_PY`, else the packages' shared
`.venv`).

- `nav.llp` is the instance: its 12 cells and their adjacency, generated from
  the gym's non-fluents (EAST, NORTH, the init state), over the lifted
  `nav_domain.llp` (the move and die rules, the weight ports go and die).
- The host maps `robot-at___x6__y12` to `at(x6_y12)`; `dead` is the robot
  being nowhere. A fired move rule (mv_north or die_north alike) is the gym's
  `move-north`: the gym decides whether the robot arrives, and the domain
  agent's watch scores the program against that answer. A beat with no move
  is one gym step with no action; the gym's horizon (40 steps) ends the
  episode.
- The weight ports are bound from the instance itself: go(C,C2) = 1 − P(C2),
  die(C,C2) = P(C2), every direction alike, 0 at the goal. They are the
  instance's parameters, not fitted.
- No intents: the program chooses the moves, and the domain agent opens the
  world with no verbs. `{"reset": {"seed": N}}` is episode N on both sides
  (the program's sampler and the gym), so an episode is deterministic per
  seed. World lines: `+at(C)`/`-at(C)` set the gym's state, `nonfluent KEY V`
  a non-fluent (`P___x9__y12 0.75`), `seed N`, `reset [N]`. They change the
  gym at once, and the program follows before its next move. A scenario moves
  the robot with both lines (`-at(x21_y12)`, `+at(x6_y12)`): the host does not
  stop a `+at` alone from putting it in two cells.

Run the case without the gym: `metisc --run nav.llp` (its `#init`, `#steps`,
`#query` lines). Through the domain agent: `python -m metis_agent.domain_agent
--domain nav --case replay`.
