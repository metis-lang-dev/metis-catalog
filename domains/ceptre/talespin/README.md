# talespin — a TALE-SPIN-style story generator

**License:** derived from interactive-lp's Ceptre examples (Chris Martens) and offered under the Anti-Capitalist Software License v1.4, not under this repository's Apache-2.0 grant: see [`../README.md`](../README.md) and [`../LICENSE`](../LICENSE).

Port of `interactive-lp/examples/talespin.cep` (Meehan 1976): a hungry bear asks a bird where the food is, is told, walks there, eats. Rule names kept; the original's `#interactive main` live.

Encodings (recipe rows "finite constructor terms" and "predicates over a constructor SUM type"):
- characters are built by constructors `joe animal`, `irving animal`, `wilma animal` (plus the constant `world`): 9+1 constants joe_bird … wilma_mouse, world, and the original's own bwd graph `is_animal (joe A) A` as is_animal(joe_bear,bear) etc.
- `information` is a SUM of three constructors (atf food location | atc character location | likes character character bool), and `question` likewise (wheref | wherec | does_like). Enumerating the sum as constants would be 260 values and tell_info would ground to millions; instead each predicate over the sum is SPLIT per constructor: knows C (atf F L) -> knows_atf(C,F,L), knows C (atc D L) -> knows_atc(C,D,L), knows C (likes D E Y) -> knows_likes(C,D,E,Y); asks likewise (asks_wheref/_wherec/_does_like). The bwd `answers Information Question` pairs each question constructor with its answer constructor (atf<->wheref, atc<->wherec, likes<->does_like), so the one tell_info rule that quantifies over it splits into tell_info_wheref / _wherec / _does_like — one rule per answers clause. The ground program is the original's, renamed.
- `solves_problem Any thirst water` is a Horn FACT WITH A VARIABLE, ported literally: fact vars are universally quantified over their position's type (spec §5), so Any ranges over every character.
- Loc/L' become Loc/M; `Someone` stays S.

$-OVERLAP SITES (tragedy-v3 caveat), written as consume-and-reproduce:
- ask: `$knows C (atc C Loc) * $knows C (atc Someone Loc)` — with Someone = C both name knows_atc(C,C,Loc). Ceptre needs TWO such tokens (each $ claims its own), so a character never asks ITSELF; a metis $-pair would let Joe ask Joe. Written as consume-two, reproduce-two.
- tell_info_*: the $knows premises can unify pairwise (Asker = Teller makes the two world-location reads one atom; Teller = world folds the answer read into them). Every knows premise of the three tell_info rules is written as consume-and-reproduce.
- ingest's `knows C (atc C L) … -o knows C (atc C L)` and move's `$knows C (atf F L')` have no same-atom partner: plain $-reads.

PUMPING RULE (noted, not fixed — the audit's explosion class): ask only reads (its consumes are all reproduced) and mints an asks token, so a hungry character asks again and again until fed; the asks for food nobody knows (Joe's honey) are never answered and pile up. Counts grow with the horizon.

Oddities kept: move may "move" to the place one already is (L = M); ingest consumes the world's food (eaten food is gone); the context lists `knows (wilma bird) (atc (joe bear) oak_tree)` twice (count 2); Wilma does not know where she herself is, so only Joe can ask.

Provenance: hand-port from `interactive-lp/examples/talespin.cep`, 2026-10-03.

The world takes no commands: the domain has no `intent.yaml`, and the domain agent opens it with no verbs (its clock beats, every intent is refused).

To run: `metisc --run talespin.llp` runs the case its `#` lines give; `#interactive main` lets you choose each event.
