"""Mutation pass: break every defence on purpose, confirm a test notices.

Passing tests prove nothing on their own. Each entry below is a small edit to
the contract that removes a defence. The suite must fail for every one of them,
and this script records WHICH test caught it, so the table in the README is
measured rather than claimed.

    python scripts/mutate.py            # run them all, print what caught what
    python scripts/mutate.py --md       # emit the markdown table for the README

An escaping mutation is a finding, not a nuisance: either a missing test, or a
later defence strict enough that an earlier test can no longer fail. The script
exits non-zero if anything escapes, and refuses to run on a red baseline.

Three rules keep the harness honest:

  * the unmutated suite must be green before anything is mutated;
  * a find string that is missing, or matches more than once, is a failure of
    the harness, never a skip, so refactoring cannot quietly turn a row off;
  * scripts/lift.py runs inside every mutated copy before the suite, so the lib
    parity test can never stand in for the behavioural test a mutation deserves.
"""

import argparse
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = pathlib.Path(__file__).absolute().parent.parent
TARGET = "rubric.py"

FENCE = '    return str(raw).replace("<", "(").replace(">", ")").replace("[", "(").replace("]", ")")'
CLOSED_IN_JUDGE = ('        if str(p.status) != OPEN:\n            raise gl.vm.UserError(f"{ERR_EXPECTED} this prize is closed")\n'
                   '        if str(e.marks) != "":')
MARKS_SHAPE = '    if len(s) != n or any(ch not in "01" for ch in s):'
SCORE = '    return sum(int(points[k]) for k in range(len(points)) if marks[k] == "1")'
JUDGE_GATE = '        if sender != p.sponsor and int(self.entry_of.get(f"{pid}:{sender.as_hex}", u256(0))) == 0:'

