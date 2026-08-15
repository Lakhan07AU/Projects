"""RAG embeddings.

Modular: a demo keyword/cosine retriever works without any model. When
sentence-transformers or an OpenAI-compatible embedding API is available it can
be enabled through the retriever without changing the pipeline.
"""
from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Chunk:
    doc_id: str
    text: str
    source: str
    tokens: set[str] = field(default_factory=set)


def chunk_text(doc_id: str, text: str, source: str = "", size: int = 800) -> list[Chunk]:
    """Naive sentence-window chunking."""
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks: list[Chunk] = []
    buf: list[str] = []
    length = 0
    for sent in sentences:
        buf.append(sent)
        length += len(sent)
        if length >= size:
            joined = " ".join(buf)
            chunks.append(Chunk(doc_id=f"{doc_id}-{len(chunks)}", text=joined,
                                source=source, tokens=tokenize(joined)))
            buf, length = [], 0
    if buf:
        joined = " ".join(buf)
        chunks.append(Chunk(doc_id=f"{doc_id}-{len(chunks)}", text=joined,
                            source=source, tokens=tokenize(joined)))
    return chunks


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]{3,}", text.lower()))


class VectorIndex:
    """In-memory demo index. Swappable for a real vector DB (pgvector, etc.)."""

    def __init__(self) -> None:
        self.chunks: list[Chunk] = []

    def add(self, chunks: list[Chunk]) -> None:
        self.chunks.extend(chunks)

    def query(self, text: str, top_k: int = 3) -> list[dict[str, Any]]:
        query_tokens = tokenize(text)
        scored = []
        for c in self.chunks:
            overlap = len(query_tokens & c.tokens)
            if overlap:
                scored.append((overlap, c))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [
            {"doc_id": c.doc_id, "text": c.text, "source": c.source, "score": s}
            for s, c in scored[:top_k]
        ]
