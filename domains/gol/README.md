# gol — Game of Life (IPPC 2011) as an RDDL world

A 3x3 grid of cells lives, dies and is born by Conway's rule, each cell with its
own noise. The program is the formalization, and the gym is the world:
`gol_host.py` steps rddlrepository's `GameOfLife_MDP_ippc2011`, instance 1,
through the catalog's RDDL world host (`tools/rddl_host.py`, which runs
`tools/rddl_gym.py` under an interpreter with pyRDDLGym: `$METIS_RDDL_PY`, else
the packages' shared `.venv`).

- `gol.llp` is metispy's GoL program written out: `metis.domains.gol.model.gen_catalog`
  (the sync compilation as text, pinned at 1e-9 against kernel.sync by
  metispy's tests/gol) over the instance's 9 cells and NEIGHBOR facts, as
  `rddl_adapter.load("1")` reads them; its `#init` is `model.catalog_init` of
  the instance's init-state, its `#steps` one tick (`steps_per_tick(9)` = 30).
  One GoL tick is three passes over the cells in a fixed order: mark (snapshot
  a/d into pa/pd), update (draw each next value, weight life(C)), sweep (commit
  to a/d), then the link back to mark.
- The host maps `alive___x1__y2` to `a(x1__y2)`; `d(x1__y2)` is derived (the
  cell is not alive).
- Actions: none. The gym's one action is `set(x,y)`; the program's `force(C)`
  is its input atom, but no rule produces it (metispy chose it code-side, the
  greedy agent in rddl_adapter). Every gym step is the noop: a beat with no
  move is one gym step with no action; the gym's horizon (40) ends the episode.
- The weight port life(C) is metispy's own binding (`model.life_bindings`), as
  it is, over the instance's NEIGHBOR and NOISE-PROB non-fluents: 1−noise(C)
  when Conway's condition (or force) holds, else noise(C). Not fitted.
- No intents: the domain agent opens the world with no verbs.
  `{"reset": {"seed": N}}` is episode N on both sides. World lines:
  `+a(C)`/`-a(C)` set the gym's cell, `nonfluent KEY V` (`NOISE-PROB___x1__y1 0.2`),
  `seed N`, `reset [N]`.

Known fit (see the step-3 NOTES): the program's a/d are consumed by its own
mark pass, so the watch's reading after the first fired row differs from the
program, and the episode turns observe-only at row 1 (a surprise every
episode); and the program's tick cycle has no rest point (sweep links back to
mark), so it never quiesces on its own.

Run the case without the gym: `metisc --run gol.llp` (one tick from the
instance's init-state). Through the domain agent: `python -m
metis_agent.domain_agent --domain gol --case replay`.
