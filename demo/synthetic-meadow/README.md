# synthetic-meadow — the wolf, the flock and the shepherd's tally

The first full surprise cycle run live in the `metis` REPL
(2026-10-09). The steps were `sink` -> `record` -> `replay` -> `mine`
-> candidate -> `gate` -> `accept` -> `replay` with `fixed: true`. The
world has the same shape as metispy's `tests/loop/test_loop.py` MEADOW
and SHEPHERD fixtures, with the `%%` docs rewritten as story
sentences. It is the world behind metis-loop `docs/TUTORIAL.md`
"Closing the loop — a surprise becomes a rule": the gate numbers match
that section exactly. It was recorded about 15 minutes after the
pantry demo (`../surprise-demo/`).

## The planted gap

`meadow.llp` is the base. In stage `hunt`, a wolf on a night either
catches a sheep (`fed`, weight `pk`) or the flock evades (`hungry`,
weight `~pk`). Then `qui hr` settles the world to `rest`. No rule
produces `safe`. The predicate is not even declared in the base.

`runs/sink.jsonl` holds one `metis-surprise` record, generated with
the kernel's own `surprise_record()` according to the session that
made it: "shepherd's ledger, wolf night ep0", init `wolf 1, sheep 3,
night 2, tally 2`, observed `safe: 1`, `kind: unmodeled`,
likelihood 0.

`shepherd_pack.llp` is the fix: pack `shepherd` (`extends meadow`)
with `n1 : tally * $fed -o loss` and `n2 : tally * $hungry -o safe`.
It is a **pure extension**. It reads base atoms only through
`$`-persist premises and produces only its own `sh` atoms. The base
`md` namespace therefore needs no pack grant. Compare
`../surprise-demo/`, whose base had to open its namespace so that its
fix could stay a pack rather than a `revise`.

## Walkthrough outcome (surprise-cycle-transcript.md)

| step | result |
|---|---|
| `record 0`, `replay` | likelihood 0, `explains: false` |
| `mine %% the shepherd tallies the flock at rest: ...` | approved text (88 chars) |
| `load shepherd_pack.llp` (hand-written; no `formalize` call) | candidate, 16 lines |
| `gate` | green; support 5; `loss` 0 -> 0.828125, `safe` 0 -> 0.390625, `tally` 1 -> 0 |
| `accept` | key 34aa7524... -> 1cdc8c1a... |
| `replay` | likelihood **0 -> 0.21875**, `fixed: true`, explanation `catch, evade, hr, n2, n1` |
| `map` (unconditioned) | `catch, catch, hr, n1, n1` -> `fed:2 loss:2` |

Re-run on 2026-10-11 with the current metispy, binding `pk = 0.5`
(see below). `gate`, `accept` and `replay` give the same keys and the
same numbers.

## Warts from the first run (runs/first-run-warts.md) and their status

`first-run-warts.md` is the REPL transcript of the first attempt
(12:12–12:15). The clean run is `surprise-cycle-transcript.md`
(12:16).

1. **The `llp <<EOF` body was lost when sent through `tmux send-keys`.**
   The multi-line send collapsed into one line that included the
   `EOF` and the next `gate`. `llp` still answered `ok: true, lines: 2`
   with no parse check, and the reader kept waiting. Status: this is a
   problem on the driver side, not in metispy, and nothing was fixed.
   A piped-stdin heredoc does work (checked on the pantry world,
   2026-10-11). The reliable scripted route is `load FILE.llp`.
2. **`query safe @6` read 0 both before and after `accept`.** The
   query reads the live session state, and that state was still empty:
   `record N` adopts the record's init as the scene that `gate`,
   `replay` and `trace` use, but it does not load that init into live
   state. Status: **still present**. On 2026-10-11 the query read 0
   until `reset`, and then 0.3906, which matches the gate's `safe`
   figure. TUTORIAL.md's line "every instrument now speaks about that
   tick" overstates this. Run `reset` after `record`.
3. **`load` rewrote the candidate.** The snapshot moved the file's
   leading `%%` comment inside `stage rest`. Status: fixed in metispy
   `d4cf1d9` ("load keeps the candidate verbatim"). Still present
   (re-run 2026-10-11): the gate's rule list shows that header comment
   glued onto `n1`'s doc, and `load` adopts it as the text (`adopted_text_chars`).
4. **The gate classification reads like a failure.** It says
   `counterexample: init: multiplicity 3 on 'sheep' — the emission covers 0/1
   programs`. This is the class-F statics tier (SPEC.md §5 step 5,
   `kernel/factorize.py`): `sheep 3` is outside the 0/1 emission. The
   gate is still `ok: true` and `accept` goes through. Unchanged.

## Findings that cost effort since

- **The unbound weight port is now fatal.** Since metispy `9214991`
  (2026-10-10, port plugins, `docs/PLUGIN-PORTS.md`), `weight pk reads {}`
  with no binding makes the REPL refuse to serve: `metis meadow.llp`
  prints "unbound weight port 'pk' — no plugin binds it". The tutorial's bare
  `$ metis meadow.llp` broke; it now passes `--plugin meadow_plugin:make`. The test fixture
  binds `pk = 0.5` (`Registry().weight("pk", 0.5)`), which keeps the
  old 1:1 catch/evade split and therefore every number above. `accept`
  refuses atomically on unbound ports (`d4cf1d9`), and `formalize`
  warns about them (`95ce5a9`).
- **The record is not blind.** Its init carries `tally: 2`, which
  belongs to the pack's vocabulary, and it observes `safe`, which the
  base never declares. Its `program_key` (945292...) matches neither
  the base key (34aa...) nor the merged key (1cdc...), and `replay`
  does not flag that. It is a teaching record, not a runtime one.

## Not solved / not to retry

- The LLM seat (`ollama:gemma3:4b`) was never used. The candidate was
  loaded from a file, and TUTORIAL.md's `formalize` line is
  illustrative only.
- `meadow_plugin.py` (added in the consolidation) binds `pk = 0.5` and
  restores the tutorial's numbers; verified 2026-10-11: replay 0 →
  0.21875, `fixed: true`.
- Do not drive `llp <<EOF` through `tmux send-keys`; use `load`.
- TUTORIAL.md lists the explanation as `..., n1, n2`, while the
  transcript shows `n2, n1`.
- `shepherd_pack.llp` is a pack. Compiled standalone it fails with
  `extends-no-base` and has to be compiled against `meadow.llp`.

## Evidence in this directory

- `meadow.llp`: the base world (the gap; weight port `pk`).
- `shepherd_pack.llp`: the fix pack (needs `meadow.llp`).
- `runs/sink.jsonl`: the surprise record.
- `surprise-cycle-transcript.md`: the clean cycle (REPL `transcript` verb).
- `runs/first-run-warts.md`: the first attempt (warts 1–4).
- `meadow_plugin.py`: binds the weight port `pk` at 0.5.

## How to run

`pk` needs a binding; `meadow_plugin.py` (beside the catalog) gives it:

```sh
cd metis-catalog/demo/synthetic-meadow
metis --plugin meadow_plugin:make meadow.llp
llp> sink runs/sink.jsonl
llp> record 0
llp> replay                 # likelihood 0, explains false
llp> load shepherd_pack.llp # leading %% comment becomes the text
llp> gate
llp> accept
llp> replay                 # 0.21875, fixed: true
llp> reset                  # put the record scene into live state
llp> query safe @6          # 0.3906 (0 without the reset)
llp> map
```
