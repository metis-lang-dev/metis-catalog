"""The pass's host (the shared-pot kitchen's director): no world of its own — it exists so the agent can take lines
into the director's session (the relayed reports and statuses, its grants' ages). Nothing to read, nothing to do."""


class PassHost:
    def __init__(self):
        self.beat, self.due, self.script, self.last = 0, (), {}, None

    def bind(self, reg):
        pass

    def tick(self, counts):
        self.beat += 1
        return []

    def on_event(self, name, args):
        pass

    def observe(self, counts):
        return {}

    def reading(self):
        return {}

    def sync(self, counts):
        return []

    def pending(self):
        return False

    def world(self, lines):
        raise ValueError("world lines: the pass has no world")

    def snapshot(self):
        return {"beat": self.beat}

    def restore(self, snap):
        self.beat = snap["beat"]


def make(case=None):
    return PassHost()
