# The Unofficial Guide

<!-- Replace this line with your name and which corpus you picked. -->

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
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
sliding window was the wrong shape from the start. My chunker instead packs
whole paragraphs up to 350 characters and never cuts one, and re-adds the
document's title to every chunk, since body text here often drops the subject
("the basement," not "the library basement").

I picked 350 by testing a few ceilings against my real paragraph lengths.
Below 300, some chunks came out shorter than 150 characters — too small to
be useful. Above 450, almost nothing split at all, which is just the
starter's old behavior with a new number. 350 splits only the 11 documents
that actually needed it.

Overlap is 0 because there's nothing to repair: splits happen between
paragraphs, not through the middle of one, and every chunk keeps its title.

One thing I changed after testing: `TOP_K`, not the chunk size. The default
of 5 buried the right chunk under near-duplicate posts (same laundry room,
same dorm noise complaint), so I lowered it to 3.

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** — source: `admin_add_drop_deadline.txt#0` — produced by: `chunker.py::split_documents`

```
On the add/drop deadline

You can add a course through the end of the second week. Dropping is a longer window — through the end of week six — but a drop after week two shows as a W on your transcript. Nothing anywhere on the registrar's site says this plainly, and students find out from each other.
```

**Chunk 2** — source: `course_biol_160_exams.txt#0` — produced by: `chunker.py::split_documents`

```
BIOL 160 Cell Biology — assessment

Four unit tests and a cumulative final. Not curved.

The unit tests come fast, roughly every three weeks; falling behind once is very hard to recover from.
```

**Chunk 3** — source: `course_math_220.txt#0` — produced by: `chunker.py::split_documents`

```
MATH 220 Linear Algebra

I lived here my sophomore year. Format is chalk-and-talk lecture, weekly problem sets marked for correctness. Assessment: two midterms and a cumulative final. Curved to a b- median.

Expect 6 to 8 hours a week, almost all of it on problem sets.

The one piece of advice: the problem sets are the course; the lectures make sense afterwards rather than during.
```

**Chunk 4** — source: `dining_the_ridgeway_cafe.txt#0` — produced by: `chunker.py::split_documents`

```
The Ridgeway Café

Second-year here. Wait times: 10 to 15 minutes at 12:30, none after 2:00. The thing worth going for is the only place on campus with real espresso. The thing to know is that seating is tight; about 40 seats for a building of 900.

Hours are 7:00am to 4:00pm weekdays only. Costs declining balance only, no meal swipes.
```

**Chunk 5** — source: `housing_innisfree_hall_laundry.txt#0` — produced by: `chunker.py::split_documents`

```
Laundry in Innisfree Hall

Machines take $1.75 wash, $1.75 dry, app-based. There are eight washers and six dryers for the building, which is the wrong ratio and means the dryers back up on Sunday evenings.

Best time to do laundry here is Tuesday or Wednesday morning. Sunday after 6pm you will wait.
```

All five above are documents that stayed whole under the 350-character ceiling (88 of 88 documents fit one chunk under the starter's numbers; 77 still do under mine). For a document the chunker actually split, here are both chunks of `transit_shuttle.txt` — the title line is re-prepended to the second chunk
because its body never says the word "shuttle":

**Split example, chunk a** — source: `transit_shuttle.txt#0` — produced by: `chunker.py::split_documents`

```
The campus shuttle

Runs a loop every 20 minutes from 7am to 11pm on weekdays and every 40 minutes on weekends. The published timetable is optimistic by about five minutes in the morning and accurate the rest of the day.
```

**Split example, chunk b** — source: `transit_shuttle.txt#1` — produced by: `chunker.py::split_documents`

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

**1.** I asked Claude to decide the chunk size and overlap and write down why before touching the chunker, since I'd noticed my documents were short posts, not sectioned guides. Instead of picking a number, it measured the actual paragraph lengths in my corpus (median 112 characters, documents 178-549) andsimulated a title-prefixed, paragraph-packing strategy at several ceilings before proposing 350/0/150. I didn't just take those numbers; after the real
`split_documents` was written, I had it re-run retrieval on my five questions and the smoke test before I'd accept the change, which is what caught that the shuttle question's distance actually improved (0.411 → 0.180) rather than
assuming the simulation would carry over exactly.

**2.** I asked it to adjust `TOP_K`, warned that too few loses the right chunk and too many buries it in loosely related material. It didn't just guess a number either; it swept k from 3 to 10 against all five test questions and a laundry-price question I'd flagged earlier as a hazard case, and showed me that the right chunk was always rank 1 no matter the k, while the *noise* grew: at k=5 a library question pulled in four dorm-noise posts that all share
one recycled sentence about the library, and the laundry question pulled in three other buildings' prices. I used that evidence to lower `TOP_K` from the starter's 5 to 3 rather than leaving it at the default, and kept one spare slot above rank 1 instead of cutting to 2, since none of my questions actually needed the extra headroom but I didn't want zero margin either.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion                              | Target | Run 1 | Run 2 | Run 3 | Verdict |
| -------------------------------------- | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer | 4 of 5 |       |       |       |         |
| 2. Every answer names a source         | 5 of 5 |       |       |       |         |
| 3. Gate stops out-of-corpus questions  | 4 of 5 |       |       |       |         |
| 4.                                     |        |       |       |       |         |
| 5.                                     |        |       |       |       |         |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
| - | --------- | ------- | ------------- |
| 1 |           |         |               |
| 2 |           |         |               |
| 3 |           |         |               |
| 4 |           |         |               |
| 5 |           |         |               |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion                              | Target | Run 1 | Run 2 | Run 3 | Verdict |
| -------------------------------------- | ------ | ----- | ----- | ----- | ------- |
| 1. Retrieved chunk contains the answer | 4 of 5 |       |       |       |         |
| 2. Every answer names a source         | 5 of 5 |       |       |       |         |
| 3. Gate stops out-of-corpus questions  | 4 of 5 |       |       |       |         |
| 4.                                     |        |       |       |       |         |
| 5.                                     |        |       |       |       |         |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
