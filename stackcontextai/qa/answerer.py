from __future__ import annotations

from openai import OpenAI


class GroundedAnswerService:
    def __init__(self, api_key: str, model: str) -> None:
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def answer(self, question: str, chunks: list[dict]) -> str:
        if not chunks:
            return "Not enough information."

        context_blocks = []
        for chunk in chunks:
            metadata = chunk["metadata"]
            context_blocks.append(
                "\n".join(
                    [
                        f"Source ID: {chunk['chunk_id']}",
                        f"Source Type: {metadata['source_type']}",
                        f"Title: {metadata['title']}",
                        f"URL: {metadata['url']}",
                        f"Timestamp: {metadata['timestamp']}",
                        f"Content: {chunk['text']}",
                    ]
                )
            )

        prompt = (
            "You answer questions about a codebase using only the provided context.\n"
            "Rules:\n"
            "- If the answer is not supported by the context, reply exactly: Not enough information.\n"
            "- Keep the answer concise.\n"
            "- Cite supporting sources inline using their URL or Source ID.\n"
            "- Do not invent facts.\n\n"
            f"Question: {question}\n\n"
            "Context:\n"
            + "\n\n---\n\n".join(context_blocks)
        )

        response = self.client.responses.create(
            model=self.model,
            input=prompt,
        )
        return response.output_text.strip()
