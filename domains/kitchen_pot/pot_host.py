"""The shared-pot kitchen's host (specialist-tree s-404d001f step 3a; steps/step3-cases-brief.md): ONE scripted
kitchen in this process, two cooks' hands and one pot, served to each cook's session through its own host.

The kitchen is metispy's scripted kitchen (metis.domains.kitchen.host: kitchen.llp's multiset effects, pure
Python), with the hand per cook and the pot shared: Overcooked is not used (overcooked_ai_py is not installed;
installing it is the user's call). Every order is due at the start: ORDERS per cook.

What a cook reads (world-private, its own copy synced by its own host): its hand (hand_free | held_onion |
held_dish | held_soup), the pot (pot_space n, pot_onion n, cooking), its orders waiting (order n). What it does
(on_event, the fired rule's name): fetch_onion, load, start, fetch_dish, plate, serve — each applied to THIS
cook's hand and the one pot. A command the kitchen cannot carry out (a load with no room, a start without three
onions, a plate with no soup cooking, a second cook acting on a pot it does not hold …) is not applied and is
logged `impossible`: the case's check counts them (the arbitration's failure), it never hides them.

The kitchen's log (every command in order, with the cook, the beat and whether it applied) is the world-facing
stream the case compares; `kitchen(key)` returns the one kitchen for its key (the composition's directory)."""
import json
import os

ORDERS = 2                    # per cook, all due at the start
HANDS = ("hand_free", "held_onion", "held_dish", "held_soup")
POT = ("pot_space", "pot_onion", "cooking")
READ = HANDS + POT + ("order",)
SHARED = {}                   # key -> Kitchen: the one kitchen every cook's host steps


class Kitchen:
    def __init__(self, cooks, orders=ORDERS):
        self.hand = {c: "hand_free" for c in cooks}
        self.orders = {c: orders for c in cooks}
        self.served = {c: 0 for c in cooks}
        self.pot = {"space": 3, "onions": 0, "cooking": None}     # cooking: the cook whose soup it is
        self.log = []                                            # [{n, cook, event, ok, why?}]
        self.fetched = {c: 0 for c in cooks}
        self.loaded = {c: 0 for c in cooks}
        self.max_onions = 0

    def reading(self, cook):
        r = {self.hand[cook]: 1}
        if self.pot["space"]:
            r["pot_space"] = self.pot["space"]
        if self.pot["onions"]:
            r["pot_onion"] = self.pot["onions"]
        if self.pot["cooking"]:
            r["cooking"] = 1
        if self.orders[cook]:
            r["order"] = self.orders[cook]
        return r

    def act(self, cook, event):
        """Apply EVENT for COOK → (applied, why not). kitchen.llp's effects, per hand, on the one pot."""
        h, p = self.hand[cook], self.pot
        why = None
        if event == "fetch_onion":
            why = None if h == "hand_free" and self.orders[cook] else "hand not free or no order"
            if not why:
                self.hand[cook] = "held_onion"
                self.fetched[cook] += 1
        elif event == "load":
            why = None if h == "held_onion" and p["space"] > 0 and not p["cooking"] else "no onion in hand or no room"
            if not why:
                self.hand[cook], p["space"], p["onions"] = "hand_free", p["space"] - 1, p["onions"] + 1
                self.loaded[cook] += 1
                self.max_onions = max(self.max_onions, p["onions"])
        elif event == "start":
            why = None if p["onions"] == 3 and not p["cooking"] else "not three onions"
            if not why:
                p["onions"], p["cooking"] = 0, cook
        elif event == "fetch_dish":
            why = None if h == "hand_free" else "hand not free"
            if not why:
                self.hand[cook] = "held_dish"
        elif event == "plate":
            why = None if h == "held_dish" and p["cooking"] == cook else "no dish or not this cook's soup"
            if not why:
                self.hand[cook], p["cooking"], p["space"] = "held_soup", None, 3
        elif event == "serve":
            why = None if h == "held_soup" and self.orders[cook] else "no soup or no order"
            if not why:
                self.hand[cook] = "hand_free"
                self.orders[cook] -= 1
                self.served[cook] += 1
        else:
            return False, None                                  # no world effect (a report, a request)
        self.log.append({"n": len(self.log), "cook": cook, "event": event, "ok": why is None, **({"why": why} if why else {})})
        return why is None, why

    STATE = ("hand", "orders", "served", "pot", "log", "fetched", "loaded", "max_onions")

    def state(self):
        return json.loads(json.dumps({k: getattr(self, k) for k in self.STATE}))

    def set_state(self, st):
        for k in self.STATE:
            setattr(self, k, json.loads(json.dumps(st[k])))

    def summary(self):
        return {"served": dict(self.served), "orders_left": dict(self.orders), "fetched": dict(self.fetched),
                "loaded": dict(self.loaded), "max_onions": self.max_onions,
                "impossible": [e for e in self.log if not e["ok"]], "commands": len(self.log)}


