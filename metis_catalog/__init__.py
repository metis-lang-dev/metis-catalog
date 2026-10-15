"""metis_catalog — the catalog's loader (domain-catalog s-2a2bc758; CATALOG.md).

Each domain is one directory under domains/ with a manifest, domain.yaml:

    name: dog
    display: the dog                  # the narrator's name
    line: "a robot dog: …"            # the one display line (consoles, the orchestrator's INSTALLED list)
    voice: own                        # own | third
    program: dog.llp                  # paths are relative to the manifest's directory
    serves: [a.llp, …]                # the served program's files, in order (pkg.mod:path allowed);
                                      #   absent: [program] + packs/*.llp — Domain.serves()
    notch: dog.notch.json
    host: dog_host.py:make            # file.py:factory (relative) or pkg.mod:factory
    agent: agent.py[:VARIANT]         # the domain-agent module; absent with intent.spec: the generic agent
    intent: {spec, grammar, prompt, examples: {gemma4: …}, corpus}   # J material only
    clock: {beats: 1}                 # env beats per orchestrator tick
    pair: [kitchen_shared]            # partners stepped inside its clock
    partner_of: kitchen               # never loaded alone
    docs: README.md
    tests: tests/
    records: records/                 # the agents' surprise records (records/<session>.jsonl)

A directory whose only catalog is one .llp needs no manifest (a
program-only domain); every other .llp is listed as a plain catalog, with
what it has read off the checkout (#plugin, #notch, a README).

    import metis_catalog as mc
    mc.root()                 # the checkout ($METIS_CATALOG, else this package's repo)
    mc.domains()              # [Domain] — every manifest, by name
    mc.get("dog")             # Domain: .program .packs() .serves() .host .host_spec_for(program_dir) .intent … .has()
    mc.index()                # every catalog for a console's list: the domains first (display line, has)

    python -m metis_catalog list [--json]
"""
import os
import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

__version__ = "0.1.0"


def root():
    """The checkout: $METIS_CATALOG, else the repo this package lives in."""
    env = os.environ.get("METIS_CATALOG")
    return Path(env).resolve() if env else Path(__file__).resolve().parents[1]


@dataclass
class Domain:
    """One manifest, its paths resolved against its directory."""
    name: str
    dir: Path
    manifest: dict = field(default_factory=dict)

    def path(self, rel):
        return (self.dir / rel).resolve() if rel else None

    @property
    def display(self):
        return self.manifest.get("display") or self.name

    @property
    def line(self):
        return self.manifest.get("line") or ""

    @property
    def voice(self):
        return self.manifest.get("voice") or "third"

    @property
    def program(self):
        return self.path(self.manifest.get("program"))

    @property
    def notch(self):
        return self.path(self.manifest.get("notch"))

    @property
    def host(self):
        """The host as the manifest names it: (absolute file, factory) for
        file.py:factory, (None, "pkg.mod:factory") for a module spec, or None."""
        h = self.manifest.get("host")
        if not h:
            return None
        mod, _, fac = h.rpartition(":")
        if mod.endswith(".py"):
            return (self.dir / mod).resolve(), fac
        return None, h

    def host_spec_for(self, program_dir=None):
        """The host spec as metispy's Repl takes it (plugin=…): a file.py
        relative to the program's directory, or the module spec as is."""
        h = self.host
        if h is None:
            return None
        f, fac = h
        if f is None:
            return fac
        base = Path(program_dir) if program_dir else (self.program.parent if self.program else self.dir)
        return "%s:%s" % (os.path.relpath(f, base), fac)

    @property
    def agent(self):
        """(the agent module's file, its variant) or None — absent with an
        intent.spec, the generic agent (metis-agent intent_domain) is the agent."""
        a = self.manifest.get("agent")
        if not a:
            return None
        f, _, var = a.partition(":")
        return self.path(f), var or None

    @property
    def intent(self):
        """The intent material's paths (spec, grammar, prompt, examples, corpus):
        J only — the REPL's tool syntax (T) is metispy's, never the catalog's."""
        i = self.manifest.get("intent") or {}
        out = {}
        for k, v in i.items():
            if isinstance(v, dict):
                out[k] = {kk: self.path(vv) for kk, vv in v.items()}
            elif isinstance(v, list):
                out[k] = [self.path(x) for x in v]
            else:
                out[k] = self.path(v)
        return out

    def packs(self):
        """The domain's extension packs: packs/*.llp beside the manifest, in
        name order (each `extends` the program). The served program is the
        program PLUS every pack (human-loop step 1, the architect's ruling):
        the domain agent builds and reloads from the union, the loop
        console's one-click open loads them, apply writes them there."""
        d = self.dir / "packs"
        return sorted(p.resolve() for p in d.glob("*.llp")) if d.is_dir() else []

    def serves(self):
        """The served program's files, in order: the program first, then
        what extends it (runtime-binding Q1, the architect's ruling). The
        manifest's `serves: [files]` — each relative to the manifest's
        directory, or `pkg.mod:path` inside an importable package (the
        kitchen pair's scenes live in metispy) — else [program] + packs().
        py, Go and the artifact emitter read the served program here only."""
        s = self.manifest.get("serves")
        if not s:
            return ([self.program] if self.program else []) + self.packs()
        return [_served_file(self.dir, x) for x in s]

    @property
    def records(self):
        return self.dir / (self.manifest.get("records") or "records")

    @property
    def readme(self):
        r = self.path(self.manifest.get("docs") or "README.md")
        return r if r and r.is_file() else None

    @property
    def clock(self):
        return dict(self.manifest.get("clock") or {"beats": 1})

    @property
    def pair(self):
        return list(self.manifest.get("pair") or [])

    @property
    def partner_of(self):
        return self.manifest.get("partner_of")

    def has(self):
        return {"program": bool(self.program and self.program.is_file()), "notch": bool(self.notch and self.notch.is_file()),
                "host": self.host is not None, "agent": self.agent is not None or bool(self.intent.get("spec")),
                "intent": bool(self.intent), "readme": self.readme is not None, "packs": bool(self.packs())}


