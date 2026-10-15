"""The plant's host (e2e-workflow s-143c3088, the acceptance domain): a
PortPlugin with no weight ports. The TIME face carries the person's commands
(the hosted day's script, or the domain agent's mapper) and the world's sun;
the SENSOR face (`observe`) reads the soil, which the plant's program predicts
— until a visitor waters it, which no rule explains: the surprise.

- tick: the outcome tokens left by the last beat retracted after the host
  has "narrated" them; `+sun` every SUN_EVERY beats while the soil is moist
  (the program's dry_out needs it); the script's commands. None ends the
  hosted day; a driver that brings its own person (the domain agent) sets
  script = {} and last = None.
- on_event: dry_out and water move the env's soil with the program.
- observe: {moist, dry} as the env has them. After VISITOR_AFTER dry beats
  a visitor waters the plant: the host reports `+visitor` (a world fact the
  program declares) and the env turns moist while the program says dry — an
  unmodeled reading, the surprise the loop console gets to explain. The pack
  `visitor_waters [dyn] : dry * visitor -o moist.` consumes the report, so
  the next visit is EXPLAINED by that rule (the kernel's recover), never
  fired by the sampler on its own (a triggerless rule would model the visit
  away and make watering unreachable — nina's finding, 2026-10-15).
PURITY: the env mutates only in tick/on_event; snapshot is total."""
import sys

OUTCOMES = ("done", "checked")

# the complementary pair the host keeps current, (needs, blocks): water needs
# dry soil, moist soil blocks it; a check needs nothing
PAIRS = (("dry", "moist"),)
WORDS = {"moist": "wait until my soil dries out"}
KEYS = {"moist": "soil"}
STANDING = ()

SUN_EVERY = 6        # beats of sun between dryings (9 s live)
VISITOR_AFTER = 8    # dry beats before a visitor waters the plant (12 s live)

SCRIPT = {   # beat -> do-lines: the hosted day (the loop console's one-click open)
    2: ["+cmd_check"],           # moist
    8: ["+cmd_check"],           # dry (the sun at 6, dry_out at 7)
    9: ["+cmd_water"],           # moist again
    16: ["+cmd_check"],          # dry again (the sun at 12)
    26: ["+cmd_check"],          # after the visitor (dry since 13, visited at 21)
}
LAST = 30


def _handle(args):
    return args.rstrip(")") if args else ""


def key(atom, names=None):
    name, _, args = atom.partition("(")
    k = KEYS.get(name)
    return None if k is None else k


def words(atom, names=None):
    name, _, args = atom.partition("(")
    return WORDS.get(name)


def flips(atom):
    name, _, args = atom.partition("(")
    for a, b in PAIRS:
        if name == a:
            return b
        if name == b:
            return a
    return None


class PlantHost:
    def __init__(self, case):
        self.beat = 0
        self.due = ()          # (beat, do-line) — the plant's world owes no answers; kept for the agent host
        self.acted = ()
        self.script, self.last = SCRIPT, LAST
        self.moist = True      # the env's soil
        self.dry_beats = 0
        self.visits = 0

    def bind(self, reg):
        pass

    def tick(self, counts):
        if self.last is not None and self.beat >= self.last:
            return None
        self.beat += 1
        dos = []
        for a, n in sorted(counts.items()):          # narrate, then clear
            if a.split("(")[0] in OUTCOMES:
                print(f"  [host beat {self.beat}] narrated {a}", file=sys.stderr)
                dos.append(f"-{a} {n}")
        dos += [d for b, d in self.due if b == self.beat]
        self.due = tuple(x for x in self.due if x[0] != self.beat)
        if self.moist and self.beat % SUN_EVERY == 0:
            dos.append("+sun")
        if not self.moist:                            # the visitor: off-model
            self.dry_beats += 1
            if self.dry_beats == VISITOR_AFTER - 1:
                dos.append("+visitor")            # the world's report: someone came by (a beat before the watering,
                print(f"  [host beat {self.beat}] a visitor came by", file=sys.stderr)   # so the record's checkpoint holds it)
            elif self.dry_beats >= VISITOR_AFTER:
                self.moist, self.dry_beats, self.visits = True, 0, self.visits + 1
                print(f"  [host beat {self.beat}] the visitor watered the plant", file=sys.stderr)
        dos += self.script.get(self.beat, [])
        return dos

    def on_event(self, name, args):
        self.acted += ((self.beat, name, tuple(args)),)
        base = name.split("[")[0].split("-")[0]
        if base == "dry_out":
            self.moist, self.dry_beats = False, 0
        elif base in ("water", "visitor_waters"):
            self.moist, self.dry_beats = True, 0

    def observe(self, counts):
        return {"moist": 1 if self.moist else 0, "dry": 0 if self.moist else 1}

    def snapshot(self):
        return (self.beat, self.due, self.acted, self.moist, self.dry_beats, self.visits)  # JSON data: arrays

    def restore(self, snap):                          # its JSON form: lists back to tuples
        beat, due, acted, self.moist, self.dry_beats, self.visits = snap
        self.beat = beat
        self.due = tuple((b, d) for b, d in due)
        self.acted = tuple((b, n, tuple(a)) for b, n, a in acted)


def make(case):
    return PlantHost(case)