def kitchen(key, cooks=("cook_a", "cook_b")):
    if key not in SHARED:
        SHARED[key] = Kitchen(cooks)
    return SHARED[key]


class PotHost:
    """One cook's host over the shared kitchen: bind · tick · on_event · observe · reading · sync · pending (the
    face metis-agent's Live reads under the tick)."""

    def __init__(self, package_dir, case=None):
        spec = json.load(open(os.path.join(package_dir, "cook.json")))
        self.cook = spec["cook"]
        self.key = os.path.abspath(os.path.join(package_dir, spec.get("kitchen", "..")))
        self.kitchen = kitchen(self.key, tuple(spec.get("cooks", ("cook_a", "cook_b"))))
        # a hosted day as metis-agent's AgentHost runs one: no person's script (the orders are the kitchen's), nothing
        # due by the clock, the beat counted at each tick
        self.beat, self.due, self.script, self.last = 0, (), {}, None
        self._pot = None                               # the latched pot (latch / unlatch), else live

    def bind(self, reg):
        pass

    def reading(self):
        r = self.kitchen.reading(self.cook)
        if self._pot is not None:                      # latched: the pot as it stood at the boundary, the hand live
            r = {a: n for a, n in r.items() if a not in POT}
            r.update(self._pot)
        return r

    def latch(self):
        """The tick's rule 2, host-defined: the pot (what the OTHER cook changes) as it stands at this boundary
        until unlatch(); this cook's own hand and orders stay live, so its own commands are never hidden from it."""
        full = self.kitchen.reading(self.cook)
        self._pot = {a: n for a, n in full.items() if a in POT}

    def unlatch(self):
        self._pot = None

    def observe(self, counts):
        return self.reading()

    def sync(self, counts):
        """The do-lines that bring the session's kitchen atoms to the kitchen as it stands (its own preds only)."""
        r, dos = self.reading(), []
        for a, n in sorted(r.items()):
            have = counts.get(a, 0)
            if n > have:
                dos.append("+%s %d" % (a, n - have))
            elif n < have:
                dos.append("-%s %d" % (a, have - n))
        for a, have in sorted(counts.items()):
            if have > 0 and a not in r and a.split("(")[0] in READ:
                dos.append("-%s %d" % (a, have))
        return dos

    def tick(self, counts):
        self.beat += 1
        return self.sync(counts)

    def world(self, lines):
        raise ValueError("world lines: the kitchen is the world; its orders are its script")

    def pending(self):
        return False

    def on_event(self, name, args):
        self.kitchen.act(self.cook, name.split("[")[0])

    def snapshot(self):
        """The one kitchen's state (a cook's undo or fork restores the kitchen both cooks stand in)."""
        return {"cook": self.cook, "kitchen": self.kitchen.state()}

    def restore(self, snap):
        self.kitchen.set_state(snap["kitchen"])


def make(case=None, package_dir=None):
    return PotHost(package_dir or os.path.dirname(os.path.abspath(__file__)), case)
