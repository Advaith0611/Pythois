from __future__ import annotations

import base64
import json
import sys
from pathlib import Path
from typing import Any


AI_CORE_DIR = Path(__file__).resolve().parents[2]
if str(AI_CORE_DIR) not in sys.path:
    sys.path.insert(0, str(AI_CORE_DIR))

from canvas_protocol import (  # noqa: E402
    CanvasAction,
    CanvasObjectSnapshot,
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
    delete_object,
    files,
    move_object,
    objects_by_kind,
    relabel_object,
    resize_object,
    selected_objects,
    webpages,
)


BLANK_PNG_DATA_URL = (
    "data:image/png;base64,"
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAFgwJ/lR0gWAAAAABJRU5ErkJggg=="
)


def text_data_url(text: str, mime_type: str) -> str:
    encoded = base64.b64encode(text.encode("utf-8")).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def binary_data_url(data: bytes, mime_type: str) -> str:
    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


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
<< /Length 45 >>
stream
BT /F1 12 Tf 30 80 Td (Pythios test PDF) Tj ET
endstream
endobj
trailer
<< /Root 1 0 R >>
%%EOF
"""
    return binary_data_url(pdf, "application/pdf")


def sample_docx_data_url() -> str:
    # This is intentionally tiny placeholder binary data for protocol training.
    # A real DOCX upload would be a zip package with Word XML inside.
    return binary_data_url(b"PK\x03\x04placeholder-docx-bytes", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")


def bounds(x: float, y: float, w: float, h: float) -> dict[str, float]:
    return {"x": x, "y": y, "w": w, "h": h}


def canvas_object(
    object_id: str,
    *,
    kind: str,
    type_: str,
    x: float,
    y: float,
    w: float,
    h: float,
    layer: int,
    source: str = "tldraw",
    style: dict[str, Any] | None = None,
    relationships: list[dict[str, Any]] | None = None,
    metadata: dict[str, Any] | None = None,
    **extra: Any,
) -> CanvasObjectSnapshot:
    return {
        "id": object_id,
        "source": source,
        "kind": kind,
        "type": type_,
        "bounds": bounds(x, y, w, h),
        "layerIndex": layer,
        "style": style or {},
        "relationships": relationships or [],
        "metadata": metadata or {},
        **extra,
    }


SAMPLE_OBJECTS: list[CanvasObjectSnapshot] = [
    canvas_object(
        "shape:generic",
        kind="shape",
        type_="geo",
        x=40,
        y=40,
        w=160,
        h=80,
        layer=0,
        text="Generic shape input",
        style={"color": "black", "fill": "none", "strokeWidth": 2, "opacity": 1},
        metadata={"training_note": "Covers generic shape kind."},
    ),
    canvas_object(
        "shape:rectangle",
        kind="rectangle",
        type_="geo",
        x=240,
        y=40,
        w=180,
        h=100,
        layer=1,
        text="Rectangle input",
        style={"color": "blue", "fill": "semi", "stroke": "solid", "dash": "draw"},
        metadata={"status": "selected and editable"},
    ),
    canvas_object(
        "shape:circle",
        kind="circle",
        type_="geo",
        x=460,
        y=40,
        w=110,
        h=110,
        layer=2,
        rotation=0.25,
        style={"color": "green", "fill": "solid"},
    ),
    canvas_object(
        "shape:arrow",
        kind="arrow",
        type_="arrow",
        x=620,
        y=70,
        w=180,
        h=40,
        layer=3,
        text="Arrow input",
        style={"color": "black", "strokeWidth": 3},
        relationships=[
            {"type": "binding", "objectId": "shape:rectangle"},
            {"type": "binding", "objectId": "shape:circle"},
        ],
        metadata={"start": {"x": 620, "y": 90}, "end": {"x": 800, "y": 110}},
    ),
    canvas_object(
        "shape:line",
        kind="line",
        type_="line",
        x=40,
        y=190,
        w=220,
        h=0,
        layer=4,
        style={"color": "red", "strokeWidth": 2},
        metadata={"start": {"x": 40, "y": 190}, "end": {"x": 260, "y": 190}},
    ),
    canvas_object(
        "shape:polygon",
        kind="polygon",
        type_="geo",
        x=300,
        y=170,
        w=150,
        h=130,
        layer=5,
        style={"color": "violet", "fill": "semi"},
        metadata={"points": [{"x": 300, "y": 300}, {"x": 375, "y": 170}, {"x": 450, "y": 300}]},
    ),
    canvas_object(
        "shape:freehand",
        kind="freehand",
        type_="draw",
        x=500,
        y=180,
        w=170,
        h=90,
        layer=6,
        style={"color": "orange", "strokeWidth": 4},
        metadata={"points": [{"x": 500, "y": 220}, {"x": 535, "y": 190}, {"x": 570, "y": 245}, {"x": 640, "y": 210}]},
    ),
    canvas_object(
        "shape:text",
        kind="text",
        type_="text",
        x=720,
        y=180,
        w=260,
        h=120,
        layer=7,
        text="Text input with exact structured text.",
        style={"color": "black", "font": "draw", "fontSize": 24},
    ),
    canvas_object(
        "group:planning",
        kind="group",
        type_="group",
        x=20,
        y=20,
        w=980,
        h=300,
        layer=8,
        relationships=[
            {"type": "child", "objectId": "shape:rectangle"},
            {"type": "child", "objectId": "shape:circle"},
            {"type": "child", "objectId": "shape:arrow"},
        ],
        metadata={"label": "Planning group"},
    ),
    canvas_object(
        "asset:image",
        kind="image",
        type_="asset",
        x=40,
        y=360,
        w=220,
        h=160,
        layer=9,
        source="embedded",
        title="sample-image.png",
        mimeType="image/png",
        size=68,
        url=BLANK_PNG_DATA_URL,
        metadata={"dataUrl": BLANK_PNG_DATA_URL, "alt": "1x1 PNG image input"},
    ),
    canvas_object(
        "asset:pdf",
        kind="pdf",
        type_="asset",
        x=300,
        y=360,
        w=220,
        h=160,
        layer=10,
        source="embedded",
        title="sample.pdf",
        mimeType="application/pdf",
        size=375,
        url=sample_pdf_data_url(),
        metadata={"dataUrl": sample_pdf_data_url(), "pages": 1},
    ),
    canvas_object(
        "asset:markdown",
        kind="markdown",
        type_="asset",
        x=560,
        y=360,
        w=240,
        h=180,
        layer=11,
        source="embedded",
        title="notes.md",
        mimeType="text/markdown",
        size=58,
        text="# Notes\n\nMarkdown input from the whiteboard.",
        url=text_data_url("# Notes\n\nMarkdown input from the whiteboard.", "text/markdown"),
        metadata={"dataUrl": text_data_url("# Notes\n\nMarkdown input from the whiteboard.", "text/markdown")},
    ),
    canvas_object(
        "asset:file-json",
        kind="file",
        type_="asset",
        x=840,
        y=360,
        w=240,
        h=160,
        layer=12,
        source="embedded",
        title="data.json",
        mimeType="application/json",
        size=47,
        url=text_data_url('{"project": "Pythios", "count": 3}', "application/json"),
        metadata={"dataUrl": text_data_url('{"project": "Pythios", "count": 3}', "application/json")},
    ),
    canvas_object(
        "asset:file-csv",
        kind="file",
        type_="asset",
        x=40,
        y=580,
        w=240,
        h=160,
        layer=13,
        source="embedded",
        title="table.csv",
        mimeType="text/csv",
        size=36,
        url=text_data_url("name,value\nalpha,1\nbeta,2\n", "text/csv"),
        metadata={"dataUrl": text_data_url("name,value\nalpha,1\nbeta,2\n", "text/csv")},
    ),
    canvas_object(
        "asset:file-text",
        kind="file",
        type_="asset",
        x=320,
        y=580,
        w=240,
        h=160,
        layer=14,
        source="embedded",
        title="plain.txt",
        mimeType="text/plain",
        size=34,
        text="Plain text file input.",
        url=text_data_url("Plain text file input.", "text/plain"),
        metadata={"dataUrl": text_data_url("Plain text file input.", "text/plain")},
    ),
    canvas_object(
        "asset:file-docx",
        kind="file",
        type_="asset",
        x=600,
        y=580,
        w=240,
        h=160,
        layer=15,
        source="embedded",
        title="document.docx",
        mimeType="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        size=26,
        url=sample_docx_data_url(),
        metadata={"dataUrl": sample_docx_data_url(), "training_note": "Placeholder DOCX data URL."},
    ),
    canvas_object(
        "embed:webpage",
        kind="webpage",
        type_="iframe",
        x=880,
        y=580,
        w=420,
        h=260,
        layer=16,
        source="embedded",
        title="Example webpage",
        url="https://example.com",
        relationships=[{"type": "embed", "objectId": "embed:webpage"}],
        metadata={"sandboxed": True, "note": "Cross-origin webpage pixels are visible only through visualContext."},
    ),
    canvas_object(
        "shape:temporary-delete-target",
        kind="rectangle",
        type_="geo",
        x=1120,
        y=40,
        w=180,
        h=100,
        layer=17,
        text="Delete action target",
        style={"color": "grey", "fill": "none"},
        metadata={"training_note": "Dedicated object used only to demonstrate delete_object output."},
    ),
]


SAMPLE_CANVAS_STATE: CanvasState = {
    "schemaVersion": "pythios.canvas.v1",
    "capturedAt": "2026-06-09T11:30:00.000Z",
    "viewport": {
        "x": 0,
        "y": 0,
        "z": 1,
        "screenBounds": bounds(0, 0, 1440, 900),
    },
    "objects": SAMPLE_OBJECTS,
    "selectedObjectIds": ["shape:rectangle", "shape:text", "asset:markdown"],
    "visibleObjectIds": [obj["id"] for obj in SAMPLE_OBJECTS],
    "sceneGraph": {
        "nodes": [
            {
                "id": "group:planning",
                "source": "tldraw",
                "kind": "group",
                "bounds": bounds(20, 20, 980, 300),
                "layerIndex": 8,
                "relationships": [
                    {"type": "child", "objectId": "shape:rectangle"},
                    {"type": "child", "objectId": "shape:circle"},
                    {"type": "child", "objectId": "shape:arrow"},
                ],
                "children": [
                    {
                        "id": "shape:rectangle",
                        "source": "tldraw",
                        "kind": "rectangle",
                        "bounds": bounds(240, 40, 180, 100),
                        "layerIndex": 1,
                        "relationships": [{"type": "parent", "objectId": "group:planning"}],
                        "children": [],
                        "parentId": "group:planning",
                    },
                    {
                        "id": "shape:circle",
                        "source": "tldraw",
                        "kind": "circle",
                        "bounds": bounds(460, 40, 110, 110),
                        "layerIndex": 2,
                        "relationships": [{"type": "parent", "objectId": "group:planning"}],
                        "children": [],
                        "parentId": "group:planning",
                    },
                ],
            }
        ],
        "flat": [
            {
                "id": obj["id"],
                "source": obj["source"],
                "kind": obj["kind"],
                "bounds": obj["bounds"],
                "layerIndex": obj["layerIndex"],
                "relationships": obj["relationships"],
                "children": [],
                **({"parentId": obj["parentId"]} if "parentId" in obj else {}),
            }
            for obj in SAMPLE_OBJECTS
        ],
    },
    "embeddedObjects": [
        {"id": obj["id"], "kind": obj["kind"], "title": obj.get("title"), "url": obj.get("url")}
        for obj in SAMPLE_OBJECTS
        if obj["source"] == "embedded"
    ],
    "metadata": {
        "pageId": "page:training-fixture",
        "purpose": "Training fixture covering every documented Pythios canvas input kind.",
    },
}


SAMPLE_VISUAL_CONTEXT: CanvasVisualContext = {
    "schemaVersion": "pythios.canvas.visual.v1",
    "capturedAt": "2026-06-09T11:30:00.000Z",
    "format": "image/png",
    "dataUrl": BLANK_PNG_DATA_URL,
    "width": 1440,
    "height": 900,
    "viewportPageBounds": bounds(0, 0, 1440, 900),
    "notes": [
        "Training fixture screenshot placeholder.",
        "In production this is a PNG capture of the visible whiteboard when Generate was clicked.",
    ],
}


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
        "viewport": canvas_state.get("viewport", {}),
        "metadata": canvas_state.get("metadata", {}),
        "object_count": len(objects),
        "selected_count": len(selected),
        "visible_object_ids": canvas_state.get("visibleObjectIds", []),
        "scene_graph": canvas_state.get("sceneGraph", {}),
        "embedded_objects": canvas_state.get("embeddedObjects", []),
        "counts_by_kind": {
            kind: len(objects_by_kind(canvas_state, kind))
            for kind in [
                "shape",
                "rectangle",
                "circle",
                "arrow",
                "line",
                "polygon",
                "freehand",
                "text",
                "group",
                "image",
                "pdf",
                "markdown",
                "file",
                "webpage",
            ]
        },
        "objects": [
            {
                "id": obj["id"],
                "source": obj["source"],
                "kind": obj["kind"],
                "type": obj["type"],
                "bounds": obj["bounds"],
                "layerIndex": obj["layerIndex"],
                "style": obj.get("style", {}),
                "relationships": obj.get("relationships", []),
                "rotation": obj.get("rotation"),
                "parentId": obj.get("parentId"),
                "groupId": obj.get("groupId"),
                "text": obj.get("text"),
                "title": obj.get("title"),
                "url": obj.get("url"),
                "mimeType": obj.get("mimeType"),
                "size": obj.get("size"),
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
                "title": obj.get("title"),
            }
            for obj in selected
        ],
        "files": [
            {
                "id": obj["id"],
                "kind": obj["kind"],
                "title": obj.get("title"),
                "mimeType": obj.get("mimeType"),
                "size": obj.get("size"),
                "has_data_url": bool(obj.get("url") or obj.get("metadata", {}).get("dataUrl")),
            }
            for obj in file_objects
        ],
        "webpages": [
            {
                "id": obj["id"],
                "title": obj.get("title"),
                "url": obj.get("url"),
                "bounds": obj["bounds"],
            }
            for obj in webpage_objects
        ],
        "visual_context": (
            {
                "format": visual_context["format"],
                "width": visual_context["width"],
                "height": visual_context["height"],
                "viewportPageBounds": visual_context["viewportPageBounds"],
                "has_data_url": bool(visual_context.get("dataUrl")),
                "notes": visual_context.get("notes", []),
            }
            if visual_context
            else None
        ),
    }


def every_output_action(
    canvas_state: CanvasState,
    visual_context: CanvasVisualContext | None = None,
    prompt: str | None = None,
) -> list[CanvasAction]:
    selected = selected_objects(canvas_state)
    selected_id = selected[0]["id"] if selected else "shape:rectangle"
    selected_bounds = selected[0]["bounds"] if selected else bounds(240, 40, 180, 100)
    canvas_input = read_everything_on_canvas(canvas_state, visual_context)

    markdown = (
        "# Pythios output training fixture\n\n"
        f"- Prompt: {prompt or 'No prompt supplied'}\n"
        f"- Objects read: {canvas_input['object_count']}\n"
        f"- Selected objects read: {canvas_input['selected_count']}\n"
        f"- File-like objects read: {len(canvas_input['files'])}\n"
        f"- Webpages read: {len(canvas_input['webpages'])}\n"
    )
    json_snapshot = json.dumps(canvas_input, indent=2)

    return [
        create_text(
            x=40,
            y=920,
            width=560,
            text="create_text output: structured text generated by the agent.",
            color="black",
            metadata={"training_output": "create_text"},
        ),
        create_rectangle(
            x=40,
            y=1020,
            width=240,
            height=120,
            fill="semi",
            color="blue",
            text="create_rectangle output",
            metadata={"training_output": "create_rectangle"},
        ),
        create_circle(
            x=320,
            y=1020,
            width=120,
            height=120,
            fill="semi",
            color="green",
            metadata={"training_output": "create_circle"},
        ),
        create_arrow(
            x=500,
            y=1080,
            end_x=720,
            end_y=1080,
            color="black",
            text="create_arrow output",
            metadata={"training_output": "create_arrow"},
        ),
        create_line(
            x=760,
            y=1080,
            end_x=980,
            end_y=1080,
            color="red",
            metadata={"training_output": "create_line"},
        ),
        create_image(
            title="generated-image.png",
            x=40,
            y=1180,
            width=260,
            height=180,
            mime_type="image/png",
            data_url=visual_context["dataUrl"] if visual_context else BLANK_PNG_DATA_URL,
            size=68,
            metadata={"training_output": "create_image"},
        ),
        create_markdown(
            title="generated-notes.md",
            x=340,
            y=1180,
            width=320,
            height=220,
            mime_type="text/markdown",
            data_url=text_data_url(markdown, "text/markdown"),
            size=len(markdown),
            metadata={"training_output": "create_markdown"},
        ),
        create_pdf(
            title="generated-report.pdf",
            x=700,
            y=1180,
            width=320,
            height=220,
            mime_type="application/pdf",
            data_url=sample_pdf_data_url(),
            size=375,
            metadata={"training_output": "create_pdf"},
        ),
        create_file(
            title="generated-canvas-input.json",
            x=1060,
            y=1180,
            width=340,
            height=220,
            mime_type="application/json",
            data_url=text_data_url(json_snapshot, "application/json"),
            size=len(json_snapshot),
            metadata={"training_output": "create_file"},
        ),
        create_webpage(
            url="https://example.com",
            x=40,
            y=1440,
            width=640,
            height=420,
            title="create_webpage output",
            metadata={"training_output": "create_webpage"},
        ),
        move_object(
            selected_id,
            x=selected_bounds["x"] + 32,
            y=selected_bounds["y"] + 32,
        ),
        resize_object(
            selected_id,
            width=max(selected_bounds["w"], 220),
            height=max(selected_bounds["h"], 140),
        ),
        relabel_object(selected_id, "relabel_object output applied by training fixture"),
        delete_object("shape:temporary-delete-target"),
        {
            "action": "create_polygon",
            "points": [{"x": 740, "y": 1460}, {"x": 860, "y": 1460}, {"x": 800, "y": 1570}],
            "color": "violet",
            "fill": "semi",
            "metadata": {"training_output": "raw_create_polygon"},
        },
        {
            "action": "create_freehand",
            "points": [{"x": 920, "y": 1490}, {"x": 950, "y": 1465}, {"x": 990, "y": 1525}, {"x": 1040, "y": 1480}],
            "color": "orange",
            "metadata": {"training_output": "raw_create_freehand"},
        },
        {
            "action": "update_metadata",
            "id": selected_id,
            "metadata": {"training_output": "raw_update_metadata", "agent_seen": True},
        },
        {
            "action": "select_objects",
            "ids": [selected_id, "shape:text", "asset:markdown"],
        },
    ]


def run(
    canvas_state: CanvasState = SAMPLE_CANVAS_STATE,
    visual_context: CanvasVisualContext | None = SAMPLE_VISUAL_CONTEXT,
    prompt: str | None = "Exercise every documented Pythios whiteboard input and output type.",
    request: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return action_batch(every_output_action(canvas_state, visual_context, prompt))


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
