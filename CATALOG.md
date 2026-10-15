# The catalog — one directory per domain

`domains/<name>/` holds everything a domain is; both consoles (metis-loop,
metis-agent) and both agent backends (go/, py/) read it through one manifest,
`domain.yaml`, and one loader, `metis_catalog` (this repo; domain-catalog
s-2a2bc758).

```
pip install -e metis-catalog                 # or: the consoles find the sibling checkout
python -m metis_catalog list [--domains] [--json]    # what both consoles list
python -m pytest -q tests                    # every manifest whole (CI)
```

## domain.yaml — one manifest per domain

Paths are relative to the manifest's directory (a program kept beside the
directory, as rddl's, is named with `../`). Every key but `name` is optional.

```
name: dog
display: the dog                  # the narrator's name for it
line: "a robot dog: …"            # the one display line: the consoles' lists, the orchestrator's INSTALLED domains
voice: own                        # own (its %% lines say "I") | third
program: dog.llp                  # the program (#plugin / #notch / #init stay in the file)
serves: [dog.llp, packs/a.llp]    # the SERVED program's files, in order: the program, then what extends it;
                                  #   each relative to this directory, or pkg.mod:path inside a package
                                  #   (the kitchen pair's scenes in metispy); absent: [program] + packs/*.llp
notch: dog.notch.json             # a fitted overlay
host: dog_host.py:make            # the host (PortPlugin): file.py:factory, or pkg.mod:factory
agent: agent.py[:variant]         # the domain-agent module; absent with intent.spec: the generic agent
intent: {spec: intent.yaml, grammar: intent/<n>.gbnf, prompt: intent/<n>-prompt.txt,
         examples: {gemma4: intent/<n>-spoken.txt}, corpus: intent/<n>-corpus.tsv, tools: {…}, bench: […]}
clock: {beats: 1}                 # env beats per orchestrator tick (the kitchen: 2)
pair: [kitchen_shared]            # partners stepped inside its clock, reloaded with it
partner_of: kitchen               # never loaded alone; listed by its lead
docs: README.md
tests: tests/
records: records/                 # the domain agents' surprise records: records/<session>.jsonl
reload: propose                   # when its files change on disk: propose (the agent console says STALE and proposes) | auto (reloaded at its next quiet tick); the agent's config may override
# packs/*.llp: extension packs, each `extends` the program — without `serves`, the
# SERVED program is the program plus every pack in name order (Domain.serves(); the
# agent builds and reloads from the union, the loop console opens them, apply writes them)
```

**The served program is `Domain.serves()`, and only that** (runtime-binding
Q1, the architect's ruling): the py domain agent's CATALOG and PACKS (the
first file and the rest), the artifact emitter (`python -m
metis.kernel.artifact <n>`), the Go agent, and the loop console's one-click
open (the packs `serves` lists after the program it opens; none when it
serves another file) all read it from the manifest. A domain module never
names its program. The kitchen and kitchen_shared list metispy's pair scenes
(`metis.domains.kitchen:catalogs/…`): `program` is the authored kitchen the
loop console opens, `serves` what the agent runs.

| who reads what | |
|---|---|
| the loop console (metis-loop) | the list (`index`), one click opens `program` + its packs (`serves` after it, else `packs/`) + `host` (as an operator's `--host`, never named by the page) + `notch` |
| the py agent (metis-agent `metis_agent.domains`) | the domain's module: `agent` executed as `metis_agent.domains.<name>` (its `variant(name)` applied), or the generic one from `intent.yaml` + the host; `display`, `voice` unless the module sets them; the served program from `serves` always |
| the Go agent (metis-agent go/, `internal/catalog`) | `name`, `display`, `line`, `voice`, every served domain's `intent.grammar` / `prompt` / `examples[template]` and `intent.yaml`'s `asks`, `clock`, `pair`, `partner_of`, `reload`, the directory (watched, `intent/` and `packs/` with it); the programs and their packs through the py domain agents it runs; the console's list through this loader (a partner as its own row, `has` with `packs`) |
| the agent console | the list, the `line`, `has` |

**The domains with a manifest:** dog (generic agent, intent.yaml), kitchen
and kitchen_shared (`agent.py:<variant>` — the agent runs the pair's scene
from metispy, its manifest's `serves`; `program` is the authored kitchen the
loop console opens), wildfire and tamarisk (rddl: program and
notch beside the directory, the port plugin in it), wgc (the specialist's:
no host, no intents). **Without one:** a directory whose one catalog is a
`.llp` is a program-only domain; every `.llp` is listed — with a host, a
notch or its own README as a domain, else as a plain catalog — what it has
read off the checkout (`#plugin`, `<stem>_host.py`, `#notch`,
`<stem>.notch.json`, a README).

### Packs and the world's reports (the architect's rulings, 2026-10-15)

A pack in `packs/` is merged into the SERVED program: the agent builds and
reloads from the program plus every pack in name order, gated and accepted
in turn (a pack the gate refuses fails the build). The key is the union's.
The watcher marks a pack's change like the program's, so a pack applied from
the loop console is proposed for reload (or reloaded under `reload: auto`).

A pack that explains an off-model change must have a trigger. **A host's
report precedes the off-model effect it explains by at least one beat.**

Take the plant (metis-catalog 0b9539e). Its host reports `+visitor` one beat
before the visitor's watering:
- At the report's tick the reading is still consistent (dry), and the
  checkpoint holds `visitor`.
- Without the pack, the next tick's watering is the surprise, its record's
  init `{dry, visitor}`: the loop mines it and writes the pack
  `visitor_waters [dyn] : dry * visitor -o moist`.
- With the pack served, `dry * visitor` is enabled at the report's tick and
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

`domain.yaml` points at the generated files: `intent: {spec: intent.yaml,
grammar: intent/<name>.gbnf, prompt: intent/<name>-prompt.txt, examples:
{gemma4: intent/<name>-spoken.txt}, corpus: intent/<name>-corpus.tsv}`.

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
