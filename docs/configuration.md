# Configuration

## 1. Configuration Source

The CLI reads configuration from:

- Shell environment variables.
- A local `.env` file.
- Built-in defaults.

Shell environment variables take priority over `.env` values.

## 2. Supported Settings

| Variable | Default | Purpose |
| --- | --- | --- |
| `DEFAULT_GITHUB_VISIBILITY` | `public` | Default visibility for `repo-create` when `--visibility` is omitted. |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Local Ollama API URL. |
| `OLLAMA_MODEL` | `llama3.1:8b` | Model used by `plan`. |
| `OLLAMA_TIMEOUT_SECONDS` | `120` | Timeout for local AI generation. |

## 3. Example `.env`

```text
DEFAULT_GITHUB_VISIBILITY=public
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=qwen2.5:7b
OLLAMA_TIMEOUT_SECONDS=180
```

## 4. Model Choice

Recommended models:

- `llama3.1:8b`: balanced default.
- `mistral:7b`: lighter local planning.
- `qwen2.5:7b`: strong structured output.
- `qwen3:8b`: newer, strong structured output.

Check installed models:

```bash
ollama list
```
