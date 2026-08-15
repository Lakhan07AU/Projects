"""RAG retriever wrapper. Kept modular so it can be enabled later without
changing API callers."""
from __future__ import annotations

from typing import Any

from app.ai.rag.embeddings import VectorIndex, chunk_text

index = VectorIndex()


def ingest_document(doc_id: str, text: str, source: str = "") -> int:
    chunks = chunk_text(doc_id, text, source)
    index.add(chunks)
    return len(chunks)


def retrieve(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    return index.query(query, top_k)


def enabled() -> bool:
    return len(index.chunks) > 0