def _served_file(base, entry):
    """One `serves` entry: a path relative to `base`, or pkg.mod:path."""
    mod, sep, rel = str(entry).partition(":")
    if sep and rel and "/" not in mod and not mod.endswith(".llp"):
        import importlib.util
        spec = importlib.util.find_spec(mod)
        if spec is None:
            raise ValueError("serves %r: no package %r" % (entry, mod))
        root = (Path(next(iter(spec.submodule_search_locations)))
                if spec.submodule_search_locations else Path(spec.origin).parent)
        return (root / rel).resolve()
    return (Path(base) / entry).resolve()


def _manifests(r=None):
    r = Path(r) if r else root()
    for p in sorted((r / "domains").rglob("domain.yaml")):
        if ".git" in p.parts or "__pycache__" in p.parts:
            continue
        m = yaml.safe_load(p.read_text()) or {}
        if not isinstance(m, dict) or not m.get("name"):
            raise ValueError("%s: a manifest needs a name" % p)
        yield Domain(str(m["name"]), p.parent.resolve(), m)


def domains(r=None):
    """Every domain with a manifest, by name (a name twice is an error)."""
    out = {}
    for d in _manifests(r):
        if d.name in out:
            raise ValueError("domain %r twice: %s and %s" % (d.name, out[d.name].dir, d.dir))
        out[d.name] = d
    return [out[k] for k in sorted(out)]


def get(name, r=None):
    for d in domains(r):
        if d.name == name:
            return d
    raise KeyError("no domain %r in %s" % (name, Path(r) if r else root()))


# ── the console's list: every catalog, the domains first ──────────────────────

_PLUGIN = re.compile(r"^#plugin\s+(\S+)", re.M)
_NOTCH = re.compile(r"^#notch\s+(\S+)", re.M)
_DRAFT = re.compile(r"(^|/)(iter\d+-world|step\d|.*_born$|.*-candidate|.*LOSSY)")


def _title(readme):
    for line in readme.read_text(errors="replace").splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return ""


