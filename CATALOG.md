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
```

| who reads what | |
|---|---|
| the loop console (metis-loop) | the list (`index`), one click opens `program` + `host` (as an operator's `--host`, never named by the page) + `notch` |
| the py agent (metis-agent `metis_agent.domains`) | the domain's module: `agent` executed as `metis_agent.domains.<name>` (its `variant(name)` applied), or the generic one from `intent.yaml` + the host; `display`, `voice`, `program` unless the module sets them |
| the Go agent (metis-agent go/) | `name`, `display`, `line`, `voice`, `intent.grammar` / `prompt` / `examples[template]`, `clock`, `pair`, `partner_of` |
| the agent console | the list, the `line`, `has` |

**The domains with a manifest:** dog (generic agent, intent.yaml), kitchen
and kitchen_shared (`agent.py:<variant>` — the agent runs the pair's scene
from metispy, `metis.domains.kitchen` catalogs; `program` is the authored
kitchen the loop console opens), wildfire and tamarisk (rddl: program and
notch beside the directory, the port plugin in it), wgc (the specialist's:
no host, no intents). **Without one:** a directory whose one catalog is a
`.llp` is a program-only domain; every `.llp` is listed — with a host, a
notch or its own README as a domain, else as a plain catalog — what it has
read off the checkout (`#plugin`, `<stem>_host.py`, `#notch`,
`<stem>.notch.json`, a README).

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
| `outcomes` | `{predicate: status}` | an outcome atom → the result status (`done`, `refused`, `progress`, `expired`, `cancelled`) |
| `alternatives` | `{max, places?: {rules, act, slot, where: [p, q]}, rules: {rule: [act]}}` | a refusal's way out as typed intents in the domain's dictionary: per rule a fixed list (`[]`: none), or for `places.rules` the handles with `p(h)` and `q(h)` true, in the program's order, at most `max` |

The outcomes' words are the program's `%%` lines; the world (complementary
pairs, a blocker's words, the answers to a long command) is the host's.

Example: `domains/dog/intent.yaml` (generates the dog's grammar with the
same rules as the hand-written one and its prompts byte for byte; the
corpus 54/54).
