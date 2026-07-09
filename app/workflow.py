import re
from typing import Any

from app.ai_planner import plan_epic
from app.config import Settings
from app.gh_client import (
    add_issue_labels,
    close_issue,
    create_issue,
    create_label,
    edit_issue_body,
    remove_issue_labels,
    view_issue,
    view_pull_request,
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


_PASSING_STATES = {"SUCCESS", "NEUTRAL", "SKIPPED"}


def ensure_pr_ready_to_merge(
    repo: str,
    number: int,
    required_reviews: int = 1,
    require_checks: bool = True,
) -> None:
    """Client-side substitute for GitHub branch protection.

    GitHub Free does not offer branch protection rules on private
    repositories, so this re-checks the same rules (review approval, CI
    passing) directly against the PR before allowing a merge.
    """
    pr = view_pull_request(repo, number)
    problems = []

    if required_reviews > 0 and pr.get("reviewDecision") != "APPROVED":
        problems.append(
            f"needs an approving review (status: {pr.get('reviewDecision') or 'REVIEW_REQUIRED'})"
        )

    if require_checks:
        checks = pr.get("statusCheckRollup") or []
        if not checks:
            problems.append("no CI checks have reported yet")
        else:
            failing = [
                check.get("name") or check.get("context") or "unknown check"
                for check in checks
                if (check.get("conclusion") or check.get("state") or "").upper() not in _PASSING_STATES
            ]
            if failing:
                problems.append(f"CI checks not passing: {', '.join(failing)}")

    if problems:
        raise ValueError(f"PR #{number} is not ready to merge: " + "; ".join(problems))


_CHECKLIST_ITEM = re.compile(r"^- \[([ xX])\] #(\d+)(.*)$", re.MULTILINE)
_PARENT_EPIC = re.compile(r"Part of epic #(\d+)", re.IGNORECASE)


def close_ticket(repo: str, number: int, comment: str = "", force: bool = False) -> str:
    """Close an issue, keeping epics and their child issues in sync.

    Closing an epic while it still has open child issues silently orphans
    those children, so this refuses unless every child is already closed
    (or --force is used). Closing a child issue instead checks its box off
    on the parent epic's checklist.
    """
    issue = view_issue(repo, number)
    labels = {label.get("name", "") for label in issue.get("labels", [])}

    if "epic" in labels and not force:
        child_numbers = [int(match.group(2)) for match in _CHECKLIST_ITEM.finditer(issue.get("body", ""))]
        open_children = [
            child_number
            for child_number in child_numbers
            if view_issue(repo, child_number).get("state", "").upper() == "OPEN"
        ]
        if open_children:
            joined = ", ".join(f"#{n}" for n in open_children)
            raise ValueError(
                f"Epic #{number} still has open child issues: {joined}. "
                "Close those first, or pass --force to close the epic anyway."
            )

    result = close_issue(repo, number, comment)

    parent_match = _PARENT_EPIC.search(issue.get("body", ""))
    if parent_match:
        epic_number = int(parent_match.group(1))
        epic = view_issue(repo, epic_number)
        updated_body = _CHECKLIST_ITEM.sub(
            lambda match: f"- [x] #{match.group(2)}{match.group(3)}"
            if int(match.group(2)) == number
            else match.group(0),
            epic.get("body", ""),
        )
        if updated_body != epic.get("body", ""):
            edit_issue_body(repo, epic_number, updated_body)

    return result


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

