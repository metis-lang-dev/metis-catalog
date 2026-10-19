# xtraffic — CrossingTraffic (IPPC 2011) as an RDDL world

A robot crosses a road to its goal while obstacles stream west along the
road's row; an obstacle on the robot's cell takes it. The program is the
formalization, and the gym is the world: `xtraffic_host.py` steps
rddlrepository's `CrossingTraffic_MDP_ippc2011`, instance 1, through the
catalog's RDDL world host (`tools/rddl_host.py`, which runs
`tools/rddl_gym.py` under an interpreter with pyRDDLGym: `$METIS_RDDL_PY`,
else the packages' shared `.venv`).

- `xtraffic.llp` is the instance: its 3×3 cells and their adjacency, the
  edges (noadj_*), the road row as a chain (cidx, succ, lastidx), the goal,
  generated from the gym's non-fluents (EAST, NORTH, MIN/MAX-YPOS, GOAL, the
  init state) by metispy's `gen_instance`, over the lifted
  `xtraffic_domain.llp` (the move stage, the obstacle shift as mark, update
  and sweep passes, the weight ports obs, go, stayw, fgo, fstayw).
- The host maps `robot-at___x3__y1` to `rob(x3_y1)` and `obstacle-at___x2__y2`
  to `o(x2_y2)`; `e(C)` (a road cell is free) and `dead` (the robot is
  nowhere) are derived. One move-stage rule fires per epoch and it is the
  gym's step: a move rule (fmv_north, fst_north, mv_north alike) is
  `move-north`; str, dier, atgoal and deadtick are the step with no action.
  The gym decides where the robot is and where the obstacles went, and the
  domain agent's watch scores the program against that answer. The gym's
  horizon (40 steps) ends the episode.
- The weight ports are metispy's binding of this program
  (`metis.domains.xtraffic.model.XTrafficModel.bindings`) as it is, over the
  topology read from the gym's own non-fluents; obs's edge arrival rate is
  the instance's INPUT-RATE (0.3), read live. The policy table is empty: the
  base policy (uniform over the goal-ward moves). Not fitted.
- The program's epoch is 14 rows (a move, then the shift over the three road
  cells), and its last link (`sm`) opens the next epoch: it never quiesces.
  The gym answers a move at once with the obstacles already shifted, which
  the program reaches 13 rows later, so the manifest's clock {lockstep: true}
  has the watch read once per epoch, when `sm` wraps back to the move stage,
  and the next epoch waits for the beat. Measured (rddl-watch s-cfe94dca, 20
  seeded episodes): no surprise; 800 moves scored, each answered as the
  program sent it; mean log P(the gym's road) per beat −0.584; reward −15.3
  (step 3, surprised at its first move in every episode: −40).
- No intents: the program chooses the moves, and the domain agent opens the
  world with no verbs. `{"reset": {"seed": N}}` is episode N on both sides.
  World lines: `+rob(C)`/`-rob(C)`, `+o(C)`/`-o(C)` set the gym's state,
  `nonfluent INPUT-RATE 0.6` the arrival rate, `seed N`, `reset [N]`.

Run the case without the gym: `metisc --run xtraffic.llp` (its `#init`,
`#steps`, `#query` lines). Through the domain agent: `python -m
metis_agent.domain_agent --domain xtraffic --case replay`.
