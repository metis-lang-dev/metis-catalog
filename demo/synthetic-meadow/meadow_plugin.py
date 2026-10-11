"""Binds the meadow's one weight port, pk (the catch/evade split), at
0.5: the 1:1 split every number in this demo was recorded with (the
same binding as metispy tests/loop/test_loop.py MEADOW). Since port
plugins (metispy 9214991) an unbound port refuses to serve, so the
demo runs as `metis --plugin meadow_plugin:make meadow.llp`."""


class MeadowPorts:
    name = "meadow-pk-half"

    def __init__(self, case):
        pass

    def bind(self, reg):
        reg.weight("pk", lambda args, counts: 0.5)

    def tick(self, counts):
        return None                      # no env clock: quiescence is DONE

    def on_event(self, name, args):
        pass

    def snapshot(self):
        return None

    def restore(self, snap):
        pass


def make(case):
    return MeadowPorts(case)
