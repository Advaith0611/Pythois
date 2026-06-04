from canvas_protocol import *
from groq import Groq
import os
from dotenv import load_dotenv

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


def canvas_input_for_text_model(canvas_input: dict) -> dict:
    screenshot = canvas_input.get("screenshot")
    if not screenshot:
        return canvas_input

    return {
        **canvas_input,
        "screenshot": {
            "width": screenshot.get("width"),
            "height": screenshot.get("height"),
            "available": bool(screenshot.get("dataUrl")),
            "dataUrlBytes": len(screenshot.get("dataUrl", "")),
            "note": "Screenshot data URL omitted from the text prompt.",
        },
    }

def model(canvas_input: dict):
    client = Groq()
    text_model_input = canvas_input_for_text_model(canvas_input)
    completion = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": f"Here is some information about various things that are on a canvas drawing: {text_model_input} \n\n Summarize it in 20 words or less. Return only the summary, no other text. Make sure the summary talks mainly about the users intent what the user wants to signify by these drawings."
            }
        ],
        temperature=0.6,
        max_completion_tokens=1024,
        top_p=0.95,
        stream=False
    )

    return completion.choices[0].message.content


def read_everything_on_canvas(
    canvas_state: CanvasState,
    visual_context: CanvasVisualContext | None = None,
) -> dict:
    objects = canvas_state.get("objects", [])
    selected = selected_objects(canvas_state)
    file_objects = files(canvas_state)
    webpage_objects = webpages(canvas_state)
    viewport = canvas_state.get("viewport", {})
    metadata = canvas_state.get("metadata", {})

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
            }
            for obj in file_objects
        ],
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

def run(
    canvas_state,
    visual_context=None,
    prompt=None,
    request=None,
):
    visual_context = ensure_visual_context(canvas_state, visual_context)
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
    return action_batch(actions)
