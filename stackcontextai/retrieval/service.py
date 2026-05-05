from __future__ import annotations

from stackcontextai.embeddings.openai_embedder import OpenAIEmbedder
from stackcontextai.embeddings.vector_store import ChromaVectorStore


class RetrievalService:
    def __init__(self, embedder: OpenAIEmbedder, vector_store: ChromaVectorStore) -> None:
        self.embedder = embedder
        self.vector_store = vector_store

    def retrieve(self, query: str, top_k: int = 6) -> list[dict]:
        query_embedding = self.embedder.embed_query(query)
        result = self.vector_store.query(query_embedding, top_k=top_k)

        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        ids = result.get("ids", [[]])[0]
        distances = result.get("distances", [[]])[0]

        chunks: list[dict] = []
        for chunk_id, document, metadata, distance in zip(ids, documents, metadatas, distances):
            chunks.append(
                {
                    "chunk_id": chunk_id,
                    "text": document,
                    "metadata": metadata,
                    "distance": distance,
                }
            )
        return chunks
