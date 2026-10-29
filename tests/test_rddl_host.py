"""The RDDL world host (tools/rddl_host.py, rddl-worlds s-242c7c3f step 1) on
nav's gym: the mapping, the gym child, one step per action, the sync, the
world lines, the snapshot replayed. Skipped where no interpreter has
pyRDDLGym (the catalog's CI installs pyyaml and pytest only)."""
import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import rddl_host  # noqa: E402


def _gym():
    try:
        py = rddl_host.interpreter()
    except RuntimeError:
        return False
    return subprocess.run([py, "-c", "import pyRDDLGym, rddlrepository"], capture_output=True).returncode == 0


needs_gym = pytest.mark.skipif(not _gym(), reason="no interpreter with pyRDDLGym ($METIS_RDDL_PY)")


def nav():
    spec = importlib.util.spec_from_file_location("nav_host_t", ROOT / "domains/nav/nav_host.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_the_mapping_is_rddl_recorders():
    assert rddl_host.atom_of("elevator-at-floor___e0__f2") == "elevator_at_floor(e0,f2)"
    assert rddl_host.atom_of("tick") == "tick"
    m = nav()
    assert m.atom("robot-at___x6__y12") == "at(x6_y12)" and m.atom("P___x6__y12") is None
    assert m.action_of("die_north[C=x21_y12,C2=x21_y15]", ()) == {"move-north": True}
    assert m.action_of("mv_west", ()) == {"move-west": True} and m.action_of("other", ()) is None


@needs_gym
def test_nav_host_steps_the_gym_per_action_and_brings_the_program_along():
    m = nav()
    h = m.make({})
    assert h.horizon == 40 and len(h.observed) == 12 and h.reading()["at(x21_y12)"] == 1 and h.reading()["dead"] == 0
    p = h.ports()
    assert p["gym"]["problem"] == "Navigation_MDP_ippc2011" and p["derived"] == ["dead"]
    assert p["actions"] == ["move-east", "move-north", "move-south", "move-west"] and p["weights"] == ["die", "go"]
    # the weight ports are the instance's: P of the target, 0 at the goal
    assert m.go(("x21_y12", "x21_y15"), {}, h) == pytest.approx(1 - h.nonfluents["P___x21__y15"])
    assert m.die(("x21_y20", "x21_y15"), {}, h) == 0.0
    h.on_event("mv_west[C=x21_y12,C2=x14_y12]", ())      # P(x14_y12) = 0: the robot arrives
    assert h.t == 1 and h.reading()["at(x14_y12)"] == 1
    dos = h.tick({"at(x21_y12)": 1})                       # the program still says x21_y12: brought along
    assert sorted(dos) == ["+at(x14_y12) 1", "-at(x21_y12) 1"] and h.t == 1     # acted this beat: no extra step
    assert h.tick({"at(x14_y12)": 1}) == [] and h.t == 2  # nothing acted: the world steps on its own
    snap = h.snapshot()
    h2 = m.make({})
    h2.restore(snap)
    assert (h2.t, h2.obs, h2.seed) == (h.t, h.obs, h.seed)


@needs_gym
def test_nav_host_world_lines_seed_and_episode_end():
    m = nav()
    h = m.make({})
    with pytest.raises(ValueError, match="observed atom"):
        h.world(["+at(nowhere)"])
    with pytest.raises(ValueError, match="world lines are"):
        h.world(["teleport"])
    h.world(["-at(x21_y12)", "+at(x6_y12)"])                # the gym changes at once (nina's review R1) ...
    assert h.reading()["at(x6_y12)"] == 1 and h.t == 0
    assert sorted(h.sync({"at(x21_y12)": 1})) == ["+at(x6_y12) 1", "-at(x21_y12) 1"] and h.t == 0   # ... no step
    h.world(["nonfluent P___x9__y12 0.75"])
    assert h.nonfluents["P___x9__y12"] == 0.75 and m.die(("x6_y12", "x9_y12"), {}, h) == 0.75
    h.world(["reset 7"])
    assert h.seed == 7 and h.t == 0 and h.reading()["at(x21_y12)"] == 1
    for _ in range(41):                                     # the first tick reads the reset world (copy semantics)
        if h.tick({}) is None:
            break
    assert h.done and h.t == 40 and h.tick({}) is None     # the gym's horizon ends the episode
    h.reseed(3)
    assert (h.seed, h.t, h.done) == (3, 0, False)


@needs_gym
def test_the_snapshot_does_not_grow_with_fired_events():
    """The repl stores the host's snapshot after every fired row: a snapshot
    that grew per event made it quadratic (a 23.7 GB xtraffic run, rddl-worlds
    step 3). It holds the episode only, bounded by the horizon."""
    import json
    h = nav().make({})
    size = len(json.dumps(h.snapshot()))
    for _ in range(500):
        h.on_event("other_rule", ())                       # a fired row that is no action
    assert len(json.dumps(h.snapshot())) == size


def wildfire():
    spec = importlib.util.spec_from_file_location("wildfire_host_t", ROOT / "domains/wildfire/wildfire_host.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@needs_gym
def test_an_observing_world_hands_the_step_in_and_reads_the_settled_cycle():
    """Observer mode (wildfire): the host acts (the seeded random agent), the
    program gets the action's atoms and a tick, the reading waits for its cycle;
    an input it never took is a stall, and the reading shows it."""
    h = wildfire().make({})
    assert h.policy == "random" and h.negatives and "tick" in h.transient
    assert h.observe({}) == {}                                   # before the first step: nothing to read
    r = h.reading()
    assert r["burning(x1,y3)"] == 1 and r["not_burning(x1,y3)"] == 0 and r["not_burning(x2,y2)"] == 1
    dos = h.tick({"burning(x1,y3)": 1})                          # the program had no not_ atoms yet
    assert h.t == 1 and "+tick" in dos and "+not_burning(x2,y2) 1" in dos
    acts = [d for d in dos if d.startswith(("+put_out", "+cut_out"))]
    assert len(acts) <= 1 and all("(" in a for a in acts)        # the agent's action, as the program's atom
    held = {"tick": 1, "walk(x1,y1)": 1}
    assert h.observe(held) == {}                                 # the cycle in flight
    assert h.observe({}) == h.reading()                          # settled: the gym's state
    assert h.tick(held) == [] and h.stalled and h.t == 1         # the input was never taken: a stall
    assert h.observe(held) == h.reading()                        # from now on read at once
    assert h.tick(held) == [] and h.t == 2                       # the world goes on without the program
    a = wildfire().make({})
    a.tick({})
    assert a.last_action == h.actions[0][1]                      # the agent is seeded per episode


@needs_gym
def test_a_restored_observing_world_draws_on_as_the_original():
    """nina's step-3 review N1: a restore draws the policy's steps again, so the
    seeded agent goes on from the same place (a replay of the draws as fixed
    actions left it at its start, and later draws differed), and `stalled` holds."""
    m = wildfire()
    h = m.make({})
    h.reseed(5)
    for _ in range(3):
        h.tick({})
    snap = h.snapshot()
    g = m.make({})
    g.restore(snap)
    assert (g.t, g.obs) == (h.t, h.obs)
    for _ in range(4):
        h.tick({})
        g.tick({})
        assert g.last_action == h.last_action and g.obs == h.obs
    h.stalled = True
    k = m.make({})
    k.restore(h.snapshot())
    assert k.stalled


def world(name):
    spec = importlib.util.spec_from_file_location("%s_host_t" % name, ROOT / "domains" / name / ("%s_host.py" % name))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


@needs_gym
def test_a_noop_observer_hands_its_start_token_when_the_program_lacks_it():
    """rddl-watch s-cfe94dca, N3: sysadmin's host steps the gym with no action
    before the program's pass (a noop observer, as gol's), and hands `m(i0)`,
    the start of the program's mark/update/sweep pipeline, with the step — only
    when the program does not hold it: the pipeline wraps and carries its own."""
    h = world("sysadmin").make({})
    assert h.policy == "noop" and h.tokens == ("m(i0)",) and world("gol").make({}).policy == "noop"
    first = h.tick({})
    assert h.t == 1 and "+m(i0)" in first
    assert {d.split()[0][1:] for d in first if d != "+m(i0)"} <= set(h.reading())   # the rest is the sync
    held = {a: n for a, n in h.reading().items() if n}
    held["m(i0)"] = 1
    again = h.tick(held)
    assert h.t == 2 and "+m(i0)" not in again
