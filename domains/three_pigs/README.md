# three_pigs — the Three Little Pigs

A port of `interactive-lp/examples/3lp.cep` — the tale of three pigs who each
build a house (straw, sticks, bricks) and a wolf who blows them down. The wolf
blows down the straw and stick houses and is spent at the brick house, so which
houses stand depends on the order; the case's own seed ends with only the brick
house. One stage, pure linear consumption, one-to-one.

The program's catalog line is `catalog three-pigs 1.` (an ident may not start
with a digit, so `3lp` survives only as the file name). The catalog domain is
`three_pigs` (a domain name is lowercase letters, digits and `_`).

The lesson of this port is in the `blow_*` heads. The original writes every
blow as consume-and-reproduce, and which atom it reproduces decides who
survives:

```
blow_straw : wolf * strawhouse  -o wolf.         (house dies)
blow_brick : wolf * brickhouse  -o brickhouse.   (wolf is spent)
```

Written as what they denote (recipe: consume-and-reproduce → `$`-read),
survival is literally which premise carries the `$`:

```
$wolf * strawhouse -o ()      vs      wolf * $brickhouse -o ().
```

No rule has a `$`-atom beside another premise of the same atom, so the
`$`-overlap caveat (tragedy v3) does not arise here.

## Provenance

- **port:interactive-lp/examples/3lp.cep** — 2026-10-03
- hand-ported, rules keep their original names
- catalog `three-pigs 1`

## Commands

This world takes no commands. The domain has no `intent.yaml`; the domain agent
opens it with no verbs (its clock beats, every intent is refused).

## Running

```
metisc --run three_pigs.llp
```

runs the case its `#` lines give (3 pigs, 1 wolf, 1 each of straw/sticks/bricks,
8 steps). The `#interactive go` line lets you choose each step; EOF falls back
to the sampler. 6 steps is the longest story: three builds and three blows.
