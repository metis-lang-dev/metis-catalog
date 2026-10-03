# Ceptre → metis: one-to-one porting track

Source: `~/repo/perotheia-packages/interactive-lp/examples/*.cep`
(github.com/chrisamaphone/interactive-lp, checkout pinned locally).
Ports land beside this file under `domains/<area>/<name>.llp`, one
`.cep` → one `.llp`, original rule names kept (with the spelling map
below). Every port is automatically roundtrip-gated by `make check`
(ci/check.sh walks `domains/*/*.llp`). Run a port with
`../metis-lang/src/metisc --run domains/<area>/<name>.llp`.

## The porting recipe (hands-on cheat sheet)

| Ceptre | LLP |
| --- | --- |
| `t : type.` + `c : t.` constants | `type t {c1 c2 ...}.` (finite, enumerated; ranges `s1..s9`) |
| `p t1 t2 : pred.` | `pred p(t1,t2) : <namespace>.` (declare `layers`, a `namespace ... produce (...)`) |
| `p t1 t2 : bwd.` + bwd rules | `bwd p(t1,t2).` + Horn facts `p(a,b).` / rules `h :- b1, b2.`; use the bwd atom directly in rule bodies as a guard |
| `name : A * B -o C.` | `name [layer] : A * B -o C.` — plus a mandatory `%%` doc line above (compiler rejects undocumented rules) |
| `rule/sub/name` | `rule-sub-name` (no `/` in idents) |
| primed vars `C' C'' L'` | rename: `D E M` (no `'` in idents) |
| `$a` (read-only premise) | `$a` — identical, EXCEPT when the same rule also consumes or `$`-reads that same atom: Ceptre's `$a` claims its own token, metis's `$a` claims none (it fires one token early and prices `c·ff(c,k)` not `ff(c,k+1)`). There, write consume-and-reproduce out: `a * a * b -o a * c` (see tragedy v3 eroticize/divorce) |
| consume-and-reproduce (`a * b -o a * c`) | write what it denotes: `$a * b -o c` — same caveat as `$a` above when `a` also appears elsewhere in the body |
| `!a` in a HEAD (persistent product) | plain atom produced once; `$`-read it everywhere else (make sure the producer consumes something that prevents re-production — else you need the guard machinery; see spec 07 P4) |
| `!a` premise on a `!`-produced fact | `$a` |
| `-o ()` | `-o ()` — identical (the LL unit; canonical spelling) |
| two rules, same body, different heads | ONE rule with the ⊕ head: `-o ( h1 @w 1 | h2 @w 1 ).` (expands to `name-1`, `name-2`) |
| `stage s {...}` + `qui * stage s -o stage s'` transitions | `stages (s s' ...).` + `stage s {...}` + `qui name [layer] : s -o s'.` links |
| `#interactive s.` | `#interactive s` directive (menu on stderr, choice on stdin; EOF falls back to the sampler) |
| `context init = {a, b, ...}.` | `#init a 1` directive lines (one per atom, counts explicit) |
| `#trace _ s init.` | `#steps N` + `#seeds K` (+ `#query atom` for presence counts) |
| unweighted nondeterminism | leave weights off (prior 1.0) — or start modeling: that's the point of the port |

Fidelity first, then measure: port 1:1 (keep even the original's
oddities, commented), get `--run` traces that look like the Ceptre
author intended, THEN consider a v2 with weights/ports where the
domain earns them. Ceptre allows a variable to unify with itself
across premise positions (C and D may bind the same constant); so
does metis grounding — add `C <> D` only where the original had
`neq`.

## The track

status: blank = unclaimed · `wip` = being ported · `ported` =
runs under `metisc --run` and passes the roundtrip gate.

