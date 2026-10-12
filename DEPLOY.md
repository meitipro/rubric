# Deploying Rubric

Everything here runs on StudioNet. It is gasless; the only GEN needed is the
prize, and the sponsor gets it from the StudioNet faucet. Nothing needs a
private key in a file.

## 1 - Check the contract

```bash
pip install -r requirements-dev.txt
pytest tests/ -q
python scripts/schema_check.py contracts/rubric.py
GENVM_VERSION=v0.3.0-rc7 genvm-lint check contracts/rubric.py
```

`schema_check.py` runs the file through the live studionet runtime with
`gen_getContractSchemaForCode`, without deploying it. On Windows, set
`PYTHONIOENCODING=utf-8` first, or the linter dies printing its own tick.

## 2 - Run the demo

```bash
python scripts/demo.py
```

It makes six accounts in memory (`sponsor`, `ann`, `ben`, `cal`, `dev`,
`stranger`), funds the sponsor with 2 GEN from the faucet, and deploys
`contracts/rubric.py` exactly as it is in this repository. The data and the
steps are in [`scripts/demo_data.py`](scripts/demo_data.py); the same list
drives the demo and `tests/test_runbook.py`.

The prize: 0.5 GEN for the best one-paragraph explanation of GenLayer for a
newcomer, entries open for ten minutes and judging for twenty-five after that. Its
rubric:

| # | Criterion | Points |
|---|---|---|
| 0 | States that several validators must agree on a result before it is accepted | 40 |
| 1 | Says that a result can be appealed to a larger group of validators | 30 |
| 2 | Gives one concrete example of a question the network could decide | 30 |

The writes, in order:

| # | From | Call | Expected |
|---|---|---|---|
| 1 | sponsor | `open(title, brief, 3 criteria, 40/30/30, 600, 1500)` paying 0.5 GEN | ok: prize 0 |
| 2 | sponsor | `enter(0, ...)` | refused: the sponsor cannot enter |
| 3 | ann | `enter(0, <agree, appeal, a logo example>)` | ok: entry 0 |
| 4 | ben | `enter(0, <agree, an insurance example, no appeals>)` | ok: entry 1 |
| 5 | cal | `enter(0, <hype>)` | ok: entry 2 |
| 6 | dev | `enter(0, <agree, appeal, a translation example>)` | ok: entry 3 |
| 7 | ann | `enter(0, ...)` | refused: one entry per entrant |
| 8 | ann | `judge(0, 0)` | refused: judging opens when entries close |
| 9 | stranger | `enter(0, ...)` after entries close | refused: entries closed |
| 10 | stranger | `judge(0, 1)` | refused: only the sponsor or an entrant |
| 11 | sponsor | `judge(0, 1)` | ok: expected **101**, 70 points |
| 12 | ann | `judge(0, 0)` | ok: expected **111**, 100 points |
| 13 | cal | `judge(0, 2)` | ok: expected **000**, 0 points |
| 14 | stranger | `award(0)` | refused: entry 3 is waiting to be judged |
| 15 | dev | `judge(0, 3)` after judging closes | refused: judging closed |
| 16 | stranger | `award(0)` | ok: the prize to the highest score; entry 3 is unjudged |

The script waits for entries to close before step 9 and for judging to close
before step 15, and stops at the first step that does not do what the table
says, because the demo claims whatever it records. The marks are whatever the
validators agree on; the live ones are in the README.

It writes [`deployments/studionet.json`](deployments/studionet.json): every
transaction hash, its sender and status, each refusal's sentence, the prize,
its rubric and every entry as the chain holds them, and every entrant's balance
before the award and after the payout landed. Then:

```bash
pytest tests/test_runbook.py -v
```

`TestTheRecord` replays the marks the validators agreed on through this
repository's contract and fails unless it scores and awards exactly what the
deployed one did, and checks the winner's balance rose by exactly the prize.

## 3 - Reads - free, no transaction

```bash
genlayer network set studionet
genlayer call <address> count
genlayer call <address> prize --args 0
genlayer call <address> rubric_of --args 0
genlayer call <address> entries_of --args 0
genlayer call <address> held_total
```

## 4 - Before the portal

```bash
python scripts/verify_deployment.py <address>
python scripts/measure.py --write
```

The first reads the deployed source back off chain, compares it with
`contracts/rubric.py` and lints the deployed bytes. The second runs the suite
and the mutation pass and writes the measured numbers and the live record into
README.md. Neither writes anything unless every check passes.
