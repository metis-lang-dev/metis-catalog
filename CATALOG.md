# The catalog — one domain package per directory

## The words (the user's, 2026-10-15)

| word | what it is |
|---|---|
| **domain** | the thing modelled: the dog, the plant, the kitchen |
| **domain package** (`pkg` in code) | its directory in the catalog, `domains/<name>/`: what the user checks out and the loop develops; the same package serves the loop and the agent |
| **extension** | a catalog in the package's `extensions/` (`catalog <card> 1. extends <name>`, the language's word): the served program is the program plus its extensions |
| **bundle** | what the emitter forms from a package for the C++/Go runtime: `ground.wire` + `sidecar.json` (+ `program.ir`, `tools.json`); `python -m metis.kernel.artifact <name>`. `ground.wire` is compiled by the OCaml compiler, `metisc --wire <program> [--extension e.llp]…` (`$METISC`, else `metisc` on PATH): OCaml-authoritative. Without metisc, metispy's `emit_artifact` covers, byte-equal (metispy gate 4 and metis-lang gate 12) and logged (`ground.wire by …`). A failing metisc is an error, never covered. `sidecar.json`, `tools.json` and `program.ir` are metispy's harness data (bundle-compiler s-3985caf6) |
| **card** | an offerable catalog at the served node (unchanged) |

**Pack and extension.** In the REPL a gated candidate is a *pack* (`gate`,
`accept`, `export` writes `pack1.llp`: the language's word, metispy's); once
accepted into a package it is written as `extensions/<card>.llp`, an
extension (the architect's ruling, 2026-10-15).

Both consoles (metis-loop, metis-agent) and both agent backends (go/, py/)
read a package through one manifest, `domain.yaml`, and one loader,
`metis_catalog` (this repo; domain-catalog s-2a2bc758, catalog-entry
s-65dd0863).

```
pip install -e metis-catalog                 # or: the consoles find the sibling checkout
python -m metis_catalog list [--domains] [--json]    # what both consoles list
python -m pytest -q tests                    # every package's manifest, files and generated intents (CI)
```

## domain.yaml — the package's manifest

**The reference: the dog** (`domains/dog/domain.yaml`, its keys):

```
display: the dog
line: "a robot dog: walks to places, finds things, sits and stands"
voice: own
program: dog.llp
host: dog_host.py:make
intent: {spec: intent.yaml}
clock: {beats: 1}
records: records/
```

with, in the directory: `dog.llp`, `dog_host.py`, `intent.yaml`, the
generated `intent/` (`dog.gbnf`, `dog-prompt.txt`, `dog-spoken.txt`,
`dog-corpus.tsv`), `README.md`, and `records/` (git-ignored). An
`extensions/` directory joins it when an extension is applied (the plant's
`extensions/visitor.llp`).

**The package's name is its directory's.** Paths are relative to the
manifest's directory (a program kept beside it, as rddl's, is named with
`../`), and **never leave the catalog root**. A package may name a
neighbour's file (`../kitchen/agent.py`), but not an absolute path or one
that climbs out of the checkout; `pkg.mod:path` and `pkg.mod:factory` name
a package, not a file. Every key is optional, and **the loader refuses any
other** (`metis_catalog.check_manifest`; `tests/test_packages.py` runs it
over every package in CI, with each package's files and its generated intent
files).

