# love_triangle — A Midsummer Night's Dream love triangle

A port of Ceptre's `love-triangle.cep` tutorial: jealousy and moving on among three characters — Helena, Hermia, and Lysander.

When A loves B and C loves A (C ≠ A), C grows angry at both A and B. Three angers at the beloved and the love dies (the `move_on` rule). The world runs to quiescence in one beat; some loves burn out, others survive.

The world takes no commands: the domain has no `intent.yaml`, and the domain agent opens it with no verbs (its clock beats, every intent is refused).

Run with `metisc --run love_triangle.llp` to replay the case its `#init`/`#steps`/`#seeds`/`#query` lines give.

## Origin

- **Port of**: `ceptre-tutorial/sol/love-triangle.cep` (Martens' Ceptre tutorial)
- **Date**: 2026-07-22
- **Lineage**: metis began as a rewrite of the Ceptre interpreter; this catalog is that heritage run through everything metis added. The operational core is deliberately identical (the falling-factorial measure is Ceptre's token-individuated choice, made exact).
