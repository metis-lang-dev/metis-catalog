# tamarisk — Tamarisk (IPPC 2014) as an RDDL world

The program `tamarisk.llp` was formalized in the metis loop from the gym's episodes
(the experiment's record, with its findings and numbers, is
`domains/rddl/tamarisk/`), and its fitted notch is `tamarisk.notch.json`. Both are
unchanged here, except one line: the `#plugin` directive now names this
package's host (`#plugin tamarisk_host.py:make`), because the experiment's path
(`tamarisk/tamarisk_plugin.py`) does not resolve from this directory. It is a
compiler-invisible directive; the program key is the same.

`tamarisk_host.py` steps rddlrepository's `Tamarisk_MDP_ippc2014`, instance 1, through
the catalog's RDDL world host (`tools/rddl_host.py`), as an OBSERVING world:
the program does not act. Each beat is one transition as rddl_recorder records
it: the program at the gym's state (the fluents and their `not_` negatives),
the gym stepped by pyRDDLGym's random agent seeded per episode (the agent the
program was formalized from), the action's atoms and a `tick` handed to the
program; the watch reads the gym once the program's cycle has settled. The
weight ports are bound prior-flat (0.5), as the experiment's plugin binds them,
and the notch rides on top.

**The pass (rddl-watch s-cfe94dca).** The manifest's clock {lockstep: true}:
the watch reads once per pass, when it ends quiet, and the beat's input
restarts the stage pipeline at its first stage (step 3 stalled at the second
step: the pipeline sat in its last stage). A pass is past the exact filter's
state budget (10000; more than 300k states), so it is priced on the declared
sampled tier: 500 reference-sampler runs seeded per episode and position,
with a 95% half-width; a sampled zero is "rare", below that resolution,
never a surprise. Measured (20 seeded episodes, 592 s): no surprise; 780
passes sampled; mean log P(the gym's next reaches) per beat −2.036 over the
beats with a nonzero estimate; 83 beats' estimates are 0 at n=500 — the
reading is below that resolution (four of them re-drawn at n=20000: p ≈
0.0065, 0.0015, 0.0001 and < 1e-4), the prior-flat ports' honest spread.

Run the case without the gym: `metisc --run tamarisk.llp`. Through the domain agent:
`python -m metis_agent.domain_agent --domain tamarisk --case replay`
(`METIS_RDDL_PY`: an interpreter with pyRDDLGym).
