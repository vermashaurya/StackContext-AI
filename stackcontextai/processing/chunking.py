from __future__ import annotations

from stackcontextai.models import TextChunk


def chunk_text(text: str, metadata: dict, chunk_size: int = 350, overlap: int = 50) -> list[TextChunk]:
    words = text.split()
    if not words:
        return []

    chunks: list[TextChunk] = []
    start = 0
    index = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunk_metadata = {
            **metadata,
            "chunk_index": index,
        }
        chunks.append(
            TextChunk(
                chunk_id=f"{metadata['source_type']}:{metadata['source_id']}:{index}",
                text=" ".join(chunk_words),
                metadata=chunk_metadata,
            )
        )
        if end >= len(words):
            break
        start = max(end - overlap, start + 1)
        index += 1

    return chunks
