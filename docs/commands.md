# Commands

## 1. Auth Check

```bash
python3 -m app.cli auth-check
```

Checks whether `gh` is authenticated.

## 2. Create Repository

```bash
python3 -m app.cli repo-create Iamprateek/example-project \
  --description "Example project" \
  --visibility public
```

Creates a GitHub repository.

## 3. View Repository

```bash
python3 -m app.cli repo-view --repo Iamprateek/example-project
```

Prints repository metadata as JSON.

## 4. Create Issue

```bash
python3 -m app.cli issue-create \
  --repo Iamprateek/example-project \
  --title "Add project README" \
  --body "Document setup and usage." \
  --labels documentation
```

Creates one GitHub issue.

## 5. List Issues

```bash
python3 -m app.cli issue-list --repo Iamprateek/example-project --state open
```

Supported states:

- `open`
- `closed`
- `all`

## 6. Close Issue

```bash
python3 -m app.cli issue-close --repo Iamprateek/example-project 1 --comment "Completed"
```

Closes an issue by number.

## 7. Reopen Issue

```bash
python3 -m app.cli issue-open --repo Iamprateek/example-project 1 --comment "Needs more work"
```

Reopens an issue by number.

## 8. Plan Issues with Ollama

Preview issue JSON:

```bash
python3 -m app.cli plan \
  --repo Iamprateek/example-project \
  --goal "Build a GitHub automation CLI"
```

Create issues directly:

```bash
python3 -m app.cli plan \
  --repo Iamprateek/example-project \
  --goal "Build a GitHub automation CLI" \
  --create
```

Read the goal from a file:

```bash
python3 -m app.cli plan \
  --repo Iamprateek/example-project \
  --goal-file docs/project-goal.md
```

## 9. Set Up Workflow Labels

```bash
python3 -m app.cli setup-labels --repo Iamprateek/example-project
```

Creates labels used by the workflow:

- `epic`
- `backlog`
- `in-progress`
- `enhancement`
- `bug`
- `documentation`
- `refactor`
- `test`
- `chore`

## 10. Create Epic and Issues from Idea

```bash
python3 -m app.cli idea \
  --repo Iamprateek/example-project \
  --idea "Build a GitHub automation CLI that uses Ollama"
```

This command:

- Creates workflow labels.
- Asks Ollama to create one epic and child issues.
- Creates the epic issue with `epic` and `backlog` labels.
- Creates child issues with `backlog` and type labels.
- Updates the epic body with a checklist of child issues.

## 11. List Backlog

```bash
python3 -m app.cli backlog --repo Iamprateek/example-project
```

Lists open issues labeled `backlog`.

## 12. Start Issue

```bash
python3 -m app.cli start --repo Iamprateek/example-project 42
```

This command:

- Reads issue `42`.
- Creates a branch like `feature/42-add-kafka-consumer`.
- Adds the `in-progress` label.
- Removes the `backlog` label.

## 13. Commit Work

```bash
python3 -m app.cli commit -m "Add Kafka consumer"
```

Runs:

```bash
git add -A
git commit -m "Add Kafka consumer"
```

Use `--no-add` to skip `git add -A`.

## 14. Push Branch

```bash
python3 -m app.cli push
```

Pushes the current branch to `origin` and sets upstream.

Use `--no-upstream` to run a normal push.

## 15. Create PR

```bash
python3 -m app.cli pr-create \
  --repo Iamprateek/example-project \
  --issue 42
```

By default, the PR:

- Uses the issue title as the PR title.
- Uses `Closes #42` as the PR body.

GitHub automatically closes the issue after the PR is merged.

## 16. Protect a Branch

```bash
python3 -m app.cli repo-protect --repo Iamprateek/example-project --branch main
```

Applies production-grade branch protection to `main`:

- Requires the PR to be up to date and passing the `ci` status check.
- Requires at least 1 approving review (`--reviews` to change).
- Blocks force pushes and branch deletion.
- Enforces the rules on admins too, unless `--allow-admin-bypass` is passed.

Use `--checks` (comma-separated) if your CI job names differ from `ci`.

## 17. Merge PR

```bash
python3 -m app.cli pr-merge --repo Iamprateek/example-project 12
```

Defaults to squash merge and branch deletion.

Supported merge methods:

- `squash`
- `merge`
- `rebase`

Before merging, this checks the PR's review decision and CI status itself
(`--reviews`, default 1) and refuses to merge if either is missing — this is
a client-side substitute for GitHub branch protection, since GitHub Free does
not offer branch protection on private repositories. Use `--skip-checks` to
bypass it (e.g. when GitHub's own branch protection is already enforcing the
same rules server-side).
