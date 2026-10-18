# three_pigs_connectives — The Three Little Pigs as a tour of linear logic's connectives

The Three Little Pigs as a tour of linear logic's connectives — simultaneity (A ⊗ B), alternatives (A & B), the unit (1) and, as a contrast, internal choice (A ⊕ B). A variant of the three_pigs domain; only `blow_stick` differs.

The program is `three_pigs_connectives.llp` (the file was `3lp_connectives.llp`), a variant of the `three_pigs` domain (`domains/three_pigs/`). Its catalog line is `catalog three-pigs-connectives 1.`

**Provenance**: `hand "tutorial: 3lp with ⊗ / & / ⊕" "2026-10-05"`.

## The connectives

- **⊗** tensor, "A and B, both at once" — LLP: `A * B`
- **⊸** lolli, "consume the left, give the right" — LLP: `-o`
- **1** unit of ⊗, the null resource (A ⊗ 1 ≡ A) — LLP: `()`
- **&** external choice, "you pick A or B" — the rules enabled in one state that compete for a resource, resolved by YOU when the stage is `#interactive`
- **⊕** internal choice, "the world picks" — an alternative head `( A @w a | B @w b )`, one site, weights a:b

`$A` is not an LL connective: it is sugar for consume-and-reproduce, so `$wolf * strawhouse -o ()` is `wolf ⊗ strawhouse ⊸ wolf`.

## The story

Three pigs (3), one wolf (1), one load each of straw, sticks, and bricks. Each pig builds a house from one material. The wolf then blows at the houses: a blow at the straw house fells it, a blow at the stick house mostly fells it (0.75) but sometimes it holds (0.25), and a blow at the brick house spends the wolf, so which houses stand depends on the order.

Simultaneity: events whose footprints are disjoint share a Foata beat — `trace` prints `build_straw | blow_stick` in one beat: their resources are available at once, so is the pair of events.

Alternatives: most enabled rules do not really compete (a build and a blow touch disjoint atoms; either order gives the same beats). The one real & is `blow_stick & blow_brick` once both houses stand: both need the single wolf, and `blow_brick` consumes him. Pick `blow_brick` first and the stick house survives — that is 3lp's exact=0.5.

The ⊕ variant: the wolf's attempt at the stick house is itself a chance event. 3 in 4 it falls; 1 in 4 it holds (the house is reproduced and the wolf may try again). The parser expands the head into `blow_stick-1` / `blow_stick-2`, one CHOICE site sharing the body.

Lesson in the weights: branch weights are not just a split of the outcome — their SUM is the site's rate against every rival in the & menu. Written as `@w 3 | @w 1` the site weighs 4 against `blow_brick`'s 1, the wolf goes for the stick house first far more often, and stickhouse survival FALLS to exact≈0.33. Written as probabilities, `@w 0.75 | @w 0.25`, the site keeps the old rate 1:1 and only the outcome splits: stickhouse survival RISES from 3lp's 0.5 to exact≈0.56. (The 10-step horizon cuts off a few long held-held-held runs; hence wolf exact≈3e-5, not 0.)

## Commands

The world takes no commands (no `cmd_*` atoms): the domain has no `intent.yaml`, and the domain agent opens it with no verbs (its clock beats, every intent is refused).

## Running

`metisc --run three_pigs_connectives.llp` runs the case its `#` lines give: `#init pig 3`, `#init wolf 1`, `#init straw 1`, `#init sticks 1`, `#init bricks 1`, `#steps 10`, `#seeds 3`, queries on `strawhouse`, `stickhouse`, `brickhouse`, `wolf`, and `#interactive go` (choices are yours; EOF falls back to the sampler).
