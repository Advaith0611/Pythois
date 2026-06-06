import json
import sys
from pathlib import Path
from typing import Any
from google import genai
from google.genai import types
import json
import os

REPO_ROOT = Path(__file__).resolve().parents[1]
AI_CORE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = REPO_ROOT / "backend"
if str(AI_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(AI_CORE_DIR))
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from canvas_protocol import *
from dotenv import load_dotenv
from groq import Groq

from app.services.file_ingestion import process_canvas_file

load_dotenv()

BLANK_PNG_DATA_URL = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAFgwJ/lR0gWAAAAABJRU5ErkJggg=="
)


def fallback_visual_context(canvas_state: CanvasState) -> CanvasVisualContext:
    viewport = canvas_state.get("viewport", {})
    screen_bounds = viewport.get("screenBounds", {})

    return {
        "schemaVersion": "pythios.canvas.visual.v1",
        "capturedAt": canvas_state.get("capturedAt"),
        "format": "image/png",
        "dataUrl": BLANK_PNG_DATA_URL,
        "width": max(1, round(screen_bounds.get("w", 1))),
        "height": max(1, round(screen_bounds.get("h", 1))),
        "viewportPageBounds": {
            "x": viewport.get("x", 0),
            "y": viewport.get("y", 0),
            "w": screen_bounds.get("w", 1),
            "h": screen_bounds.get("h", 1),
        },
        "notes": ["Generated fallback because no browser visual context was provided."],
    }


def ensure_visual_context(
    canvas_state: CanvasState,
    visual_context: CanvasVisualContext | None = None,
) -> CanvasVisualContext:
    if visual_context and visual_context.get("dataUrl"):
        return visual_context

    return fallback_visual_context(canvas_state)




def model(canvas_input: dict) -> str:
    screenshot = canvas_input.get("screenshot")
    context = {k: v for k, v in canvas_input.items() if k != "screenshot"}

    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"]
    )

    prompt = f"""
You are Pythios.

Your job is to determine the user's intent.

You are given:

1. Structured canvas data.
2. A screenshot of the current whiteboard.

Use BOTH sources of information.

The screenshot helps you understand layout, drawings, sketches, diagrams and visual meaning.

The structured canvas data helps you understand exact text, object metadata, files and webpages.

Combine both sources.

Return ONLY a concise description of what the user is trying to accomplish.

Examples:

"Creating a landing page wireframe for a startup that works on book selling."

"Brainstorming a machine learning architecture for a model that classify's images."

"Designing a dashboard for analytics for a clothing store."

"Planning a software project for a whiteboard app."

Do not explain your reasoning.
Do not list canvas objects.
Return only the user's likely intent.
Be specific list all the information you can see 
Canvas Data:

{json.dumps(context)}
"""

    contents = [prompt]

    if screenshot:
        contents.append(
            types.Part.from_bytes(
                data=screenshot["dataUrl"].split(",", 1)[1],
                mime_type="image/png",
            )
        )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=contents,
        config=types.GenerateContentConfig(
            temperature=0.1,
            max_output_tokens=500,
        ),
    )

    return response.text.strip()

