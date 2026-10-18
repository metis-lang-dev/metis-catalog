# tragedy — a Shakespearean romantic-tragedy story world

A port of `interactive-lp/examples/tragedy.cep` (Martens et al., "Generative Story Worlds as Linear Logic Programs", INT 7 2014). The program tells stories of love, rivalry, insult, and violence among characters from *Romeo and Juliet* — Capulets, Montagues, and townsfolk — driven by opinion formation, flirtation, marriage, and murder.

Every Ceptre rule is here under its original name, with the Ceptre idiom `consume-and-reproduce` written as the `$`-read it denotes, and Ceptre's neutral-opinion rule pair written as one rule with the `⊕` alternative-head sugar. Three versions:
- **v1**: the one-to-one port — every Ceptre rule under its name.
- **v2**: distinctness guards (`<>`) added to prevent self-unification artifacts.
- **v3**: fidelity fix — at the two sites where the original overlaps `$a` with another `a` premise (eroticize, divorce), the tokens are written out as consume-and-reproduce, matching Ceptre's semantics.

The world takes no commands: the domain has no `intent.yaml`, and the domain agent opens it with no verbs (its clock beats, every intent is refused).

**Provenance**: hand port, 2026-10-03. `interactive-lp/examples/tragedy.cep`.

## How to run

- `metisc --run tragedy.llp` runs the case its `#init` / `#steps` / `#seeds` / `#query` lines give.
- `#interactive all` lets you choose each event.
