# Pythios AI Core

Pythios AI Core is a Python-first canvas interaction layer.

It does not render the canvas, control the browser, or run by itself. The user stays in control:

```txt
User edits canvas
       ↓
User clicks Generate
       ↓
Canvas state and visual context are exported
       ↓
AI Core processes state
       ↓
AI Core returns actions
       ↓
Frontend applies actions
       ↓
Canvas updates
```

No AI Core code should auto-generate, auto-modify, auto-insert, or auto-update canvas content while the user is drawing or editing. Future AI behavior must run only inside the Generate request path.

## Overview

The canvas is exposed to Python as three structures:

- `CanvasState`: a snapshot of the current canvas.
- `CanvasVisualContext`: a PNG image of the visible whiteboard area captured when Generate was clicked.
- `CanvasAction`: a dictionary describing one requested canvas change.

Python AI code reads `CanvasState` and, when needed, `CanvasVisualContext`. It decides what should happen and returns a batch of `CanvasAction` dictionaries. The frontend is the only layer that applies those actions to the live canvas.

The Python helper module is:

```python
from canvas_protocol import (
    action_batch,
    create_rectangle,
    create_text,
    selected_objects,
    webpages,
)
```

This is infrastructure only. It does not implement intelligence.

## Generate Entry Point

The backend calls `ai-core/main.py` every time the user clicks Generate. The file must expose a callable `run` function:

```python
def run(canvas_state, visual_context=None, prompt=None, request=None) -> dict:
    ...
```

The backend also supports the shorter form:

```python
def run(canvas_state) -> dict:
    ...
```

Put future AI behavior behind this function. You do not need to modify the frontend when adding new AI capabilities; the frontend only sends the current canvas state to `/generate` and applies the returned action batch.

The actual runtime path is:

```txt
CanvasToolbar Generate button
       ↓
frontend/src/ai/api.ts POST /generate
       ↓
backend/app/api/routes.py
       ↓
backend/app/pipelines/ai_core_runner.py
       ↓
ai-core/main.py run(...)
       ↓
CanvasActionBatch returned to frontend
       ↓
frontend/src/canvas/aiCanvasBridge.ts applies actions
```

## Reading Canvas State

A Generate request may include a `canvasState` payload with this shape:

```python
canvas_state = {
    "schemaVersion": "pythios.canvas.v1",
    "capturedAt": "2026-06-02T10:00:00.000Z",
    "viewport": {
        "x": 0,
        "y": 0,
        "z": 1,
        "screenBounds": {"x": 0, "y": 0, "w": 1280, "h": 720},
    },
    "objects": [],
    "selectedObjectIds": [],
    "visibleObjectIds": [],
    "sceneGraph": {"nodes": [], "flat": []},
    "embeddedObjects": [],
    "metadata": {},
}
```

Each object snapshot may include:

```python
object_snapshot = {
    "id": "shape:box1",
    "source": "tldraw",
    "kind": "rectangle",
    "type": "geo",
    "bounds": {"x": 100, "y": 200, "w": 400, "h": 250},
    "layerIndex": 0,
    "text": "Revenue",
    "style": {"color": "blue", "fill": "semi"},
    "relationships": [],
    "metadata": {},
}
```

Supported object kinds:

- `shape`
- `rectangle`
- `circle`
- `arrow`
- `line`
- `polygon`
- `freehand`
- `text`
- `group`
- `image`
- `pdf`
- `markdown`
- `file`
- `webpage`

### Reading Scene State

```python
from canvas_protocol import CanvasState


def summarize_canvas(state: CanvasState) -> dict:
    return {
        "object_count": len(state["objects"]),
        "selected_count": len(state["selectedObjectIds"]),
        "visible_count": len(state["visibleObjectIds"]),
        "page_id": state.get("metadata", {}).get("pageId"),
    }
```

### Reading Selected Objects

```python
from canvas_protocol import CanvasState, selected_objects


def selected_text(state: CanvasState) -> list[str]:
    return [
        obj.get("text", "")
        for obj in selected_objects(state)
        if obj.get("text")
    ]
```

### Reading Files

