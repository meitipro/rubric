"""Integration tests, run against StudioNet.

    pip install genlayer-py==0.18.0
    GENLAYER_STUDIO=1 pytest tests/test_integration.py -v

They are opt in. Without GENLAYER_STUDIO set they skip, so `pytest tests/ -q`
stays clean and offline on a reviewer's machine whatever is installed there,
and an unreachable network can never be mistaken for a broken contract.

They exercise the deterministic half on a real runtime, where the simulator is
weakest: the sender is derived from a signature rather than set by a test, the
prize is real value attached to a real transaction, a TreeMap is keyed on a
real address, and the free refusals before any model are shown to cost no
inference. The judgings themselves cost inference on every validator and are
on the record from scripts/demo.py.
"""

import os
import pathlib
import sys

import pytest

if not os.environ.get("GENLAYER_STUDIO"):
    pytest.skip("integration tests run against StudioNet and are opt in: set GENLAYER_STUDIO=1. "
                "Everything else runs offline with pytest tests/ -q", allow_module_level=True)

pytest.importorskip("genlayer_py", reason="pip install genlayer-py==0.18.0")

sys.path.insert(0, str(pathlib.Path(__file__).absolute().parent.parent / "scripts"))
from studio import Studio                                     # noqa: E402

CODE = (pathlib.Path(__file__).absolute().parent.parent / "contracts" / "rubric.py").read_text(encoding="utf-8")
TITLE = "Rubric, integration run"
BRIEF = "One paragraph for a newcomer explaining how GenLayer reaches a decision."
CRITERIA = "States that several validators must agree|Gives one concrete example of a question"
POINTS = "60|40"
ENTRY = "Several validators each answer and must agree, for example on whether a parcel arrived late."
PRIZE = 10 ** 15


@pytest.fixture(scope="module")
def world():
    s = Studio()
    sponsor = s.account("sponsor", gen=1)
    entrant = s.account("entrant")
    address = s.deploy(sponsor, CODE, [])
    s.write(sponsor, address, "open", [TITLE, BRIEF, CRITERIA, POINTS, 3600, 3600], value=PRIZE, step="open a prize")
    return s, address, sponsor, entrant


def test_a_prize_opens_with_the_signer_as_sponsor_and_the_value_held(world):
    s, address, sponsor, _ = world
    p = s.read(address, "prize", [0])
    assert p["status"] == "open" and p["sponsor"].lower() == sponsor.address.lower() and p["criteria"] == 2
    assert p["amount"] == str(PRIZE) and int(s.read(address, "held_total")) == PRIZE


def test_the_sponsor_cannot_enter(world):
    s, address, sponsor, _ = world
    row = s.write(sponsor, address, "enter", [0, ENTRY], step="the sponsor enters", expect="refused")
    assert "the sponsor cannot enter" in row["refusal"]


def test_an_entrant_enters_once_keyed_on_its_real_address(world):
    s, address, _, entrant = world
    s.write(entrant, address, "enter", [0, ENTRY], step="an entrant enters")
    row = s.write(entrant, address, "enter", [0, ENTRY], step="the entrant enters again", expect="refused")
    assert "enters once per prize" in row["refusal"]
    assert [e["by"].lower() for e in s.read(address, "entries_of", [0])["entries"]] == [entrant.address.lower()]


def test_a_judging_before_entries_close_is_refused_for_free(world):
    s, address, _, entrant = world
    row = s.write(entrant, address, "judge", [0, 0], step="judge too early", expect="refused")
    assert "judging opens when entries close" in row["refusal"]
    assert s.read(address, "entries_of", [0])["entries"][0]["marks"] == ""


def test_an_unknown_prize_is_a_refusal_not_the_newest_row(world):
    s, address, _, entrant = world
    row = s.write(entrant, address, "award", [99], step="award a prize that does not exist", expect="refused")
    assert "no such prize" in row["refusal"]
