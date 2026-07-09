# Architecture

## 1. Overview

The project is a command-line GitHub automation tool.

```text
Idea
  -> app.cli
  -> app.workflow
  -> app.ai_planner -> app.ollama_client -> Ollama
  -> app.gh_client -> gh -> GitHub issues
  -> app.git_client -> git branches, commits, pushes
```

## 2. GitHub Layer

`app/gh_client.py` shells out to GitHub CLI.

This avoids maintaining GitHub API authentication code inside the project. Authentication, scopes, and host configuration stay with `gh`.

## 3. AI Layer

`app/ollama_client.py` calls the local Ollama HTTP API.

`app/ai_planner.py` turns a repository goal into issue JSON.

## 4. CLI Layer

`app/cli.py` uses `argparse` and exposes all user-facing commands.

No third-party Python CLI framework is required.

## 5. Workflow Layer

`app/workflow.py` coordinates multi-step GitHub flows:

- Create labels.
- Create epic.
- Create child issues.
- Update epic checklist.
- Start issue work.
- Move issue from backlog to in progress.

## 6. Git Layer

`app/git_client.py` wraps local git commands:

- Create branch.
- Commit changes.
- Push current branch.

## 7. Configuration Layer

`app/config.py` loads `.env` and environment variables.

It controls GitHub defaults and Ollama settings.

## 8. Data Ownership

GitHub owns project data.

The CLI does not keep a local database or task state.
