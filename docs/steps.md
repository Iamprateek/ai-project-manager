# Steps

## 1. Install Prerequisites

Install GitHub CLI and Ollama:

```bash
brew install gh ollama
```

Python 3.9 or newer is required.

## 2. Authenticate GitHub

Run:

```bash
gh auth login
```

Then verify from this project:

```bash
python3 -m app.cli auth-check
```

## 3. Start Ollama

Ollama usually runs in the background after installation.

If needed:

```bash
ollama serve
```

## 4. Pull a Local Model

Recommended:

```bash
ollama pull llama3.1:8b
```

Other options:

```bash
ollama pull mistral:7b
ollama pull qwen2.5:7b
```

## 5. Configure Defaults

Copy the example config:

```bash
cp .env.example .env
```

Edit `.env` if needed:

```text
DEFAULT_GITHUB_VISIBILITY=public
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_TIMEOUT_SECONDS=120
```

## 6. Create a Repository

```bash
python3 -m app.cli repo-create Iamprateek/example-project \
  --description "Example repo created by AI Project Manager" \
  --visibility public
```

## 7. Create a Ticket Manually

```bash
python3 -m app.cli issue-create \
  --repo Iamprateek/example-project \
  --title "Set up CLI entrypoint" \
  --body "Create the first command line entrypoint." \
  --labels enhancement
```

## 8. Generate Epic and Tickets with AI

Create one epic and child backlog issues:

```bash
python3 -m app.cli idea \
  --repo Iamprateek/example-project \
  --idea "Build a CLI that automates GitHub repo and ticket management"
```

The command creates:

- One `epic` issue.
- Multiple child issues.
- `backlog` labels.
- A checklist in the epic body.

## 9. View Backlog

```bash
python3 -m app.cli backlog --repo Iamprateek/example-project
```

## 10. Start an Issue

```bash
python3 -m app.cli start --repo Iamprateek/example-project 42
```

This creates a branch like:

```text
feature/42-add-kafka-consumer
```

It also moves the issue from `backlog` to `in-progress`.

## 11. Code, Commit, and Push

After coding:

```bash
python3 -m app.cli commit -m "Add Kafka consumer"
python3 -m app.cli push
```

## 12. Create and Merge PR

Create a PR that closes the issue:

```bash
python3 -m app.cli pr-create --repo Iamprateek/example-project --issue 42
```

Merge it:

```bash
python3 -m app.cli pr-merge --repo Iamprateek/example-project 12
```

Because the PR body includes `Closes #42`, GitHub closes the issue automatically after merge.

## 13. Generate Flat Tickets with AI

Preview planned issues:

```bash
python3 -m app.cli plan \
  --repo Iamprateek/example-project \
  --goal "Build a CLI that automates GitHub repo and ticket management"
```

Create the planned issues:

```bash
python3 -m app.cli plan \
  --repo Iamprateek/example-project \
  --goal "Build a CLI that automates GitHub repo and ticket management" \
  --create
```

## 14. Manage Tickets

List issues:

```bash
python3 -m app.cli issue-list --repo Iamprateek/example-project
```

Close issue `1`:

```bash
python3 -m app.cli issue-close --repo Iamprateek/example-project 1 --comment "Done"
```

Reopen issue `1`:

```bash
python3 -m app.cli issue-open --repo Iamprateek/example-project 1 --comment "Reopening for more work"
```
