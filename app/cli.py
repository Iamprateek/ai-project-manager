import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from app.ai_planner import plan_github_issues
from app.config import get_settings
from app.gh_client import (
    GitHubCliError,
    close_issue,
    create_pull_request,
    create_issue,
    create_repo,
    list_issues,
    merge_pull_request,
    protect_branch,
    reopen_issue,
    require_auth,
    view_repo,
    view_issue,
)
from app.git_client import GitCliError, commit_changes, push_current_branch
from app.ollama_client import OllamaError
from app.workflow import (
    create_epic_from_idea,
    ensure_pr_ready_to_merge,
    ensure_workflow_labels,
    start_issue,
)


def main(argv: Optional[list[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    settings = get_settings()

    try:
        if args.command == "auth-check":
            require_auth()
            print("GitHub CLI is authenticated.")
        elif args.command == "repo-create":
            output = create_repo(
                name=args.name,
                description=args.description,
                visibility=args.visibility or settings.default_github_visibility,
                clone=args.clone,
            )
            print(output or f"Created repository {args.name}")
        elif args.command == "repo-view":
            print(json.dumps(view_repo(args.repo), indent=2))
        elif args.command == "issue-create":
            labels = _split_csv(args.labels)
            print(create_issue(args.repo, args.title, args.body, labels, args.assignee))
        elif args.command == "issue-list":
            print(json.dumps(list_issues(args.repo, args.state, args.limit, _split_csv(args.labels)), indent=2))
        elif args.command == "issue-close":
            print(close_issue(args.repo, args.number, args.comment))
        elif args.command == "issue-open":
            print(reopen_issue(args.repo, args.number, args.comment))
        elif args.command == "setup-labels":
            ensure_workflow_labels(args.repo)
            print(f"Workflow labels are ready in {args.repo}.")
        elif args.command == "repo-protect":
            protect_branch(
                args.repo,
                args.branch,
                args.reviews,
                _split_csv(args.checks),
                not args.allow_admin_bypass,
            )
            print(f"Branch protection applied to {args.branch} in {args.repo}.")
        elif args.command == "idea":
            idea = _read_goal(args.idea, args.idea_file)
            result = create_epic_from_idea(settings, args.repo, idea)
            print(json.dumps(result, indent=2))
        elif args.command == "backlog":
            print(json.dumps(list_issues(args.repo, "open", args.limit, ["backlog"]), indent=2))
        elif args.command == "start":
            branch = start_issue(args.repo, args.issue, args.branch_prefix)
            print(f"Started issue #{args.issue} on branch {branch}")
        elif args.command == "commit":
            print(commit_changes(args.message, not args.no_add))
        elif args.command == "push":
            print(push_current_branch(not args.no_upstream))
        elif args.command == "pr-create":
            issue = view_issue(args.repo, args.issue)
            title = args.title or issue["title"]
            body = args.body or f"Closes #{args.issue}"
            print(create_pull_request(args.repo, title, body, args.base, args.draft))
        elif args.command == "pr-merge":
            if not args.skip_checks:
                ensure_pr_ready_to_merge(args.repo, args.number, args.reviews)
            print(merge_pull_request(args.repo, args.number, args.method, not args.keep_branch))
        elif args.command == "plan":
            goal = _read_goal(args.goal, args.goal_file)
            issues = plan_github_issues(settings, args.repo, goal)
            if args.create:
                for issue in issues:
                    url = create_issue(args.repo, issue["title"], issue["body"], issue["labels"])
                    print(url)
            else:
                print(json.dumps(issues, indent=2))
        else:
            parser.print_help()
            return 1
    except (GitHubCliError, GitCliError, OllamaError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ai-project-manager",
        description="AI-assisted GitHub repo and issue automation using gh and local Ollama.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("auth-check", help="Check GitHub CLI authentication.")

    repo_create = subparsers.add_parser("repo-create", help="Create a GitHub repository.")
    repo_create.add_argument("name", help="Repository name, for example owner/repo or repo.")
    repo_create.add_argument("--description", default="", help="Repository description.")
    repo_create.add_argument("--visibility", choices=["public", "private", "internal"])
    repo_create.add_argument("--clone", action="store_true", help="Clone after creating.")

    repo_view = subparsers.add_parser("repo-view", help="View repository metadata.")
    repo_view.add_argument("--repo", required=True, help="Repository in owner/name format.")

    issue_create = subparsers.add_parser("issue-create", help="Create a GitHub issue.")
    issue_create.add_argument("--repo", required=True, help="Repository in owner/name format.")
    issue_create.add_argument("--title", required=True)
    issue_create.add_argument("--body", default="")
    issue_create.add_argument("--labels", default="", help="Comma-separated labels.")
    issue_create.add_argument("--assignee", default="")

    issue_list = subparsers.add_parser("issue-list", help="List GitHub issues.")
    issue_list.add_argument("--repo", required=True, help="Repository in owner/name format.")
    issue_list.add_argument("--state", choices=["open", "closed", "all"], default="open")
    issue_list.add_argument("--limit", type=int, default=30)
    issue_list.add_argument("--labels", default="", help="Comma-separated labels.")

    issue_close = subparsers.add_parser("issue-close", help="Close a GitHub issue.")
    issue_close.add_argument("--repo", required=True, help="Repository in owner/name format.")
    issue_close.add_argument("number", type=int)
    issue_close.add_argument("--comment", default="")

    issue_open = subparsers.add_parser("issue-open", help="Reopen a GitHub issue.")
    issue_open.add_argument("--repo", required=True, help="Repository in owner/name format.")
    issue_open.add_argument("number", type=int)
    issue_open.add_argument("--comment", default="")

    setup_labels = subparsers.add_parser("setup-labels", help="Create workflow labels.")
    setup_labels.add_argument("--repo", required=True, help="Repository in owner/name format.")

    repo_protect = subparsers.add_parser(
        "repo-protect", help="Apply production branch protection rules to a branch."
    )
    repo_protect.add_argument("--repo", required=True, help="Repository in owner/name format.")
    repo_protect.add_argument("--branch", default="main", help="Branch to protect.")
    repo_protect.add_argument("--reviews", type=int, default=1, help="Required approving reviews.")
    repo_protect.add_argument(
        "--checks", default="ci", help="Comma-separated required status check names."
    )
    repo_protect.add_argument(
        "--allow-admin-bypass",
        action="store_true",
        help="Let repo admins merge without meeting the rules above.",
    )

    idea = subparsers.add_parser("idea", help="Create an epic and backlog issues from an idea.")
    idea.add_argument("--repo", required=True, help="Repository in owner/name format.")
    idea_group = idea.add_mutually_exclusive_group(required=True)
    idea_group.add_argument("--idea", help="Idea to turn into an epic and issues.")
    idea_group.add_argument("--idea-file", help="Path to a file containing the idea.")

    backlog = subparsers.add_parser("backlog", help="List open backlog issues.")
    backlog.add_argument("--repo", required=True, help="Repository in owner/name format.")
    backlog.add_argument("--limit", type=int, default=30)

    start = subparsers.add_parser("start", help="Start an issue: create branch and mark in progress.")
    start.add_argument("--repo", required=True, help="Repository in owner/name format.")
    start.add_argument("issue", type=int, help="Issue number to start.")
    start.add_argument("--branch-prefix", default="feature", help="Branch prefix.")

    commit = subparsers.add_parser("commit", help="Commit local coding work.")
    commit.add_argument("-m", "--message", required=True, help="Commit message.")
    commit.add_argument("--no-add", action="store_true", help="Do not run git add -A before commit.")

    push = subparsers.add_parser("push", help="Push the current branch.")
    push.add_argument("--no-upstream", action="store_true", help="Do not set upstream origin branch.")

    pr_create = subparsers.add_parser("pr-create", help="Create a PR that closes an issue.")
    pr_create.add_argument("--repo", required=True, help="Repository in owner/name format.")
    pr_create.add_argument("--issue", required=True, type=int, help="Issue number closed by the PR.")
    pr_create.add_argument("--title", default="", help="Override PR title.")
    pr_create.add_argument("--body", default="", help="Override PR body.")
    pr_create.add_argument("--base", default="", help="Base branch.")
    pr_create.add_argument("--draft", action="store_true", help="Create a draft PR.")

    pr_merge = subparsers.add_parser("pr-merge", help="Merge a PR.")
    pr_merge.add_argument("--repo", required=True, help="Repository in owner/name format.")
    pr_merge.add_argument("number", type=int, help="PR number.")
    pr_merge.add_argument("--method", choices=["merge", "squash", "rebase"], default="squash")
    pr_merge.add_argument("--keep-branch", action="store_true", help="Do not delete branch after merge.")
    pr_merge.add_argument(
        "--reviews", type=int, default=1, help="Approving reviews required before merge."
    )
    pr_merge.add_argument(
        "--skip-checks",
        action="store_true",
        help="Skip the client-side review/CI gate (GitHub branch protection still applies if configured).",
    )

    plan = subparsers.add_parser("plan", help="Use Ollama to generate GitHub issues.")
    plan.add_argument("--repo", required=True, help="Repository in owner/name format.")
    goal_group = plan.add_mutually_exclusive_group(required=True)
    goal_group.add_argument("--goal", help="Project goal to break into GitHub issues.")
    goal_group.add_argument("--goal-file", help="Path to a file containing the project goal.")
    plan.add_argument("--create", action="store_true", help="Create planned issues on GitHub.")

    return parser


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def _read_goal(goal: Optional[str], goal_file: Optional[str]) -> str:
    if goal is not None:
        return goal
    if goal_file is None:
        raise ValueError("goal or goal_file is required")
    return Path(goal_file).read_text(encoding="utf-8").strip()


if __name__ == "__main__":
    raise SystemExit(main())