```python
from canvas_protocol import CanvasState, files


def file_titles(state: CanvasState) -> list[str]:
    return [
        obj.get("title", obj["id"])
        for obj in files(state)
    ]
```

### Reading Webpage Embeds

```python
from canvas_protocol import CanvasState, webpages


def embedded_urls(state: CanvasState) -> list[str]:
    return [
        obj["url"]
        for obj in webpages(state)
        if obj.get("url")
    ]
```

## Reading Visual Context

A Generate request may also include `visualContext`, which is a PNG snapshot of the visible whiteboard area at the moment the user clicked Generate.

The visual context is not captured continuously. It is not captured while the user draws. It is created only in the Generate path.

```python
visual_context = {
    "schemaVersion": "pythios.canvas.visual.v1",
    "capturedAt": "2026-06-02T10:00:00.000Z",
    "format": "image/png",
    "dataUrl": "data:image/png;base64,...",
    "width": 1280,
    "height": 720,
    "viewportPageBounds": {"x": 0, "y": 0, "w": 1280, "h": 720},
    "notes": [
        "Captured only when the user clicked Generate."
    ],
}
```

Decode the image in Python:

```python
import base64
from pathlib import Path

from canvas_protocol import CanvasVisualContext


def save_visual_context_image(visual: CanvasVisualContext, output_path: str) -> None:
    prefix = "data:image/png;base64,"
    data_url = visual["dataUrl"]

    if not data_url.startswith(prefix):
        raise ValueError("Expected PNG data URL")

    image_bytes = base64.b64decode(data_url[len(prefix):])
    Path(output_path).write_bytes(image_bytes)
```

Use the visual context with structured state:

```python
from canvas_protocol import CanvasState, CanvasVisualContext


def describe_generate_input(
    canvas_state: CanvasState,
    visual_context: CanvasVisualContext | None,
) -> dict:
    return {
        "objects": len(canvas_state["objects"]),
        "selected": len(canvas_state["selectedObjectIds"]),
        "has_screenshot": visual_context is not None,
        "screenshot_size": (
            [visual_context["width"], visual_context["height"]]
            if visual_context
            else None
        ),
    }
```

For future vision-capable AI systems, pass `visualContext["dataUrl"]` as the image input and use `canvasState` as the precise object graph. The image shows what the user was looking at; the state tells the system exactly which objects can be changed.

Webpage embeds are represented by their visible frame metadata in the generated image because browser security prevents reading cross-origin iframe pixels.

## Copy-Paste Input Reader

Use this pattern when you want to read everything currently on the screen/canvas when Generate is clicked.

```python
from canvas_protocol import CanvasState, CanvasVisualContext, files, selected_objects, webpages


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
            if visual_context
            else None
        ),
    }
```

Inside `run(...)`, call it like this:

```python
def run(canvas_state, visual_context=None, prompt=None, request=None):
    canvas_input = read_everything_on_canvas(canvas_state, visual_context)
    ...
```

Do not call `read_everything_on_canvas(canvas_state)` at the top level of `main.py`. `canvas_state` only exists inside `run(...)`.

## Creating Objects

AI Core returns actions. It does not directly edit the canvas.

### Create Shapes

```python
from canvas_protocol import action_batch, create_arrow, create_circle, create_rectangle


def create_basic_shapes() -> dict:
    actions = [
        create_rectangle(
            x=100,
            y=200,
            width=400,
            height=250,
            fill="#3498db",
            text="New panel",
        ),
        create_circle(
            x=560,
            y=220,
            width=160,
            height=160,
            fill="semi",
            color="blue",
        ),
        create_arrow(
            x=500,
            y=300,
            end_x=560,
            end_y=300,
            color="black",
        ),
    ]
    return action_batch(actions)
```

### Create Text

```python
from canvas_protocol import action_batch, create_text


def create_label() -> dict:
    return action_batch([
        create_text(
            x=120,
            y=140,
            width=320,
            text="Quarterly planning",
            color="black",
        )
    ])
```

### Create Images

