from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    base_dir: Path = Path("data")
    github_token: str | None = os.getenv("GITHUB_TOKEN")
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    chat_model: str = os.getenv("OPENAI_CHAT_MODEL", "gpt-4.1-mini")
    chunk_size: int = 350
    chunk_overlap: int = 50
    retrieval_k: int = 6


def get_settings() -> Settings:
    return Settings()
