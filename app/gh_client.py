import json
import subprocess
from dataclasses import dataclass
from typing import Any, Optional


class GitHubCliError(RuntimeError):
    pass


@dataclass(frozen=True)
class CommandResult:
    stdout: str
    stderr: str


def run_gh(args: list[str], parse_json: bool = False) -> Any:
    command = ["gh"] + args
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "GitHub CLI command failed"
        raise GitHubCliError(message)
    stdout = result.stdout.strip()
    if parse_json:
        return json.loads(stdout) if stdout else None
    return CommandResult(stdout=stdout, stderr=result.stderr.strip())


def require_auth() -> None:
    run_gh(["auth", "status"])


def create_repo(
    name: str,
    description: str,
    visibility: str,
    clone: bool = False,
) -> str:
    visibility_flag = _visibility_flag(visibility)
    args = ["repo", "create", name, visibility_flag]
    if description:
        args.extend(["--description", description])
    if clone:
        args.append("--clone")
    result = run_gh(args)
    return result.stdout


def create_issue(
    repo: str,
    title: str,
    body: str,
    labels: Optional[list[str]] = None,
    assignee: Optional[str] = None,
) -> str:
    args = ["issue", "create", "--repo", repo, "--title", title, "--body", body]
    for label in labels or []:
        args.extend(["--label", label])
    if assignee:
        args.extend(["--assignee", assignee])
    result = run_gh(args)
    return result.stdout


def list_issues(
    repo: str,
    state: str = "open",
    limit: int = 30,
    labels: Optional[list[str]] = None,
) -> list[dict[str, Any]]:
    args = [
        "issue",
        "list",
        "--repo",
        repo,
        "--state",
        state,
        "--limit",
        str(limit),
        "--json",
        "number,title,state,labels,assignees,url",
    ]
    for label in labels or []:
        args.extend(["--label", label])
    return run_gh(args, parse_json=True)


def view_issue(repo: str, number: int) -> dict[str, Any]:
    return run_gh(
        [
            "issue",
            "view",
            str(number),
            "--repo",
            repo,
            "--json",
            "number,title,body,state,labels,url",
        ],
        parse_json=True,
    )


def edit_issue_body(repo: str, number: int, body: str) -> str:
    result = run_gh(["issue", "edit", str(number), "--repo", repo, "--body", body])
    return result.stdout


def add_issue_labels(repo: str, number: int, labels: list[str]) -> str:
    if not labels:
        return ""
    args = ["issue", "edit", str(number), "--repo", repo]
    for label in labels:
        args.extend(["--add-label", label])
    result = run_gh(args)
    return result.stdout


def remove_issue_labels(repo: str, number: int, labels: list[str]) -> str:
    if not labels:
        return ""
    args = ["issue", "edit", str(number), "--repo", repo]
    for label in labels:
        args.extend(["--remove-label", label])
    result = run_gh(args)
    return result.stdout


def close_issue(repo: str, number: int, comment: str = "") -> str:
    args = ["issue", "close", str(number), "--repo", repo]
    if comment:
        args.extend(["--comment", comment])
    result = run_gh(args)
    return result.stdout


def reopen_issue(repo: str, number: int, comment: str = "") -> str:
    args = ["issue", "reopen", str(number), "--repo", repo]
    if comment:
        args.extend(["--comment", comment])
    result = run_gh(args)
    return result.stdout


def view_repo(repo: str) -> dict[str, Any]:
    return run_gh(
        [
            "repo",
            "view",
            repo,
            "--json",
            "name,nameWithOwner,description,visibility,url,defaultBranchRef",
        ],
        parse_json=True,
    )


def create_label(repo: str, name: str, color: str, description: str = "") -> None:
    args = ["label", "create", name, "--repo", repo, "--color", color]
    if description:
        args.extend(["--description", description])
    try:
        run_gh(args)
    except GitHubCliError as exc:
        if "already exists" not in str(exc).lower():
            raise


def create_pull_request(
    repo: str,
    title: str,
    body: str,
    base: str = "",
    draft: bool = False,
) -> str:
    args = ["pr", "create", "--repo", repo, "--title", title, "--body", body]
    if base:
        args.extend(["--base", base])
    if draft:
        args.append("--draft")
    result = run_gh(args)
    return result.stdout


def merge_pull_request(repo: str, number: int, method: str = "squash", delete_branch: bool = True) -> str:
    if method not in {"merge", "squash", "rebase"}:
        raise ValueError("method must be merge, squash, or rebase")
    args = ["pr", "merge", str(number), "--repo", repo, f"--{method}"]
    if delete_branch:
        args.append("--delete-branch")
    result = run_gh(args)
    return result.stdout


def _visibility_flag(visibility: str) -> str:
    normalized = visibility.lower()
    if normalized not in {"public", "private", "internal"}:
        raise ValueError("visibility must be public, private, or internal")
    return f"--{normalized}"