```python
from canvas_protocol import action_batch, create_image


def create_image_object(data_url: str) -> dict:
    return action_batch([
        create_image(
            title="diagram.png",
            x=120,
            y=160,
            width=360,
            height=260,
            mime_type="image/png",
            data_url=data_url,
            metadata={"source": "ai-core"},
        )
    ])
```

### Create Markdown Files

```python
import base64

from canvas_protocol import action_batch, create_markdown


def create_markdown_file() -> dict:
    markdown = "# Notes\n\nGenerated after the user clicked Generate.\n"
    data_url = "data:text/markdown;base64," + base64.b64encode(markdown.encode()).decode()

    return action_batch([
        create_markdown(
            title="notes.md",
            x=200,
            y=200,
            width=420,
            height=300,
            data_url=data_url,
        )
    ])
```

### Create PDF Files

```python
from canvas_protocol import action_batch, create_pdf


def create_pdf_file(pdf_data_url: str) -> dict:
    return action_batch([
        create_pdf(
            title="report.pdf",
            x=260,
            y=260,
            width=420,
            height=300,
            mime_type="application/pdf",
            data_url=pdf_data_url,
        )
    ])
```

### Create Generic Files

```python
from canvas_protocol import action_batch, create_file


def create_generic_file() -> dict:
    return action_batch([
        create_file(
            title="data.json",
            x=320,
            y=320,
            width=420,
            height=300,
            mime_type="application/json",
            metadata={"purpose": "future-ai-output"},
        )
    ])
```

### Create Webpage Embeds

```python
from canvas_protocol import action_batch, create_webpage


def create_webpage_embed() -> dict:
    return action_batch([
        create_webpage(
            url="https://example.com",
            x=500,
            y=300,
            width=800,
            height=600,
        )
    ])
```

## Complete Output Example

This example reads all canvas input and returns one of every main output type: shapes, text, connectors, image, markdown, PDF, generic file, webpage, and common modification actions.

Paste this into `ai-core/main.py` when you want a complete test fixture:

