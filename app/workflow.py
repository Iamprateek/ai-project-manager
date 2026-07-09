import re
from typing import Any

from app.ai_planner import plan_epic
from app.config import Settings
from app.gh_client import (
    add_issue_labels,
    create_issue,
    create_label,
    edit_issue_body,
    remove_issue_labels,
    view_issue,
)
from app.git_client import create_branch, issue_branch_name


WORKFLOW_LABELS = {
    "epic": ("7b3fbc", "Large body of work that groups related issues."),
    "backlog": ("ededed", "Issue is planned but not started."),
    "in-progress": ("f9d0c4", "Issue is actively being worked on."),
    "enhancement": ("a2eeef", "New feature or improvement."),
    "bug": ("d73a4a", "Something is broken."),
    "documentation": ("0075ca", "Documentation work."),
    "refactor": ("c5def5", "Code cleanup without behavior change."),
    "test": ("bfdadc", "Test coverage work."),
    "chore": ("d4c5f9", "Maintenance work."),
}


def ensure_workflow_labels(repo: str) -> None:
    for name, (color, description) in WORKFLOW_LABELS.items():
        create_label(repo, name, color, description)


def create_epic_from_idea(settings: Settings, repo: str, idea: str) -> dict[str, Any]:
    ensure_workflow_labels(repo)
    plan = plan_epic(settings, repo, idea)
    epic = plan["epic"]
    issues = plan["issues"]

    epic_url = create_issue(repo, epic["title"], epic["body"], ["epic", "backlog"])
    epic_number = _issue_number_from_url(epic_url)
    created_issues = []

    for issue in issues:
        body = f"{issue['body']}\n\nPart of epic #{epic_number}."
        labels = sorted(set(issue["labels"] + ["backlog"]))
        issue_url = create_issue(repo, issue["title"], body, labels)
        created_issues.append(
            {
                "number": _issue_number_from_url(issue_url),
                "title": issue["title"],
                "url": issue_url,
            }
        )

    checklist = "\n".join(
        f"- [ ] #{issue['number']} {issue['title']}" for issue in created_issues
    )
    epic_body = f"{epic['body']}\n\n## Child Issues\n\n{checklist}\n"
    edit_issue_body(repo, epic_number, epic_body)

    return {
        "epic": {"number": epic_number, "title": epic["title"], "url": epic_url},
        "issues": created_issues,
    }


def start_issue(repo: str, issue_number: int, branch_prefix: str = "feature") -> str:
    issue = view_issue(repo, issue_number)
    branch = issue_branch_name(issue_number, issue["title"], branch_prefix)
    create_branch(branch)
    add_issue_labels(repo, issue_number, ["in-progress"])
    remove_issue_labels(repo, issue_number, ["backlog"])
    return branch


def _issue_number_from_url(url: str) -> int:
    match = re.search(r"/issues/(\d+)", url)
    if not match:
        raise ValueError(f"Could not parse issue number from URL: {url}")
    return int(match.group(1))

