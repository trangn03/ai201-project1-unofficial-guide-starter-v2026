# The Unofficial Guide

<!-- Replace this line with your name and which corpus you picked. -->

> **This file is your submission.** Fill it in as you go, most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders, you can leave them
> or remove them.

---

# Unit 1

## What This Does

<!-- Three or four sentences. Which corpus you picked, and the kinds of
     questions your system answers. Write it for someone who has never seen
     this repo.

     Milestone 5. -->

I built this over `campus_life`: about 88 short, first-person posts on student life at one college, covering course workloads and exam formats, deadlines for pass/fail and add/drop, dining hall wait times, dorm laundry costs, parking and the housing lottery. It answers specific factual questions ("how often
does the shuttle run on weekends," "how late can I declare pass/fail") by retrieving the post that actually contains the answer and asking a model to answer from that post alone, rather than from anything it already knows. The
corpus reads like a pile of short reviews rather than a handbook: most posts are one to three paragraphs, and the answer to a well-formed question is usually one sentence, so a good answer here is short and cites one file, not
several.

## Chunking Strategy

**Chunk size:** 350 characters, used as a ceiling, not a fixed window
**Overlap:** 0

<!-- What about YOUR documents made you pick these numbers? Short posts and
     long sectioned guides don't want the same chunking, and "800 seemed
     reasonable" earns nothing. Point at something you noticed when you read
     the documents in Milestone 1.

     If you changed your mind partway through, say so and say why. That's worth
     more than pretending you got it right first time.

     Milestone 3. -->

My documents are short posts (178–549 characters), not long guides, so a fixed
sliding window was the wrong shape from the start. My chunker instead packs whole paragraphs up to 350 characters and never cuts one, and re-adds the document's title to every chunk, since body text here often drops the subject
("the basement," not "the library basement").

I picked 350 by testing a few ceilings against my real paragraph lengths. Below 300, some chunks came out shorter than 150 characters, too small to be useful. Above 450, almost nothing split at all, which is just the starter's old behavior with a new number. 350 splits only the 11 documents that actually needed it.

Overlap is 0 because there's nothing to repair: splits happen between paragraphs, not through the middle of one, and every chunk keeps its title.

One thing I changed after testing: `TOP_K`, not the chunk size. The default of 5 buried the right chunk under near-duplicate posts (same laundry room, same dorm noise complaint), so I lowered it to 3.

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it, the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** (source: `admin_add_drop_deadline.txt#0`, produced by: `chunker.py::split_documents`)

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window, through the end of week six, but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** (source: `course_biol_160_exams.txt#0`, produced by: `chunker.py::split_documents`)

```
BIOL 160 Cell Biology, assessment

Four unit tests and a cumulative final. Not curved.

The unit tests come fast, roughly every three weeks; falling behind once is very hard to recover from.
```

**Chunk 3** (source: `course_math_220.txt#0`, produced by: `chunker.py::split_documents`)

```
MATH 220 Linear Algebra

I lived here my sophomore year. Format is chalk-and-talk lecture, weekly problem sets marked for correctness. Assessment: two midterms and a cumulative final. Curved to a b- median.

Expect 6 to 8 hours a week, almost all of it on problem sets.

The one piece of advice: the problem sets are the course; the lectures make sense afterwards rather than during.
```

**Chunk 4** (source: `dining_the_ridgeway_cafe.txt#0`, produced by: `chunker.py::split_documents`)

```
The Ridgeway Café

Second-year here. Wait times: 10 to 15 minutes at 12:30, none after 2:00. The thing worth going for is the only place on campus with real espresso. The thing to know is that seating is tight; about 40 seats for a building of 900.

Hours are 7:00am to 4:00pm weekdays only. Costs declining balance only, no meal swipes.
```

**Chunk 5** (source: `housing_innisfree_hall_laundry.txt#0`, produced by: `chunker.py::split_documents`)

```
Laundry in Innisfree Hall

Machines take $1.75 wash, $1.75 dry, app-based. There are eight washers and six dryers for the building, which is the wrong ratio and means the dryers back up on Sunday evenings.

Best time to do laundry here is Tuesday or Wednesday morning. Sunday after 6pm you will wait.
```

All five above are documents that stayed whole under the 350-character ceiling (88 of 88 documents fit one chunk under the starter's numbers; 77 still do under mine). For a document the chunker actually split, here are both chunks of `transit_shuttle.txt`, the title line is re-prepended to the second chunk
because its body never says the word "shuttle":

**Split example, chunk a** (source: `transit_shuttle.txt#0`, produced by: `chunker.py::split_documents`)

```
The campus shuttle

Runs a loop every 20 minutes from 7am to 11pm on weekdays and every 40 minutes on weekends. The published timetable is optimistic by about five minutes in the morning and accurate the rest of the day.
```

**Split example, chunk b** (source: `transit_shuttle.txt#1`, produced by: `chunker.py::split_documents`)

```
The campus shuttle

It's free with a student ID. The stop outside Fenwick Court is the one that gets skipped when the driver is behind, which is worth knowing if you live there.
```

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:** How often does the campus shuttle run on weekends?

**Answer:**

```
(best distance 0.180, cutoff 0.6)

Based on the documents provided, the campus shuttle runs every 40 minutes on weekends.

Source: `transit_shuttle.txt`

Sources retrieved: course_stat_150_workload.txt, dining_verrill_street_grill.txt, transit_shuttle.txt
```

**My relevance cutoff:**

`THRESHOLD = 0.6` in `config.py`.

I ran my five test questions and the five `OUT_OF_SCOPE` questions through `python app.py retrieve` and recorded the best (rank-1) distance for each.
The two groups didn't overlap:

- **In-scope** best distances: 0.180, 0.202, 0.214, 0.229, 0.306 (worst: 0.306)
- **Out-of-scope** best distances: 0.825, 0.849, 0.886, 0.891, 0.934 (best: 0.825)

That's a 0.52-wide empty band between 0.306 and 0.825, with no question from either group landing inside it. I put the cutoff at 0.6, not exactly centered, but with real margin on both sides (0.29 above my worst real question, 0.22
below my closest fake one), rather than tightening it toward the in-scope side. The five `OUT_OF_SCOPE` questions are all trivially far (everything in this corpus is campus-flavoured, so even Mongolia's capital lands on a history
course post at 0.825), so a tighter cutoff would pass the same test today without being better tested. The real risk 0.6 has to survive is a question that sounds like the corpus but isn't covered by it, and none of my ten questions test that case, so there's no evidence yet to justify moving off a cutoff that already has room on both sides.

| #  | Question                                                               | In corpus? | Best distance |
| -- | ---------------------------------------------------------------------- | ---------- | ------------- |
| 1  | How late can you declare a course pass/fail?                           | yes        | 0.202         |
| 2  | What happens to leftover dining dollars at the end of spring semester? | yes        | 0.229         |
| 3  | How is the housing lottery order decided for juniors and seniors?      | yes        | 0.214         |
| 4  | How often does the campus shuttle run on weekends?                     | yes        | 0.180         |
| 5  | Why is the library basement full by mid-morning?                       | yes        | 0.306         |
| 6  | What is the capital of Mongolia?                                       | no         | 0.825         |
| 7  | How do I change the oil in a diesel engine?                            | no         | 0.934         |
| 8  | Who won the 1994 World Cup?                                            | no         | 0.886         |
| 9  | What is the recommended dosage of ibuprofen for a headache?            | no         | 0.849         |
| 10 | How do I write a for loop in Rust?                                     | no         | 0.891         |

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1.** I asked Claude to decide the chunk size and overlap and write down why before touching the chunker, since I'd noticed my documents were short posts, not sectioned guides. Instead of picking a number, it measured the actual paragraph lengths in my corpus (median 112 characters, documents 178-549) andsimulated a title-prefixed, paragraph-packing strategy at several ceilings before proposing 350/0/150. I didn't just take those numbers; after the real `split_documents` was written, I had it re-run retrieval on my five questions and the smoke test before I'd accept the change, which is what caught that the shuttle question's distance actually improved (0.411 → 0.180) rather than assuming the simulation would carry over exactly.

**2.** I asked it to adjust `TOP_K`, warned that too few loses the right chunk and too many buries it in loosely related material. It didn't just guess a number either; it swept k from 3 to 10 against all five test questions and a laundry-price question I'd flagged earlier as a hazard case, and showed me that the right chunk was always rank 1 no matter the k, while the *noise* grew: at k=5 a library question pulled in four dorm-noise posts that all share
one recycled sentence about the library, and the laundry question pulled in three other buildings' prices. I used that evidence to lower `TOP_K` from the starter's 5 to 3 rather than leaving it at the default, and kept one spare slot above rank 1 instead of cutting to 2, since none of my questions actually needed the extra headroom but I didn't want zero margin either.

**3.** For unit 2's improvement, I asked Claude to propose a second chunking
strategy targeting the risk from my diagnosis (multi-paragraph documents
untested for criterion 1); it suggested splitting each paragraph into its own chunk. After I ran the before/after comparison, I asked it to find a pattern across the two run logs rather than explain them question by question. It caught that both variants scored 5/5 on criterion 1 despite the library question's distance getting worse (0.306 → 0.374), meaning the criterion couldn't actually tell the regression from a non-event, something I'd missed reading the tables myself. Separately, checking every chunk the new function produced (not just the 5-chunk sample) turned up 8 chunks under my 150-character floor, traced to the floor-merge step only checking backward, not forward. I verified that finding myself by rerunning the same check against `split_documents`,
which came back clean, before accepting it as a real difference between the two strategies.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1, the point is that someone can see what you said before you knew
     how it went. -->

## Run Log: Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion                                                 | Target                  | Run 1 | Run 2 | Run 3 | Verdict |
| --------------------------------------------------------- | ----------------------- | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer                    | 4 of 5                  | 5/5   | 5/5   | 5/5   | MET     |
| 2. Every answer names a source                            | 5 of 5                  | 5/5   | 5/5   | 5/5   | MET     |
| 3. Gate stops out-of-corpus questions                     | 4 of 5                  | 5/5   | 5/5   | 5/5   | MET     |
| 4. Chunks keep title line and stay whole                  | 5 of 5, none <150 chars | 5/5   | 5/5   | 5/5   | MET     |
| 5. Named source is the one that actually holds the answer | 5 of 5                  | 5/5   | 5/5   | 5/5   | MET     |

Source: `results/run_2026-09-21_0759_before.md`, produced by `run_eval.py::main`.

Criterion 1: for each question, the run log's "Sources retrieved" line includes the document that actually answers the question, and the generated text states that document's fact correctly, so all 5 count as containing the answer in every run (retrieval is deterministic; only phrasing changes between runs):

| Question           | Answering doc retrieved?          |
| ------------------ | --------------------------------- |
| Pass/fail deadline | admin_pass_fail_option.txt: yes |
| Dining dollars     | admin_dining_dollars.txt: yes   |
| Housing lottery    | admin_housing_lottery.txt: yes  |
| Shuttle frequency  | transit_shuttle.txt: yes        |
| Library basement   | study_library_hours.txt: yes    |

Criterion 2: every one of the 15 generated answers (5 questions × 3 runs) names a source, in one of three phrasings (`Source: file.txt`, `(file.txt)`, `(source: file.txt)`), so it's 5/5 in every run.

Criterion 3: from the out-of-scope table in the same run log: 5 of 5 refused (distances 0.825–0.934, all above the 0.6 cutoff), measured once since the gate is a deterministic comparison, not a model call.

Criterion 4: from `python app.py chunks -n 5` (chunks produced by `chunker.py::split_documents`): all 5 sampled chunks begin with their source document's title line, none ends or begins mid-sentence, and the shortest is well above the 150-character floor. Deterministic like
criterion 3, so one measurement covers all three run columns. (Full set of 5 already pasted in the Sample Chunks section above, same output, chunking doesn't vary between runs.)

Criterion 5: for each of the 5 test questions, the source named in the answer is the document that actually contains the fact (verified against each source file directly), 5/5 in every run, see the table under criterion 1 for per-question detail.

I additionally tested the laundry hazard case named in criteria.md:
"How much does laundry cost in Morrow House?"

```
(best distance 0.112, cutoff 0.6)

Laundry in Morrow House costs $1.50 to wash and $1.25 to dry (using either coin or card).

Sources: `housing_morrow_house_laundry.txt` and `housing_morrow_house.txt`

Sources retrieved: housing_morrow_house.txt, housing_morrow_house_laundry.txt
```

The answer named `housing_morrow_house_laundry.txt` and gave $1.50 wash / $1.25 dry, matching that file exactly, with no other building's laundry document among the top-3 retrieved (`app.py ask --show-prompt`, run manually, not part of the automated 5).

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit, not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion                                              | Verdict | How I decided                                                                                                                                                                 |
| - | ------------------------------------------------------ | ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1 | Retrieved chunks contain the answer                    | MET     | Target was 4 of 5; came out 5/5 in all three runs, not just once, the two multi-paragraph documents I flagged as the risk (shuttle, library) retrieved correctly every run. |
| 2 | Every answer names a source                            | MET     | Target was 5 of 5; came out 5/5 in all three runs.                                                                                                                            |
| 3 | Gate stops out-of-corpus questions                     | MET     | Target was 4 of 5; came out 5/5, measured once since the gate is a deterministic comparison, not something that can vary between runs.                                        |
| 4 | Chunks keep title line and stay whole                  | MET     | Target was 5 of 5, none under 150 chars; came out 5/5, deterministic like criterion 3, chunking doesn't change between runs of the same corpus.                             |
| 5 | Named source is the one that actually holds the answer | MET     | Target was 5 of 5; came out 5/5 in all three runs, plus the Morrow House laundry hazard case I tested separately also named the correct document and price.                   |

## Diagnoses

I missed nothing, all five criteria came out MET, so there's no stage or mechanism to diagnose here.

Two of my targets have no slack: criteria 2 and 5 were both set at 5 of 5 and came out 5 of 5, so a single wrong source or a single answer that dropped the source line would have missed. Those are already as tight as a target can be.

The other three (criteria 1, 3, and 4) were all set at 4 of 5 and came out 5 of 5 with real margin behind the number, not a close 5/5:

- Criterion 1: my two riskiest questions (the ones reading facts out of multi-paragraph documents, shuttle at 0.180 and library at 0.306) still retrieved the right chunk despite being my worst distances by a wide margin over the single-paragraph questions (0.202–0.229).
- Criterion 3: the in-scope/out-of-scope groups sit in a 0.52-wide empty band (0.306 vs. 0.825), not a close call near the 0.6 cutoff.
- Criterion 4: my shortest sampled chunk (~330 characters) is well clear of the 150-character floor.

Of these, I'd tighten **criterion 1** to 5 of 5. It's the one where I explicitly named the risk when I set it, a future chunking change breaking one of the two multi-paragraph documents, and then set the target as though I expected to lose one anyway. A 4/5 target can absorb exactly the failure it was written to catch without ever registering as a miss. Criteria 3 and 4 I'd leave alone: their margins come from a structural gap in the data (the distance band, the corpus's paragraph lengths) rather than from an untested risk, so loosening or tightening
either wouldn't make them measure anything different.

## The Improvement

**What I changed:**

Added `chunker.py::split_documents_by_paragraph`, one paragraph per chunk (still title-prefixed), no packing toward the 350-char ceiling, and built
a second index under `--variant paragraph` so the default index stayed untouched. `python app.py index --chunker paragraph --variant paragraph`,
then `python run_eval.py --variant paragraph --label after`.

**Why I picked it:**

My Diagnoses section named criterion 1's margin as untested precisely because packing multiple paragraphs into one chunk (the shuttle and library questions) had never been tried unpacked, this change tests that exact risk directly instead of leaving it a theoretical margin.

### Run Log: After

Source: `results/run_2026-09-21_2112_after.md`, produced by `run_eval.py::main`, chunks from `chunker py::split_documents_by_paragraph`, index variant `paragraph`.

| Criterion                              | Target | Run 1 | Run 2 | Run 3 | Verdict |
| -------------------------------------- | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 2. Every answer names a source         | 5 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 3. Gate stops out-of-corpus questions  | 4 of 5 | 5/5   | 5/5   | 5/5   | MET     |
| 4. Chunks keep title line and stay whole | 5 of 5, none <150 chars | 0/5 | 0/5 | 0/5 | MISSED |
| 5. Named source is the one that actually holds the answer | 5 of 5 | 5/5 | 5/5 | 5/5 | MET |

Criterion 4 verdict is 0/5 rather than a partial count because it isn't about the 5 sampled chunks specifically, it's that the corpus now produces 8 chunks under the 150-character floor at all (checked directly against every chunk `split_documents_by_paragraph` produces, not just a sample of 5):

```
course_econ_101_exams.txt#0        119 chars
housing_aldridge_hall_noise.txt#0  121 chars
housing_fenwick_court_noise.txt#0  130 chars
housing_morrow_house_noise.txt#0   131 chars
housing_tamsin_court_noise.txt#0   125 chars
course_econ_101_workload.txt#0     140 chars
housing_calder_annexe_noise.txt#0  141 chars
housing_innisfree_hall_noise.txt#0 145 chars
```

Every one of these is a document's *first* paragraph. The floor-merge step in `split_documents_by_paragraph` only merges a too-short group backward into the previous one (`packed[-1] = packed[-1] + group`); a short first paragraph has no predecessor yet (`packed` is still empty),
so it's appended as an orphan instead of merged. That bug was already latent in `split_documents` too, but packing paragraphs up to a 350-char ceiling almost always absorbed a short first paragraph into a longer group before the floor check ever mattered, de-packing is what exposed it.

**Did it help?**

No. Criterion 1 stayed at 5/5 (no improvement, my two flagged multi-paragraph questions, shuttle and library, already passed before), and the library-basement question's best distance got *worse* (0.306 → 0.374): splitting `study_library_hours.txt`'s two paragraphs apart means the "outlets" paragraph alone is a weaker semantic match to the question than the two paragraphs combined were, and at top-k=3 its two halves now consume two of the three retrieval slots, crowding out a document (`housing_morrow_house_noise.txt`) that used to make the top 3. The answer text itself still came out correct in all 3 runs, so criterion 1 survived, but the retrieval margin it was resting on shrank, not grew.

Worse, this change introduced a new failure on criterion 4 that the packed strategy never had: 8 orphaned under-floor chunks from a floor-merge bug that packing happened to paper over. My diagnosis was right that packing was untested risk, but the untested risk cut the
other way, packing was hiding a bug, not creating one.

## What's Still Broken

**Criterion 4 (chunks keep their title line and stay whole, none under 150 characters)**, missed under `split_documents_by_paragraph`, met under the
original `split_documents`.

What I'd do: fix the floor-merge step itself rather than the chunker strategy. Right now it only merges a too-short group backward into the one before it (`packed[-1] = packed[-1] + group`); a short *first* paragraph in a document has no predecessor yet, so it can't merge backward and comes out as an orphan under the floor. The fix is to also allow forward merging, a too-short first group should absorb the next
paragraph instead of standing alone, which would catch all 8 of the cases I found (`course_econ_101_exams.txt`, the six noise documents, and `course_econ_101_workload.txt`) without giving up the one-paragraph-per-chunk approach I was testing.

Why I stopped where I did: I ran out of time this milestone to rewrite and re-verify the floor-merge logic properly, and since the paragraph variant made criterion 1 worse rather than better anyway, fixing this bug
wouldn't have changed my recommendation, I'm keeping `split_documents` (the packed strategy) as the shipped chunker, not `split_documents_by_paragraph`, so this bug doesn't affect the actual system I'm submitting. It's worth fixing before anyone builds on the paragraph variant specifically, which is why I'm naming it here rather
than treating the failed experiment as closed.

## What I'd Do Differently

I'd rewrite **criterion 1** ("retrieved chunks contain the answer, 4 of 5").
Running the actual before/after comparison exposed a gap in how I wrote it: both the packed and paragraph chunkers scored 5/5 on it, so the criterion couldn't tell a real retrieval regression from a non-event. The only reason I caught the library question getting worse was that I
happened to also look at the raw distance number and the retrieved-source list, neither of which criterion 1 as written actually checks. Next unit I'd write it as something like "for at least 4 of 5 questions, the retrieved chunks contain the answer *and* the best distance stays within 0.1 of its baseline", since a pass/fail count on its own is too coarse to catch a change that makes retrieval measurably worse while the answer still happens to come out right.
