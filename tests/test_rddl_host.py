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
    h.world(["-at(x21_y12)", "+at(x6_y12)"])
    dos = h.tick({"at(x21_y12)": 1})
    assert h.reading()["at(x6_y12)"] == 1 and sorted(dos) == ["+at(x6_y12) 1", "-at(x21_y12) 1"]
    h.world(["nonfluent P___x9__y12 0.75"])
    h.tick({"at(x6_y12)": 1})
    assert h.nonfluents["P___x9__y12"] == 0.75 and m.die(("x6_y12", "x9_y12"), {}, h) == 0.75
    h.world(["reset 7"])
    h.tick({})
    assert h.seed == 7 and h.t == 0 and h.reading()["at(x21_y12)"] == 1
    for _ in range(40):
        if h.tick({}) is None:
            break
    assert h.done and h.t == 40 and h.tick({}) is None     # the gym's horizon ends the episode
    h.reseed(3)
    assert (h.seed, h.t, h.done) == (3, 0, False)
