#!/usr/bin/env python3
"""Lockstep bisimulation drive: the REAL Ceptre interpreter against
a metis port, choice by choice.

The driver is the policy (the bus doctrine: mechanism carries, the
driver decides); the POLICY IS THE METIS MEASURE — the seeded
reference sampler over parity weights, which by Theorem 1 is
exactly Ceptre's uniform token picker. No notching is needed to
imitate Ceptre: parity prior IS its choice rule.

At every interactive step:
  1. Ceptre's menu is parsed — one entry PER TOKEN CHOICE, so the
     entry count of an instance is its transition multiplicity;
  2. the metis side enumerates its enabled events with
     transition_count — the two MENUS MUST MATCH (instance set and
     multiplicities); a mismatch is a fidelity bug caught at the
     exact state;
  3. one event is sampled from the metis measure, its index is fed
     to Ceptre, and the metis state applies the same event.
At the end (quiescence, or --steps budget + EOF) the final states
must match.

Usage:
  tools/ceptre_lockstep.py PORT.llp CEPTRE.cep [--seed N]
      [--steps N] [--ceptre PATH]

Scope: catalogs whose rules live in ONE #interactive stage (3lp,
tragedy, tower_of_hanoi, blocks-world, ll); stage links are not
driven. Exit 0 = every menu and the final state matched.

The .cep runs from a TEMP COPY with `#interactive <stage>` ensured
(stage taken from its #trace line) — many originals ship it
commented out and would free-run otherwise. --drop-line REGEX
removes a line from the copy (tower_of_hanoi's `post : place.` is
a hard error in current Ceptre); every such edit is printed.
--ctor rel=name renders a port's constructor-graph constants back
into Ceptre's structured terms (topof=top_of: top_r1 <-> (top_of
r1)) so menu labels compare."""
import argparse
import os
import random
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve()
                       .parents[2] / "metispy"))

from metis.kernel.refsample import canonical_events          # noqa: E402
from metis.kernel.weight import choice_weight                 # noqa: E402
from metis.lang import (compile_catalog, parse,               # noqa: E402
                        resolve_includes)
from metis.lang.directives import embedded_case               # noqa: E402

_MENU = re.compile(r"^(\d+): (.+?)\s*$")
_NAME = re.compile(r"^([A-Za-z0-9_'-]+)(?:\[(.*)\])?$")


def metis_label(ev_name):
    """'jealousy[A=x,B=y]' -> ('jealousy', ('x','y')) — binding
    values in the rule's declared order, matching Ceptre's arg
    print order."""
    m = _NAME.match(ev_name)
    args = tuple(b.split("=", 1)[1]
                 for b in m.group(2).split(",")) if m.group(2) else ()
    return (m.group(1), args)


def sexpr_args(text):
    """'r1 (top_of r2) x' -> ['r1', '(top_of r2)'] — balanced
    top-level tokens, inner whitespace normalized."""
    out, depth, cur = [], 0, []
    for ch in text:
        if ch == "(":
            depth += 1
        if ch == ")":
            depth -= 1
        if ch.isspace() and depth == 0:
            if cur:
                out.append("".join(cur))
                cur = []
        else:
            cur.append(ch)
    if cur:
        out.append("".join(cur))
    return [" ".join(t.replace("(", " ( ").replace(")", " ) ")
                     .split()).replace("( ", "(").replace(" )", ")")
            for t in out]


def build_renders(doc, ctors):
    """const -> its Ceptre term string, via the port's constructor
    graphs: rel(c, a1..ak) with --ctor rel=name renders c as
    '(name r(a1) .. r(ak))', recursively."""
    graph = {}
    for ent in doc.catalog.entries:
        p = ent.payload
        if type(p).__name__ == "HornClause" and not p.body:
            pred, args = p.head
            if pred in ctors and args:
                name, pos = ctors[pred]
                c = args[pos - 1]
                rest = args[:pos - 1] + args[pos:]
                if c not in graph:
                    graph[c] = (name, rest)
    render = {}

    def r(c):
        if c in render:
            return render[c]
        if c not in graph:
            return c
        name, args = graph[c]
        render[c] = f"({name} {' '.join(r(a) for a in args)})"
        return render[c]
    return {c: r(c) for c in graph}


