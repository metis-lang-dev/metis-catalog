"""The one CI check over every domain package (catalog-entry step 2): every
manifest carries only the package's keys (the loader refuses any other),
its files are there, and its generated intent files are what its
intent.yaml makes (python -m metis.intents check), and its own cases pass
through the interface stub (cases/*.yaml: the package's program alone, its
manifest's interface closed by the cases' facts; metis-lang spec/15 §10.4)."""
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from metis.catalog import manifests as mc  # noqa: E402  (the loader: metispy's since metis-packages)

PACKAGES = mc.domains(ROOT)          # raises ManifestError on a key a package does not carry


def test_every_package_loads():
    assert {"dog", "plant", "kitchen", "kitchen_shared"} <= {d.name for d in PACKAGES}


@pytest.mark.parametrize("d", [d for d in PACKAGES if d.intent.get("spec")], ids=lambda d: d.name)
def test_the_generated_intent_files_are_current(d):
    r = subprocess.run([sys.executable, "-m", "metis.intents", "check", d.name], cwd=ROOT,
                       capture_output=True, text=True, env=dict(os.environ, METIS_CATALOG=str(ROOT)))
    assert r.returncode == 0, r.stdout + r.stderr
    assert {"grammar", "prompt", "examples"} <= set(d.intent), d.name


@pytest.mark.parametrize("d", PACKAGES, ids=lambda d: d.name)
def test_the_packages_files_are_there(d):
    # a pkg.mod:path whose top-level package is not installed here (the
    # kitchen pair's scenes live in metispy): skipped; any other serves
    # error — a typo'd module with the package installed — fails
    tops = {str(x).partition(":")[0].split(".")[0] for x in d.manifest.get("serves") or []
            if ":" in str(x) and not str(x).partition(":")[0].endswith(".llp")}
    missing = sorted(t for t in tops if importlib.util.find_spec(t) is None)
    if missing:
        pytest.skip(f"{d.name} serves from {', '.join(missing)}, not installed here")
    for p in ([d.program] if d.manifest.get("program") else []) + d.extensions() + d.serves():
        assert p.is_file(), (d.name, p)


@pytest.mark.parametrize("d", [d for d in PACKAGES if (d.dir / "cases").is_dir()], ids=lambda d: d.name)
def test_the_packages_own_cases_pass_through_the_interface_stub(d):
    # the specialist alone (no director, no world): metispy's one generic stub, driven by the manifest
    from metis.catalog import stub
    rs = stub.run_package(d)
    assert rs, "%s: cases/ holds no case" % d.name
    assert all(r.passed for r in rs), stub.render(rs)


def test_the_kitchen_cooks_cancels_are_as_their_generator_writes_them():
    # a stop's cancels (specialist-tree step 3c, the architect's ruling (c)): kept in the lifted cook base, which no
    # installer regenerates — metispy's protocol_stub over the base's own rules, calm its idle, the world-private
    # preds the world's (regenerate: python -m metis.catalog.protocol_stub … --write, the arguments below)
    from metis.catalog import protocol_stub
    kit = ROOT / "domains" / "kitchen_pot"
    text = (kit / "cook_domain.llp").read_text()
    assert protocol_stub.BEGIN in text
    assert protocol_stub.refresh(text, "S", idle="calm", namespace="cook", bind="$self(S)",
                                 world=protocol_stub.world_private(kit / "cook_a" / "domain.yaml")) == text


@pytest.mark.parametrize("member", ["responder", "planner"])
def test_the_road_members_cancels_are_as_their_generator_writes_them(member):
    # the road domains (road-world s-e812715d step 2): each member base's stop stub, from metispy's protocol_stub
    from metis.catalog import protocol_stub
    road = ROOT / "domains" / "road"
    text = (road / ("%s_domain.llp" % member)).read_text()
    assert protocol_stub.BEGIN in text
    assert protocol_stub.refresh(text, member, idle="idle", namespace=member,
                                 world=protocol_stub.world_private(road / member / "domain.yaml")) == text


METISC = Path(os.environ.get("METISC") or ROOT.parent / "metis-lang" / "src" / "metisc")


@pytest.mark.skipif(not METISC.is_file(), reason="no metisc (METISC, else metis-lang/src/metisc beside)")
@pytest.mark.parametrize("case", ["gap", "tight"])
def test_the_road_lane_change_risk_is_its_golden(case):
    # the instrument's lane-change query over the road's world model (spec/16 §10.1, tick: ego): needs a metisc of
    # metis-lang master >= 97b8749 (rows by tick)
    ev = ROOT / "domains" / "road" / "eval"
    r = subprocess.run([str(METISC), "--evaluate", "cases/%s.yaml" % case], cwd=ev, capture_output=True, text=True)
    assert r.stdout + r.stderr + "rc %d\n" % r.returncode == (ev / "goldens" / ("%s.txt" % case)).read_text()