```python
from __future__ import annotations

import base64
import json
from typing import Any

from canvas_protocol import (
    CanvasState,
    CanvasVisualContext,
    action_batch,
    create_arrow,
    create_circle,
    create_file,
    create_image,
    create_line,
    create_markdown,
    create_pdf,
    create_rectangle,
    create_text,
    create_webpage,
    files,
    move_object,
    relabel_object,
    resize_object,
    selected_objects,
    webpages,
)


def run(
    canvas_state: CanvasState,
    visual_context: CanvasVisualContext | None = None,
    prompt: str | None = None,
    request: dict[str, Any] | None = None,
) -> dict[str, Any]:
    canvas_input = read_everything_on_canvas(canvas_state, visual_context)
    origin = output_origin(canvas_state)
    selected = selected_objects(canvas_state)

    markdown = (
        "# AI Core canvas input\n\n"
        f"- Prompt: {prompt or 'No prompt'}\n"
        f"- Objects: {canvas_input['object_count']}\n"
        f"- Selected: {canvas_input['selected_count']}\n"
        f"- Webpages: {len(canvas_input['webpages'])}\n"
        f"- Files: {len(canvas_input['files'])}\n"
    )
    markdown_data_url = text_data_url(markdown, "text/markdown")

    json_file = json.dumps(canvas_input, indent=2)
    json_data_url = text_data_url(json_file, "application/json")

    png_data_url = (
        visual_context["dataUrl"]
        if visual_context
        else transparent_png_data_url()
    )

    pdf_data_url = sample_pdf_data_url()

    actions = [
        create_text(
            x=origin["x"],
            y=origin["y"],
            width=520,
            text=f"AI Core received {canvas_input['object_count']} objects. Prompt: {prompt or 'none'}",
            color="black",
            metadata={"source": "ai-core/main.py"},
        ),
        create_rectangle(
            x=origin["x"],
            y=origin["y"] + 80,
            width=260,
            height=140,
            fill="semi",
            color="blue",
            text="Rectangle output",
            metadata={"source": "ai-core/main.py"},
        ),
        create_circle(
            x=origin["x"] + 300,
            y=origin["y"] + 80,
            width=140,
            height=140,
            fill="semi",
            color="green",
            metadata={"source": "ai-core/main.py"},
        ),
        create_arrow(
            x=origin["x"] + 470,
            y=origin["y"] + 150,
            end_x=origin["x"] + 610,
            end_y=origin["y"] + 150,
            color="black",
            text="arrow",
            metadata={"source": "ai-core/main.py"},
        ),
        create_line(
            x=origin["x"],
            y=origin["y"] + 250,
            end_x=origin["x"] + 260,
            end_y=origin["y"] + 250,
            color="red",
            metadata={"source": "ai-core/main.py"},
        ),
        {
            "action": "create_polygon",
            "points": [
                {"x": origin["x"] + 300, "y": origin["y"] + 250},
                {"x": origin["x"] + 430, "y": origin["y"] + 250},
                {"x": origin["x"] + 365, "y": origin["y"] + 330},
            ],
            "color": "violet",
            "fill": "semi",
            "metadata": {"source": "ai-core/main.py"},
        },
        {
            "action": "create_freehand",
            "points": [
                {"x": origin["x"] + 470, "y": origin["y"] + 255},
                {"x": origin["x"] + 500, "y": origin["y"] + 280},
                {"x": origin["x"] + 530, "y": origin["y"] + 260},
                {"x": origin["x"] + 560, "y": origin["y"] + 295},
            ],
            "color": "orange",
            "metadata": {"source": "ai-core/main.py"},
        },
        create_image(
            title="canvas-screenshot-or-placeholder.png",
            x=origin["x"],
            y=origin["y"] + 370,
            width=360,
            height=240,
            mime_type="image/png",
            data_url=png_data_url,
            metadata={"source": "ai-core/main.py"},
        ),
        create_markdown(
            title="ai-core-summary.md",
            x=origin["x"] + 390,
            y=origin["y"] + 370,
            width=420,
            height=300,
            data_url=markdown_data_url,
            metadata={"source": "ai-core/main.py"},
        ),
        create_pdf(
            title="ai-core-sample.pdf",
            x=origin["x"] + 840,
            y=origin["y"] + 370,
            width=420,
            height=300,
            mime_type="application/pdf",
            data_url=pdf_data_url,
            metadata={"source": "ai-core/main.py"},
        ),
        create_file(
            title="canvas-input.json",
            x=origin["x"],
            y=origin["y"] + 700,
            width=420,
            height=300,
            mime_type="application/json",
            data_url=json_data_url,
            metadata={"source": "ai-core/main.py"},
        ),
        create_webpage(
            url=first_webpage_url(canvas_state) or "https://example.com",
            x=origin["x"] + 450,
            y=origin["y"] + 700,
            width=640,
            height=420,
            title="AI Core webpage output",
            metadata={"source": "ai-core/main.py"},
        ),
    ]

    if selected:
        first = selected[0]
        selected_id = first["id"]
        selected_bounds = first["bounds"]
        actions.extend(
            [
                relabel_object(selected_id, "Updated by AI Core"),
                move_object(
                    selected_id,
                    x=selected_bounds["x"] + 24,
                    y=selected_bounds["y"] + 24,
                ),
                resize_object(
                    selected_id,
                    width=max(selected_bounds["w"], 180),
                    height=max(selected_bounds["h"], 100),
                ),
                {
                    "action": "update_metadata",
                    "id": selected_id,
                    "metadata": {"updated_by": "ai-core/main.py"},
                },
                {
                    "action": "select_objects",
                    "ids": [selected_id],
                },
            ]
        )

    return action_batch(actions)


def read_everything_on_canvas(
    canvas_state: CanvasState,
    visual_context: CanvasVisualContext | None = None,
) -> dict[str, Any]:
    objects = canvas_state.get("objects", [])
    selected = selected_objects(canvas_state)
    file_objects = files(canvas_state)
    webpage_objects = webpages(canvas_state)

    return {
        "captured_at": canvas_state.get("capturedAt"),
        "object_count": len(objects),
        "selected_count": len(selected),
        "visible_object_ids": canvas_state.get("visibleObjectIds", []),
        "viewport": canvas_state.get("viewport", {}),
        "metadata": canvas_state.get("metadata", {}),
        "objects": [
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
        "selected": [
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
            if visual_context
            else None
        ),
    }


def output_origin(canvas_state: CanvasState) -> dict[str, float]:
    viewport = canvas_state.get("viewport", {})
    return {
        "x": float(viewport.get("x", 100)) + 80,
        "y": float(viewport.get("y", 100)) + 80,
    }


def first_webpage_url(canvas_state: CanvasState) -> str | None:
    for obj in webpages(canvas_state):
        if obj.get("url"):
            return obj["url"]
    return None


def text_data_url(text: str, mime_type: str) -> str:
    encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def transparent_png_data_url() -> str:
    return (
        "data:image/png;base64,"
        "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII="
    )


def sample_pdf_data_url() -> str:
    pdf = b"""%PDF-1.1
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 144] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length 44 >>
stream
BT /F1 12 Tf 30 80 Td (Generated by AI Core) Tj ET
endstream
endobj
trailer
<< /Root 1 0 R >>
%%EOF
"""
    encoded = base64.b64encode(pdf).decode("ascii")
    return f"data:application/pdf;base64,{encoded}"
```