| example | lines | stages | #interactive | bwd | status | port | notes |
| --- | ---: | ---: | --- | --- | --- | --- | --- |
| 3lp | 25 | 1 | yes |  |  |  |  |
| arith | 26 | 1 |  | yes |  |  |  |
| barman | 121 | 1 | yes | yes |  |  |  |
| blocks-world | 37 | 1 | yes |  |  |  |  |
| broadcast | 41 | 3 |  |  |  |  |  |
| buffy-reenactment | 352 | 5 | yes | yes |  |  |  |
| buffy-thesis | 390 | 6 | yes | yes |  |  |  |
| buffy | 498 | 7 | yes | yes |  |  |  |
| cell | 54 | 1 |  | yes |  |  |  |
| cellular-automata | 35 | 2 |  | yes |  |  |  |
| citysim | 68 | 4 |  |  |  |  |  |
| civ | 63 | 2 | yes |  |  |  |  |
| cloak_of_darkness | 58 | 1 | yes | yes |  |  |  |
| cocktails | 49 | 1 |  |  |  |  |  |
| cocktails2 | 468 | 2 | yes | yes |  |  |  |
| comicgen | 228 | 5 | yes | yes |  |  |  |
| context-test | 13 | 1 |  |  |  |  |  |
| cooking-multistage | 99 | 3 | yes |  |  |  |  |
| cooking-v1 | 100 | 1 |  |  |  |  |  |
| cooking | 83 | 1 | yes |  |  |  |  |
| defense-defense | 117 | 6 | yes | yes |  |  |  |
| drama_llamas | 153 | 1 | yes | yes |  |  |  |
| ecology | 25 | 1 | yes |  |  |  |  |
| elements | 31 | 1 | yes |  |  |  |  |
| family-tree-inverted-with-siblings | 87 | 1 | yes | yes |  |  |  |
| family-tree-inverted | 78 | 1 | yes | yes |  |  |  |
| family-tree | 105 | 1 | yes | yes |  |  |  |
| five | 79 | 1 |  |  |  |  |  |
| fptp | 51 | 3 |  | yes |  |  |  |
| garden-iter3 | 136 | 3 | yes | yes |  |  |  |
| garden-med | 87 | 3 | yes | yes |  |  |  |
| garden-small | 63 | 2 | yes | yes |  |  |  |
| garden | 141 | 3 | yes | yes |  |  |  |
| gossip | 61 | 2 |  |  | ported | social/gossip.llp | `says` nesting flattened (unbounded constructor — outside the finite-type fragment); !posted/!knows latching via not_posted/unheard once-tokens (P4 recipe); posters keep NOT knowing their own initial posts (original quirk, see `knows(p1,m1)` query); closure identical over 3 seeds; read->say link guarded by `$not_posted` so the saturated network QUIESCES (the original ping-pongs to the step bound) |
| grammar-tinkering | 90 | 1 |  | yes |  |  |  |
| hearthstone | 61 | 3 |  | yes |  |  |  |
| hello-world | 10 | 1 | yes |  |  |  |  |
| herstory | 112 | 4 |  |  |  |  |  |
| if-rpg | 1 | 0 |  |  |  |  |  |
| if | 56 | 1 | yes | yes |  |  |  |
| instant-runnoff-voting | 103 | 5 | yes | yes |  |  |  |
| interative-stage-test | 15 | 1 | yes |  |  |  |  |
| lambda-ed | 83 | 2 | yes | yes |  |  |  |
| leq | 14 | 0 |  | yes |  |  |  |
| ll | 56 | 1 | yes |  |  |  |  |
| lola | 392 | 2 | yes |  |  |  |  |
| love-triangle | 35 | 1 | yes | yes | ported* | fiction/love_triangle.llp | tutorial-variant port (ceptre-tutorial sol); examples/ version differs slightly — re-diff when touched |
| mario | 96 | 1 | yes | yes |  |  |  |
| mazegen | 70 | 4 |  | yes |  |  |  |
| mazegen2 | 78 | 5 |  | yes |  |  |  |
| minecraft | 35 | 1 | yes |  |  |  |  |
| move_grid | 81 | 1 | yes | yes |  |  |  |
| negation | 24 | 3 |  |  |  |  |  |
| numbers | 19 | 1 |  |  |  |  |  |
| pandemic-multistage | 189 | 4 | yes | yes |  |  |  |
| pandemic | 98 | 1 | yes | yes |  |  |  |
| paper | 182 | 7 |  |  |  |  |  |
| parable | 37 | 0 |  | yes |  |  |  |
| planting | 45 | 1 | yes |  |  |  |  |
| primes | 34 | 2 |  | yes |  |  |  |
| printXY | 36 | 1 |  |  |  |  |  |
| professor | 31 | 1 | yes |  |  |  |  |
| promweek | 1 | 0 |  |  |  |  |  |
| quarto | 140 | 2 |  | yes |  |  |  |
| recipes | 143 | 1 | yes | yes |  |  |  |
| regexp | 105 | 3 | yes | yes |  |  |  |
| relgraph | 71 | 1 | yes | yes |  |  |  |
| rope | 87 | 1 | yes | yes |  |  |  |
| rpg-tiny | 34 | 2 | yes |  |  |  |  |
| rpg | 230 | 11 | yes | yes |  |  |  |
| sense | 40 | 2 |  |  |  |  |  |
| shuffle | 20 | 1 |  |  |  |  |  |
| siedler1 | 150 | 5 | yes | yes |  |  |  |
| siedler_core | 50 | 2 | yes |  |  |  |  |
| simwar | 114 | 7 | yes | yes |  |  |  |
| small-charsim | 48 | 1 | yes |  |  |  |  |
| small | 73 | 4 |  | yes |  |  |  |
| snake | 132 | 1 | yes | yes |  |  |  |
| social-practice-meeting | 110 | 2 | yes | yes |  |  |  |
| social_story_gen | 138 | 1 |  | yes |  |  |  |
| sokoban-checkwins | 50 | 5 |  |  |  |  |  |
| sokoban-grid | 82 | 1 | yes | yes |  |  |  |
| sort | 45 | 3 |  | yes |  |  |  |
| string-grammars-direct | 81 | 1 |  | yes |  |  |  |
| string-grammars | 81 | 1 |  | yes |  |  |  |
| string-input | 48 | 1 | yes | yes |  |  |  |
| talespin | 122 | 1 | yes | yes |  |  |  |
| thanksgiving | 52 | 1 |  |  |  |  |  |
| tiny | 7 | 0 |  |  |  |  |  |
| tower_of_hanoi | 56 | 1 | yes | yes |  |  |  |
| tragedy | 220 | 1 | yes | yes | ported | fiction/tragedy.llp | v2: adds the `<>` guards the original lacked (self-murder/steal/witness/vengeance artifacts removed; suicide stays the one self-death); ⊕ head (formOpinion), $-read idiom, `#interactive all` live. v3: eroticize/divorce written as consume-and-reproduce — the original's `$a` beside `a` needs its own token (fidelity fix) |
| vampire | 34 | 1 |  |  |  |  |  |
| werewolves-witches-slayers | 231 | 8 | yes | yes |  |  |  |
| wilds | 12 | 1 |  |  |  |  |  |