| key | shape | who reads it |
|---|---|---|
| `program` | `dog.llp` — the program (`#plugin` / `#notch` / `#init` stay in the file) | the loop console's one-click open; the served program's first file |
| `extensions` | `[extensions/a.llp, …]`; absent: `extensions/*.llp` in name order | the served program after the program (`Domain.extensions()`); the loop console opens them with it, apply writes them there |
| `serves` | `[a.llp, …]`, each relative or `pkg.mod:path` in a package; absent: `[program] + extensions` | **the served program, and only this** (`Domain.serves()`): the py agent's CATALOG + EXTENSIONS, the bundle emitter, the Go agent, the loop console's open (the extensions it lists after the program) |
| `host` | `file.py:factory` or `pkg.mod:factory` (a PortPlugin) | the py agent (attached to its Repl), the loop console (an operator's `--host`, never named by the page) |
| `intent` | `{spec: intent.yaml}` only | the generic py agent (mapper, replier from the spec); the intent pass's files are **derived** at fixed names, `intent/<name>.gbnf`, `<name>-prompt.txt`, `<name>-spoken.txt` (the gemma4 template's examples), `<name>-corpus.tsv`, listed in `Domain.intent` when present — py and Go read them there. J material only: T (the REPL's tool-call syntax) is metispy's |
| `clock` | `{beats: 1}` — env beats per orchestrator tick (the kitchen: 2) | the agents' clock |
| `reload` | `propose` (the agent console says STALE and proposes) \| `auto` (reloaded at its next quiet tick); the agent's config may override | the agents' watch |
| `records` | `records/` (git-ignored) — the agents' surprise records, `records/<session>.jsonl` | the agents' sink; the loop console's Records dock |
| `display` | the narrator's name for it | the orchestrator, the narrator, both consoles |
| `line` | the one display line | the consoles' lists, the orchestrator's INSTALLED domains |
| `voice` | `own` (its `%%` lines say "I") \| `third` | the narrator, the replier |
| `agent` | `agent.py[:variant]` — the domain-agent module; absent with `intent`: the generic agent | the py agent (`metis_agent.domains.<name>`, its `variant(name)` applied): the kitchen pair, wgc |
| `pair` | `[kitchen_shared]` — partners stepped inside its clock, reloaded with it | both agents |
| `partner_of` | `kitchen` — never loaded alone, listed by its lead | both agents, the consoles' lists |
| `notch` | `wildfire.notch.json` — a fitted overlay | the loop console's open |

Gone with catalog-entry step 2 (their readers derive them): `name` (the
directory's), `docs` (`README.md` by convention), `tests`, and
`intent.grammar` / `prompt` / `examples` / `corpus` (the fixed names above).
Gone with step 1: `intent.tools` / `intent.bench` (E9's T bench).

**The served program.** The kitchen and kitchen_shared list metispy's pair
scenes in `serves` (`metis.domains.kitchen:catalogs/…`): `program` is the
authored kitchen the loop console opens, `serves` what the agent runs. A
domain module never names its program.

**The packages:** dog (generic agent, intent.yaml), plant (generic agent,
an extension), kitchen and kitchen_shared (`agent.py:<variant>`, the pair's
scenes), wildfire and tamarisk (rddl: program and notch beside the
directory, the port plugin in it), wgc (`domains/wgc`, the
specialist's: no host, no intents). **Without a manifest:** a directory
whose one catalog is a `.llp` is a program-only domain; every `.llp` is
listed — with a host, a notch or its own README as a domain, else as a plain
catalog — what it has read off the checkout (`#plugin`, `<stem>_host.py`,
`#notch`, `<stem>.notch.json`, a README).

**Units (catalog-packages, 2026-10-19).** Every package's program carries a `#`
case (`#steps`, and `#init` where it is the live start already); its `metisc
--run` trace is `goldens/traces/<name>.txt`. Where the program fires nothing
from its live start (dog, plant, kitchen, sysadmin), the firing start is a CI
case, `goldens/cases/<name>.llp` (the program included, unchanged): a CI case,
not a domain. `ci/packages.py` holds both, with metispy's twin and the bundle's
wire (catalog CI, job `packages`).

### Extensions and the world's reports (the architect's rulings, 2026-10-15)

An extension in `extensions/` is merged into the SERVED program: the agent
builds and reloads from the program plus every extension in order, gated and
accepted in turn (an extension the gate refuses fails the build). The key is
the union's. The watcher marks an extension's change like the program's, so
an extension applied from the loop console is proposed for reload (or
reloaded under `reload: auto`).

An extension that explains an off-model change must have a trigger. **A host's
report precedes the off-model effect it explains by at least one beat.**

Take the plant (metis-catalog 0b9539e). Its host reports `+visitor` one beat
before the visitor's watering:
- At the report's tick the reading is still consistent (dry), and the
  checkpoint holds `visitor`.
- Without the extension, the next tick's watering is the surprise, its
  record's init `{dry, visitor}`: the loop mines it and writes the extension
  `visitor_waters [dyn] : dry * visitor -o moist`.
- With the extension served, `dry * visitor` is enabled at the report's tick and
  the kernel fires `visitor_waters` itself, so the visit is modelled and
  raises no surprise.

Two shapes fail:
- **A report and the change it explains in the same tick.** No record can
  explain it: the watch reads the env before any rule fires.
- **A triggerless rule** (`dry -o moist`). The sampler fires it on its own,
  so it models the change away (and here makes watering unreachable).

The watch compares the reading with the program at every tick, and stays so
(no "settle before comparing").

## intent.yaml — what the person may ask the domain (frozen 2026-10-14)

Agreed by nina and opus (e2e-workflow s-143c3088, WORKFLOW.md stage 3). The
source of a domain's intents: the intent pass's grammar and prompts are
**generated** from it, never written by hand, and the generic domain agent
(metis-agent py `intent_domain.py`) reads its mapper and replier tables, so
a domain with a host needs no Python in metis-agent.

```
python3 tools/intents.py gen <name>      # → domains/<name>/intent/<name>.gbnf, <name>-prompt.txt, <name>-spoken.txt
python3 tools/intents.py check <name>    # the generated files are what intent.yaml makes (CI)
python3 tools/intents.py schema <name>   # the JSON schema the grammar is made from
metis-agent/py: .venv/bin/python -m metis_agent.intent_check <name> [--no-model]   # the corpus through them
```

`domain.yaml` names only the spec, `intent: {spec: intent.yaml}`; the
generated files sit at the fixed names above (`intent/<name>.gbnf`,
`<name>-prompt.txt`, `<name>-spoken.txt`, `<name>-corpus.tsv`).

### The intent pass (generated into intent/)

| key | shape | becomes |
|---|---|---|
| `persona` | text | the prompt's head |
| `verbs` | `[{verb: V \| [V, W], meaning}]` | the schema's `intent` enum (in order) and the prompt's category table (one row may name two) |
| `slots` | `{name: number \| string \| {enum: [...]} \| {object: [types]} \| {relations: [...], reference: [types]}}` | the intent JSON's optional fields after `intent`, in order; an `object` slot is `{type, description, attributes?}` |
| `guidance` | text | the paragraph after the table |
| `examples` | `[[utterance, {intent JSON}] \| {note: text}]` | the mapper's examples (`"utt" → {json}`), notes between them verbatim |
| `spoken` | `{heading, text, examples: [[utterance, json, said]]}` | the pass-2 examples (the spoken response after the JSON) |

YAML 1.1 reads a bare `ON`, `OFF`, `YES`, `NO` as a boolean: quote such a
name (`"ON"`); the generator refuses a non-name enum value.

### The mapper (the card's table)

| key | shape | meaning |
|---|---|---|
| `map` | `[{verb, when?: {slot: VALUE}, atom, act}]` | an intent → one command atom of the program; `atom` is a template: `cmd_go({goal:place})` resolves the slot to a handle of that kind, `cmd_turn({direction:side})` looks the slot's value up in `values` |
| `values` | `{set: {VALUE: word}}` | a slot value → the program's constant |
| `handles` | `{kind: {handle: {description: [...], type?: [...], tag_id?, near?: [...]}}}` | the perception vocabulary: what a target resolves to, first match in order |
| `fallback` | `{kind: handle}` | a target the host cannot resolve |
| `standing` | `[handle]` | handles that stand for a place without naming one: never an alternative, no words |
| `enders` | `[atom]` | commands that end what runs: they act on the tick they arrive |

### The replier

| key | shape | meaning |
|---|---|---|
| `outcomes` | `{predicate: status}` | an outcome atom → the result status (`done`, `refused`, `progress`, `expired`, `cancelled`): every atom a command's rule produces that no rule reads (the plant's `checked`, so CHECK's answer is its `%%` line); the skeleton infers them |
| `alternatives` | `{max, places?: {rules, act, slot, where: [p, q]}, rules: {rule: [act]}}` | a refusal's way out as typed intents in the domain's dictionary: per rule a fixed list (`[]`: none), or for `places.rules` the handles with `p(h)` and `q(h)` true, in the program's order, at most `max` |

The outcomes' words are the program's `%%` lines; the world (complementary
pairs, a blocker's words, the answers to a long command) is the host's.

### The orchestrator (e2e-workflow step 4)

| key | shape | meaning |
|---|---|---|
| `asks` | `[VERB]` | the verbs that ask the domain a question (the dog's `QUERY`, the plant's `CHECK`): words in question form mapped to one are the domain's question, never judged talk by the orchestrator's info-or-command judge. Every rule of an ask's command keeps the state (only `$`-premises besides the command): `check` refuses one that consumes, and the loop console's `intents` propose refuses it with why; the skeleton lists the candidates (the commands whose rules only read the state) |

With several intent domains served, the orchestrator's J names its domain
first (`{"domain":"plant","intent":"WATER"}`), under the union of the
domains' generated grammars (metis-agent DESIGN, "Several intent domains").

Example: `domains/dog/intent.yaml` (generates the dog's grammar with the
same rules as the hand-written one and its prompts byte for byte; the
corpus 54/54).
