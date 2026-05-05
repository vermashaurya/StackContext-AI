from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import urlparse


def parse_github_repo_url(repo_url: str) -> tuple[str, str]:
    parsed = urlparse(repo_url)
    if parsed.netloc != "github.com":
        raise ValueError("Only github.com repository URLs are supported.")

    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) < 2:
        raise ValueError("Repository URL must look like https://github.com/owner/repo")

    owner = parts[0]
    repo = parts[1].removesuffix(".git")
    return owner, repo


def repo_slug(owner: str, repo: str) -> str:
    return f"{owner}__{repo}"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_json(path: Path, payload: object) -> None:
    ensure_dir(path.parent)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def clean_whitespace(text: str) -> str:
    text = re.sub(r"\r\n?", "\n", text or "")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
