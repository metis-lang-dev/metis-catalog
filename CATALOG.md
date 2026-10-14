# The catalog — one directory per domain

`domains/<name>/` holds everything a domain is; both consoles (metis-loop,
metis-agent) and both agent backends (go/, py/) read it. The manifest
`domain.yaml` (name, display, line, voice, program, notch, host, agent,
intent, clock, pair, docs, tests) is documented here by the domain-catalog
subject (s-2a2bc758, nina) — section to come.

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
