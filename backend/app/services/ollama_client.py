import os

import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")


def ollama_reason(prompt: str, model: str | None = None) -> str | None:
    try:
        response = requests.post(
            f"{OLLAMA_URL.rstrip('/')}/api/generate",
            json={"model": model or OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=8,
        )
        response.raise_for_status()
        return response.json().get("response")
    except requests.RequestException:
        return None
