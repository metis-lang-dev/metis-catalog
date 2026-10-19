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
| primed RULE names (`topR'`) | `topR-prime` — never `topR-1`: `<name>-<k>` is reserved for ⊕ branches (ll) |
| `_` wildcard in a premise | a fresh variable, e.g. `ctx(X)` (ll) |
| `$a` (read-only premise) | `$a` — identical, EXCEPT when the same rule also consumes or `$`-reads that same atom: Ceptre's `$a` claims its own token, metis's `$a` claims none (it fires one token early and prices `c·ff(c,k)` not `ff(c,k+1)`). There, write consume-and-reproduce out: `a * a * b -o a * c` (see tragedy v3 eroticize/divorce) |
| consume-and-reproduce (`a * b -o a * c`) | write what it denotes: `$a * b -o c` — same caveat as `$a` above when `a` also appears elsewhere in the body |
| `!a` in a HEAD (persistent product) | Ceptre's `!` splits into two disciplined cases. STATIC truth (never produced in a run — `!actor C`): not state at all; it is a type or a bwd fact — the Horn world IS the persistent zone (unlimited reads, no multiplicity). MONOTONE DYNAMIC truth (`!dead C`): plain atom + a one-shot PERMISSION the producer consumes — for monotone facts `!p` is interderivable with spending an affine permission token. Often the permission already exists: every tragedy death consumes the victim's single `at` token, so `dead(X) <= 1` is invariant with no extra atom (verified by lockstep, 5/5 seeds, and the exact measure). Inheritance rule: a `!`-fact whose only producers are themselves one-shot per instance (`!murdered C C'` behind the death) needs nothing. Add a fresh token (`life(C)`) ONLY when no consumed premise already enforces at-most-once; `$`-read the fact everywhere else |
| `!a` premise on a `!`-produced fact | `$a` |
| `-o ()` | `-o ()` — identical (the LL unit; canonical spelling) |
| two rules, same body, different heads | ONE rule with the ⊕ head: `-o ( h1 @w 1 | h2 @w 1 ).` (expands to `name-1`, `name-2`) |
| `stage s {...}` + `qui * stage s -o stage s'` transitions | `stages (s s' ...).` + `stage s {...}` + `qui name [layer] : s -o s'.` links |
| STATE-CARRYING transitions (`qui * stage s * a -o stage t * b`) | the link takes premises and products beside the stage names: `qui name [layer] : s * a -o t * b.` (fptp `elect`, herstory `act2`..`act4`) |
| `#interactive s.` | `#interactive s` directive (menu on stderr, choice on stdin; EOF falls back to the sampler) |
| `context init = {a, b, ...}.` | `#init a 1` directive lines (one per atom, counts explicit) |
| `#trace _ s init.` | `#steps N` + `#seeds K` (+ `#query atom` for presence counts) |
| finite constructor terms (`top_of ring : place`, `(top_of R)` in rules) | LLP terms are flat (`term ::= ident \| num`). Enumerate the constructor's image as named constants of the target type (`top_r1 …`), declare the constructor as a bwd GRAPH relation with one fact per constant (`topof(r1,top_r1).`), and where the original writes `(top_of R)` write a fresh var plus the guard: `clear(T) * topof(R,T)`. Grounding prunes the rest, so the ground program is the original's (tower_of_hanoi, cellular-automata) |
| RECURSIVE constructor types (`lolli prop prop : prop`) | no finite type holds them: enumerate only the subterms of the original's context (subformula property — check the rules only ever produce direct subterms of their premises), name them so they spell the term, and use the graph-relation row above. State the bound in the header; a new context needs a new enumeration (ll) |
| `#builtin NAT` / `s nat : nat` unary naturals | no counterpart: bound `nat` to an enumerated range (`n0..n2`) and make `s` the bwd successor graph `s(X,SX)`. State the bound in the header (cellular-automata) |
| predicates over a constructor SUM type (`knows C (atf F L)` with `information` = atf \| atc \| likes) | enumerating the sum as constants explodes grounding; SPLIT the predicate per constructor (`knows_atf(C,F,L)`, `knows_atc(C,D,L)`, …), and split any rule that quantifies over the sum (e.g. via a bwd `answers Info Question` pairing constructors) into one rule per case, named `rule_case` (never `rule-k`). Ground program = the original's, renamed (talespin) |
| Horn FACT with variables (`plus z N N.`, `solves_problem Any thirst water.`) | port it literally: `plus(n0,N,N).` — a fact var is universally quantified over its position's type (spec §5, since 2026-10-04; both toolchains). Only a query that leaves it UNBOUND (a reads-scope guard) is an error — guard such a var with a predicate that enumerates it (primes, talespin) |
| empty `stage s = { }` / `context init = {}` | `stage s { }` is legal; no `#init` lines (the world starts empty and quiesces at once) |
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
| 3lp | 25 | 1 | yes |  | ported | three_pigs/three_pigs.llp | catalog `three-pigs` (no leading digit in idents); consume-and-reproduce blows written as $-reads — survival is WHICH premise is `$` (`$wolf * strawhouse` vs `wolf * $brickhouse`); exact: brick 1, straw/stick 0.5 each, wolf spent 1; `#interactive go` live |
| arith | 26 | 1 |  | yes |  |  |  |
| barman | 121 | 1 | yes | yes |  |  |  |
| blocks-world | 37 | 1 | yes |  | ported | blocks_world/blocks_world.llp | 1:1, no frame axioms; win_condition commented in the original (kept) so the world never quiesces; exact: the 6-move plan c-table/b-on-c/a-on-b reached by a random walk at 6 steps with P[on(a,b)]=1/27; no $-overlap, no pumping |
| broadcast | 41 | 3 |  |  |  |  |  |
| buffy-reenactment | 352 | 5 | yes | yes |  |  |  |
| buffy-thesis | 390 | 6 | yes | yes |  |  |  |
| buffy | 498 | 7 | yes | yes |  |  |  |
| cell | 54 | 1 |  | yes |  |  |  |
| cellular-automata | 35 | 2 |  | yes | ported | cellular_automata/cellular_automata.llp | the original is a SKELETON ("wrote no actual code yet"): both stages empty, empty context; ported as-is (grid + nbr, no update rule invented — a v2 for the user to author). nat bounded to n0..n2 (`#builtin NAT` has no counterpart); `pos` via the constructor-graph row; the 8 nbr facts give 6 of 8 Moore neighbours (anti-diagonal absent — kept) |
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
| fptp | 51 | 3 |  | yes | ported | fptp/fptp.llp | state-carrying qui links (`count -o pick * max(n0)`, `pick * hopeful(C,N) -o done * elected(C)`); `!elected`/`!defeated` via the P4 workaround (produced once: each producer consumes the candidate's single hopeful token); nat bounded n0..n6 (6 ballots); exact: alice elected P=1, bob/charlie defeated P=1; ties would be elected uniformly (kept, none here); no $-overlap, no pumping |
| garden-iter3 | 136 | 3 | yes | yes |  |  |  |
| garden-med | 87 | 3 | yes | yes |  |  |  |
| garden-small | 63 | 2 | yes | yes |  |  |  |
| garden | 141 | 3 | yes | yes |  |  |  |
| gossip | 61 | 2 |  |  | ported | gossip/gossip.llp | `says` nesting flattened (unbounded constructor — outside the finite-type fragment); !posted/!knows latching via not_posted/unheard once-tokens (P4 recipe); posters keep NOT knowing their own initial posts (original quirk, see `knows(p1,m1)` query); closure identical over 3 seeds; read->say link guarded by `$not_posted` so the saturated network QUIESCES (the original ping-pongs to the step bound) |
| grammar-tinkering | 90 | 1 |  | yes |  |  |  |
| hearthstone | 61 | 3 |  | yes |  |  |  |
| hello-world | 10 | 1 | yes |  |  |  |  |
| herstory | 112 | 4 |  |  | ported | herstory/herstory.llp | 4 acts = 4 stages, named state-carrying links; oddities kept (date_carl consumes alive carl, parents_die leaves no dead atoms); every life/death marginal is exactly 0 or 1 — the plot is determined, only the interleaving varies; no $-overlap, no pumping |
| if-rpg | 1 | 0 |  |  |  |  |  |
| if | 56 | 1 | yes | yes |  |  |  |
| instant-runnoff-voting | 103 | 5 | yes | yes |  |  |  |
| interative-stage-test | 15 | 1 | yes |  |  |  |  |
| lambda-ed | 83 | 2 | yes | yes |  |  |  |
| leq | 14 | 0 |  | yes |  |  |  |
| ll | 56 | 1 | yes |  | ported | ll/ll.llp | recursive `prop` enumerated as the subformulas of `context test` (bound stated); topR' -> topR-prime, `_` -> X; the original's open question "oneR requires quiescence/absence?" kept OPEN in the header (not solved); with rules commented as in the original; the test theorem is proved on every run (P=1, all goals/ctx consumed) |
| lola | 392 | 2 | yes |  |  |  |  |
| love-triangle | 35 | 1 | yes | yes | ported* | love_triangle/love_triangle.llp | tutorial-variant port (ceptre-tutorial sol); examples/ version differs slightly — re-diff when touched |
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
| primes | 34 | 2 |  | yes | ported | primes/primes.llp | limit 12 (the original's own) -> nat n0..n12; plus/mult Horn clauses (plus/z, mult/z: quantified facts, literal); **$-overlap site**: collide's `$here N * here M` with `_`=1 makes M=N — written consume-and-reproduce (the literal `$` form erases every prime: P[here(n7)]=0); exact: primes 2,3,5,7,11 survive P=1, composites P=0; no pumping |
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
| talespin | 122 | 1 | yes | yes | ported | talespin/talespin.llp | character constructors via the graph row; the `information`/`question` SUM types split per constructor (knows_atf/_atc/_likes, asks_*; tell_info -> tell_info_wheref/_wherec/_does_like); `solves_problem Any …` ported literally (quantified fact); **$-overlap sites**: ask (Someone=C) and the tell_info knows pairs — consume-and-reproduce; **pumping**: ask (re-asks until fed; unanswered honey asks pile up) — noted, not fixed; P[fed @8]=0.43 |
| thanksgiving | 52 | 1 |  |  |  |  |  |
| tiny | 7 | 0 |  |  |  |  |  |
| tower_of_hanoi | 56 | 1 | yes | yes | ported | tower_of_hanoi/tower_of_hanoi.llp | `top_of R`/`bottom P` via the constructor-graph row (`topof`/`bottomof` bwd); `smaller` = the original's Horn closure over `succ` (first `:-` rules in the catalog); unused constant `post : place` dropped, noted; optimal solve = 7 moves = 14 steps; no $-overlap, no pumping |
| tragedy | 220 | 1 | yes | yes | ported | tragedy/tragedy.llp | v2: adds the `<>` guards the original lacked (self-murder/steal/witness/vengeance artifacts removed; suicide stays the one self-death); ⊕ head (formOpinion), $-read idiom, `#interactive all` live. v3: eroticize/divorce written as consume-and-reproduce — the original's `$a` beside `a` needs its own token (fidelity fix) |
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

## Lockstep verification (tools/ceptre_lockstep.py)

The REAL Ceptre interpreter (built at `../interactive-lp/ceptre`)
driven in lockstep against a port: every interactive menu must
equal the metis `events` menu — instance set AND token
multiplicities (a Ceptre menu lists one entry per token choice,
which IS transition_count) — the sampled choice (the metis measure;
Theorem 1: parity prior = Ceptre's picker) is fed to both, and the
final states must be identical. The .cep runs from a printed-edit
temp copy (`#interactive` ensured; `--drop-line` for lines current
Ceptre rejects). Verified 2026-10-04, seeds 1-3 unless noted:

    T=tools/ceptre_lockstep.py; E=../interactive-lp/examples
    $T domains/three_pigs/three_pigs.llp $E/3lp.cep
    $T domains/love_triangle/love_triangle.llp $E/love-triangle.cep
    $T domains/tragedy/tragedy.llp $E/tragedy.cep --steps 300 \
      --strip-prefix do/ \
      --alias formOpinion-like=formOpinion-1 \
      --alias formOpinion-dislike=formOpinion-2 \
      --alias mixed_feelings=mixed-feelings \
      --alias ending_1=ending-marriage-and-death \
      --alias ending_2=ending-love-triangle \
      --alias ending_3=ending-vengeance
    $T domains/blocks_world/blocks_world.llp $E/blocks-world.cep --steps 30
    $T domains/tower_of_hanoi/tower_of_hanoi.llp $E/tower_of_hanoi.cep \
      --steps 80 --drop-line '^post : place\.' \
      --ctor topof=top_of@2 --ctor bottomof=bottom@2 \
      --proj pickup=2,3 --proj putdown_on_ring=1,3 \
      --proj putdown_on_post=1,3
    $T domains/ll/ll.llp $E/ll.cep \
      --ctor at=at --ctor tensor=tensor --ctor lolli=lolli \
      --proj lolliR=2,3 --proj lolliL=2,3 --proj tensorL=2,3 \
      --proj tensorR=2,3 --proj init=2

Results: 3lp, love_triangle (self-anger states included),
blocks-world, tower_of_hanoi (80 menus/seed), ll (proof to the
empty context) and tragedy (seeds 1-5, 65-300 menus each, final
states to 366 tokens) ALL lockstep-identical. An earlier run had
flagged tragedy seed 2 as a `!dead` persistence gap; that was
withdrawn on evidence — `dead(X) <= 1` is structural in the port
(every death consumes the victim's single `at`: the de-facto
permission token; confirmed by the exact measure and by the full
seed-2 drive), and the transient mismatch did not reproduce (one
component was this tool's own final-state parser dropping `!`
inside parenthesized facts, since fixed). The `!a` recipe row now
carries the general reduction. Broken originals (the interpreter
itself says so): gossip.cep crashes ("0 is an invalid program
index", the #trace stage name), tower_of_hanoi.cep does not load
("Cannot redefine post as a constant") — both oddities the ports
documented.