def read_everything_on_canvas(
    canvas_state: CanvasState,
    visual_context: CanvasVisualContext | None = None,
) -> dict[str, Any]:
    objects = canvas_state.get("objects", [])
    selected = selected_objects(canvas_state)
    file_objects = files(canvas_state)
    webpage_objects = webpages(canvas_state)
    viewport = canvas_state.get("viewport", {})
    metadata = canvas_state.get("metadata", {})
    processed_files = [_read_canvas_file(obj) for obj in file_objects]

    return {
        "captured_at": canvas_state.get("capturedAt"),
        "object_count": len(objects),
        "selected_count": len(selected),
        "visible_object_ids": canvas_state.get("visibleObjectIds", []),
        "viewport": viewport,
        "page_id": metadata.get("pageId"),
        "all_objects": [
            {
                "id": obj["id"],
                "source": obj["source"],
                "kind": obj["kind"],
                "type": obj["type"],
                "bounds": obj["bounds"],
                "text": obj.get("text"),
                "title": obj.get("title"),
                "url": obj.get("url"),
                "mimeType": obj.get("mimeType"),
                "size": obj.get("size"),
                "hasDataUrl": bool(obj.get("dataUrl")),
                "metadata": obj.get("metadata", {}),
            }
            for obj in objects
        ],
        "selected_objects": [
            {
                "id": obj["id"],
                "kind": obj["kind"],
                "bounds": obj["bounds"],
                "text": obj.get("text"),
            }
            for obj in selected
        ],
        "files": [
            {
                "id": obj["id"],
                "title": obj.get("title"),
                "mimeType": obj.get("mimeType"),
                "size": obj.get("size"),
                "hasDataUrl": bool(obj.get("dataUrl")),
            }
            for obj in file_objects
        ],
        "processed_files": processed_files,
        "webpages": [
            {
                "id": obj["id"],
                "title": obj.get("title"),
                "url": obj.get("url"),
            }
            for obj in webpage_objects
        ],
        "screenshot": (
            {
                "width": visual_context["width"],
                "height": visual_context["height"],
                "dataUrl": visual_context["dataUrl"],
            }
            if visual_context and visual_context.get("dataUrl")
            else None
        ),
    }


def _read_canvas_file(file_object: dict[str, Any]) -> dict[str, Any]:
    """Read a canvas file object and return model-safe extracted content."""

    processed = process_canvas_file(file_object)
    image_data_url = processed.get("image_data_url")
    text_content = processed.get("text_content")

    return {
        "id": file_object.get("id"),
        "kind": file_object.get("kind"),
        "title": processed["title"] or file_object.get("title") or file_object.get("id"),
        "mime_type": processed["mime_type"] or file_object.get("mimeType"),
        "size": file_object.get("size"),
        "text_content": text_content,
        "text_length": len(text_content) if text_content else 0,
        "has_image_data_url": bool(image_data_url),
        "image_data_url_length": len(image_data_url) if image_data_url else 0,
        "metadata": processed["metadata"],
        "error": processed["error"],
    }


def run(
    canvas_state,
    visual_context=None,
    prompt=None,
    request=None,
):
    visual_context = ensure_visual_context(canvas_state, visual_context)
    canvas_input = read_everything_on_canvas(canvas_state, visual_context)
    actions = [
        create_text(
            x=130,
            y=130,
            width=700,
            text="PYTHIOS",
        ),
        create_text(
            x=130,
            y=180,
            width=700,
            text="SEE • UNDERSTAND • FORESEE",
        ),
        create_text(
            x=130,
            y=240,
            width=650,
            text=(
                "AI features are currently under development.\n\n"
                "Soon Pythios will be able to:\n"
                "• Understand drawings and diagrams\n"
                "• Generate interfaces from sketches\n"
                "• Create and edit shapes automatically\n"
                "• Analyze uploaded files and images\n"
                "• Generate markdown and PDF documents\n"
                "• Create interactive webpage embeds\n"
                "• Transform visual ideas into working applications\n\n"
                "For now, this is a preview of the upcoming AI capabilities."
            ),
            color="black",
        ),
    ]
    summary = (
        f"Objects: {canvas_input['object_count']}\n"
        f"Selected: {canvas_input['selected_count']}\n"
        f"Files: {len(canvas_input['files'])}\n"
        f"Webpages: {len(canvas_input['webpages'])}\n"
        f"Screenshot: {canvas_input['screenshot'] is not None}"
    )
    try:
        answer = model(canvas_input)
    except Exception as error:
        answer = f"Canvas read succeeded. AI summary unavailable: {error}"
    actions.append(
        create_text(
            x=130,
            y=1080,
            width=650,
            text=answer,
        ),
    )
    return action_batch(actions)
