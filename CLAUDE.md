# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A course starter for AI201 Project 1 ("The Unofficial Guide") — a local RAG
pipeline over a small text corpus. It is a **student assignment**, not a
library: several files ship deliberately incomplete and the student fills them
in across milestones. `RUNNING.md` is the full user-facing manual and is
explicitly marked "leave that file alone."

The work is graded on the student's own reasoning, so when helping here, prefer
explaining and reviewing over silently writing the parts that are theirs to
write (see *Files the student owns* below).

## Commands

Always run inside the activated venv (`.venv\Scripts\Activate.ps1` on Windows,
`source .venv/bin/activate` elsewhere).

```bash
python test.py                              # environment check — Python version, pins, API key, one live model call
python app.py corpora                       # list available corpora
python app.py index                         # load → chunk → embed → store (re-run after any chunker or corpus change)
python app.py ask "question"                # full pipeline, one question
python app.py ask                           # interactive loop
python app.py chunks -n 5                   # sample chunks with source + producing function
python app.py chunks --from-doc NAME        # every chunk of one document (use to compare before/after a chunker change)
python app.py retrieve "question"           # distances only, no model call
python run_eval.py --label before           # 3 runs per question, caching off, writes results/run_<stamp>_before.md
python serve.py                             # same pipeline over HTTP on :5000
python tools/smoke_test.py                  # end-to-end plumbing check, no API key or model download needed
```

Flags: `--corpus NAME` (all), `--variant NAME` (`index`/`ask`/`retrieve` — keeps
two indexes of the same corpus side by side), `--top-k`, `--threshold` (`ask`),
`--show-prompt` (`ask`, prints the exact assembled prompt).

There is no test framework, linter, or build step. `test.py` checks the
environment; `tools/smoke_test.py` checks the starter's plumbing by setting
`AI201_FAKE_EMBEDDINGS=1` and stubbing the model call.

## Architecture

Five named stages. The vocabulary matters: unit 2 asks the student to diagnose
each failure by naming which stage caused it, so refer to failures by stage.

| Stage | File | Notes |
|---|---|---|
| 1 loading | `ingest.py` | reads `.txt`/`.md` from `corpora/<name>/documents/`, `clean_text` normalises whitespace |
| 2 chunking | `chunker.py` | `split_documents` is the seam the student replaces; `fallback_split` is the original and must be kept |
| 3 embedding | `store.py` | local ONNX `all-MiniLM-L6-v2` bundled by Chroma — no PyTorch, no Hugging Face, no API quota |
| 4 retrieval | `store.py::search` | returns `Result` objects carrying `distance` |
| 5 generation | `generate.py` | the **only** outbound service call in the whole project |

`gate.py` sits between 4 and 5: `check()` refuses when the best distance is
above `config.THRESHOLD`. Refusal is a normal outcome, not an error — `/ask`
returns it as HTTP 200 with `"refused": true`.

`app.py::ask_pipeline` is the single shared entry point for retrieve → gate →
answer. It prints nothing and returns a dict; `app.py::_ask_one` formats it for
the CLI and `serve.py` turns it into JSON. Keep it that way — a second copy of
the gate logic in the web layer would drift from the CLI's.

### Invariants worth not breaking

- **Cosine distance.** The Chroma collection is created with
  `metadata={"hnsw:space": "cosine"}`. Chroma defaults to squared L2; every
  distance number and the 0.6 threshold assume cosine.
- **Lower distance is better.** 0.3 close, 0.9 unrelated. The gate passes when
  `best < threshold`.
- **Every model call goes through `generate.generate()`.** Rate pacing, retry on
  429, the session request budget (`QuotaGuard`), response caching, and token
  accounting all live there once. Do not call the genai client elsewhere.
- **Caching is on while building, off while evaluating.** `run_eval.py` passes
  `cache=False` so three runs are three real answers.
- **`Chunk.produced_by` is a graded field.** It names the function that made the
  chunk and is printed by `app.py chunks` and stored in Chroma metadata; a
  student-written `split_documents` should set it to
  `"chunker.py::split_documents"`.
- **`serve.py` has no logging or timing on purpose** — building that is the
  unit 9 exercise. Don't add it.
- **`results/` is intentionally not gitignored.** Run logs are graded evidence.

### Configuration

`config.py` holds everything tunable; `.env` values win over its defaults
(`AI201_CORPUS`, `AI201_MODEL`, `AI201_CACHE=0`, `GEMINI_API_KEY`).
`collection_name(corpus, variant)` sanitises names to Chroma's rules, so a
corpus rename changes the collection and requires re-indexing.

Changing `EMBEDDING_MODEL` away from `all-MiniLM-L6-v2` switches to the
sentence-transformers path, which needs an extra install and shifts every
distance — the threshold has to be re-measured afterwards.

## Files the student owns

`questions.py` (five questions, currently blank), `criteria.md` (criteria 4 and
5 are blank), `chunker.py::split_documents`, `THRESHOLD` and the chunking
numbers in `config.py`, `README.md` (the submission itself), and `scorer.py` —
a file that does not exist yet. If a student creates `scorer.py` exporting
`judge(question, expects, answer, results) -> bool`, `run_eval.py` picks it up
automatically and fills the verdict columns.

## Committing

At least four new commits per unit; the history is what shows criteria existed
before results did. Never delete and recreate the repo — `.github/MAINTAINERS.md`
explains that commit hashes here are a pinned grading baseline.
