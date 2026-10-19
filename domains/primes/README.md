# primes — a sieve of Eratosthenes up to 12

A port of interactive-lp's `primes.cep`. Stage `gen` generates the numbers 2..12, the `sieve` link moves to `primes`, and there every number annihilates its multiples (`collide`). What is left are the primes: 2, 3, 5, 7 and 11 survive with probability 1, and the composites with probability 0.

The world takes no commands: no `intent.yaml`, no host. The domain agent opens it with no verbs.

Run `metisc --run primes.llp` to replay the case its `#init`/`#steps`/`#seeds`/`#query` lines give. Its expected trace is `goldens/traces/primes.txt` (catalog CI).

## Origin

- **Port of**: `interactive-lp/examples/primes.cep`, 2026-10-03 (`provenance hand "port:interactive-lp/examples/primes.cep"`).
- **Encodings** (the program's header has the details): `nat` bounded to n0..n12, the original's own limit; the successor graph and the four Horn clauses for plus/mult; collide's `$`-overlap site written as consume-and-reproduce.
- **Row**: `domains/CEPTRE-PORTS.md`, primes.
- Moved from `domains/arith/primes.llp` (catalog-packages s-a2c529d6), with the program unchanged.
