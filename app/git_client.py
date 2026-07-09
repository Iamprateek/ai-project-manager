import re
import subprocess


class GitCliError(RuntimeError):
    pass


def run_git(args: list[str]) -> str:
    result = subprocess.run(["git"] + args, capture_output=True, text=True)
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "Git command failed"
        raise GitCliError(message)
    return result.stdout.strip()


def create_branch(branch_name: str) -> str:
    return run_git(["checkout", "-b", branch_name])


def current_branch() -> str:
    return run_git(["branch", "--show-current"])


def commit_changes(message: str, add_all: bool = True) -> str:
    if add_all:
        run_git(["add", "-A"])
    return run_git(["commit", "-m", message])


def push_current_branch(set_upstream: bool = True) -> str:
    branch = current_branch()
    if not branch:
        raise GitCliError("Could not determine current branch")
    args = ["push"]
    if set_upstream:
        args.extend(["-u", "origin", branch])
    return run_git(args)


def issue_branch_name(issue_number: int, issue_title: str, prefix: str = "feature") -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", issue_title.lower()).strip("-")
    slug = slug[:48].strip("-") or "issue"
    return f"{prefix}/{issue_number}-{slug}"

