"""Deploy Rubric to StudioNet and put every path on the explorer.

    pip install genlayer-py==0.18.0
    python scripts/demo.py

The run deploys contracts/rubric.py exactly as it is in this repository, then
sends the steps in scripts/demo_data.py (STEPS), including the ones that end in
a refusal, and writes what happened to deployments/studionet.json: every
transaction hash, its sender and status, the refusal sentence where there was
one, the prize, its rubric and every entry as the chain holds them, and the
entrants' balances before the award and after the payout landed. Nothing in
that file is typed by hand.

Six accounts act, each in one role: the sponsor, four entrants and a stranger.
They are made in memory for this run and never written to disk. The sponsor is
funded from the StudioNet faucet to pay the prize in; nobody else needs GEN.
"""

import datetime
import hashlib
import json
import pathlib
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).absolute().parent))
import demo_data as D                                       # noqa: E402
from studio import EXPLORER, Studio                         # noqa: E402

ROOT = pathlib.Path(__file__).absolute().parent.parent
SOURCE = ROOT / "contracts" / "rubric.py"
OUT = ROOT / "deployments" / "studionet.json"


def utc_seconds(iso):
    t = datetime.datetime.fromisoformat(iso.replace("Z", "+00:00"))
    return int(t.timestamp())


def wait_past(iso, label):
    """Sleep until the chain clock has passed `iso`, with a margin, because
    the contract compares against the time of the transaction that arrives."""
    target = utc_seconds(iso) + 20
    left = target - int(time.time())
    if left > 0:
        print(f"  waiting {left}s for {label} ({iso})")
        time.sleep(left)


def args_for(method, spec):
    if method == "open":
        title, brief, rubric, ew, jw = spec
        criteria, points = D.joined(rubric)
        return [title, brief, criteria, points, ew, jw], D.PRIZE
    return list(spec), 0


def wait_for_balance(s, address, at_least, label, tries=24):
    """A payout can land a little after the transaction that sent it, so the
    balance is read until it has arrived rather than once."""
    for _ in range(tries):
        b = s.balance(address)
        if b >= at_least:
            return b
        time.sleep(5)
    print(f"  {label}: the payout had not landed after {tries * 5}s")
    return s.balance(address)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    code = SOURCE.read_text(encoding="utf-8")
    s = Studio()

    print("\naccounts (in memory, StudioNet test GEN only)")
    who = {name: s.account(name, gen=2 if name == "sponsor" else 0)
           for name in ("sponsor", "ann", "ben", "cal", "dev", "stranger")}

    print("\ndeploy")
    address = s.deploy(who["sponsor"], code, [])

    print("\nthe demo")
    before = {}
    for step in D.STEPS:
        actor, method, spec, expect, label = step[:5]
        if "after_entries" in step[5:]:
            wait_past(s.read(address, "prize", [0])["entries_close"], "entries to close")
        if "after_judging" in step[5:]:
            wait_past(s.read(address, "prize", [0])["judge_close"], "judging to close")
        if method == "award" and expect == "ok":
            before = {name: s.balance(who[name].address) for name in ("sponsor", "ann", "ben", "cal", "dev")}
        args, value = args_for(method, spec)
        s.write(who[actor], address, method, args, value=value, step=label, expect=expect)

    n = int(s.read(address, "count"))
    prizes = [{
        "prize": s.read(address, "prize", [k]),
        "rubric": s.read(address, "rubric_of", [k])["criteria"],
        "entries": s.read(address, "entries_of", [k])["entries"],
    } for k in range(n)]
    after = {}
    won = prizes[0]["prize"]["winner"] or prizes[0]["prize"]["sponsor"]
    for name in before:
        if who[name].address.lower() == won.lower():
            want = before[name] + int(prizes[0]["prize"]["amount"])
            after[name] = wait_for_balance(s, who[name].address, want, name)
    for name in before:
        if name not in after:
            after[name] = s.balance(who[name].address)
    record = {
        "network": "studionet",
        "chain_id": 61999,
        "contract": address,
        "explorer": f"{EXPLORER}/address/{address}",
        "source_sha256": hashlib.sha256(SOURCE.read_bytes().replace(b"\r\n", b"\n")).hexdigest(),
        "constructor": {},
        "accounts": {name: a.address for name, a in who.items()},
        "balances": {f"{name}_{when}": str(v[name]) for when, v in (("before", before), ("after", after))
                     for name in before},
        "held_after": str(s.read(address, "held_total")),
        "steps": s.log,
        "prizes": prizes,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(record, indent=2, default=str) + "\n", encoding="utf-8", newline="\n")

    print(f"\n  contract   {address}")
    print(f"  explorer   {EXPLORER}/address/{address}")
    for k, pz in enumerate(prizes):
        p = pz["prize"]
        print(f"  prize {k}   {p['status']:<9} winning entry {p['winning_entry']}  "
              f"marks {[(e['id'], e['marks'], e['score']) for e in pz['entries']]}")
    print(f"  written    {OUT.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