`*` the love-triangle port predates this track.

Non-`.cep` material in the source tree (`broken/`, `non-ceptre/`,
`tamara/`, `regression/`) is out of scope.

## Bus candidates (multi-interpreter cooperation)

Scan 2026-10-03, for the loop bus (metis-loop `loop/bus.py`: N
`metis --json` interpreters message-passing through the broker's
dict-as-blackboard — SPEC §10 tier 2). Criterion: the example cuts
into interpreters whose INTERFACE (predicates crossing the cut) is
narrow relative to each side's own vocabulary; the interface
atoms become blackboard keys, moved by a driver. Heuristic scan
(cross-stage shared-predicate ratio over all 96 `.cep`) plus a
read of the shapes. Port each side 1:1 per the recipe above; the
cut itself is DRIVER policy, never new syntax.

| example | cut (one interpreter each) | interface → bb keys | why it's bus-shaped |
| --- | --- | --- | --- |
| gossip | one world per PERSON (or say vs read) | `posted P M` | literally a message board: `!posted` is a blackboard write, `knows` is private state — the flagship |
| simwar | one world per PLAYER (symmetric; `#interactive play`) | `turn T`, visible `money/factories/offense/defense` | two-seat war sim; each seat's hidden hand stays private, the bb is the table |
| defense-defense | one world per TEAM (blue/yellow) | `team_turn T`, `attack`, `health` | turn alternation is already a hand-off token |
| garden (+ -iter3/-med/-small) | NATURE (advance_day/grow) vs GARDENER (`#interactive play`) | plant status atoms (`healthy/wilting/dead/needs_water`) | agent-vs-world; the gardener reads the garden's word, never its mechanism |
| pandemic-multistage | BOARD (infect/outbreak) vs PLAYERS (actions) | `disease C N`, `outbreaks N`, turn token | co-op board game = shared board, private seats |
| siedler_core / siedler1 | ECONOMY vs TURN mechanics | `development_card` (core: 1/21 shared — the narrowest seam in the corpus) | the economy serves any number of player worlds |
| cooking-multistage | KITCHEN (timers) vs COOK (actions) | `in_pan`, `pre_timepass` (2/30) | the pan does not care who stirs |
| lola | CITY world vs CHARACTER (beliefs/desires) | `location`, `has`, observations | BDI agent against a world — the loop's own shape (world posts surprises, agent formalizes) |

Anti-candidates, for contrast: mazegen/sort/primes/regexp are
PIPELINES (stages = phases of one algorithm — parallelizing them is
tier 1, Foata layers, not the bus); cocktails2/rpg share ~half
their vocabulary across stages (one world, thick seams).

First wiring to try: gossip with three person-worlds — each
interpreter's `posted` head becomes a driver `bb_set`, each
`knows` init a driver `bb_get`+`init`, and the bus run should
reproduce the single-world trace (the same propagation, now
message-passed). That reproduction IS the acceptance test of the
cut.
