import json
import sys
import time
from urllib import error, request

from app.config import Settings


class OllamaError(RuntimeError):
    pass


def generate_text(settings: Settings, prompt: str) -> str:
    url = f"{settings.ollama_base_url.rstrip('/')}/api/generate"
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": True,
    }
    encoded_payload = json.dumps(payload).encode("utf-8")
    http_request = request.Request(
        url,
        data=encoded_payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    print(
        f"Calling Ollama model '{settings.ollama_model}' at {settings.ollama_base_url} "
        f"(timeout {settings.ollama_timeout_seconds}s)...",
        file=sys.stderr,
    )
    started = time.monotonic()
    last_update = started
    chunks: list[str] = []

    try:
        with request.urlopen(http_request, timeout=settings.ollama_timeout_seconds) as response:
            for raw_line in response:
                line = raw_line.decode("utf-8").strip()
                if not line:
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                chunks.append(event.get("response", ""))

                now = time.monotonic()
                if now - last_update >= 3:
                    print(
                        f"  ...still generating ({int(now - started)}s elapsed, "
                        f"{len(''.join(chunks))} chars so far)",
                        file=sys.stderr,
                    )
                    last_update = now

                if event.get("done"):
                    break
    except error.URLError as exc:
        raise OllamaError(f"Could not reach Ollama at {settings.ollama_base_url}") from exc

    generated = "".join(chunks).strip()
    print(f"Ollama responded in {int(time.monotonic() - started)}s.", file=sys.stderr)
    if not generated:
        raise OllamaError("Ollama response did not include generated text")
    return generated

