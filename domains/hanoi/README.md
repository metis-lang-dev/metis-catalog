# hanoi — Tower of Hanoi (rddlrepository arcade) as an RDDL world

Disks move between three rods, one at a time, and never onto a smaller disk.
The program is the formalization, and the gym is the world: `hanoi_host.py`
steps rddlrepository's `TowerOfHanoi_arcade`, instance 0 (its only one),
through the catalog's RDDL world host (`tools/rddl_host.py`, which runs
`tools/rddl_gym.py` under an interpreter with pyRDDLGym: `$METIS_RDDL_PY`,
else the packages' shared `.venv`).

- `hanoi.llp` is the program of the Tier-2 probe `../rddl/hanoi/`, byte for
  byte: 3 disks and 3 rods as one type `spot`, the size order as 12 `fits`
  facts, one move rule `mv` and the goal rule `done` (all on r3 → `solved`).
  See `../rddl/hanoi/README.md` for how it was formalized from the RDDL header.
- The gym's state is `disk-on-rod___d1__r1` and the int `disk-order___d1`
  (0 at the base). The host derives the program's view from both: on each
  rod, the lowest disk is `on(D,rod)`, every other disk is `on(D,the disk
  below)`, the top is `clear(D)`, and an empty rod is `clear(rod)`. The reading
  covers `on(D,S)` for the program's three disks and every other spot, plus
  `clear(S)` for all six spots. No gym fluent is an observed atom by itself.
- The instance has 4 disks and the program has 3. The host reads d4, the
  largest, as part of the rod it stands on: a disk on d4 is on that rod, and
  d4 clear means the rod is clear. No rule moves d4, so it stays on r1, and the gym restricted
  to d1..d3 is the program's puzzle. The gym's reward (all four disks on r3)
  is out of the program's reach.
- A fired `mv(D,P,E)` is the gym's `move___D__R`, where R is E itself if E
  is a rod, or the rod E stands on, read from the gym's state as the move is
  sent. `done` is no action. The program never stops moving, so one beat holds
  the whole episode: the gym's horizon (20 steps) ends it, and the program's
  21st move, which the gym no longer answers, is a surprise.
- No weight ports: the program declares none (mv is uniform over the legal moves).
- No intents: the program chooses the moves, and the domain agent opens the
  world with no verbs. `{"reset": {"seed": N}}` is episode N on both sides.
  The gym's start is fixed, so the seed is the program's sampler. Atom world
  lines (`+on(..)`) are refused because every atom is derived. `nonfluent KEY
  V`, `seed N` and `reset [N]` work.

Run the case without the gym: `metisc --run hanoi.llp` (its `#init`,
`#steps`). Through the domain agent: `python -m metis_agent.domain_agent
--domain hanoi --case replay`.
