# port-proto: the port-plugin conformance fixtures

**What:** three small catalogs whose rates and inputs come from a live
Python environment through the **PortPlugin** protocol (bind / tick /
on_event / snapshot / restore). The protocol contract lives in metis-loop
`docs/PLUGIN-PORTS.md`, the implementation in metispy (`metis/fw/plugin.py`,
REPL verbs `plugin`/`ports`/`port`/`tick`/`notch`, `#plugin` directive).
These fixtures were the acceptance tests of subject port-plugins
(s-63feaf1d). The Wildfire, Tamarisk and elevators catalogs
(`../../rddl/`) are served the same way: `metis --plugin X:make FILE.llp`.

**Why it matters:** this is the runtime half of the LL/runtime split.
- The catalog declares `weight f(args) reads {scope}` and prices
  outcomes `@w f | @w ~f`.
- The value comes at serve time from a binding: a plugin base, plus
  session or episode notch overlays.
- The catalog key never changes when a rate does.

## The fixtures

| fixture | catalog + plugin | proves |
|---|---|---|
| sensor | `sensor.llp` + `sensor_plugin.py` (+ `sensor_leaky.llp`) | a weight reads live env: a tick closing the gap 18 m → 6 m re-prices `query crash` 0.3 → 0.9 exactly; counterfactual honesty (`whatif 0 do(+ck)` prices both arms under the env as it was at #0: 0.51 / 0.3, while live is at 6 m); `fork`/`back`/`undo` restore the env; session notch overlay 0.2857 then `notch pop` → 0.3; **G5** scope teeth: `sensor_leaky` (declares `reads {}` but reads more) raises `ScopeViolation`, listed as `reads-undeclared` |
| reservoir | `reservoir.llp` + `reservoir_plugin.py` | a REAL-valued state behind a port: the level behind `pspill`, the season clock behind `prain`; 14-day episodes; every spill under the high class; release actuation feeds back into the env; notch rows per read-scope class (`pspill | highc=1 : 0.253 → 0.302 (n=5)`) |
| clock | `clock.llp` + `clock_plugin.py` | the TIME/input face: scheduled door and customer arrivals injected as exogenous `[env]` rows; 3 sales in hours, 1 missed after close; `why missed` names `do +customer` and `lose`; **G6**: a quiet world ticks instead of latching DONE |

Run (metispy venv, from this directory): `python clock_proto.py`, `python
port_proto.py`, `python reservoir_proto.py`. The drivers speak only REPL
verbs to a `metis` subprocess (`_drive.py`) and rewrite `transcripts/<name>.md`.
`kernel-face/` keeps the original drivers, which used internal APIs
(`weight_policy`, `onecmd`, `_candidates`), for comparison.

## Intelligence: what cost effort

1. **G6 — quiescence is not death.** The kernel's `do_step` latched
   stage=DONE at quiescence, and a world with an env attached never
   revived. Now, with a plugin attached, quiescence ticks the env:
   - `tick()` returning `[]` is a quiet beat;
   - only `None` ends the episode;
   - a tick at DONE revives the stage the world rested in.
   This is the same area as the bridge-torch post-terminal qui-spin
   (`../../planning/bridge-torch/`).
2. **Exogenous input is a fired row, not a hand `do`.** A hand `do`
   rebases the graph, so fork/whatif could not reach back past the last
   tick. As `exo` rows (`[env]` in log/graph/why/narrate), input is
   first-class, replays exactly, and is **excluded from the likelihood**
   (conditioning, not chance).
3. **Env snapshots ride with every world snapshot**: one per fired row,
   restored by fork/back/undo/reset. whatif prices each arm under its
   own env snapshot. Without this, counterfactuals silently use the
   live env.
4. **G5 — scope must have teeth in the SAMPLING tier too.** The sampler
   lacked ScopedCounts, so an undeclared read went unnoticed.
   `PortPricer` (name-keyed, scoped by default) prices every interactive
   tier identically: masked, pruned or quotient programs. The exact
   tier runs on the priced whole world, never the quotient, because a
   port's scope can name atoms the quotient drops.
5. **Policy index spaces.** `run_trace` indexes by `canonical_events`,
   the filter by `program.events()`. Use `pricer.policy(prog,
   canonical=True)` for traces. This bug priced the wrong events until
   Wildfire caught it.
6. **Unbound ports are strict.**
   - A catalog with an unbound `@w f` refuses to serve.
   - A reload keeps the old catalog.
   - At gate it is a finding.
   - `accept` refuses atomically (fixed after Tamarisk).
   Before, an unbound port was silently treated as weight 1.
7. **D4: the plugin is operator code, terminal only.** The web or shared
   console never imports a plugin, and a ported catalog is refused
   there. metisc (OCaml) rejects `#plugin`.
8. **Session notch = the paired estimator.** Only SAMPLED port-priced
   steps count (forced/do/env rows never do). The prior is the mean
   base value at the exposures. The posterior is (α·p0+s)/(α+n), α=10.
   For episode data, see the notches in `../../rddl/wildfire/`
   (whole-step rejection) and `../../rddl/tamarisk/` (per-slot, EM).

## Not solved / open

- Env inside a cone: port values are constant per arm snapshot. A tick
  that changes the env mid-horizon breaks the static cone (sampled tier
  only, or segment the horizon per beat).
- Who supplies the env fixture for gate scenarios of port catalogs: the
  factory takes the case row, which is not specified further.
- `weight_policy` (the legacy path) is not scoped by default. Turning it
  on may surface latent scope violations in production bindings.
- An `@env` footprint chaining exo rows into the causal graph is parked.