### Step-By-Step For Your Own Code

1. Put all AI behavior inside `run(...)` in `ai-core/main.py`.
2. Read the current canvas from `canvas_state["objects"]`.
3. Read selected objects with `selected_objects(canvas_state)`.
4. Read uploaded files/images/PDFs with `files(canvas_state)`.
5. Read webpage embeds with `webpages(canvas_state)`.
6. Read the screenshot with `visual_context["dataUrl"]` when `visual_context` is not `None`.
7. Create outputs by appending actions to an `actions` list.
8. Return `action_batch(actions)`.
9. Click Generate in the frontend. The backend imports `main.py`, calls `run(...)`, validates the action batch, and the frontend applies the actions.
10. If the code in `main.py` has a syntax error or raises an exception, Generate will fail and the backend terminal will show the error.

The most important rule: `canvas_state`, `visual_context`, and `prompt` are only available inside `run(...)`. Do not use them in top-level code.

## Modifying Objects

### Move Objects

```python
from canvas_protocol import action_batch, move_object


def move_panel() -> dict:
    return action_batch([
        move_object("shape:box1", x=160, y=220)
    ])
```

### Resize Objects

```python
from canvas_protocol import action_batch, resize_object


def resize_panel() -> dict:
    return action_batch([
        resize_object("shape:box1", width=500, height=260)
    ])
```

### Delete Objects

```python
from canvas_protocol import action_batch, delete_object


def delete_panel() -> dict:
    return action_batch([
        delete_object("shape:box1")
    ])
```

### Update Text

```python
from canvas_protocol import action_batch, relabel_object


def rename_panel() -> dict:
    return action_batch([
        relabel_object("shape:box1", "Updated revenue")
    ])
```

### Group And Ungroup

```python
from canvas_protocol import action_batch


def group_shapes() -> dict:
    return action_batch([
        {
            "action": "group_objects",
            "ids": ["shape:box1", "shape:box2"],
            "id": "ai-group-1",
        }
    ])


def ungroup_shapes() -> dict:
    return action_batch([
        {
            "action": "ungroup_objects",
            "ids": ["shape:ai-group-1"],
        }
    ])
```

## Action Schemas

All actions are plain Python dictionaries.

Create actions:

