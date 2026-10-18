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

**Baseline (rddl-worlds step 3, ruling A): the furthest stage.** The program's
`#init` step runs. At the next tick its stage pipeline is not restarted at its
first stage (the domain agent does not do that yet), so the program does not
take the step: the host says so by reading at once, and the gym's next state is
a surprise (one per episode; the beats after it have likelihood 0). Measured
over 20 seeded episodes in the step-3 report.

Run the case without the gym: `metisc --run tamarisk.llp`. Through the domain agent:
`python -m metis_agent.domain_agent --domain tamarisk --case replay`
(`METIS_RDDL_PY`: an interpreter with pyRDDLGym).