def _table(r):
    rows, readme = {}, r / "README.md"
    if readme.is_file():
        for m in re.finditer(r"^\|\s*`([^`]+)/`\s*\|\s*(.+?)\s*\|\s*$", readme.read_text(errors="replace"), re.M):
            rows[m.group(1).strip("/")] = re.sub(r"\s+", " ", m.group(2))
    return rows


def _first_comment(text):
    for line in text.splitlines():
        if line.startswith("%"):
            s = line.lstrip("% ").strip()
            if s and not s.startswith(("SOURCE:", "//", "/")):
                return s
        elif line.strip():
            break
    return ""


def _short(s, n=140):
    s = re.sub(r"\*\*|`", "", s or "")
    return s if len(s) <= n else s[: n - 1].rsplit(" ", 1)[0] + "…"


def _inferred(r, path, table):
    """A catalog with no manifest: what it has, read off the checkout."""
    rel = path.relative_to(r).with_suffix("").as_posix()
    text = path.read_text(errors="replace")
    host = (m.group(1) if (m := _PLUGIN.search(text)) else
            "%s_host.py:make" % path.stem if (path.parent / ("%s_host.py" % path.stem)).is_file() else None)
    notch = (m.group(1) if (m := _NOTCH.search(text)) else
             "%s.notch.json" % path.stem if (path.parent / ("%s.notch.json" % path.stem)).is_file() else None)
    readme = next((x for x in (path.parent / path.stem / "README.md", path.parent / "README.md")
                   if x.is_file() and (x.parent.name == path.stem or len(list(x.parent.glob("*.llp"))) == 1)), None)
    row = table.get(path.parent.relative_to(r).as_posix(), "")
    alone = len(list(path.parent.glob("*.llp"))) == 1
    line = (_title(readme) if readme else "") or (row if alone else "") or _first_comment(text) or row
    domain = bool(host or notch or readme) and not _DRAFT.search(rel)
    return {"name": path.stem, "path": rel, "line": _short(line), "kind": "domain" if domain else "catalog",
            "manifest": None, "host": host, "notch": notch,
            "readme": readme.relative_to(r).as_posix() if readme else None,
            "has": {"program": True, "host": bool(host), "notch": bool(notch), "readme": bool(readme),
                    "agent": False, "intent": False, "packs": False}}


def index(r=None):
    """Every catalog of the checkout for a console's list: the manifests'
    domains first (their display line, what they have, the host spec as
    the program's Repl takes it), then the other .llp files — a program
    with a host, a notch or its own README is still a domain; the rest are
    plain catalogs."""
    r = (Path(r) if r else root()).resolve()
    table = _table(r)
    out, covered = [], set()
    for d in domains(r):
        if d.partner_of:                       # never loaded alone: the pair's lead lists it
            continue
        prog = d.program
        if prog is not None:
            covered.add(prog)
        has = d.has()
        line = d.line or (_title(d.readme) if d.readme else "") or (_first_comment(prog.read_text()) if prog and prog.is_file() else "")
        out.append({"name": d.name, "path": prog.relative_to(r).with_suffix("").as_posix() if prog and prog.is_relative_to(r) else None,
                    "line": _short(line), "kind": "domain", "manifest": (d.dir / "domain.yaml").relative_to(r).as_posix(),
                    "display": d.display, "host": d.host_spec_for() if prog else None,
                    "notch": os.path.relpath(d.notch, prog.parent) if d.notch and prog else None,
                    "readme": d.readme.relative_to(r).as_posix() if d.readme else None, "has": has,
                    "pair": d.pair})
    for p in sorted(r.rglob("*.llp")):
        if ".git" in p.parts or p.resolve() in covered:
            continue
        out.append(_inferred(r, p, table))
    return sorted(out, key=lambda e: (e["kind"] != "domain", e["manifest"] is None, e["name"] if e["kind"] == "domain" else e["path"]))


def readme_head(rel, limit=1600, r=None):
    """A README's opening (its title and first paragraphs, cut at a paragraph)."""
    p = (Path(r) if r else root()) / rel
    if not p.is_file():
        return ""
    out, n = [], 0
    for para in p.read_text(errors="replace").split("\n\n"):
        if n + len(para) > limit and out:
            break
        out.append(para)
        n += len(para) + 2
    return "\n\n".join(out)
