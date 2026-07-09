from dataclasses import dataclass
import os
from pathlib import Path


def _load_dotenv() -> None:
    env_path = Path(".env")
    if not env_path.exists():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith("#") or "=" not in stripped_line:
            continue
        name, value = stripped_line.split("=", 1)
        os.environ.setdefault(name.strip(), value.strip().strip('"').strip("'"))


def _env(name: str, default: str) -> str:
    value = os.getenv(name)
    return value if value not in (None, "") else default


def _env_int(name: str, default: int) -> int:
    raw_value = _env(name, str(default))
    try:
        return int(raw_value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    default_github_visibility: str
    ollama_base_url: str
    ollama_model: str
    ollama_timeout_seconds: int


def get_settings() -> Settings:
    _load_dotenv()
    return Settings(
        default_github_visibility=_env("DEFAULT_GITHUB_VISIBILITY", "public"),
        ollama_base_url=_env("OLLAMA_BASE_URL", "http://localhost:11434"),
        ollama_model=_env("OLLAMA_MODEL", "llama3.1:8b"),
        ollama_timeout_seconds=_env_int("OLLAMA_TIMEOUT_SECONDS", 120),
    )
