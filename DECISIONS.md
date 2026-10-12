# DECISIONS

Why Rubric is built the way it is. Each section names the alternative that was
rejected and what it would have cost.

## The model marks criteria, never picks a winner

The obvious design hands the model every entry and asks for the best one. It
does two jobs at once: reading each entry against the rubric, and weighing the
entries against each other. The second is a judge's taste wearing a model's
clothes, and the most confident entry wins it.

So the model answers one question per criterion about one entry at a time: met
or not. It never sees another entry, the points or the prize. The score is the
sum of the points of the criteria met, and the winner is the highest score:
both are the contract's own counting.
`tests/test_e2e.py::TestStorageShape::test_the_block_never_touches_storage_and_never_sees_points_or_money`
fails if points or money are ever passed into the block, and
`test_the_model_is_never_shown_the_points_or_the_prize` checks every prompt of
a real judging.

## One 0 or 1 per criterion, not a score out of ten

A score is a number two honest models will rarely agree on exactly, and a
tolerance band would only move the argument to its edge. A yes or no per
criterion is the coarsest answer that still carries the judgment, and the
points turn it into a ranking without asking the model for one. The answer is
a string of exactly as many characters as there are criteria; anything else
is unusable, retried once, and then raised as `[LLM_ERROR]`.

## Both orders, and a criterion counts only if both say met

The leader marks the entry against the criteria in the frozen order and again
against them reversed, and reads the second answer back. A criterion is met
only if both passes say so; a mark that depends on where the criterion sat in
the list is not clear enough to score. A model that answers by position, say
"first met, the rest not", meets nothing it is unsure of, and the tests check
it. The uncertainty goes into the value (not met), never into the comparison.

## Partly is not met

The prompt says 1 only if the entry clearly does what the criterion asks, and
0 if it does not, only partly does, or the model cannot tell. A rubric is
published so that entrants can write to it; an entry that wants the points
does the thing.

## Every judgment has a clock

Entries close at a fixed time, and judging closes a fixed window after that.
After `judge_close`, `judge()` refuses before any model is asked, and the award
marks an entry nobody judged as `unjudged`, which scores nothing. Without that
bound an entry could be judged after the award, or the award held hostage by
an entry nobody asks about. The demo's fourth entry was as good as the winner's
and was never judged in time; it did not win.

## Who may ask for a judging

The sponsor or any entrant on this prize, about any entry, once per entry. A
judging spends inference on every validator, so a stranger cannot ask, and an
entrant may ask about a rival, so a sponsor cannot sit on the entry it does
not want judged.

## The sponsor cannot enter, judge differently, or pick a winner

The sponsor writes the rubric and pays the prize in, before any entry exists.
After that it has the same one judging per entry as anyone else, and
`award()` is open to anyone and reads only the stored scores.
`test_the_sponsor_has_no_say_over_the_winner_in_code` fails if the award ever
reads the sponsor for anything but returning a prize nobody won.

## The prize is paid in at open

The value attached to `open()` is the prize, held by the contract under a
`held` counter. A sponsor cannot announce a prize it does not have, and cannot
take it back once entries arrive. If nothing scores above zero the prize goes
back to the sponsor; otherwise it goes to the highest score, the earliest entry
on a tie. Every payout goes through one guarded path, after the state that
justifies it is written.

## One entry per entrant, at most twelve per prize

An entrant is keyed `"prize:address"` in one map, so a second entry is refused
without scanning, and two prizes never see each other's entrants. Twelve
entries bound what a single award reads.

## Tagging untrusted text is not a fence

The title, brief, criteria and entry are all written by someone with a stake.
`fence()` replaces `< > [ ]` at the prompt boundary, length preserved, and the
contract numbers the criteria itself after fencing them, so the only square
brackets in a prompt are the ones it wrote. An entry cannot close its block or
forge a criterion. Stored text is kept verbatim; only the prompt is fenced.

## The reason string is leader-supplied

`because` is stored next to each entry, sanitised and capped at 140
characters, and is not part of consensus. Nothing in the contract acts on it,
and the view says so.

## Second lines that no public call reaches

Two checks are unreachable today and kept on purpose, each pinned by a
structural test so a refactor cannot quietly drop it: the agreed marks are
checked again before they score (the validator already refuses unsound marks),
and the award passes which entries were judged (an unjudged entry already has
a score of zero).

## Known limits

- On StudioNet a payout can land a little after the transaction that sent it,
  so `scripts/demo.py` reads the winner's balance until it has arrived.
- The value of a refused payable call stays at the contract's address on
  StudioNet; `held` counts only accepted prizes, so it is never paid out.

## Why the tests are built the way they are

- **Each node gets its own answers**, so a contract that assumes both nodes read the same thing is caught offline.
- **A leader can lie**, so the validator's checks are reachable, and the free layer is measured: unsound marks must cost the validator zero prompts, and the free refusals before the block must cost everyone zero prompts.
- **The runbook is a test.** The demo is replayed offline from `scripts/demo_data.py` before a transaction is spent, and once `deployments/studionet.json` exists the validators' real marks are replayed through this file.
- **Mutation testing.** `scripts/mutate.py` removes each defence and names the test that caught it.

## GenVM constraints this contract obeys

- the runner is pinned (`py-genlayer:1jb45aa8...`), never `test` or `latest`
- the class is named after the product, because `genvm-lint validate` does not see a class named `Contract`; the storage row is called `Prize` so no dataclass shares its name
- no `int`, `list`, `dict` or `tuple` as a storage type, and no collection inside a storage dataclass; TreeMap keys are strings
- every persistent field is declared in the class body, and every stored field is read somewhere
- the block returns a flat dict of strings
- `gl.nondet` is reached only from `ask`, called only from inside the block
- payouts use `@gl.evm.contract_interface` and `emit_transfer(value=...)`
- the file is pure ASCII
- `genvm-lint` validates against GenVM `v0.3.0-rc7`, the release that ships the pinned runner; `scripts/verify_deployment.py` sets `GENVM_VERSION` accordingly
- `scripts/schema_check.py` validates the file against the live studionet runtime with `gen_getContractSchemaForCode` before a deploy is spent

## Not upgradable

There is no owner and no admin method. A prize's rubric, points and clocks are
frozen at `open()`, and marks on record stay the marks.