```python
{"action": "create_rectangle", "x": 100, "y": 200, "width": 400, "height": 250, "fill": "#3498db"}
{"action": "create_circle", "x": 100, "y": 200, "width": 160, "height": 160, "fill": "semi"}
{"action": "create_arrow", "x": 100, "y": 100, "endX": 300, "endY": 200, "color": "black"}
{"action": "create_line", "x": 100, "y": 100, "endX": 300, "endY": 100, "color": "black"}
{"action": "create_polygon", "points": [{"x": 0, "y": 0}, {"x": 100, "y": 0}, {"x": 50, "y": 80}]}
{"action": "create_freehand", "points": [{"x": 0, "y": 0}, {"x": 10, "y": 8}, {"x": 22, "y": 15}]}
{"action": "create_text", "x": 100, "y": 100, "text": "Hello canvas"}
{"action": "create_image", "x": 100, "y": 100, "width": 360, "height": 260, "title": "image.png", "dataUrl": "data:image/png;base64,..."}
{"action": "create_pdf", "x": 100, "y": 100, "width": 420, "height": 300, "title": "report.pdf", "dataUrl": "data:application/pdf;base64,..."}
{"action": "create_markdown", "x": 100, "y": 100, "width": 420, "height": 300, "title": "notes.md", "dataUrl": "data:text/markdown;base64,..."}
{"action": "create_file", "x": 100, "y": 100, "width": 420, "height": 300, "title": "data.json", "mimeType": "application/json"}
{"action": "create_webpage", "url": "https://example.com", "x": 500, "y": 300, "width": 800, "height": 600}
```

Modify actions:

```python
{"action": "move_object", "id": "shape:box1", "x": 160, "y": 220}
{"action": "resize_object", "id": "shape:box1", "width": 500, "height": 260}
{"action": "update_style", "id": "shape:box1", "style": {"color": "blue", "fill": "semi"}}
{"action": "relabel_object", "id": "shape:box1", "text": "Updated label"}
{"action": "update_webpage", "id": "embed-page1", "url": "https://docs.example.com", "title": "Docs"}
{"action": "update_metadata", "id": "shape:box1", "metadata": {"source": "ai-core"}}
{"action": "duplicate_object", "id": "shape:box1"}
{"action": "delete_object", "id": "shape:box1"}
{"action": "bring_to_front", "id": "shape:box1"}
{"action": "send_to_back", "id": "shape:box1"}
{"action": "group_objects", "ids": ["shape:box1", "shape:box2"], "id": "group-1"}
{"action": "ungroup_objects", "ids": ["shape:group-1"]}
{"action": "select_objects", "ids": ["shape:box1"]}
```

Action batch:

```python
{
    "schemaVersion": "pythios.canvas.actions.v1",
    "actions": [
        {"action": "create_text", "x": 100, "y": 100, "text": "Hello canvas"}
    ],
}
```

## Backend Validation

The backend exposes a validation endpoint for action batches. It validates structure only; it does not mutate the canvas.

```python
import requests


def validate_actions(api_url: str, batch: dict) -> dict:
    response = requests.post(
        f"{api_url}/canvas/actions/validate",
        json=batch,
        timeout=10,
    )
    response.raise_for_status()
    return response.json()
```

## Generate Handler Pattern

Future Python AI code should be shaped like this:

```python
from canvas_protocol import (
    CanvasState,
    CanvasVisualContext,
    action_batch,
    create_text,
    selected_objects,
)


def run(
    canvas_state: CanvasState,
    visual_context: CanvasVisualContext | None = None,
    prompt: str | None = None,
) -> dict:
    selected = selected_objects(canvas_state)
    screenshot_note = ""

    if visual_context:
        screenshot_note = f" Screenshot size: {visual_context['width']}x{visual_context['height']}."

    if selected:
        first = selected[0]
        bounds = first["bounds"]
        actions = [
            create_text(
                x=bounds["x"],
                y=bounds["y"] + bounds["h"] + 24,
                text=f"Generated note for {first['id']}.{screenshot_note}",
            )
        ]
    else:
        actions = [
            create_text(
                x=100,
                y=100,
                text=(prompt or "Generated after the user clicked Generate") + screenshot_note,
            )
        ]

    return action_batch(actions)
```

Do not call this function from file watchers, timers, background jobs, websocket loops, canvas change events, or drawing events. Call it only from the explicit Generate request path.

The `/generate` endpoint returns:

```python
{
    "source": "ai-core",
    "actionBatch": {
        "schemaVersion": "pythios.canvas.actions.v1",
        "actions": [
            {"action": "create_text", "x": 100, "y": 100, "text": "Hello canvas"}
        ],
    },
    "generatedUI": None,
}
```

`generatedUI` is optional legacy preview data. Canvas changes should be returned through `actionBatch`.
