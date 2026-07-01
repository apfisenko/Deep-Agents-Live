"""Split B2C program markdown into per-lesson chunks for extraction."""

from __future__ import annotations

import re

from neo4j_graphrag.experimental.components.text_splitters.base import TextSplitter
from neo4j_graphrag.experimental.components.types import TextChunk, TextChunks

_LESSON_HEADER = re.compile(
    r"^###\s+(?:Тема|Модуль)\s+(\d+)\.\s*(.+?)\s*$",
    re.MULTILINE,
)


class ProgramSectionSplitter(TextSplitter):
    """One chunk per «### Тема N» / «### Модуль N» section."""

    async def run(self, text: str) -> TextChunks:
        matches = list(_LESSON_HEADER.finditer(text))
        if not matches:
            return TextChunks(chunks=[TextChunk(text=text.strip(), index=0)])

        chunks: list[TextChunk] = []
        for idx, match in enumerate(matches):
            start = match.start()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(text)
            section = text[start:end].strip()
            module_number = int(match.group(1))
            title = match.group(2).strip()
            chunks.append(
                TextChunk(
                    text=section,
                    index=idx,
                    metadata={
                        "moduleNumber": module_number,
                        "moduleTitle": title,
                    },
                ),
            )
        return TextChunks(chunks=chunks)
