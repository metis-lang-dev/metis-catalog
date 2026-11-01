# road — the road family: the platform-neutral road semantics over roles

**The family** (road-family s-f62c0ed8, 2026-11-01; metis-lang spec/18 §1, §6): the rules every road platform shares, written over ROLES, geometry in the host, prices in the projection's parameters (the framework's six rules, road-world s-e812715d). Two consumers derive from it (spec/18 §2: inclusion by name, extension by packs, parametrization, unit choice; never a copy, never an override): the road WORLD (metis-worlds `road/`: cars on the exerciser, SUMO and CARLA's Town nets) and the WHEELCHAIR (metis-wheelchair: the chair on the sidewalk among people). Each names its own host and includes these units through `METIS_HOME` = this directory, at a pin of this repository.

| unit | what | who includes it |
| --- | --- | --- |
| `capacity.llp` | the role vocabulary and the closed types the instance completes: lead, follower, leadleft/followleft, leadright/followright, a1..a3, vru1; nextzone; the sides; the situation layer's constellations and responses | every consumer (the chair's `capacity.llp` extends it with the walker roles and wc's zone roles) |
| `tick_types.llp` | the protocol's types for the tree | every consumer |
| `responder_domain.llp` | the FAST member: the proper response (brake at the asked response, stop a lateral move toward a side a response stands at, hand the controls back; the free-space response for a person near the chair). FINAL: no consumer changes it | every consumer |
| `planner_domain.llp` | the SLOW member without the lane change: the safety stage (yield at a zone not the ego's, the walker, the zipper, the crossing's soft brake) before the progress stage (accel with room, keep at the limit, keep the gap, follow a slow lead, ease off behind a closing lead) | the chair (the sidewalk has no lanes to change) |
| `change.llp` | the lane change: a unit of its own that brings `planner_domain.llp` with it (spec/18 §3: a leavable block lives in a unit of its own) | the car (the road world) |
| `responder/`, `planner/` | the family's member packages: the programs over the units, the cases, no host (a consumer's package names its host) | the family's own cases and traces |
| `goldens/traces/` | the members' traces (metisc --run), byte for byte | CI |

**The ports.** The family's rules read verdicts, never numbers (rule 2). The prices a platform sets are the projection's parameters in `libs/semantic-world` (`situation`, `dynamics_for`: the RSS response times and accelerations, the lateral margins, the stopping reach that defines `near`), passed by the consumer's host, and the rules' `@w` weights (e.g. `keep_lead` 0.01). A number that differs by platform never enters a rule.

**What comes next** (road-family steps 3–4): `junction.llp` (priority at a zone over the roles the projection emits on a junction's internal lanes) and `signals.llp` (semaphores: `signal(zone, state)`), learned and refined by the pi loop on traces (trace-replay s-c111ff41), with this family's, the road world's and the chair's goldens as the gate.

**Provenance.** From metis-catalog `domains/road` (parked, 2026-10) to metis-worlds `road/domains` (road-move, 2026-10-26: the domains beside their world) and back as the family (2026-11-01), the world keeping its world: the exerciser, the SUMO host, the car members' hosts, the director and the page.