def ceptre_label(text, unrender, strip="", alias=None):
    parts = sexpr_args(text)
    if len(parts) == 1 and parts[0].startswith("("):
        # a parameterized entry comes wrapped: (jealousy a b c)
        parts = sexpr_args(parts[0][1:-1])
    name = parts[0]
    if strip and name.startswith(strip):
        name = name[len(strip):]           # the port's spelling map:
    name = name.replace("/", "-")          # rule/sub -> rule-sub
    parts[0] = (alias or {}).get(name, name)
    return (parts[0], tuple(unrender.get(a, a) for a in parts[1:]))


def prep_cep(cep, drop):
    """Temp copy with `#interactive <stage>` ensured and --drop-line
    lines removed; every edit printed."""
    import tempfile
    src = Path(cep).read_text()
    lines = src.splitlines()
    out = []
    stage = None
    m = re.search(r"#trace\s+\S+\s+(\S+)", src)
    if m:
        stage = m.group(1)
    have = re.search(rf"^\s*#interactive\s+{stage}\s*\.",
                     src, re.M) if stage else None
    for ln in lines:
        if drop and re.search(drop, ln):
            print(f"  [prep] dropped: {ln.strip()}")
            continue
        if (stage and not have
                and re.match(rf"\s*%\s*#interactive\s+{stage}\b", ln)):
            print(f"  [prep] uncommented: #interactive {stage}.")
            out.append(f"#interactive {stage}.")
            have = True
            continue
        out.append(ln)
    if stage and not have:
        idx = next(i for i, ln in enumerate(out)
                   if ln.lstrip().startswith("#trace"))
        out.insert(idx, f"#interactive {stage}.")
        print(f"  [prep] injected: #interactive {stage}.")
    f = tempfile.NamedTemporaryFile("w", suffix=".cep", delete=False)
    f.write("\n".join(out) + "\n")
    f.close()
    return f.name


def read_menu(proc):
    """Lines up to the '?- ' prompt -> {idx: label}; None on EOF
    (Ceptre then prints the final state on stdout)."""
    buf = ""
    while True:
        b = os.read(proc.stdout.fileno(), 4096)
        if not b:
            return None, buf
        buf += b.decode()
        if "?- " in buf:
            break
    menu = {}
    for line in buf.splitlines():
        m = _MENU.match(line.strip())
        if m:
            menu[int(m.group(1))] = m.group(2)
    return menu, buf


