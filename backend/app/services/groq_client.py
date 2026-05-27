import json
import os

import requests
from dotenv import load_dotenv

from app.models.schemas import GeneratedUI

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


def generate_with_groq(intent: dict) -> GeneratedUI | None:
    if not GROQ_API_KEY:
        return None

    prompt = (
        "Convert this spatial canvas intent into the requested JSON schema. "
        "Return only valid JSON with app_type, title, summary, theme, layout, "
        "generated_at, source, and components. Components must use only these "
        "types: metric, chart, table, button, input, list, kanban, timeline, workflow, note.\n\n"
        f"Intent:\n{json.dumps(intent, indent=2)}"
    )

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": GROQ_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.2,
            "response_format": {"type": "json_object"},
        },
        timeout=18,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    payload = json.loads(content)
    payload["source"] = "backend"
    return GeneratedUI.model_validate(payload)
