from __future__ import annotations

import argparse

from stackcontextai.config import get_settings
from stackcontextai.embeddings.openai_embedder import OpenAIEmbedder
from stackcontextai.embeddings.vector_store import ChromaVectorStore
from stackcontextai.ingestion.github_client import GitHubClient
from stackcontextai.ingestion.service import GitHubIngestionService
from stackcontextai.processing.pipeline import build_chunks
from stackcontextai.qa.answerer import GroundedAnswerService
from stackcontextai.retrieval.service import RetrievalService
from stackcontextai.storage.repository import LocalRepositoryStore
from stackcontextai.utils import parse_github_repo_url, repo_slug


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="stackcontextai")
    subparsers = parser.add_subparsers(dest="command", required=True)

    index_parser = subparsers.add_parser("index-repo", help="Ingest and index a GitHub repository.")
    index_parser.add_argument("repo_url", help="GitHub repository URL")

    ask_parser = subparsers.add_parser("ask", help="Ask a grounded question about the indexed repository.")
    ask_parser.add_argument("question", help="Natural language question")
    ask_parser.add_argument("--repo", dest="repo_slug", help="Optional repo slug like owner__repo")
    ask_parser.add_argument("--top-k", dest="top_k", type=int, default=None, help="Number of chunks to retrieve")

    return parser


def handle_index(repo_url: str) -> int:
    settings = get_settings()
    if not settings.openai_api_key:
        print("OPENAI_API_KEY is required for indexing.")
        return 1

    owner, repo = parse_github_repo_url(repo_url)
    slug = repo_slug(owner, repo)
    store = LocalRepositoryStore(settings.base_dir)

    ingestion = GitHubIngestionService(GitHubClient(token=settings.github_token))
    raw_payload = ingestion.ingest(owner, repo)

    store.save_raw(slug, "commits", raw_payload["commits"])
    store.save_raw(slug, "pull_requests", raw_payload["pull_requests"])
    store.save_raw(slug, "issues", raw_payload["issues"])

    records = raw_payload["commits"] + raw_payload["pull_requests"] + raw_payload["issues"]
    chunks = build_chunks(records, chunk_size=settings.chunk_size, overlap=settings.chunk_overlap)
    store.save_processed(slug, "chunks", [chunk.to_dict() for chunk in chunks])
    store.save_manifest(
        slug,
        {
            "repo_url": repo_url,
            "owner": owner,
            "repo": repo,
            "slug": slug,
            "record_count": len(records),
            "chunk_count": len(chunks),
        },
    )
    store.set_last_repo(slug)

    if not chunks:
        print(f"Indexed {repo_url}")
        print(f"Records: {len(records)}")
        print("Chunks: 0")
        print("No text content was available to embed.")
        return 0

    embedder = OpenAIEmbedder(api_key=settings.openai_api_key, model=settings.embedding_model)
    vector_store = ChromaVectorStore(
        persist_directory=str(store.vector_dir),
        collection_name=slug,
    )
    vector_store.reset()
    embeddings = embedder.embed_texts([chunk.text for chunk in chunks])
    vector_store.upsert_chunks(chunks, embeddings)

    print(f"Indexed {repo_url}")
    print(f"Records: {len(records)}")
    print(f"Chunks: {len(chunks)}")
    print(f"Saved raw data under: {store.repo_raw_dir(slug)}")
    return 0


def handle_ask(question: str, requested_slug: str | None, top_k: int | None) -> int:
    settings = get_settings()
    if not settings.openai_api_key:
        print("OPENAI_API_KEY is required for asking questions.")
        return 1

    store = LocalRepositoryStore(settings.base_dir)
    slug = requested_slug or store.get_last_repo()
    if not slug:
        print("No indexed repository found. Run index-repo first.")
        return 1

    manifest = store.load_manifest(slug)
    embedder = OpenAIEmbedder(api_key=settings.openai_api_key, model=settings.embedding_model)
    vector_store = ChromaVectorStore(
        persist_directory=str(store.vector_dir),
        collection_name=slug,
    )
    retrieval = RetrievalService(embedder=embedder, vector_store=vector_store)
    answerer = GroundedAnswerService(api_key=settings.openai_api_key, model=settings.chat_model)

    chunks = retrieval.retrieve(question, top_k=top_k or settings.retrieval_k)
    answer = answerer.answer(question, chunks)

    print(f"Repository: {manifest['repo_url']}")
    print(f"Question: {question}\n")
    print("Answer:")
    print(answer)
    print("\nSources:")
    seen_urls: set[str] = set()
    for chunk in chunks:
        metadata = chunk["metadata"]
        if metadata["url"] in seen_urls:
            continue
        seen_urls.add(metadata["url"])
        print(f"- {chunk['chunk_id']} | {metadata['url']}")

    return 0


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "index-repo":
        raise SystemExit(handle_index(args.repo_url))
    if args.command == "ask":
        raise SystemExit(handle_ask(args.question, args.repo_slug, args.top_k))

    raise SystemExit(1)


if __name__ == "__main__":
    main()
