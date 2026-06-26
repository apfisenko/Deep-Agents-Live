"""In-memory vector store for RAG chunks."""

from dataclasses import dataclass, field


@dataclass
class StoredChunk:
    chunk_id: str
    doc_id: str
    text: str
    embedding: list[float]
    audience: str
    source_path: str
    sparse_indices: list[int] | None = None
    sparse_values: list[float] | None = None


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


_store: RagStore | None = None


def get_store() -> RagStore:
    global _store
    if _store is None:
        _store = RagStore()
    return _store


def reset_store() -> None:
    global _store
    _store = RagStore()
