# herstory — a four-act family tragedy

Hannah and Eve, twins; Simon; a wig and a mirror. One stage per act — beginning, courtship, tragedy, betrayal — each run to quiescence, then a link sets up the next act with new props. Rule names kept; the original's anonymous `qui * stage X -o stage Y * …` links are named (act2, act3, act4) and keep their products. The readout is life and death: alive/dead marginals per character.

## Origin

Port of `interactive-lp/examples/herstory.cep`, provenance hand, 2026-10-03.

## Oddities (kept in the 1:1 port)

- `date_carl` consumes `alive carl` — dating Hannah ends Carl's life as far as the board knows (no `dead carl` is minted).
- `parents_die` consumes alive mother/father and produces nothing (no dead atoms either): the parents simply leave the board.
- `hannah_gets_pregnant` consumes the marriage; `eve_simon_affair` consumes Eve's jealousy; `hannah_poses_as_eve` consumes the wig that `eve_performs`/`eve_simon_affair`/`hannah_discover_affair` only `$`-read. That looks like a race but is not one: posing needs `hannah_knows`, which needs the affair, which needs the wig — so the wig is always spent last.
- Nothing ever consumes `alive eve`/`alive hannah`.

## The lesson

Every life/death marginal is exactly 0 or 1 (Florence and Simon die, the twins live, Carl and the parents leave the board, Hannah miscarries, Eve reaches Glasgow). The plot is determined; only the interleaving of independent beats varies (act three's three beats fire in any order — one Foata beat). Generative nondeterminism without outcome nondeterminism. No `$`-overlap sites: no rule `$`-reads an atom another of its premises names. No pumping rules: every rule consumes.

## Commands

This world takes no commands. Its `intent.yaml` knows only UNKNOWN, present because the domain agent opens no domain without one.

## Running

`metisc --run herstory.llp` runs the case its `#` lines give.