def final_counts(text, unrender=None):
    """Ceptre 'Final state: {a, (p x y), (clear (top_of r1))}' ->
    Counter of metis atom spellings; comma-split at depth 0, nested
    constructor terms unrendered; stage/qui bookkeeping dropped."""
    m = re.search(r"Final state:\s*\{(.*?)\}", text, re.S)
    if not m:
        return None
    out = Counter()
    items, depth, cur = [], 0, []
    for ch in m.group(1):
        depth += ch == "("
        depth -= ch == ")"
        if ch == "," and depth == 0:
            items.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    items.append("".join(cur))
    for tok in items:
        tok = tok.strip().lstrip("!")
        if tok.startswith("(") and tok.endswith(")"):
            tok = tok[1:-1].strip().lstrip("!")   # (!dead tybalt)
        if not tok or tok == "qui" or tok.startswith("stage"):
            continue
        parts = tok.split(None, 1)
        args = sexpr_args(parts[1]) if len(parts) > 1 else []
        if unrender:
            args = [unrender.get(a, a) for a in args]
        out[parts[0] + (f"({','.join(args)})" if args else "")] += 1
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("port"), ap.add_argument("cep")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--steps", type=int, default=400)
    ap.add_argument("--ctor", action="append", default=[],
                    metavar="REL=NAME")
    ap.add_argument("--drop-line", default=None, metavar="REGEX")
    ap.add_argument("--strip-prefix", default="",
                    help="rule-name prefix the port dropped (do/)")
    ap.add_argument("--proj", action="append", default=[],
                    metavar="RULE=I,J",
                    help="keep only these 1-based args of OUR label "
                         "(a port's guard var: pickup=2,3 drops the "
                         "constructed-place var Ceptre never prints)")
    ap.add_argument("--alias", action="append", default=[],
                    metavar="THEIRS=OURS",
                    help="ceptre rule name -> port name (an ⊕-head "
                         "port: formOpinion-like=formOpinion-1)")
    ap.add_argument("--ceptre", default=str(
        Path(__file__).resolve().parents[2]
        / "interactive-lp" / "ceptre"))
    ns = ap.parse_args()

    text = Path(ns.port).read_text()
    doc = compile_catalog(resolve_includes(parse(text),
                                           Path(ns.port).parent))
    case = embedded_case(text)
    prog = doc.catalog.ground(dict(case["init"]))
    events = canonical_events(prog)
    counts = {a: n for a, n in case["init"].items() if n > 0}
    stage = prog.init_stage
    rng = random.Random(ns.seed)
    ctors = {}
    for c in ns.ctor:                 # rel=name[@POS]; POS = which
        rel, name = c.split("=", 1)   # arg is the DEFINED constant
        name, _, pos = name.partition("@")
        ctors[rel] = (name, int(pos or 1))
    alias = dict(a.split("=", 1) for a in ns.alias)
    proj = {k: tuple(int(i) for i in v.split(","))
            for k, v in (p0.split("=", 1) for p0 in ns.proj)}

    def ours_label(ev_name):
        name, args = metis_label(ev_name)
        if name in proj:
            args = tuple(args[i - 1] for i in proj[name])
        return (name, args)
    renders = build_renders(doc, ctors)
    unrender = {v: k for k, v in renders.items()}
    cep = prep_cep(ns.cep, ns.drop_line)

    proc = subprocess.Popen([ns.ceptre, cep],
                            stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    tail, step = "", 0
    try:
        for step in range(1, ns.steps + 1):
            menu, raw = read_menu(proc)
            print(f"[step {step}] menu={len(menu) if menu else menu}", file=sys.stderr)
            tail += raw
            if menu is None:
                break
            theirs = Counter(
                ceptre_label(v, unrender, ns.strip_prefix, alias)
                for k, v in menu.items() if k != 0)
            enabled = [(i, ev, int(choice_weight(ev, counts)))
                       for i, (kind, s, ev) in enumerate(events)
                       if kind == "clause" and s == stage]
            enabled = [(i, ev, w) for i, ev, w in enabled if w > 0]
            ours = Counter()
            for _, ev, w in enabled:
                ours[ours_label(ev.name)] += w
            if theirs != ours:
                print(f"MENU MISMATCH at step {step}:")
                names = {a for lab in (set(theirs) | set(ours))
                         for a in (lab[0],) + lab[1]}
                rel = {a: n for a, n in sorted(counts.items())
                       if any(x in a for x in names)}
                print(f"  [state] {rel}")
                print("  [ceptre menu] " + "; ".join(
                    f"{k}:{v}" for k, v in sorted(menu.items())))
                for lab in sorted(set(theirs) | set(ours),
                                  key=str):
                    a, b = theirs.get(lab, 0), ours.get(lab, 0)
                    if a != b:
                        print(f"  {lab}: ceptre={a} metis={b}")
                return 1
            if not enabled:                     # joint quiescence
                proc.stdin.write(b"0\n"), proc.stdin.flush()
                continue
            tot = sum(w for _, _, w in enabled)
            r, pick = rng.random() * tot, enabled[-1]
            for cand in enabled:
                r -= cand[2]
                if r < 0:
                    pick = cand
                    break
            lab = ours_label(pick[1].name)
            idx = next(k for k, v in menu.items()
                       if k != 0
                       and ceptre_label(v, unrender, ns.strip_prefix,
                                        alias) == lab)
            proc.stdin.write(f"{idx}\n".encode()), proc.stdin.flush()
            for q, n in pick[1].consume.items():
                counts[q] = counts.get(q, 0) - n
                if counts[q] <= 0:
                    counts.pop(q)
            for q, n in pick[1].produce.items():
                counts[q] = counts.get(q, 0) + n
        proc.stdin.close()
        tail += proc.stdout.read().decode()
    finally:
        proc.kill()

    fin = final_counts(tail, unrender)
    mine = Counter({a: n for a, n in counts.items() if n > 0})
    if fin is None:
        print(f"no Ceptre final state captured ({step} steps)")
        return 1
    if fin != mine:
        print("FINAL STATE MISMATCH:")
        for a in sorted(set(fin) | set(mine)):
            if fin.get(a, 0) != mine.get(a, 0):
                print(f"  {a}: ceptre={fin.get(a, 0)} "
                      f"metis={mine.get(a, 0)}")
        return 1
    print(f"LOCKSTEP OK — {step} menus matched, final state "
          f"identical ({sum(mine.values())} tokens), seed {ns.seed}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
