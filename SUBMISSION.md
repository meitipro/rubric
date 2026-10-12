# Submission

One submission, under **Builder -> Intelligent Contracts**. This repository is
one standalone primitive.

---

## Before you submit, in order

1. **Measure, do not estimate.**

   ```bash
   python scripts/measure.py --write
   ```

   Runs the suite and the full mutation pass, renders the live record, and
   writes all three into README.md. It refuses to write anything if the suite
   is red, a mutation escapes, or the record is of a different contract file.

2. **Prove the address is evidence for this repository.**

   ```bash
   python scripts/verify_deployment.py <address>
   ```

   Reads the source back off chain, compares it with `contracts/rubric.py` and
   runs `genvm-lint check` on those bytes.

3. **Open the explorer page and check it.** It must show the deploy, the paid
   open, the four entries, the three judgings with a consensus result beside
   them, the award, and the seven refusals, each with its reason.

---

## On chain

The address, every transaction, every set of marks and the award are in the
[README](README.md#it-is-live-and-every-path-is-on-chain), rendered from
[`deployments/studionet.json`](deployments/studionet.json), and every
transaction with the wallet that sent it is in [EVIDENCE.md](EVIDENCE.md).

## What to say in the portal

**What it does.** Rubric is a prize with its marking scheme published before
the first entry. The sponsor pays the prize in and freezes a rubric of
criteria, each worth points, and two windows. Anyone else enters once. After
entries close, validators mark each entry met or not met per criterion, in both
criterion orders and without ever seeing the points or another entry; the
contract sums the points and pays the highest score. An entry nobody judged
before judging closed scores nothing.

**Why it needs GenLayer.** Whether a paragraph "says that a result can be
appealed to a larger group of validators" is a judgment in natural language,
and the sponsor who funds the prize is the one party who cannot be trusted to
make it. Independent validators must agree on every mark, and the sponsor
cannot enter, mark or choose.

**What it learned from earlier work.** The model is asked the coarsest
question that still carries the judgment, one bit per criterion, one entry at a
time, and is never shown points or money. Every judgment has a clock. The
uncertainty goes into the value (a mark that depends on the order is not met),
and the award is counting, not judging.
