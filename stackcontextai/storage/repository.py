from __future__ import annotations

from pathlib import Path

from stackcontextai.utils import ensure_dir, read_json, write_json


class LocalRepositoryStore:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = base_dir
        self.raw_dir = ensure_dir(base_dir / "raw")
        self.processed_dir = ensure_dir(base_dir / "processed")
        self.vector_dir = ensure_dir(base_dir / "vectorstore")
        self.state_path = base_dir / "index_state.json"

    def repo_raw_dir(self, slug: str) -> Path:
        return ensure_dir(self.raw_dir / slug)

    def repo_processed_dir(self, slug: str) -> Path:
        return ensure_dir(self.processed_dir / slug)

    def save_raw(self, slug: str, name: str, payload: object) -> Path:
        path = self.repo_raw_dir(slug) / f"{name}.json"
        write_json(path, payload)
        return path

    def save_processed(self, slug: str, name: str, payload: object) -> Path:
        path = self.repo_processed_dir(slug) / f"{name}.json"
        write_json(path, payload)
        return path

    def load_processed(self, slug: str, name: str) -> object:
        return read_json(self.repo_processed_dir(slug) / f"{name}.json")

    def save_manifest(self, slug: str, payload: object) -> Path:
        return self.save_processed(slug, "manifest", payload)

    def load_manifest(self, slug: str) -> object:
        return self.load_processed(slug, "manifest")

    def set_last_repo(self, slug: str) -> None:
        write_json(self.state_path, {"last_repo": slug})

    def get_last_repo(self) -> str | None:
        if not self.state_path.exists():
            return None
        data = read_json(self.state_path)
        return data.get("last_repo")
