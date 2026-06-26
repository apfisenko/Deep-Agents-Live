"""Document chunking strategies for RAG indexing."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

if TYPE_CHECKING:
    from app.config import Settings

_MARKDOWN_HEADERS = [
    ("##", "section"),
    ("###", "subsection"),
]


def split_document_text(text: str, file_path: Path, settings: Settings) -> list[str]:
    """Split document text using markdown-aware rules when applicable."""
    recursive = RecursiveCharacterTextSplitter(
        chunk_size=settings.chunk_size,
        chunk_overlap=settings.chunk_overlap,
    )
    suffix = file_path.suffix.lower()
    if suffix != ".md" or not settings.chunk_markdown_by_headers:
        return [part for part in recursive.split_text(text) if part.strip()]

    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=_MARKDOWN_HEADERS,
        strip_headers=False,
    )
    sections = header_splitter.split_text(text)
    if not sections:
        return [part for part in recursive.split_text(text) if part.strip()]

    chunks: list[str] = []
    for section in sections:
        content = section.page_content.strip()
        if not content:
            continue
        if len(content) <= settings.chunk_size:
            chunks.append(content)
            continue
        chunks.extend(part for part in recursive.split_text(content) if part.strip())

    if chunks:
        return chunks
    return [part for part in recursive.split_text(text) if part.strip()]
