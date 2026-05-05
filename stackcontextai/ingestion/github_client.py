from __future__ import annotations

import time
from typing import Any

import requests


class GitHubClient:
    def __init__(self, token: str | None = None) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "StackContextAI-MVP",
            }
        )
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def paginate(self, endpoint: str, params: dict[str, Any] | None = None, limit: int = 200) -> list[dict[str, Any]]:
        params = {"per_page": 100, **(params or {})}
        page = 1
        items: list[dict[str, Any]] = []

        while len(items) < limit:
            current_params = {**params, "page": page}
            response = self.session.get(endpoint, params=current_params, timeout=30)
            response.raise_for_status()
            batch = response.json()
            if not isinstance(batch, list) or not batch:
                break

            items.extend(batch)
            if len(batch) < current_params["per_page"]:
                break

            page += 1
            time.sleep(0.1)

        return items[:limit]

    def get_json(self, url: str) -> Any:
        response = self.session.get(url, timeout=30)
        response.raise_for_status()
        return response.json()
