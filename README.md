# StackContext-AI

StackContextAI is an MVP developer context engine that ingests GitHub repository activity, chunks and embeds it, stores it in Chroma, and answers natural language questions with grounded citations.

## MVP Scope

- Ingest GitHub commits, pull requests, and issues
- Persist raw source data locally as JSON
- Normalize and chunk text into retrieval-friendly units
- Generate embeddings with OpenAI
- Store and query vectors with Chroma
- Answer questions with citation-backed RAG through a CLI

## Project Structure

```text
stackcontextai/
  ingestion/    # GitHub API fetch + source mapping
  processing/   # normalization + chunking
  embeddings/   # OpenAI embeddings + Chroma storage
  retrieval/    # top-k retrieval
  qa/           # grounded answer generation
  storage/      # local filesystem persistence
```

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
cp .env.example .env
```

Required environment variables:

- `GITHUB_TOKEN`
- `OPENAI_API_KEY`

Optional:

- `OPENAI_EMBEDDING_MODEL`
- `OPENAI_CHAT_MODEL`

## Usage

```bash
stackcontextai index-repo https://github.com/owner/repo
stackcontextai ask "Why was the authentication flow changed?"
```

`ask` uses the last indexed repository by default. You can also pass `--repo owner__repo`.

## Notes

- Chunking uses a simple word-based approximation tuned to the requested 300-500 token target.
- Answers are instructed to return `Not enough information.` when the retrieved context does not support a grounded answer.
