import json
from typing import Any

from app.config import Settings
from app.ollama_client import generate_text


def plan_github_issues(settings: Settings, repo: str, goal: str) -> list[dict[str, Any]]:
    prompt = f"""
You are an engineering project manager that writes GitHub issues.

Create a practical implementation plan for the repository below.
Return strict JSON only. Do not include markdown or commentary.

JSON shape:
[
  {{
    "title": "Issue title",
    "body": "Issue body with acceptance criteria",
    "labels": ["enhancement"]
  }}
]

Rules:
- Create 5 to 10 issues.
- Keep titles specific and action-oriented.
- Body must include context, implementation notes, and acceptance criteria.
- Use labels from this set only: enhancement, bug, documentation, refactor, test, chore.

Repository: {repo}
Goal: {goal}
"""
    response = generate_text(settings, prompt)
    return _normalize_issues(_parse_json_array(response))


def plan_epic(settings: Settings, repo: str, idea: str) -> dict[str, Any]:
    prompt = f"""
You are an engineering project manager that writes GitHub epics and issues.

Turn the idea below into one epic and 5 to 10 implementation issues.
Return strict JSON only. Do not include markdown or commentary.

JSON shape:
{{
  "epic": {{
    "title": "Epic title",
    "body": "Epic body with goal, scope, and success criteria"
  }},
  "issues": [
    {{
      "title": "Issue title",
      "body": "Issue body with context, implementation notes, and acceptance criteria",
      "labels": ["enhancement"]
    }}
  ]
}}

Rules:
- Keep every issue specific and independently actionable.
- Body must include acceptance criteria.
- Use labels from this set only: enhancement, bug, documentation, refactor, test, chore.

Repository: {repo}
Idea: {idea}
"""
    response = generate_text(settings, prompt)
    parsed = _parse_json_object(response)
    epic = parsed.get("epic", {})
    issues = parsed.get("issues", [])
    return {
        "epic": {
            "title": str(epic.get("title", "Project epic")).strip(),
            "body": str(epic.get("body", idea)).strip(),
        },
        "issues": _normalize_issues(issues if isinstance(issues, list) else []),
    }


def _parse_json_array(text: str) -> list[Any]:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("[")
        end = text.rfind("]")
        if start == -1 or end == -1 or end <= start:
            return []
        try:
            parsed = json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return []
    return parsed if isinstance(parsed, list) else []


def _parse_json_object(text: str) -> dict[str, Any]:
    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start == -1 or end == -1 or end <= start:
            return {}
        try:
            parsed = json.loads(text[start : end + 1])
        except json.JSONDecodeError:
            return {}
    return parsed if isinstance(parsed, dict) else {}


def _normalize_issues(items: list[Any]) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    allowed_labels = {"enhancement", "bug", "documentation", "refactor", "test", "chore"}
    for item in items:
        if not isinstance(item, dict) or not item.get("title"):
            continue
        labels = item.get("labels", [])
        if not isinstance(labels, list):
            labels = []
        normalized_labels = [str(label) for label in labels if str(label) in allowed_labels]
        issues.append(
            {
                "title": str(item["title"]).strip(),
                "body": str(item.get("body", "")).strip(),
                "labels": normalized_labels,
            }
        )
    return issues
