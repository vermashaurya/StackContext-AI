from __future__ import annotations

from stackcontextai.utils import clean_whitespace


def normalize_record_text(record: dict) -> str:
    parts = [
        f"Type: {record['source_type']}",
        f"Title: {record['title']}",
        f"Description: {record['description']}",
    ]
    comments = [clean_whitespace(comment) for comment in record.get("comments", []) if clean_whitespace(comment)]
    if comments:
        parts.append("Comments:\n" + "\n\n".join(comments))
    return clean_whitespace("\n\n".join(parts))
