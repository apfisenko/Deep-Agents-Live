"""In-memory vector store for RAG chunks."""

import math
from dataclasses import dataclass, field


@dataclass
class StoredChunk:
    chunk_id: str
    doc_id: str
    text: str
    embedding: list[float]
    audience: str
    source_path: str


@dataclass
class RagStore:
    chunks: dict[str, StoredChunk] = field(default_factory=dict)
    doc_chunk_ids: dict[str, list[str]] = field(default_factory=dict)

    def upsert_document(self, doc_id: str, chunks: list[StoredChunk]) -> None:
        self.remove_document(doc_id)
        ids: list[str] = []
        for chunk in chunks:
            self.chunks[chunk.chunk_id] = chunk
            ids.append(chunk.chunk_id)
        self.doc_chunk_ids[doc_id] = ids

    def remove_document(self, doc_id: str) -> None:
        for chunk_id in self.doc_chunk_ids.pop(doc_id, []):
            self.chunks.pop(chunk_id, None)

    @property
    def indexed_docs_count(self) -> int:
        return len(self.doc_chunk_ids)

    def search(
        self,
        query_embedding: list[float],
        *,
        audience: str,
        limit: int = 5,
    ) -> list[StoredChunk]:
        scored: list[tuple[float, StoredChunk]] = []
        for chunk in self.chunks.values():
            if chunk.audience != audience:
                continue
            score = _cosine_similarity(query_embedding, chunk.embedding)
            scored.append((score, chunk))
        scored.sort(key=lambda item: item[0], reverse=True)
        return [chunk for _, chunk in scored[:limit]]


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


_store: RagStore | None = None


def get_store() -> RagStore:
    global _store
    if _store is None:
        _store = RagStore()
    return _store


def reset_store() -> None:
    global _store
    _store = RagStore()
