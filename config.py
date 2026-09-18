"""
Settings for The Unofficial Guide.

Everything you're likely to change lives here, at the top, on purpose.
You'll edit THRESHOLD in Milestone 4 and the chunking numbers in Milestone 3.

Anything you set in your .env file wins over the defaults here.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).parent
load_dotenv(ROOT / ".env")


# ─── The corpus you're working with ──────────────────────────────────────────
# Change this to switch corpora, or pass --corpus on the command line.
# Options are the folder names inside corpora/. See corpora/README.md.

CORPUS = os.getenv("AI201_CORPUS", "campus_life")


# ─── Chunking (Milestone 3) ──────────────────────────────────────────────────
# Decided before writing split_documents, from measurements of campus_life.
#
# What the corpus is: 88 short posts, not guides. Documents run 178–549
# characters (median 305), with a title line of ~26 and one to four body
# paragraphs. Body paragraphs are short — median 112 characters, 124 of 183
# under 150 — and each usually carries one self-contained fact.
#
# CHUNK_SIZE is a CEILING, not a window. split_documents packs whole paragraphs
# up to it and never cuts one, so a post under the ceiling stays a single chunk.
#
# Why 350 and not smaller: it is above the median document (305), so the
# two-paragraph majority stays whole, and only the 11 documents whose bodies
# genuinely run long get split — the 3- and 4-paragraph posts where the facts
# really are independent. Simulated, 350 gives 99 chunks, mean 285, none under
# 150. Dropping to 300 splits 17 documents and 250 splits 30 but puts 7 chunks
# under the 150 floor criterion 4 sets, which is the point where splitting
# starts producing fragments instead of facts.
#
# Why 350 and not larger: 450 splits only 3 documents and 600 splits none,
# which is the starter's accidental behaviour re-labelled. If a multi-fact post
# like transit_shuttle.txt (weekday hours, weekend hours, cost, a skipped stop)
# stays one chunk, its embedding is an average of four unrelated facts — which
# is why it is already my worst-retrieving question at 0.411.
#
# Why overlap is 0: overlap exists to repair context lost to an arbitrary cut.
# Splits now land on paragraph boundaries and every chunk re-carries its title
# line, so there is nothing to repair. At a 350 ceiling the median paragraph
# (112) would be a third of a chunk duplicated, leaving two near-identical
# chunks competing for the same query. The starter's 120-character overlap is
# also what produced the 2- and 6-character orphan tails I measured when
# forcing fallback_split to a smaller size.

CHUNK_SIZE = 350        # ceiling: pack whole paragraphs up to this, never cut one
CHUNK_OVERLAP = 0       # paragraph boundaries + repeated title replace overlap
CHUNK_MIN = 150         # floor: a group this small is merged back, not emitted


# ─── Retrieval (Milestone 4) ─────────────────────────────────────────────────

# Swept 3-10 against all five test questions: the right chunk is always rank 1,
# by a wide margin, at every k tried. What increasing k buys is not correctness
# but noise — at k=5 the library question pulls in four dorm-noise posts that
# all share one recycled sentence ("the library is open until 2am"), and a
# laundry-price question pulls in three other buildings' prices. At k=2 that
# laundry noise drops to zero; at k=3 it drops to one. Chose 3 to keep one
# spare slot beyond rank 1 for a question where the top match isn't the right
# one, while still roughly halving the near-duplicate material that reaches
# the prompt — see criterion 5 in criteria.md.
TOP_K = 3               # how many chunks to pull back per question

# The relevance gate. If the best chunk is further away than this, the system
# refuses to answer instead of handing the model thin material.
#
# LOWER IS BETTER: 0.3 is a close match, 0.9 is unrelated.
#
# 0.6 is a reasonable starting point, not a right answer. Milestone 4 has you
# measure your own two groups of distances and put the cutoff in the gap.
# Most corpora land somewhere between 0.45 and 0.75.
THRESHOLD = 0.6


# ─── Models ──────────────────────────────────────────────────────────────────
# Embeddings run on your own machine and cost no API quota.
# Only generation calls out to a service.

# This is the model Chroma bundles, and leaving it alone is the fast path: it
# downloads about 80 MB from Chroma's own CDN and needs nothing else installed.
#
# Setting it to any other name — unit 2's "try a second embedding model"
# stretch option — switches to loading that model from Hugging Face instead,
# which needs `pip install 'sentence-transformers>=3.4,<3.5'` first. store.py
# says so with a real error message rather than a stack trace if you forget.
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
MODEL = os.getenv("AI201_MODEL", "gemini-3.5-flash-lite")


# ─── Rate limiting and quota guards ──────────────────────────────────────────
# You should not need to touch these. They exist so that a runaway loop costs
# you a warning instead of your whole day's allowance.

REQUESTS_PER_MINUTE = 30       # outgoing calls the limiter will allow per minute
SESSION_REQUEST_BUDGET = 300   # stop and warn rather than draining the daily quota
MAX_RETRIES = 4                # on 429 / resource-exhausted, with backoff

CACHE_ENABLED = os.getenv("AI201_CACHE", "1") != "0"
CACHE_DIR = ROOT / ".cache"


# ─── Paths ───────────────────────────────────────────────────────────────────

CORPORA_DIR = ROOT / "corpora"
CHROMA_DIR = ROOT / "chroma_db"
RESULTS_DIR = ROOT / "results"


def corpus_path(name: str | None = None) -> Path:
    """Folder holding the documents for a corpus."""
    return CORPORA_DIR / (name or CORPUS) / "documents"


def collection_name(name: str | None = None, variant: str = "default") -> str:
    """
    Name of the vector-store collection for a corpus.

    `variant` lets you index the same corpus two different ways and query both
    without deleting anything — you'll want that in unit 2 when you compare
    chunking strategies.

    Chroma is fussy about collection names: 3 to 63 characters, starting and
    ending with a letter or digit, and nothing but letters, digits, underscores
    and hyphens in between. If you bring your own corpus and name the folder
    something Chroma won't accept, this cleans it up rather than failing.
    """
    import re

    raw = f"{name or CORPUS}__{variant}"
    cleaned = re.sub(r"[^A-Za-z0-9_-]", "-", raw)
    cleaned = cleaned.strip("_-")          # must start and end alphanumeric
    if not cleaned or not cleaned[0].isalnum():
        cleaned = f"c{cleaned}"
    if not cleaned[-1].isalnum():
        cleaned = f"{cleaned}0"
    return cleaned[:63].rstrip("_-") or "collection"
