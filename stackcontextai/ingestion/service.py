from __future__ import annotations

from typing import Any

from stackcontextai.models import SourceRecord

from .github_client import GitHubClient


def _login(user: dict[str, Any] | None) -> str:
    return (user or {}).get("login", "unknown")


class GitHubIngestionService:
    def __init__(self, client: GitHubClient) -> None:
        self.client = client

    def ingest(self, owner: str, repo: str) -> dict[str, list[dict[str, Any]]]:
        base = f"https://api.github.com/repos/{owner}/{repo}"
        commits = self.client.paginate(f"{base}/commits", limit=200)
        pulls = self.client.paginate(f"{base}/pulls", params={"state": "all"}, limit=200)
        issues = self.client.paginate(f"{base}/issues", params={"state": "all"}, limit=200)
        issues = [item for item in issues if "pull_request" not in item]

        commit_records = [self._map_commit(owner, repo, commit) for commit in commits]
        pr_records = [self._map_pull_request(pr) for pr in pulls]
        issue_records = [self._map_issue(issue) for issue in issues]

        return {
            "commits": [record.to_dict() for record in commit_records],
            "pull_requests": [record.to_dict() for record in pr_records],
            "issues": [record.to_dict() for record in issue_records],
        }

    def _map_commit(self, owner: str, repo: str, item: dict[str, Any]) -> SourceRecord:
        sha = item["sha"]
        message = item["commit"]["message"]
        lines = message.splitlines()
        title = lines[0]
        description = "\n".join(lines[1:]).strip()
        comments = self.client.get_json(f"https://api.github.com/repos/{owner}/{repo}/commits/{sha}/comments")
        return SourceRecord(
            source_type="commit",
            source_id=sha,
            title=title,
            description=description,
            comments=[comment.get("body", "") for comment in comments],
            author=_login(item.get("author")) if item.get("author") else item["commit"]["author"].get("name", "unknown"),
            timestamp=item["commit"]["author"]["date"],
            url=item["html_url"],
            raw=item,
        )

    def _map_pull_request(self, item: dict[str, Any]) -> SourceRecord:
        issue_comments = self.client.get_json(item["comments_url"])
        review_comments = self.client.get_json(item["review_comments_url"])
        return SourceRecord(
            source_type="pull_request",
            source_id=str(item["number"]),
            title=item["title"],
            description=item.get("body") or "",
            comments=[comment.get("body", "") for comment in [*issue_comments, *review_comments]],
            author=_login(item.get("user")),
            timestamp=item["updated_at"],
            url=item["html_url"],
            raw=item,
        )

    def _map_issue(self, item: dict[str, Any]) -> SourceRecord:
        comments = self.client.get_json(item["comments_url"])
        return SourceRecord(
            source_type="issue",
            source_id=str(item["number"]),
            title=item["title"],
            description=item.get("body") or "",
            comments=[comment.get("body", "") for comment in comments],
            author=_login(item.get("user")),
            timestamp=item["updated_at"],
            url=item["html_url"],
            raw=item,
        )
