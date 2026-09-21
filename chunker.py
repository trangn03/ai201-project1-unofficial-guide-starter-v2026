"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

from dataclasses import dataclass

import config
from ingest import Document


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def _blocks(text: str) -> list[str]:
    """A document's blank-line-separated blocks, empties dropped."""
    return [b.strip() for b in text.split("\n\n") if b.strip()]


def split_documents(
    documents: list[Document],
    chunk_size: int | None = None,
    chunk_min: int | None = None,
) -> list[Chunk]:
    """
    Title-prefixed, paragraph-packed chunks. Never cuts a paragraph.

    `campus_life` is 88 short posts, not guides: 178–549 characters each
    (median 305), a title line of ~26, and one to four body paragraphs that
    each carry a self-contained fact. Two things follow from that, and this
    function is built out of them.

    First, the title line is the only topic label a chunk gets. Body sentences
    drop the subject — the advice line in `course_cs_210.txt` never says
    "CS 210", and `study_library_hours.txt` says "the basement" without saying
    "library" — so every chunk gets the title prepended. A chunk that loses it
    is close to unretrievable.

    Second, `config.CHUNK_SIZE` is a ceiling here rather than a window. Whole
    paragraphs are packed until the next one would exceed it, so a post shorter
    than the ceiling stays one chunk and nothing is ever cut mid-sentence. That
    is the opposite of `fallback_split`, which indexes by character and will
    happily cut mid-word.

    Groups that would come out under `config.CHUNK_MIN` are merged back into
    their predecessor rather than emitted, which is what keeps a trailing
    one-line paragraph from becoming an orphan chunk. A single paragraph longer
    than the ceiling is kept whole and over-length on purpose: cutting it is
    the failure this function exists to avoid.
    """
    ceiling = chunk_size or config.CHUNK_SIZE
    floor = chunk_min or config.CHUNK_MIN

    chunks: list[Chunk] = []
    for doc in documents:
        blocks = _blocks(doc.text)
        if not blocks:
            continue

        title, bodies = blocks[0], blocks[1:]
        if not bodies:
            # Title-only document — keep it as-is rather than invent a body.
            bodies = [title]

        def assemble(group: list[str]) -> str:
            return f"{title}\n\n" + "\n\n".join(group)

        # Pack whole paragraphs up to the ceiling.
        groups: list[list[str]] = []
        current: list[str] = []
        for body in bodies:
            if current and len(assemble(current + [body])) > ceiling:
                groups.append(current)
                current = [body]
            else:
                current.append(body)
        if current:
            groups.append(current)

        # Merge anything under the floor back into the chunk before it.
        packed: list[list[str]] = []
        for group in groups:
            if packed and len(assemble(group)) < floor:
                packed[-1] = packed[-1] + group
            else:
                packed.append(group)

        for index, group in enumerate(packed):
            chunks.append(
                Chunk(
                    text=assemble(group),
                    source=doc.source,
                    index=index,
                    produced_by="chunker.py::split_documents",
                )
            )

    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
