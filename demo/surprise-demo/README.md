# surprise-demo — the pantry world

A synthetic teaching world for the metis surprise loop (metis-loop
`docs/SPEC.md` §1): a surprise record becomes mined text, then a
candidate pack, then `gate`, `accept` and a verified `replay`, all as
verbs of one `metis` REPL session. Written by hand on 2026-10-09 in
answer to the request "I haven't seen a transcript with a surprise in
the REPL; do a synthetic example first". It was the first such
transcript. The meadow version (`../synthetic-meadow/`) was recorded
about 15 minutes later.

## The planted gap

`pantry.llp` has a keeper, a pantry door, a cat and a mouse. The base
treats the door as the only way into the pantry. The keeper (when home)
opens and closes it, the cat walks through it, the cat hunts the mouse
in the pantry, and the cat scratches at the closed door (a pure-read
no-op). The broken floor vent is **deliberately left out**.

`runs/pantry-sink.jsonl` holds one hand-written `metis-surprise`
record ("house camera, day 3, keeper away"). The keeper is absent and
the door stays closed, yet after 4 steps the cat is inside the pantry,
the mouse is gone and the cat is fed. Without `keeper_home` no rule
can open the door, so the base gives this observation likelihood 0.
In other words, the rule is missing; no weight is wrong.

The base also opens its `hs` namespace to packs on purpose
(`namespace hs produce (dyn pack) consume (dyn pack)`). That is what
lets the fix be a **pack**. Containment admission (SPEC.md §4) allows a
pack to consume or produce a base atom only when the base namespace
grants that right. `vent_in` consumes `cat(kitchen)` and produces
`cat(pantry)`. Without the grant the same rule would have to go
through `revise` (a base edit: the world is replaced and accepted packs
are dropped).

## Walkthrough outcome (runs/pantry-demo-transcript.md)

| step | result |
|---|---|
| `trace` (embedded case, keeper home) | open, close, open, enter, hunt, close: the normal day |
| `record 0`, `replay` | likelihood 0, `explains: false` |
| `mine <text>` | approved text: the cat squeezes through the broken floor vent; the door never opened |
| `llp <<EOF` (hand-written; no `formalize` call) | pack `vent`, one rule `vent_in [pack] : cat(kitchen) * $door_closed -o cat(pantry)` |
| `gate` | green, class-F; support 3; `fed` 0 -> 0.6875, `cat(pantry)` 0 -> 0.9375 |
| `accept` | key fd07cf22... -> ea5be7ec... |
| `replay` | likelihood **0 -> 0.6875**, `fixed: true`, explanation `vent_in, hunt, scratch, scratch` |
| `why fed` (after `run 4`) | cone `#init -> vent_in -> hunt`; the keeper's open/close pruned as irrelevant |
| `necessity 1 fed` | PN ≈ 0.75 (but see the footgun below) |

Re-run on 2026-10-11 with the current metispy (piped stdin, the same
candidate). `gate`, `accept` and `replay` give the same key and the same
numbers (0.6875, `fixed: true`).

## Findings that cost effort

- **The `#init` case footgun.** The file's embedded case is a
  *normal* day (`#init keeper_home 1`), but the record's tick has no
  keeper. `record 0` adopts the record's init as the scene, and
  `trace`, `gate` and `replay` use that scene. The live session state
  stays on the embedded case until you `reset`. The transcript's
  `run 4` therefore ran with the keeper home (`vent_in open close hunt`,
  final state `keeper_home:1`), so its **PN ≈ 0.75 measures the
  normal-day world, not the surprise**. After `reset` on the record
  scene (re-run 2026-10-11) the result is `vent_in hunt scratch scratch`,
  and `necessity 1 fed` gives **PN ≈ 1** (without vent_in, P(fed) = 0,
  "impossible"). Rule: `record N` -> `reset` -> `run` before using
  any live-graph instrument (`why`, `necessity`, `query`, `state`).
- **Live-graph instruments need events.** `why fed` and `necessity`
  right after `accept` answered "never produced" / "needs an event of
  the graph". They read the session's fired-event graph, not a `trace`
  sample, so you must `run` first.
- **`gate` refuses without approved text.** `llp <<EOF` alone yields
  "empty source text — the text is the approved unit". Run
  `mine <text>` first. (`load FILE` instead adopts the file's leading
  comment block as the text when no text is set yet.)
- **The no-op `scratch` rule pads explanations.** `$cat(R) * $door_closed
  -o ()` stays enabled and soaks up the leftover steps of the 4-step
  horizon, so the MAP explanation ends in two `scratch` events. It is
  harmless, but it adds noise to narration and to `map`.
- **The pack does not mention the keeper.** `vent_in` can also fire on
  a normal day, where it races the door. SPEC.md §5 treats this as a
  race that the measure prices, not as a contradiction. The gate
  accepts it. Whether that is the intended story is a modelling
  choice, and it was not examined here.

## Not solved / not to retry

- The record is hand-written. Its `program_key` is `""`, and `replay`
  does not check it. No runtime produced it.
- The LLM seat (`ollama:gemma3:4b`) was configured but never used:
  the candidate was typed by hand. This demo says nothing about
  `formalize` quality.
- The vent pack exists only inside the transcript (heredoc). No
  `vent.llp` file was saved.
- `docs/TUTORIAL.md` does not use this world. Its "Closing the loop"
  section uses the meadow (`../synthetic-meadow/`).

## Evidence in this directory

- `pantry.llp`: the base world, with its gap and the normal-day `#init` case.
- `runs/pantry-sink.jsonl`: the surprise record (`kind: unmodeled`, likelihood 0).
- `runs/pantry-demo-transcript.md`: the REPL `transcript` log
  (2026-10-09 11:57). It contains every command, the heredoc body, the
  candidate snapshot and the accept. About 80 lines of it are the
  narrate system prompt boilerplate.

## How to run

```sh
cd metis-catalog/demo/surprise-demo
metis pantry.llp
llp> trace                         # the normal day (embedded case)
llp> sink runs/pantry-sink.jsonl
llp> record 0
llp> replay                        # likelihood 0, explains false
llp> mine the cat squeezes through the broken floor vent; the door never opened.
llp> llp <<EOF
catalog vent 1.
extends pantry.
provenance text "the broken floor vent, mined from record 0" "2026-10-09".
stage day {
  %% "it squeezes through the broken floor vent — the door never opened"
  vent_in [pack] : cat(kitchen) * $door_closed -o cat(pantry).
}
EOF
llp> gate
llp> accept
llp> replay                        # 0.6875, fixed: true
llp> reset                         # load the RECORD scene into live state
llp> run 4
llp> why fed
llp> necessity 1 fed               # PN ≈ 1 on the record scene
```

Add `transcript FILE.md` at the start to log a new session.
