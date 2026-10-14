"""The dog's host, a PortPlugin with no weight ports: the TIME face
carries the person's commands (as the domain agent would type them) and
the world's reports; the OUTPUT face actuates the robot and schedules
what the world answers. One tick = one beat of the dog's day.

- tick: the scripted command of the beat as a do-line (+cmd_*), the
  reports due this beat (+arrived(P), +locked_away(T), …), and the
  outcome tokens left by the last beat retracted after the host has
  "narrated" them (here: printed to stderr). [] is a quiet beat; None
  ends the day.
- on_event: a fired `go` schedules arrived(P) or blocked(P) two beats
  on, `find` schedules spotted(T) or locked_away(T), `follow` schedules
  lost; the body actions actuate and return. The world's answers are
  the E10 corpus's (go/tools/e10-corpus.py CMDS).
PURITY: the env mutates only in tick/on_event; snapshot is total."""
import sys

OUTCOMES = ("done", "refused", "progress", "expired", "cancelled")

# the complementary pairs the host keeps current (dog.llp: "exactly one of
# each pair holds"). A refusal whose blocker is one side of a pair is
# something the person can change in the world (the consult's `missing`);
# a blocker outside the pairs is `unexplained`. Handed to the domain agent
# at load; the catalog never sees it. ORDER IS A CONVENTION: (needs, blocks)
# — the first side is what a command needs, the second the side that blocks
# it; the agent reads the blocking side from that order (domain-agent step 5).
PAIRS = (
    ("battery_ok", "battery_low"),
    ("floor_dry", "floor_wet"),
    ("free", "obstacle"),           # by side
    ("clear", "wall"),              # by way
    ("leg_ok", "leg_hot"),
    ("mapped", "unmapped"),         # by place
    ("open", "closed"),             # by place
    ("person_in_view", "nobody"),
    ("seen", "unseen"),             # by thing
    ("spotted", "locked_away"),     # by thing, while searching
)


# What the person does to flip a blocking side, in the person's words: the
# resource.words of a `missing` consult answer (DESIGN v3), templated by the
# harness, never written by the model (E13 step 2: "you in front of me" is
# not a thing a person can supply; "come where I can see you" is). {P} is a
# place handle's display name, {T} a thing's.
WORDS = {
    "battery_low": "put me on my charger",
    "floor_wet": "dry the floor here, or move me to a dry spot",
    "obstacle": "move whatever is beside me on that side",
    "wall": "turn me away from the wall",
    "leg_hot": "give my front leg a minute to cool",
    "unmapped": "walk me to {P} once so I can map it",
    "closed": "open the way to {P}",
    "nobody": "come where I can see you",
    "unseen": "show me {T} once so I know it",
    "locked_away": "unlock where {T} is kept",
}


def words(atom, names=None):
    """The person's words for flipping `atom` (a blocking side, possibly with
    an argument), or None when the atom is not a blocking side. `names` maps
    handles to display names; a bare handle is used when it is missing."""
    name, _, args = atom.partition("(")
    w = WORDS.get(name)
    if w is None:
        return None
    arg = args.rstrip(")") if args else ""
    shown = (names or {}).get(arg, arg.replace("_", " "))
    return w.replace("{P}", shown).replace("{T}", shown)


def flips(atom):
    """The complement of a blocker atom, or None when it is not a pair's side
    (then the refusal is not about the world: busy, already, must stand)."""
    name, _, args = atom.partition("(")
    for a, b in PAIRS:
        if name == a:
            return b + ("(" + args if args else "")
        if name == b:
            return a + ("(" + args if args else "")
    return None

SCRIPT = {   # beat -> do-lines: the person's command, and world changes
    1: ["+cmd_sit"],
    2: ["+cmd_go(kitchen)"],            # the kitchen door is closed
    3: ["+cmd_stand"],
    4: ["+cmd_go(tag3)"],               # mapped and open: accepted
    5: ["+cmd_find(keys)"],             # busy: refused
    7: ["+cmd_move(backward)"],         # a wall right behind
    8: ["+cmd_find(extinguisher)"],     # accepted; the storage room is locked
    9: ["+cmd_query(chair)"],
    11: ["+cmd_follow"],
    12: ["+cmd_stop"],
    13: ["+cmd_unknown"],
    14: ["+cmd_paw"],
    15: ["-battery_ok", "+battery_low", "+cmd_find(bottle)"],   # the world changes
    16: ["+cmd_sit"],
    17: ["+cmd_turn(left)"],            # sitting: has to stand first
}
ANSWERS = {  # what the world says back to a long command, and when
    "go": {"tag3": ("arrived", 2), "door": ("arrived", 2), "window_chair": ("blocked", 2)},
    "find": {"extinguisher": ("locked_away", 2), "keys": ("spotted", 3), "bottle": ("spotted", 3)},
}
LAST = 18


class DogHost:
    def __init__(self, case):
        self.beat = 0
        self.due = ()        # (beat, do-line) scheduled by on_event
        self.acted = ()      # actuation log

    def bind(self, reg):
        pass                 # no weight ports: the dog's choices are the state's

    def tick(self, counts):
        if self.beat >= LAST:
            return None
        self.beat += 1
        dos = []
        for a, n in sorted(counts.items()):          # narrate, then clear
            if a.split("(")[0] in OUTCOMES:
                print(f"  [host beat {self.beat}] narrated {a}", file=sys.stderr)
                dos.append(f"-{a} {n}")
        dos += [d for b, d in self.due if b == self.beat]
        self.due = tuple(x for x in self.due if x[0] != self.beat)
        dos += SCRIPT.get(self.beat, [])
        return dos

    def on_event(self, name, args):
        self.acted += ((self.beat, name, tuple(args)),)
        base = name.split("[")[0].split("-")[0]   # "go[P=tag3]" -> "go"
        if base in ANSWERS and args:
            kind, delay = ANSWERS[base].get(args[0], ("timeout", 3))
            atom = "+timeout" if kind == "timeout" else f"+{kind}({args[0]})"
            self.due += ((self.beat + delay, atom),)
        elif base == "follow":
            self.due += ((self.beat + 4, "+lost"),)
        elif base.startswith(("stop_", "cancel_")):
            self.due = ()        # the task is over: the world owes it no answer

    def snapshot(self):
        return (self.beat, self.due, self.acted)

    def restore(self, snap):
        self.beat, self.due, self.acted = snap


def make(case):
    return DogHost(case)
