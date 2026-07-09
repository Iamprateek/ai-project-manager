import json
from urllib import error, request

from app.config import Settings


class OllamaError(RuntimeError):
    pass


def generate_text(settings: Settings, prompt: str) -> str:
    url = f"{settings.ollama_base_url.rstrip('/')}/api/generate"
    payload = {
        "model": settings.ollama_model,
        "prompt": prompt,
        "stream": False,
    }
    encoded_payload = json.dumps(payload).encode("utf-8")
    http_request = request.Request(
        url,
        data=encoded_payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(http_request, timeout=settings.ollama_timeout_seconds) as response:
            response_payload = json.loads(response.read().decode("utf-8"))
    except error.URLError as exc:
        raise OllamaError(f"Could not reach Ollama at {settings.ollama_base_url}") from exc
    except json.JSONDecodeError as exc:
        raise OllamaError("Ollama returned an invalid response") from exc

    generated = response_payload.get("response")
    if not isinstance(generated, str):
        raise OllamaError("Ollama response did not include generated text")
    return generated.strip()

