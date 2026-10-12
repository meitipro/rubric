"""
The demo, replayed offline.

scripts/demo.py puts the demo on StudioNet from scripts/demo_data.py (STEPS).
This file replays the same steps against the real contract in the simulator,
so a demo that could not succeed is caught before a single transaction is
spent on it.

When deployments/studionet.json exists, the replay goes further: it feeds the
simulator the marks the validators actually agreed on, and checks that the
contract in this repository scores and awards exactly what the deployed one
did, and refuses exactly where it refused.

    pytest tests/test_runbook.py -v
"""

import hashlib
import importlib.util
import json
import pathlib

import pytest

import glsim as S

CONTRACT_PATH = "contracts/rubric.py"
M = S.load_contract(CONTRACT_PATH)
RECORD = pathlib.Path("deployments/studionet.json")

_spec = importlib.util.spec_from_file_location("demo_data", "scripts/demo_data.py")
D = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(D)

WHO = {"sponsor": "0x" + "a1" * 20, "ann": "0x" + "b2" * 20, "ben": "0x" + "c3" * 20,
       "cal": "0x" + "d4" * 20, "dev": "0x" + "e5" * 20, "stranger": "0x" + "f6" * 20}
T0 = 1_790_000_000
NAMES = [c for c, _ in D.RUBRIC]

# the entry each ok judging is about, in order
JUDGED = [s[2][1] for s in D.STEPS if s[1] == "judge" and s[3] == "ok"]


def args_for(method, spec):
    if method == "open":
        title, brief, rubric, ew, jw = spec
        criteria, points = D.joined(rubric)
        return [title, brief, criteria, points, ew, jw], D.PRIZE
    return list(spec), 0


def replay(marks):
    """Run STEPS. `marks` are what the ok judgings come back with, in order."""
    S.reset_transfers()
    c = S.deploy(CONTRACT_PATH)
    queue = list(marks)
    outcomes = []
    clock = T0
    for step in D.STEPS:
        actor, method, spec, expect, label = step[:5]
        clock += 30
        if "after_entries" in step[5:]:
            clock = max(clock, M.seconds(c.prize(0)["entries_close"]) + 20)
        if "after_judging" in step[5:]:
            clock = max(clock, M.seconds(c.prize(0)["judge_close"]) + 20)
        S.set_time(M.iso(clock))
        S.set_mocks()
        args, value = args_for(method, spec)
        if method == "judge" and expect == "ok":
            want = queue.pop(0)
            S.set_mocks(leader_prompts={"<criteria>\n[0] " + NAMES[0]: {"marks": want, "because": "replayed"},
                                        "<criteria>\n[0] " + NAMES[-1]: {"marks": want[::-1], "because": "replayed"}})
        S.set_sender(WHO[actor])
        try:
            S.call(c, method, *args, value=value)
            outcomes.append(("ok", ""))
        except S.UserError as e:
            outcomes.append(("refused", e.message))
    return c, outcomes


class TestDemoData:
    def test_every_value_the_demo_sends_passes_the_bounds(self):
        criteria, points = D.joined(D.RUBRIC)
        assert M.rubric_refusal(M.split_list(criteria), M.parse_points(points)) == ""
        assert M.MIN_TITLE <= len(D.TITLE) <= M.MAX_TITLE and M.MIN_BRIEF <= len(D.BRIEF) <= M.MAX_BRIEF
        for w in (D.ENTRY_WINDOW, D.JUDGE_WINDOW):
            assert M.MIN_WINDOW <= w <= M.MAX_WINDOW
        assert 1 <= D.PRIZE <= M.MAX_PRIZE
        for text in (D.ANN, D.BEN, D.CAL, D.DEV, D.LATE):
            assert M.MIN_ENTRY <= len(M.clean_text(text)) <= M.MAX_ENTRY

    def test_each_entry_changes_one_thing(self):
        assert "appeal" in D.ANN and "appeal" not in D.BEN          # Ben leaves out appeals
        assert "validator" not in D.CAL.lower()                      # Cal explains nothing
        assert "appeal" in D.DEV and "agree" in D.DEV                # Dev was as good, and never judged

    def test_the_windows_outlast_the_steps_meant_to_land_inside_them(self):
        """Seven transactions after open are meant to find entries open, and
        four after entries close are meant to find judging open (three of them
        judgings); at up to 60 s a transaction (90 s for a judging) they land
        inside both windows with room to spare."""
        assert D.ENTRY_WINDOW >= 7 * 60 + 120
        assert D.JUDGE_WINDOW >= 3 * 90 + 3 * 60 + 60


