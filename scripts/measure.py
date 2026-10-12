"""Measure, do not estimate. Write the numbers into README.md.

    python scripts/measure.py            # measure and print, write nothing
    python scripts/measure.py --write    # measure and write between the markers

Three sections of the README are generated, between `<!-- measured:NAME:start -->`
and `<!-- measured:NAME:end -->`:

    tests        the suite's own count, from a run made now
    mutations    the mutation table, from a run made now
    deployment   the live run, rendered from deployments/studionet.json

It refuses to write anything if the suite is red, if a mutation escapes, or if
the recorded deployment is not of the contract file in this repository, so a
number in the README is always one that was checked.
"""

import argparse
import hashlib
import json
import pathlib
import re
import subprocess
import sys

ROOT = pathlib.Path(__file__).absolute().parent.parent
README = ROOT / "README.md"
RECORD = ROOT / "deployments" / "studionet.json"
SOURCE = ROOT / "contracts" / "rubric.py"
EXPLORER = "https://explorer-studio.genlayer.com"
GEN = 10 ** 18


def gen(wei):
    v = int(wei) / GEN
    return f"{v:.4f}".rstrip("0").rstrip(".") + " GEN"


def tx(h):
    return f"[`{h[:10]}...`]({EXPLORER}/tx/{h})"


def run_tests():
    proc = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-q", "-p", "no:cacheprovider"],
                          cwd=ROOT, capture_output=True, text=True)
    tail = (proc.stdout + proc.stderr).strip().splitlines()[-1]
    if proc.returncode != 0:
        raise SystemExit("the suite is red; nothing written:\n" + tail)
    passed = int(re.search(r"(\d+) passed", tail).group(1))
    skipped = int((re.search(r"(\d+) skipped", tail) or [0, 0])[1])
    return passed, skipped


def run_mutations():
    proc = subprocess.run([sys.executable, "scripts/mutate.py", "--md"], cwd=ROOT,
                          capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit("a mutation escaped or the baseline is red; nothing written:\n" + proc.stderr[-2000:])
    rows = [line for line in proc.stdout.splitlines() if line.startswith("| ") and "`" in line]
    return len(rows), proc.stdout.strip()


def render_deployment(rec):
    here = hashlib.sha256(SOURCE.read_bytes().replace(b"\r\n", b"\n")).hexdigest()
    if rec["source_sha256"] != here:
        raise SystemExit("deployments/studionet.json records a different contract file; redeploy "
                         "with python scripts/demo.py before measuring")
    addr = rec["contract"]
    deploy = [s for s in rec["steps"] if s["step"] == "deploy"][0]
    out = [
        f"Deployed on studionet at [`{addr}`]({EXPLORER}/address/{addr}) (deploy {tx(deploy['tx'])}). "
        f"Every value below was read back from the chain by `scripts/demo.py` and written to "
        f"[`deployments/studionet.json`](deployments/studionet.json); none of it is typed by hand.",
        "",
        "| Prize | Amount | Status | Winning entry | Paid to |",
        "|---|---|---|---|---|",
    ]
    for k, pz in enumerate(rec["prizes"]):
        p = pz["prize"]
        won = f"entry {p['winning_entry']}" if p["winning_entry"] >= 0 else "none"
        paid = p["winner"] or p["sponsor"]
        out.append(f"| {k}: {p['title']} | {gen(p['amount'])} | {p['status']} | {won} | `{paid}` |")
    out += ["", "The rubric, frozen at open, and how many judged entries met each criterion:", "",
            "| # | Criterion | Points | Met |", "|---|---|---|---|"]
    for c in rec["prizes"][0]["rubric"]:
        out.append(f"| {c['index']} | {c['text']} | {c['points']} | {c['met']} |")
    out += ["", "Every entry, and the marks the validators agreed on (one per criterion, in order):", "",
            "| Entry | Text | Marks | Score | Reason the leader gave (not consensus) |", "|---|---|---|---|---|"]
    for pz in rec["prizes"]:
        for e in pz["entries"]:
            text = e["text"] if len(e["text"]) <= 80 else e["text"][:77] + "..."
            reason = e["why"].replace("|", "/") if e["why"] else "-"
            out.append(f"| {e['id']} | {text} | **{e['marks']}** | {e['score']} | {reason} |")
    b = rec["balances"]
    win = rec["prizes"][0]["prize"]["winner"]
    if win:
        name = [n for n, a in rec["accounts"].items() if a.lower() == win.lower()][0]
        gained = int(b[f"{name}_after"]) - int(b[f"{name}_before"])
        out += ["", f"The winner's balance, read from the chain before the award and after it landed: "
                    f"{gen(b[f'{name}_before'])} to {gen(b[f'{name}_after'])}, a gain of **{gen(gained)}**. "
                    f"Held by the contract afterwards: {rec['held_after']} wei."]
    out += ["", "Every transaction, in order, refusals included, with the wallet that sent it:", "",
            "| Step | From | Outcome | Transaction |", "|---|---|---|---|"]
    names = {a.lower(): n for n, a in rec["accounts"].items()}
    for s in rec["steps"]:
        if s["step"] == "deploy":
            continue
        outcome = "ok" if s["ok"] else "refused: " + s["refusal"].replace("[EXPECTED] ", "").replace("|", "/")
        out.append(f"| {s['step']} | {names.get(str(s.get('from', '')).lower(), '-')} | {outcome} | {tx(s['tx'])} |")
    out += ["", "`tests/test_runbook.py::TestTheRecord` replays these marks through this repository's "
                "contract and fails unless it scores and awards exactly what the deployed one did."]
    return "\n".join(out)


def replace(text, name, body):
    start, end = f"<!-- measured:{name}:start -->", f"<!-- measured:{name}:end -->"
    pattern = re.compile(re.escape(start) + r".*?" + re.escape(end), re.S)
    if not pattern.search(text):
        raise SystemExit(f"README.md has no {name} markers")
    return pattern.sub(lambda _: f"{start}\n{body}\n{end}", text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    args = ap.parse_args()

    passed, skipped = run_tests()
    tests = (f"Measured: **{passed} passed**, {skipped} skipped. The skipped tests are the opt-in "
             f"StudioNet integration tests, which run with `GENLAYER_STUDIO=1`.")
    n, table = run_mutations()
    mutations = f"Measured: **{n} mutations, {n} caught, 0 escaped.**\n\n{table}"
    if not RECORD.exists():
        raise SystemExit("no deployments/studionet.json; run python scripts/demo.py first")
    deployment = render_deployment(json.loads(RECORD.read_text(encoding="utf-8")))

    text = README.read_text(encoding="utf-8")
    text = replace(text, "tests", tests)
    text = replace(text, "mutations", mutations)
    text = replace(text, "deployment", deployment)
    print(f"  tests      {passed} passed, {skipped} skipped")
    print(f"  mutations  {n} caught, 0 escaped")
    print(f"  deployment {json.loads(RECORD.read_text(encoding='utf-8'))['contract']}")
    if args.write:
        README.write_text(text, encoding="utf-8", newline="\n")
        print("  README.md written")


if __name__ == "__main__":
    main()
