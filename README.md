# AI Project Manager

This is going to be an AI product manager.

AI-assisted GitHub project automation from the command line.

This tool uses:

- GitHub CLI (`gh`) for repository and issue operations.
- Ollama for local, free, open-source AI planning.
- Python standard library only for the app code.

It does not use OpenAI, Claude, Next.js, a web dashboard, or a local task database.

## What It Can Do

- Check GitHub CLI authentication.
- Create GitHub repositories.
- View repository metadata.
- Create workflow labels.
- Turn an idea into one GitHub epic and child issues with Ollama.
- Create GitHub issues.
- List open, closed, or all issues.
- List backlog issues.
- Start an issue by creating a branch and marking it in progress.
- Commit local code changes.
- Push the current branch.
- Create a pull request that closes an issue.
- Merge pull requests.
- Close issues.
- Reopen issues.

## Target Workflow

```text
Idea
  -> AI creates Epic
  -> AI creates Issues
  -> Backlog
  -> Start Issue
  -> create branch feature/42-add-kafka-consumer
  -> Issue marked In Progress
  -> Coding
  -> Commit
  -> Push
  -> Create PR with "Closes #42"
  -> CI must pass, 1 approving review required (main is protected)
  -> Merge
  -> Issue closes automatically
```

## Production Git Workflow

- `setup-labels` creates the workflow labels used throughout.
- `repo-protect` locks down `main` on GitHub's side: PR-only merges, required CI check, required review, no force pushes, no branch deletion. GitHub Free only offers this for **public** repositories — private repos on Free get a clear error explaining that instead of a raw API failure.
- `pr-merge` re-checks review approval and CI status itself before merging, regardless of plan or visibility. This gives you the same guarantees as branch protection on a private Free-plan repo, where GitHub's server-side enforcement isn't available. Use `--skip-checks` to bypass it.
- `.github/workflows/ci.yml` runs a compile + smoke test on every PR and push to `main`; this is the `ci` check branch protection requires.
- `.github/pull_request_template.md` and `.github/ISSUE_TEMPLATE/` give PRs and manual issues a consistent shape. Issue creation itself stays AI-managed via `idea` / `plan`.

## Quick Start

Install prerequisites:

```bash
brew install gh ollama
```

Authenticate GitHub CLI:

```bash
gh auth login
```

Pull an Ollama model:

```bash
ollama pull llama3.1:8b
```

Check auth:

```bash
python3 -m app.cli auth-check
```

Create an epic and backlog issues from an idea:

```bash
python3 -m app.cli idea \
  --repo Iamprateek/ai-project-manager \
  --idea "Build a CLI that creates repos and manages GitHub tickets using Ollama"
```

Start issue `42`:

```bash
python3 -m app.cli start --repo Iamprateek/ai-project-manager 42
```

Commit, push, and open a PR:

```bash
python3 -m app.cli commit -m "Add Kafka consumer"
python3 -m app.cli push
python3 -m app.cli pr-create --repo Iamprateek/ai-project-manager --issue 42
```

## Documentation

- [What was done](docs/what-was-done.md)
- [Steps](docs/steps.md)
- [Configuration](docs/configuration.md)
- [Architecture](docs/architecture.md)
- [Commands](docs/commands.md)
