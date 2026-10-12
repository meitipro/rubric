# Rubric - a prize scored against a rubric written before the first entry

A GenLayer Intelligent Contract for a writing prize whose marking scheme was
published before anyone entered. The sponsor pays the prize in and opens it
with a brief, a short rubric of criteria, each worth a number of points, an
entry window and a judging window. Anyone else enters once. After entries
close, validators decide **one thing per entry and per criterion: met, or
not**. The contract does the rest: the score is the sum of the points of the
criteria met, and the highest score is paid the prize. The model is never
shown the points, the prize or another entry, and the sponsor cannot enter,
mark or pick a winner.

- **Contract:** [`contracts/rubric.py`](contracts/rubric.py)
- **Tests:** `pip install pytest && pytest tests/ -q` - nothing else to install
- **Deployed:** see [It is live](#it-is-live-and-every-path-is-on-chain) below, and [`deployments/studionet.json`](deployments/studionet.json)
- **Every transaction and the wallet that sent it:** [EVIDENCE.md](EVIDENCE.md), read back from the chain
- **Run the demo yourself:** [DEPLOY.md](DEPLOY.md)
- **Verify a deployment:** `python scripts/verify_deployment.py 0x...` - compares the on-chain source with this file and lints it
- **Decisions:** [DECISIONS.md](DECISIONS.md)
- **License:** MIT

---

## It is live, and every path is on chain

<!-- measured:deployment:start -->
Deployed on studionet at [`0x180a2aF66032CE523E2bab92Fc5e1E0427D9Da0B`](https://explorer-studio.genlayer.com/address/0x180a2aF66032CE523E2bab92Fc5e1E0427D9Da0B) (deploy [`0x1edb206a...`](https://explorer-studio.genlayer.com/tx/0x1edb206a5b5a424c44a19870662a2466f8659169cada261bdabd52f771025482)). Every value below was read back from the chain by `scripts/demo.py` and written to [`deployments/studionet.json`](deployments/studionet.json); none of it is typed by hand.

| Prize | Amount | Status | Winning entry | Paid to |
|---|---|---|---|---|
| 0: Explain GenLayer to a newcomer in one paragraph | 0.5 GEN | awarded | entry 0 | `0x0FaaE5e6de55Ca5fF589F541b5fF01f9675a9CEd` |

The rubric, frozen at open, and how many judged entries met each criterion:

| # | Criterion | Points | Met |
|---|---|---|---|
| 0 | States that several validators must agree on a result before it is accepted | 40 | 2 |
| 1 | Says that a result can be appealed to a larger group of validators | 30 | 1 |
| 2 | Gives one concrete example of a question the network could decide | 30 | 2 |

Every entry, and the marks the validators agreed on (one per criterion, in order):

| Entry | Text | Marks | Score | Reason the leader gave (not consensus) |
|---|---|---|---|---|
| 0 | GenLayer lets a group of independent validators answer questions that need ju... | **111** | 100 | All three criteria clearly addressed in the entry. |
| 1 | GenLayer is a network where several validators each work out the answer to a ... | **101** | 70 | Meets agreement and example criteria but omits appeal. |
| 2 | GenLayer is the future of everything. It is faster, smarter and better than a... | **000** | 0 | It does not explain validator agreement, appeals, or any concrete example of a question GenLayer could decide. |
| 3 | On GenLayer many validators answer a judgment question, like whether a transl... | **unjudged** | 0 | - |

The winner's balance, read from the chain before the award and after it landed: 0 GEN to 0.5 GEN, a gain of **0.5 GEN**. Held by the contract afterwards: 0 wei.

Every transaction, in order, refusals included, with the wallet that sent it:

| Step | From | Outcome | Transaction |
|---|---|---|---|
| prize 0 opened: 0.5 GEN, three criteria | sponsor | ok | [`0xae757dfc...`](https://explorer-studio.genlayer.com/tx/0xae757dfc46d11edd9947b837bd3fcfe7f2a2dc3cbd9356ca69cf81f639d36e0e) |
| the sponsor enters its own prize | sponsor | refused: the sponsor cannot enter its own prize | [`0x4483394a...`](https://explorer-studio.genlayer.com/tx/0x4483394a29ea436d6a52572ef6c59f1c73220ceb329e4f7aae70ecfd709ca271) |
| entry 0: Ann | ann | ok | [`0x3a513fb1...`](https://explorer-studio.genlayer.com/tx/0x3a513fb16e860884367426d28481faf16f299f82f300c969abe5b9ae8b49982c) |
| entry 1: Ben, leaves out appeals | ben | ok | [`0x178933a0...`](https://explorer-studio.genlayer.com/tx/0x178933a079a5d05a48ef2cc1842b1bd0f5aeeee3867c6a33430458ebf319351c) |
| entry 2: Cal, hype | cal | ok | [`0x0300c94d...`](https://explorer-studio.genlayer.com/tx/0x0300c94d3d7f3775a33f23ca1c8a7a607da6515bf533854bed902ef11504a4ad) |
| entry 3: Dev | dev | ok | [`0xc04daa47...`](https://explorer-studio.genlayer.com/tx/0xc04daa47102494beda8cc734848ea1ead89958822ae126bbc7aaed14a86d0237) |
| Ann enters a second time | ann | refused: an entrant enters once per prize | [`0x7ff48e85...`](https://explorer-studio.genlayer.com/tx/0x7ff48e856c93b3732b02e747e0c805dbc3a7826ee7b87d52a7975fc3e5c0c225) |
| a judging before entries close | ann | refused: judging opens when entries close at 2026-10-12T06:48:42Z | [`0xda2e7007...`](https://explorer-studio.genlayer.com/tx/0xda2e7007f407db543ade66e8383f61afd9c8ae0e22de90bca49180b6a8744c01) |
| an entry after entries closed | stranger | refused: entries closed at 2026-10-12T06:48:42Z | [`0x1b2da61d...`](https://explorer-studio.genlayer.com/tx/0x1b2da61da086024903bcde814c04b981d89ec136cb5885f3921fc3f1726f4f1f) |
| a stranger asks for a judging | stranger | refused: only the sponsor or an entrant on this prize may ask for a judging | [`0x5dcfe38d...`](https://explorer-studio.genlayer.com/tx/0x5dcfe38d92a16dee539bbf16ccb3abe47c456b2e0820f6ca2a0419e3f1dee537) |
| entry 1 judged: both orders | sponsor | ok | [`0x5ec297c4...`](https://explorer-studio.genlayer.com/tx/0x5ec297c49c6933fa7542c5098748a83033fdcf1daadcd1ab8c50d08bd47e7b9c) |
| entry 0 judged: both orders | ann | ok | [`0xf0b8f7fe...`](https://explorer-studio.genlayer.com/tx/0xf0b8f7fef6352f3f6ae9da98a5588bda4e093e78c880227f62e8962bd41d248a) |
| entry 2 judged: both orders | cal | ok | [`0x80ab936d...`](https://explorer-studio.genlayer.com/tx/0x80ab936d281c35b71c01df92acd869a8b9943b86bf4d163511795e00ef6b1e8b) |
| an award while entry 3 waits | stranger | refused: entry 3 is waiting to be judged until 2026-10-12T07:13:42Z | [`0x9e87e5db...`](https://explorer-studio.genlayer.com/tx/0x9e87e5db5093650628a8ed4198285d9cda5a02c70306efb7c5059457e51fa423) |
| entry 3 judged after judging closed | dev | refused: judging closed at 2026-10-12T07:13:42Z; an entry nobody judged scores nothing at the award | [`0xd45a6e69...`](https://explorer-studio.genlayer.com/tx/0xd45a6e692a178e29750a67b8932d915f5056fa28de73c8b6604d706dd042e912) |
| prize 0 awarded | stranger | ok | [`0x9757501d...`](https://explorer-studio.genlayer.com/tx/0x9757501ddecd8ef097817faa94e012e364f069fd1d4690e0a746d2742808c4da) |

`tests/test_runbook.py::TestTheRecord` replays these marks through this repository's contract and fails unless it scores and awards exactly what the deployed one did.
<!-- measured:deployment:end -->

## The problem

Every competition publishes criteria, and every losing entrant suspects the
judges did not apply them. Whoever judges also picks the winner, so a
favourite's entry "showed real originality" and a rival's "missed the brief",
and nobody outside the room can tell which happened.

Asking a model "which entry is best?" does not fix it. It hands the model the
whole judgment in one opaque choice and gets back the entry it liked. Rubric
splits it: the criteria and their points are frozen before the first entry;
the model answers only *does this entry do what this criterion asks*, one
entry at a time, one bit per criterion, without the points; and the score and
the winner are counted, not judged.

## How consensus is used

### Before any model: could any answer change the outcome?

The contract refuses for free, before a single prompt, a judging asked for by
anyone but the sponsor or an entrant, before entries have closed, after
judging has closed, or of an entry already judged.

### The judging

Otherwise the block sees the prize, the brief, the criteria and one entry, and
answers with one character per criterion:

```
<criteria>
[0] States that several validators must agree on a result before it is accepted
[1] Says that a result can be appealed to a larger group of validators
[2] Gives one concrete example of a question the network could decide
</criteria>

<entry>
GenLayer is a network where several validators each work out the answer ...
</entry>

Number of criteria: 3. Answer with exactly 3 characters, each 0 or 1 ...

answer: {"marks": "101", "because": "..."}
```

1 only if the entry clearly does what the criterion asks; 0 if it does not,
only partly does, or the model cannot tell. The model is told it is not shown
any points or any other entry, and is not.

### Both orders

The leader asks **twice**, with the criteria in the frozen order and then
reversed and renumbered, and reads the second answer back into the frozen
order. A criterion is met only if both passes say met. A mark that depends on
where the criterion sat in the list is not clear enough to score, and a model
that marks by position meets nothing it is unsure of. The uncertainty goes
into the **value** (not met), never into the comparison.

### The validator, in two layers

1. **Structural, and free.** The marks are exactly one 0 or 1 per criterion.
   Anything else is refused before the validator spends a single prompt.
2. **Exact agreement.** The validator asks both orders itself and compares the
   folded marks character for character.

An unusable answer is retried once inside the block and then raised as
`[LLM_ERROR]`, which a validator never agrees with, so a broken model can never
score an entry. There is no equivalence principle and no tolerance anywhere.

## What the contract decides, not the model

| At the award | Outcome |
|---|---|
| judged entries | score = the points of the criteria marked met |
| the highest score above zero | **awarded**: the prize is paid to its entrant; on a tie, the earliest entry |
| an entry nobody judged before judging closed | **unjudged**: scores nothing, however good |
| nothing scores above zero, or nobody entered | **returned**: the prize goes back to the sponsor |

## The state machine and its clocks

```
open       entries until entries_close; judging from entries_close until judge_close
awarded    the prize was paid to the winner
returned   nothing scored; the prize went back to the sponsor
```

| Clock | What happens after it |
|---|---|
| `entries_close` = open + entry window | no more entries; judging opens |
| `judge_close` = entries close + judging window | `judge()` refuses for free, before any model; an unjudged entry scores nothing, so a late judging can never change a winner |
| the award | anyone, once every entry is judged or once judging has closed, whichever is first |

## Who may write

| Method | Caller | Why |
|---|---|---|
| `open(title, brief, criteria, points, entry_window, judge_window)` payable | anyone, paying the prize in | the caller becomes the sponsor |
| `enter(id, text)` | anyone but the sponsor, once per prize, until entries close | the entrant is recorded, and is the one paid |
| `judge(id, entry)` | the sponsor or any entrant on this prize, once per entry | a judging spends inference on every validator, so only parties to the prize may ask; an entrant may ask about a rival |
| `award(id)` | anyone, deliberately | it reads no model and only counts the stored scores; a sponsor who has vanished cannot strand the prize |

`tests/test_e2e.py::TestStorageShape::test_every_gated_write_checks_the_sender`
fails if `enter()` or `judge()` stops checking the sender, and
`test_the_sponsor_has_no_say_over_the_winner_in_code` fails if the award ever
reads the sponsor for anything but returning a prize nobody won.

## The API

| View | Returns |
|---|---|
| `count()` | number of prizes |
| `status(id)` | `open`, `awarded` or `returned`: one word for another contract |
| `prize(id)` | sponsor, amount, status, the clocks, how many entries and judgings, the winning entry and the winner |
| `rubric_of(id)` | the criteria in the frozen order, their points, and how many judged entries met each |
| `entries_of(id)` | every entry: entrant, text, marks, score, who asked for the judging, and the leader's reason |
| `held_total()` | wei owed to open prizes |

## Running the tests

```bash
pip install pytest
pytest tests/ -q
```

<!-- measured:tests:start -->
Measured: **141 passed**, 1 skipped. The skipped tests are the opt-in StudioNet integration tests, which run with `GENLAYER_STUDIO=1`.
<!-- measured:tests:end -->

The suite runs on [`tests/glsim.py`](tests/glsim.py), a small GenVM stand-in
that executes the real contract file, gives the leader and the validator their
own mock answers, can make a leader lie, rolls back storage on a refusal,
records every transfer, and refuses what GenVM refuses.

- [`tests/test_logic.py`](tests/test_logic.py) - the pure rules: the rubric's shape, the points, the marks, the fold of both orders, the agreement, the score, `winner()`, the fence and the prompt, and that `lib/rubric_consensus.py` is the contract's own code
- [`tests/test_e2e.py`](tests/test_e2e.py) - the contract executed: the paid open, entering and its limits, the free refusals (zero prompts), the points the model never sees, the criteria in both orders, order-dependence, a leader that inflates or deflates the marks, `[LLM_ERROR]` never agreed with, every clock on its last second, the award, its ties and its money, and static checks over the parsed source
- [`tests/test_runbook.py`](tests/test_runbook.py) - the demo replayed offline before a transaction is spent, and the live record replayed through this code
- [`tests/test_integration.py`](tests/test_integration.py) - opt in, `GENLAYER_STUDIO=1`: senders, real value, a TreeMap on a real address, and the free refusals on a real runtime

### The tests have teeth

[`scripts/mutate.py`](scripts/mutate.py) removes every defence one at a time
and names the test that caught each mutant. It refuses to run on a red
baseline and exits non-zero if anything escapes.

<!-- measured:mutations:start -->
Measured: **75 mutations, 75 caught, 0 escaped.**

| Mutation | Caught by |
|---|---|
| marks of the wrong length are accepted | `test_marks_are_one_0_or_1_per_criterion_and_nothing_else` |
| marks in words are accepted | `test_an_unusable_answer_is_an_error_and_never_a_score` |
| commas between marks are not tolerated | `test_marks_are_one_0_or_1_per_criterion_and_nothing_else` |
| the second pass is asked in the forward order | `test_the_criteria_are_asked_in_both_orders` |
| the reversed marks are not read back | `test_a_criterion_met_in_only_one_order_is_not_met` |
| a criterion met in one order only is met | `test_a_criterion_met_in_only_one_order_is_not_met` |
| only the forward order counts | `test_a_criterion_met_in_only_one_order_is_not_met` |
| marks of different lengths are folded | `test_the_fold_meets_a_criterion_only_if_both_orders_meet_it` |
| an unusable answer is not retried | `test_an_unusable_answer_is_an_error_and_never_a_score` |
| an unusable answer is read as nothing met | `test_an_unusable_answer_is_an_error_and_never_a_score` |
| an answer that is not an object crashes the block | `test_an_unusable_answer_is_an_error_and_never_a_score` |
| the validator agrees with an error | `test_an_unusable_answer_is_an_error_and_never_a_score` |
| the validator skips the structural check | `test_marks_that_are_not_one_per_criterion_are_refused_for_free` |
| the validator agrees with anything sound | `test_nodes_that_mark_differently_do_not_agree` |
| the validator agrees when its own model fails | `test_a_validator_whose_model_fails_does_not_agree` |
| agreement ignores soundness | `test_agreement_is_exact_symmetric_and_over_sound_marks` |
| the agreed marks are not checked again | `test_the_agreed_marks_are_checked_again_before_they_score` |
| the score counts every criterion | `test_the_score_is_the_points_of_the_criteria_met` |
| the score counts the unmet criteria | `test_the_score_is_the_points_of_the_criteria_met` |
| a criterion's tally is not kept | `test_the_score_is_the_points_of_the_criteria_met` |
| the judged count is not kept | `test_the_score_is_the_points_of_the_criteria_met` |
| who asked is not recorded | `test_the_sponsor_or_any_entrant_may_ask_even_about_a_rival` |
| a leader's reason is stored as sent | `test_the_reason_is_not_compared_and_is_stored_sanitised` |
| a leader's reason is stored uncapped | `test_the_reason_is_not_compared_and_is_stored_sanitised` |
| anyone may ask for a judging | `test_only_the_sponsor_or_an_entrant_may_ask` |
| only the sponsor may ask for a judging | `test_the_sponsor_or_any_entrant_may_ask_even_about_a_rival` |
| an entry is judged twice | `test_an_entry_is_judged_once` |
| judging opens before entries close | `test_judging_waits_for_entries_to_close` |
| judging never closes | `test_a_judging_on_the_last_second_lands_and_one_after_is_refused_for_free` |
| judging closes a second early | `test_a_judging_on_the_last_second_lands_and_one_after_is_refused_for_free` |
| an entry of another prize is judged | `test_an_entry_of_another_prize_is_refused` |
| a decided prize is judged | `test_a_decided_prize_takes_nothing_more` |
| the sponsor may enter | `test_the_sponsor_cannot_enter` |
| an entrant enters twice | `test_an_entrant_enters_once` |
| entries never close | `test_entries_close_on_the_clock` |
| entries close a second early | `test_entries_close_on_the_clock` |
| entries are unlimited | `test_a_prize_takes_at_most_twelve_entries` |
| an entry of any length is accepted | `test_the_entry_length_bounds` |
| an entrant is not remembered | `test_an_entrant_enters_once` |
| entries are not linked | `test_a_judging_on_the_last_second_lands_and_one_after_is_refused_for_free` |
| the award waits for nobody | `test_a_better_entry_nobody_judged_cannot_win` |
| an unjudged entry can win | `test_the_award_passes_which_entries_were_judged` |
| an unjudged entry is not marked | `test_a_better_entry_nobody_judged_cannot_win` |
| the award comes while entries are open | `test_nothing_is_awarded_while_entries_are_open` |
| a prize is awarded twice | `test_a_decided_prize_takes_nothing_more` |
| a tie goes to the latest entry | `test_a_tie_goes_to_the_earliest_entry` |
| a zero score can win | `test_nothing_scores_and_the_prize_goes_back_to_the_sponsor` |
| the lowest score wins | `test_the_highest_score_wins_the_prize` |
| the winner is off by one | `test_the_highest_score_wins_the_prize` |
| the prize goes to the sponsor anyway | `test_the_highest_score_wins_the_prize` |
| a prize nobody won is kept | `test_nothing_scores_and_the_prize_goes_back_to_the_sponsor` |
| the prize may be free | `test_a_prize_must_be_paid_in` |
| the held counter is not raised | `test_a_prize_opens_with_its_rubric_and_clocks_frozen_and_the_prize_held` |
| a payout beyond what is held is sent | `test_a_payout_beyond_what_is_held_is_refused` |
| the held counter is not lowered | `test_the_highest_score_wins_the_prize` |
| the rubric refusal is ignored | `test_a_malformed_rubric_is_refused` |
| more than six criteria are accepted | `test_a_malformed_rubric_is_refused` |
| a criterion of any length is accepted | `test_a_malformed_rubric_is_refused` |
| two criteria with the same wording are accepted | `test_a_malformed_rubric_is_refused` |
| points that do not match the criteria are accepted | `test_a_malformed_rubric_is_refused` |
| points of any size are accepted | `test_a_malformed_rubric_is_refused` |
| a missing criterion is dropped and the rest renumbered | `test_a_malformed_rubric_is_refused` |
| the windows are unbounded | `test_both_windows_are_bounded` |
| the judging window is unbounded | `test_both_windows_are_bounded` |
| judging closes with the entries | `test_a_prize_opens_with_its_rubric_and_clocks_frozen_and_the_prize_held` |
| the title is unbounded | `test_the_other_bounds` |
| the brief is unbounded | `test_the_other_bounds` |
| the fence is removed | `test_caller_text_is_stored_verbatim_and_fenced_only_at_the_prompt` |
| the fence leaves square brackets | `test_caller_text_is_stored_verbatim_and_fenced_only_at_the_prompt` |
| the entry reaches the prompt unfenced | `test_caller_text_is_stored_verbatim_and_fenced_only_at_the_prompt` |
| the criteria reach the prompt unfenced | `test_caller_text_is_stored_verbatim_and_fenced_only_at_the_prompt` |
| the title reaches the prompt unfenced | `test_every_value_interpolated_into_the_prompt_is_fenced_or_ours` |
| the prompt no longer says partly is not met | `test_the_prompt_states_the_count_and_never_points` |
| the prompt no longer states the count | `test_the_prompt_states_the_count_and_never_points` |
| control characters are stored | `test_clean_text_collapses_whitespace_and_control_characters` |
<!-- measured:mutations:end -->

## Design rules applied

- **Settle what can be settled before the model:** a judging that could change nothing is refused for free.
- **The coarsest answer that still carries the judgment:** one bit per criterion, per entry.
- **No single call reveals what only the contract should see:** no points or money ever enter the prompt, and no entry is compared with another by a model.
- **Uncertainty in the value, never in the comparison:** a mark that depends on the order is not met.
- **Every judgment has a clock:** nothing is judged after `judge_close`, and an unjudged entry cannot win.
- **Tagging untrusted text is not a fence:** `fence()` at the prompt boundary, criteria numbered by the contract.
- **The deployment is the submission:** `scripts/verify_deployment.py` reads the deployed source back and lints it.

## Further reading in this repository

- [DECISIONS.md](DECISIONS.md) - why each rule is the way it is
- [DEPLOY.md](DEPLOY.md) - the demo, step by step
- [SUBMISSION.md](SUBMISSION.md) - what to check before submitting
- [`lib/rubric_consensus.py`](lib/rubric_consensus.py) - the marking and award rules, generated from the contract

## Related work

- [Tender](https://github.com/meitipro/tender) - a procurement round awarded to the cheapest bid that meets frozen requirements
- [Warranty](https://github.com/meitipro/warranty) - a warranty with its payouts paid in before the sale closes
- [Tally](https://github.com/meitipro/tally) - an invoice paid line by line, only for what the order ordered
