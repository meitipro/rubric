"""The demo's data, in one place.

scripts/demo.py sends exactly these values to StudioNet, and
tests/test_runbook.py replays them offline, so the demo on the explorer and the
demo the tests check cannot drift apart.

One prize of 0.5 GEN for the best one-paragraph explanation of GenLayer for a
newcomer, with a three-criterion rubric, and four entrants. Each entry changes
one thing, so each rule of the contract shows once, on chain:

  ANN    meets all three criteria: 100 points, and the prize
  BEN    meets two, leaves out appeals: 70 points
  CAL    hype with no explanation at all: 0 points
  DEV    meets all three too, but nobody asks for it to be judged before
         judging closes: unjudged, no score

The prize goes to Ann: Dev's entry may have been as good, but an entry nobody
judged in time scores nothing.
"""

GEN = 10 ** 18

TITLE = "Explain GenLayer to a newcomer in one paragraph"
BRIEF = ("One paragraph for someone who has never used a blockchain, explaining how GenLayer decides "
         "questions that need judgment.")
RUBRIC = [
    # (criterion, points)
    ("States that several validators must agree on a result before it is accepted", 40),
    ("Says that a result can be appealed to a larger group of validators", 30),
    ("Gives one concrete example of a question the network could decide", 30),
]
PRIZE = 50 * GEN // 100
ENTRY_WINDOW = 600
JUDGE_WINDOW = 1500

ANN = ("GenLayer lets a group of independent validators answer questions that need judgment, such as whether "
       "a freelancer's delivered logo matches the brief. Each validator runs the question itself, and the "
       "answer is only accepted when they agree. If someone thinks the answer is wrong, they can appeal, and "
       "a larger group of validators looks at it again.")
BEN = ("GenLayer is a network where several validators each work out the answer to a question that needs "
       "judgment, for example whether an insurance claim describes a covered event, and the result is "
       "only accepted once they agree with each other.")
CAL = ("GenLayer is the future of everything. It is faster, smarter and better than any other chain, and "
       "everyone who gets in early will be glad they did. Do not miss out on this revolution.")
DEV = ("On GenLayer many validators answer a judgment question, like whether a translation is faithful to "
       "its source, and their answer stands only when they agree. A disputed answer can be appealed to a "
       "bigger panel of validators.")
LATE = ("GenLayer validators must agree on an answer, which can be appealed to more validators, for example "
        "about whether a delivery was late.")


def joined(rubric):
    """(criteria, points) as the two pipe joined strings open() takes."""
    return "|".join(c for c, _ in rubric), "|".join(str(p) for _, p in rubric)


# The demo, step by step, exactly as scripts/demo.py sends it and
# tests/test_runbook.py replays it: (who, method, arguments, expected, label).
# A step marked "after_entries" waits until entries have closed;
# "after_judging" until judging has closed. Entries are numbered as the
# contract numbers them: 0 Ann, 1 Ben, 2 Cal, 3 Dev.
STEPS = [
    ("sponsor", "open", (TITLE, BRIEF, RUBRIC, ENTRY_WINDOW, JUDGE_WINDOW), "ok", "prize 0 opened: 0.5 GEN, three criteria"),
    ("sponsor", "enter", (0, ANN), "refused", "the sponsor enters its own prize"),
    ("ann", "enter", (0, ANN), "ok", "entry 0: Ann"),
    ("ben", "enter", (0, BEN), "ok", "entry 1: Ben, leaves out appeals"),
    ("cal", "enter", (0, CAL), "ok", "entry 2: Cal, hype"),
    ("dev", "enter", (0, DEV), "ok", "entry 3: Dev"),
    ("ann", "enter", (0, BEN), "refused", "Ann enters a second time"),
    ("ann", "judge", (0, 0), "refused", "a judging before entries close"),
    ("stranger", "enter", (0, LATE), "refused", "an entry after entries closed", "after_entries"),
    ("stranger", "judge", (0, 1), "refused", "a stranger asks for a judging"),
    ("sponsor", "judge", (0, 1), "ok", "entry 1 judged: both orders"),
    ("ann", "judge", (0, 0), "ok", "entry 0 judged: both orders"),
    ("cal", "judge", (0, 2), "ok", "entry 2 judged: both orders"),
    ("stranger", "award", (0,), "refused", "an award while entry 3 waits"),
    ("dev", "judge", (0, 3), "refused", "entry 3 judged after judging closed", "after_judging"),
    ("stranger", "award", (0,), "ok", "prize 0 awarded", "after_judging"),
]

# What each ok judging is expected to come back with, in order.
EXPECTED_MARKS = ["101", "111", "000"]
