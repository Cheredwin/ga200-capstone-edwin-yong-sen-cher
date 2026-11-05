"""Load ANTHROPIC_API_KEY from a local .env file using the standard library only. The key is never printed."""
import os
from pathlib import Path

KEY_NAME = "ANTHROPIC_API_KEY"


def load_api_key(path):
    """Set ANTHROPIC_API_KEY from the file at path if it is not already set. Return True if a key is configured."""
    path = Path(path)
    if not os.environ.get(KEY_NAME) and path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            name, value = line.split("=", 1)
            if name.strip() != KEY_NAME:
                continue
            value = value.strip().strip('"').strip("'")
            if value:
                os.environ[KEY_NAME] = value
            break
    return bool(os.environ.get(KEY_NAME))
