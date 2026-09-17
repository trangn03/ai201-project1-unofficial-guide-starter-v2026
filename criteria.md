# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that
contains the answer.

**Why this target:**

<!-- e.g. "One of my questions is about a topic only two documents mention, so
     I expect that one to be hard." -->

Two of my questions read facts out of multi-paragraph documents and already
retrieve worst (0.411 for the shuttle, 0.306 for the library, against 0.20–0.23
for the three single-paragraph ones), so those are the ones a chunking change
can break and I am allowing one failure for them. Three of five would still
pass with both multi-fact documents broken, which is the exact failure this
criterion exists to catch.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**

<!-- Why all five and not four? What about your setup makes that achievable —
     or what would have to go wrong for it not to be? -->

Naming a source is a property of the prompt, not of the question: every answer
goes through `generate.build_prompt`, which labels each chunk`[from <filename>]` and asks for the file by name, so no question takes a path that skips it. Four of five would mean accepting that the model ignores a
standing instruction once per five questions, which I would rather see as a
failure than build into the target.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**

<!-- What did your distances look like when you set the cutoff in Milestone 4?
     Was there a clean gap, or did the two groups overlap? -->

The two groups don't overlap: in-scope came back at 0.202–0.411 and the five
`OUT_OF_SCOPE` questions at 0.825–0.934, a 0.41-wide empty band with the 0.6
cutoff near its middle, so I kept 0.6 because I measured it rather than assumed
it. With a gap that clean I expect 5 of 5 and claim 4 because these five
questions are trivially far away — the real risk is a question that sounds like
my corpus but isn't in it, and the spare failure is for that.

---

## 4. Chunks keep their title line and stay whole

In a sample of five chunks from `python app.py chunks -n 5`, all five begin
with their source document's title line, and none begins or ends mid-sentence.
No chunk is shorter than 150 characters.

<!-- YOU WRITE THIS ONE.

     How would you know if your chunks were the right size? Name something
     countable or observable.

     Examples of the right shape — don't copy these, they should come from
     what you actually saw in Milestone 3:
       - "At least 4 of 5 sampled chunks read as a complete thought, with no
          sentence cut in half at either end."
       - "No chunk is shorter than 200 characters, since anything below that
          in my corpus turned out to be a heading with no content under it." -->

**Why this target:**

The title line is the only topic label a chunk gets here — body sentences drop
the subject, so `course_cs_210.txt`'s advice line never says "CS 210" — which
makes a titleless chunk effectively unretrievable rather than merely worse, and
that is why I require all five and not four. I put the floor at 150 characters
rather than 200 because the shortest chunk today is already 178 (mean 317), so
a 200 floor would flag documents that are simply short instead of chunks that
are actually broken.

---

## 5. The source named is the one that actually holds the answer

For all 5 of my test questions, the source document the answer names is the
document that actually contains the answer — not merely some document that was retrieved. And for a question about one building's laundry prices, the price
given matches that building.

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. It could be about
     speed, about refusals, about a particular kind of question your corpus
     handles badly, about source attribution being correct rather than merely
     present — anything, as long as it names a number or an observable
     outcome. -->

**Why this target:**

Criterion 2 is too easy to satisfy wrongly in this corpus: asking for Morrow
House laundry prices put the right document first at 0.103 but also pulled four
near-identical laundry posts under the gate at 0.36–0.41, so the model sees
three different wash prices at once and criterion 2 would score a confidently
wrong one as a pass. I require 5 of 5 rather than 4 because a wrong source is
worse than a refusal — it is the one failure a reader of the guide cannot
detect for themselves.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
