from __future__ import annotations

from stackcontextai.models import TextChunk
from stackcontextai.processing.chunking import chunk_text
from stackcontextai.processing.normalize import normalize_record_text


def build_chunks(records: list[dict], chunk_size: int, overlap: int) -> list[TextChunk]:
    chunks: list[TextChunk] = []
    for record in records:
        text = normalize_record_text(record)
        metadata = {
            "source_type": record["source_type"],
            "source_id": record["source_id"],
            "url": record["url"],
            "timestamp": record["timestamp"],
            "author": record["author"],
            "title": record["title"],
        }
        chunks.extend(chunk_text(text, metadata=metadata, chunk_size=chunk_size, overlap=overlap))
    return chunks