MUTATIONS = [
    # -- reading the marks
    ("marks of the wrong length are accepted", MARKS_SHAPE, '    if any(ch not in "01" for ch in s):'),
    ("marks in words are accepted", MARKS_SHAPE, "    if len(s) != n:"),
    ("commas between marks are not tolerated", 'ch not in " ,")', 'ch not in " ")'),

    # -- the two orders
    ("the second pass is asked in the forward order",
     "            rev, _ = ask(title, brief, reversed_names, entry, n)", "            rev, _ = ask(title, brief, names, entry, n)"),
    ("the reversed marks are not read back", "    return marks[::-1]", "    return marks"),
    ("a criterion met in one order only is met",
     '"1" if a == "1" and b == "1" else "0"', '"1" if a == "1" or b == "1" else "0"'),
    ("only the forward order counts",
     '            return {"marks": fold(fwd, unreverse(rev)), "because": because}',
     '            return {"marks": fwd, "because": because}'),
    ("marks of different lengths are folded",
     '    if forward == "" or reverse_unreversed == "" or len(forward) != len(reverse_unreversed):',
     '    if forward == "" or reverse_unreversed == "":'),

    # -- reading the model
    ("an unusable answer is not retried",
     "    for _ in range(2):\n        raw = gl.nondet.exec_prompt(", "    for _ in range(1):\n        raw = gl.nondet.exec_prompt("),
    ("an unusable answer is read as nothing met",
     '    raise gl.vm.UserError(f"{ERR_LLM} the model gave no usable mark for every criterion")', '    return "0" * n, ""'),
    ("an answer that is not an object crashes the block",
     "        if isinstance(raw, dict):\n            marks", "        if True:\n            marks"),

    # -- the validator
    ("the validator agrees with an error",
     "                return False\n            theirs", "                return True\n            theirs"),
    ("the validator skips the structural check",
     "            if not marks_sound(proposed, n):\n                return False", "            if False:\n                return False"),
    ("the validator agrees with anything sound", '            return rubric_agrees(mine["marks"], proposed, n)', "            return True"),
    ("the validator agrees when its own model fails",
     "            except gl.vm.UserError:\n                return False", "            except gl.vm.UserError:\n                return True"),
    ("agreement ignores soundness",
     "    return marks_sound(mine, n) and marks_sound(theirs, n) and str(mine) == str(theirs)",
     "    return str(mine) == str(theirs)"),

    # -- the deterministic half
    ("the agreed marks are not checked again",
     "        if not marks_sound(marks, n):\n            raise", "        if False:\n            raise"),
    ("the score counts every criterion", SCORE, "    return sum(int(points[k]) for k in range(len(points)))"),
    ("the score counts the unmet criteria", SCORE,
     '    return sum(int(points[k]) for k in range(len(points)) if marks[k] == "0")'),
    ("a criterion's tally is not kept", "                c.met = u256(int(c.met) + 1)", "                c.met = u256(int(c.met))"),
    ("the judged count is not kept", "        p.n_judged = u256(int(p.n_judged) + 1)", "        p.n_judged = u256(int(p.n_judged))"),
    ("who asked is not recorded", "        e.judged_by = sender", "        e.judged_by = p.sponsor"),
    ("a leader's reason is stored as sent",
     '        e.why = sanitise_reason(res.get("because", ""))', '        e.why = str(res.get("because", ""))'),
    ("a leader's reason is stored uncapped",
     '    return " ".join("".join(out).split())[:limit]', '    return " ".join("".join(out).split())'),

    # -- the free refusals
    ("anyone may ask for a judging", JUDGE_GATE, "        if False:"),
    ("only the sponsor may ask for a judging", JUDGE_GATE, "        if sender != p.sponsor:"),
    ("an entry is judged twice", '        if str(e.marks) != "":\n            raise', "        if False:\n            raise"),
    ("judging opens before entries close",
     '        if now <= int(p.entries_close):\n            raise gl.vm.UserError(f"{ERR_EXPECTED} judging',
     '        if False:\n            raise gl.vm.UserError(f"{ERR_EXPECTED} judging'),
    ("judging never closes", "        if now > int(p.judge_close):\n            raise", "        if False:\n            raise"),
    ("judging closes a second early",
     "        if now > int(p.judge_close):\n            raise", "        if now >= int(p.judge_close):\n            raise"),
    ("an entry of another prize is judged",
     "        if i < 0 or i >= len(self.entries) or int(self.entries[i].prize_id) != int(prize_id):",
     "        if i < 0 or i >= len(self.entries):"),
    ("a decided prize is judged", CLOSED_IN_JUDGE,
     CLOSED_IN_JUDGE.replace("        if str(p.status) != OPEN:", "        if False:", 1)),

    # -- entering
    ("the sponsor may enter", "        if sender == p.sponsor:\n            raise", "        if False:\n            raise"),
    ("an entrant enters twice", "        if int(self.entry_of.get(key, u256(0))) > 0:", "        if False:"),
    ("entries never close", "        if self._now() > int(p.entries_close):", "        if False:"),
    ("entries close a second early",
     "        if self._now() > int(p.entries_close):", "        if self._now() >= int(p.entries_close):"),
    ("entries are unlimited", "        if int(p.n_entries) >= MAX_ENTRIES:", "        if False:"),
    ("an entry of any length is accepted", "        if len(body) < MIN_ENTRY or len(body) > MAX_ENTRY:", "        if False:"),
    ("an entrant is not remembered", "        self.entry_of[key] = u256(eid + 1)", "        pass"),
    ("entries are not linked", "            self.entries[int(p.last_entry)].next = u256(eid)", "            pass"),

    # -- the award
    ("the award waits for nobody", "                if not late:\n                    raise", "                if False:\n                    raise"),
    ("an unjudged entry can win", "[str(self.entries[i].marks) != UNJUDGED for i in ids]", "[True for i in ids]"),
    ("an unjudged entry is not marked", "                e.marks = UNJUDGED", "                pass"),
    ("the award comes while entries are open",
     '        if now <= int(p.entries_close):\n            raise gl.vm.UserError(f"{ERR_EXPECTED} entries are open',
     '        if False:\n            raise gl.vm.UserError(f"{ERR_EXPECTED} entries are open'),
    ("a prize is awarded twice",
     '        if str(p.status) != OPEN:\n            raise gl.vm.UserError(f"{ERR_EXPECTED} this prize was already decided',
     '        if False:\n            raise gl.vm.UserError(f"{ERR_EXPECTED} this prize was already decided'),
    ("a tie goes to the latest entry", "        if best < 0 or int(scores[k]) > int(scores[best]):",
     "        if best < 0 or int(scores[k]) >= int(scores[best]):"),
    ("a zero score can win", "        if not judged[k] or int(scores[k]) <= 0:", "        if not judged[k]:"),
    ("the lowest score wins", "        if best < 0 or int(scores[k]) > int(scores[best]):",
     "        if best < 0 or int(scores[k]) < int(scores[best]):"),
    ("the winner is off by one", "        p.winning_entry = u256(ids[k] + 1)", "        p.winning_entry = u256(ids[k])"),
    ("the prize goes to the sponsor anyway",
     "        self._send(self.entries[ids[k]].by, int(p.amount))", "        self._send(p.sponsor, int(p.amount))"),
    ("a prize nobody won is kept",
     "            p.status = RETURNED\n            self._send(p.sponsor, int(p.amount))", "            p.status = RETURNED"),

    # -- money
    ("the prize may be free", "        if amount < 1 or amount > MAX_PRIZE:", "        if amount > MAX_PRIZE:"),
    ("the held counter is not raised", "        self.held = u256(int(self.held) + amount)", "        pass"),
    ("a payout beyond what is held is sent", "        if amount > int(self.held):", "        if False:"),
    ("the held counter is not lowered", "        self.held = u256(int(self.held) - amount)", "        pass"),

    # -- opening
    ("the rubric refusal is ignored", '        if refusal != "":', "        if False:"),
    ("more than six criteria are accepted", "    if len(criteria) > MAX_CRITERIA:", "    if False:"),
    ("a criterion of any length is accepted",
     "        if len(c) < MIN_CRITERION or len(c) > MAX_CRITERION:", "        if False:"),
    ("two criteria with the same wording are accepted",
     "    if len(set(c.lower() for c in criteria)) != len(criteria):", "    if False:"),
    ("points that do not match the criteria are accepted",
     "    if points is None or len(points) != len(criteria):", "    if points is None:"),
    ("points of any size are accepted", "        if v < MIN_POINTS or v > MAX_POINTS:", "        if False:"),
    ("a missing criterion is dropped and the rest renumbered",
     '    return [clean_text(part) for part in str(text).split("|")]',
     '    return [clean_text(part) for part in str(text).split("|") if clean_text(part)]'),
    ("the windows are unbounded",
     "        if ew < MIN_WINDOW or ew > MAX_WINDOW or jw < MIN_WINDOW or jw > MAX_WINDOW:", "        if False:"),
    ("the judging window is unbounded",
     "        if ew < MIN_WINDOW or ew > MAX_WINDOW or jw < MIN_WINDOW or jw > MAX_WINDOW:",
     "        if ew < MIN_WINDOW or ew > MAX_WINDOW:"),
    ("judging closes with the entries", "judge_close=u256(now + ew + jw)", "judge_close=u256(now + ew)"),
    ("the title is unbounded", "        if len(t) < MIN_TITLE or len(t) > MAX_TITLE:", "        if False:"),
    ("the brief is unbounded", "        if len(b) < MIN_BRIEF or len(b) > MAX_BRIEF:", "        if False:"),

    # -- the prompt boundary
    ("the fence is removed", FENCE, "    return str(raw)"),
    ("the fence leaves square brackets", FENCE, '    return str(raw).replace("<", "(").replace(">", ")")'),
    ("the entry reaches the prompt unfenced", "{fence(entry)}", "{entry}"),
    ("the criteria reach the prompt unfenced", 'f"[{k}] {fence(criteria[k])}"', 'f"[{k}] {criteria[k]}"'),
    ("the title reaches the prompt unfenced", "{fence(title)}", "{title}"),
    ("the prompt no longer says partly is not met",
     "0 if it does not, or only\npartly, or you cannot tell", "0 if it does not"),
    ("the prompt no longer states the count", "Number of criteria: {n}. ", ""),
    ("control characters are stored", '            out.append(" ")\n        else:', "            out.append(ch)\n        else:"),
]