class TestReplay:
    def test_the_demo_succeeds_and_refuses_exactly_where_it_says(self):
        _, outcomes = replay(D.EXPECTED_MARKS)
        assert [o for o, _ in outcomes] == [s[3] for s in D.STEPS]

    def test_the_refusals_say_why(self):
        _, outcomes = replay(D.EXPECTED_MARKS)
        msgs = [m for o, m in outcomes if o == "refused"]
        wants = ["the sponsor cannot enter", "enters once per prize", "judging opens when entries close",
                 "entries closed at", "only the sponsor or an entrant", "entry 3 is waiting to be judged",
                 "judging closed at"]
        assert len(msgs) == len(wants)
        for msg, want in zip(msgs, wants):
            assert want in msg, (want, msg)

    def test_the_expected_marks_award_ann_and_leave_dev_unjudged(self):
        c, _ = replay(D.EXPECTED_MARKS)
        assert [(e["by"], e["marks"], e["score"]) for e in c.entries_of(0)["entries"]] == [
            (WHO["ann"], "111", 100), (WHO["ben"], "101", 70), (WHO["cal"], "000", 0), (WHO["dev"], "unjudged", 0)]
        p = c.prize(0)
        assert (p["status"], p["winning_entry"], p["winner"]) == ("awarded", 0, WHO["ann"])
        assert S.transfers() == [(WHO["ann"], D.PRIZE)] and c.held_total() == 0


@pytest.mark.skipif(not RECORD.exists(), reason="no deployment recorded yet: python scripts/demo.py")
class TestTheRecord:
    """The live run, checked against this repository."""

    def _record(self):
        return json.loads(RECORD.read_text(encoding="utf-8"))

    def test_the_record_is_of_this_source(self):
        here = hashlib.sha256(pathlib.Path(CONTRACT_PATH).read_bytes().replace(b"\r\n", b"\n")).hexdigest()
        assert self._record()["source_sha256"] == here, "the deployed contract is not this file; redeploy"

    def test_every_step_on_chain_did_what_the_demo_expected(self):
        steps = [s for s in self._record()["steps"] if s["step"] != "deploy"]
        assert [("ok" if s["ok"] else "refused") for s in steps] == [s[3] for s in D.STEPS]

    def test_this_contract_awards_what_the_deployed_one_awarded(self):
        rec = self._record()
        by_id = {e["id"]: e for e in rec["prizes"][0]["entries"]}
        c, outcomes = replay([by_id[i]["marks"] for i in JUDGED])
        assert [o for o, _ in outcomes] == [s[3] for s in D.STEPS]
        assert [(e["marks"], e["score"]) for e in c.entries_of(0)["entries"]] == \
            [(e["marks"], e["score"]) for e in rec["prizes"][0]["entries"]]
        mine, theirs = c.prize(0), rec["prizes"][0]["prize"]
        for field in ("status", "winning_entry", "amount"):
            assert str(mine[field]) == str(theirs[field]), field

    def test_the_winner_was_paid_the_prize_on_chain(self):
        rec = self._record()
        win = rec["prizes"][0]["prize"]["winner"]
        if win:
            name = [n for n, a in rec["accounts"].items() if a.lower() == win.lower()][0]
            gained = int(rec["balances"][f"{name}_after"]) - int(rec["balances"][f"{name}_before"])
            assert gained == int(rec["prizes"][0]["prize"]["amount"])
        assert rec["held_after"] == "0"
