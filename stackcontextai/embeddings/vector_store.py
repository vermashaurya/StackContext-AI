from __future__ import annotations

from chromadb import PersistentClient

from stackcontextai.models import TextChunk


class ChromaVectorStore:
    def __init__(self, persist_directory: str, collection_name: str) -> None:
        self.client = PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def reset(self) -> None:
        ids = self.collection.get().get("ids", [])
        if ids:
            self.collection.delete(ids=ids)

    def upsert_chunks(self, chunks: list[TextChunk], embeddings: list[list[float]]) -> None:
        self.collection.upsert(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            embeddings=embeddings,
            metadatas=[chunk.metadata for chunk in chunks],
        )

    def query(self, embedding: list[float], top_k: int) -> dict:
        return self.collection.query(query_embeddings=[embedding], n_results=top_k)