PYTEST = [sys.executable, "-m", "pytest", "tests/", "-x", "-q", "--no-header", "-p", "no:cacheprovider"]


def copy_repo(tmp):
    dst = pathlib.Path(tmp) / "repo"
    shutil.copytree(ROOT, dst, ignore=shutil.ignore_patterns(
        "__pycache__", ".pytest_cache", ".git", "artifacts", "*.pyc"))
    return dst


def run_one(label, find, replace):
    with tempfile.TemporaryDirectory() as tmp:
        dst = copy_repo(tmp)
        target = dst / "contracts" / TARGET
        src = target.read_text(encoding="utf-8")
        hits = src.count(find)
        if hits == 0:
            return "PATTERN NOT FOUND", None
        if hits > 1:
            return "PATTERN NOT UNIQUE", None
        target.write_text(src.replace(find, replace, 1), encoding="utf-8", newline="\n")
        subprocess.run([sys.executable, "scripts/lift.py"], cwd=dst, capture_output=True)
        proc = subprocess.run(PYTEST, cwd=dst, capture_output=True, text=True)
        if proc.returncode == 0:
            return "ESCAPED", None
        text = proc.stdout + proc.stderr
        m = re.search(r"^(?:FAILED|ERROR) (\S+?)::(\S+?)(?:\[|\s|$)", text, re.M)
        if m:
            return "caught", m.group(2).split("::")[-1]
        m = re.search(r"^E\s+(\w*(?:Error|Exception))", text, re.M)
        if m:
            return "caught", m.group(1) + " at import"
        return "caught", "unnamed failure"


def baseline_is_green():
    with tempfile.TemporaryDirectory() as tmp:
        dst = copy_repo(tmp)
        proc = subprocess.run(PYTEST, cwd=dst, capture_output=True, text=True)
        return proc.returncode == 0, (proc.stdout + proc.stderr)[-2000:]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", action="store_true", help="emit the README table")
    args = ap.parse_args()

    green, tail = baseline_is_green()
    if not green:
        print("the unmutated suite is not green; every mutation would look caught:\n" + tail, file=sys.stderr)
        return 2

    rows, escaped = [], []
    for label, find, replace in MUTATIONS:
        status, test = run_one(label, find, replace)
        if status == "caught":
            rows.append((label, test))
            if not args.md:
                print("  caught   %-70s %s" % (label, test), flush=True)
        else:
            escaped.append((label, status))
            print("  %-8s %s" % (status, label), file=sys.stderr, flush=True)

    if args.md:
        print("| Mutation | Caught by |")
        print("|---|---|")
        for label, test in rows:
            print("| %s | `%s` |" % (label, test))
    else:
        print()
        print("  %d mutations, %d caught, %d escaped" % (len(MUTATIONS), len(rows), len(escaped)))
    return 1 if escaped else 0


if __name__ == "__main__":
    sys.exit(main())
