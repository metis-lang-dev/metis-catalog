"""metis_catalog, the loader both consoles and both agent backends read
(domain-catalog s-2a2bc758 step 2): the manifests, their paths, the host as
the program's Repl takes it, the console's index."""
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import metis_catalog as mc  # noqa: E402


def test_every_manifest_is_whole():
    ds = {d.name: d for d in mc.domains(ROOT)}
    assert {"dog", "kitchen", "kitchen_shared", "wildfire", "tamarisk", "wgc"} <= set(ds)
    for d in ds.values():
        if d.manifest.get("program"):
            assert d.program.is_file(), d.name
        if d.manifest.get("notch"):
            assert d.notch.is_file(), d.name
        h = d.host
        if h and h[0] is not None:
            assert h[0].is_file(), d.name
        if d.agent:
            assert d.agent[0].is_file(), d.name
        for k, v in d.intent.items():
            for p in (v.values() if isinstance(v, dict) else v if isinstance(v, list) else [v]):
                assert p.is_file(), (d.name, k, p)
        if d.partner_of:
            assert d.partner_of in ds and d.name in ds[d.partner_of].pair


def test_paths_and_the_host_spec():
    dog, wf, kit = mc.get("dog", ROOT), mc.get("wildfire", ROOT), mc.get("kitchen", ROOT)
    assert dog.program == ROOT / "domains/dog/dog.llp" and dog.voice == "own" and dog.display == "the dog"
    assert dog.host_spec_for() == "dog_host.py:make" and dog.intent["grammar"].name == "dog.gbnf"
    assert dog.agent is None and dog.has()["agent"] and dog.has()["intent"]          # the generic agent, from intent.yaml
    assert wf.program == ROOT / "domains/rddl/wildfire.llp"
    assert wf.host_spec_for() == "wildfire/wildfire_plugin.py:make"                  # as wildfire.llp's own #plugin
    assert "#plugin wildfire/wildfire_plugin.py:make" in wf.program.read_text()
    assert kit.host_spec_for() == "metis.domains.kitchen.host:make" and kit.agent[1] == "kitchen"
    assert kit.clock == {"beats": 2} and kit.pair == ["kitchen_shared"]
    with pytest.raises(KeyError):
        mc.get("nope", ROOT)


def test_the_index_lists_every_catalog_the_domains_first():
    es = mc.index(ROOT)
    llps = [p for p in ROOT.rglob("*.llp") if ".git" not in p.parts]
    assert len(es) == len(llps)                                                      # every program once
    kinds = [e["kind"] for e in es]
    assert kinds == sorted(kinds, key=lambda k: k != "domain")
    named = [e["name"] for e in es if e["manifest"]]
    assert named[:6] == ["dog", "kitchen", "plant", "tamarisk", "wgc", "wildfire"]  # the manifests first
    assert "kitchen_shared" not in [e["name"] for e in es]                           # a partner is listed by its lead
    by = {e["path"]: e for e in es}
    assert by["domains/rddl/wildfire"]["notch"] == "wildfire.notch.json"
    assert by["domains/fiction/3lp"]["kind"] == "catalog"                            # program only, no manifest


def test_list_cli():
    out = subprocess.run([sys.executable, "-m", "metis_catalog", "list", "--domains"], cwd=ROOT,
                         capture_output=True, text=True, check=True).stdout
    assert "a robot dog" in out and out.splitlines()[1].split()[:2] == ["domain", "dog"]
