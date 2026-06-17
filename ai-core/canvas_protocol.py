from __future__ import annotations

from typing import Any, Literal, NotRequired, TypedDict


CanvasObjectSource = Literal["tldraw", "embedded"]
CanvasObjectKind = Literal[
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


class CanvasBounds(TypedDict):
    x: float
    y: float
    w: float
    h: float


class CanvasStyle(TypedDict, total=False):
    color: str
    fill: str
    stroke: str
    strokeWidth: float
    opacity: float
    dash: str
    font: str
    fontSize: float


class CanvasRelationship(TypedDict):
    type: Literal["parent", "child", "group", "binding", "embed"]
    objectId: str


class CanvasObjectSnapshot(TypedDict):
    id: str
    source: CanvasObjectSource
    kind: CanvasObjectKind
    type: str
    bounds: CanvasBounds
    layerIndex: int
    style: CanvasStyle
    relationships: list[CanvasRelationship]
    metadata: dict[str, Any]
    rotation: NotRequired[float]
    parentId: NotRequired[str]
    groupId: NotRequired[str]
    text: NotRequired[str]
    url: NotRequired[str]
    mimeType: NotRequired[str]
    size: NotRequired[int]
    title: NotRequired[str]
    raw: NotRequired[Any]


class SceneGraphNode(TypedDict):
    id: str
    source: CanvasObjectSource
    kind: CanvasObjectKind
    bounds: CanvasBounds
    layerIndex: int
    relationships: list[CanvasRelationship]
    children: list["SceneGraphNode"]
    parentId: NotRequired[str]


class SceneGraph(TypedDict):
    nodes: list[SceneGraphNode]
    flat: list[SceneGraphNode]


class CanvasState(TypedDict):
    schemaVersion: Literal["pythios.canvas.v1"]
    capturedAt: str
    viewport: dict[str, Any]
    objects: list[CanvasObjectSnapshot]
    selectedObjectIds: list[str]
    visibleObjectIds: list[str]
    sceneGraph: SceneGraph
    embeddedObjects: list[dict[str, Any]]
    metadata: dict[str, Any]


class CanvasVisualContext(TypedDict):
    schemaVersion: Literal["pythios.canvas.visual.v1"]
    capturedAt: str
    format: Literal["image/png"]
    dataUrl: str
    width: int
    height: int
    viewportPageBounds: CanvasBounds
    notes: list[str]


CanvasAction = dict[str, Any]


def selected_objects(state: CanvasState) -> list[CanvasObjectSnapshot]:
    selected_ids = set(state.get("selectedObjectIds", []))
    return [obj for obj in state.get("objects", []) if obj["id"] in selected_ids]


def objects_by_kind(state: CanvasState, kind: CanvasObjectKind) -> list[CanvasObjectSnapshot]:
    return [obj for obj in state.get("objects", []) if obj["kind"] == kind]


def files(state: CanvasState) -> list[CanvasObjectSnapshot]:
    return [obj for obj in state.get("objects", []) if obj["kind"] in {"image", "pdf", "markdown", "file"}]


def webpages(state: CanvasState) -> list[CanvasObjectSnapshot]:
    return objects_by_kind(state, "webpage")


def create_rectangle(
    *,
    x: float,
    y: float,
    width: float,
    height: float,
    fill: str | None = None,
    color: str | None = None,
    text: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> CanvasAction:
    return _without_none(
        {
            "action": "create_rectangle",
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "fill": fill,
            "color": color,
            "text": text,
            "metadata": metadata,
        }
    )


def create_circle(
    *,
    x: float,
    y: float,
    width: float,
    height: float,
    fill: str | None = None,
    color: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> CanvasAction:
    return _without_none(
        {
            "action": "create_circle",
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "fill": fill,
            "color": color,
            "metadata": metadata,
        }
    )


def create_text(
    *,
    x: float,
    y: float,
    text: str,
    width: float | None = None,
    color: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> CanvasAction:
    return _without_none(
        {
            "action": "create_text",
            "x": x,
            "y": y,
            "width": width,
            "text": text,
            "color": color,
            "metadata": metadata,
        }
    )


def create_arrow(
    *,
    x: float,
    y: float,
    end_x: float,
    end_y: float,
    color: str | None = None,
    text: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> CanvasAction:
    return _connector("create_arrow", x, y, end_x, end_y, color, text, metadata)


def create_line(
    *,
    x: float,
    y: float,
    end_x: float,
    end_y: float,
    color: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> CanvasAction:
    return _connector("create_line", x, y, end_x, end_y, color, None, metadata)


def create_freehand(
    *,
    points: list[dict[str, float]],
    color: str | None = None,
    stroke_width: float | None = None,
    metadata: dict[str, Any] | None = None,
) -> CanvasAction:
    return _without_none(
        {
            "action": "create_freehand",
            "points": points,
            "color": color,
            "strokeWidth": stroke_width,
            "metadata": metadata,
        }
    )


def create_webpage(
    *,
    url: str,
    x: float,
    y: float,
    width: float,
    height: float,
    title: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> CanvasAction:
    return _without_none(
        {
            "action": "create_webpage",
            "url": url,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "title": title,
            "metadata": metadata,
        }
    )


def create_file(
    *,
    title: str,
    x: float,
    y: float,
    width: float,
    height: float,
    mime_type: str | None = None,
    data_url: str | None = None,
    size: int | None = None,
    metadata: dict[str, Any] | None = None,
) -> CanvasAction:
    return _embedded_file("create_file", title, x, y, width, height, mime_type, data_url, size, metadata)


def create_image(
    *,
    title: str,
    x: float,
    y: float,
    width: float,
    height: float,
    mime_type: str | None = None,
    data_url: str | None = None,
    size: int | None = None,
    metadata: dict[str, Any] | None = None,
) -> CanvasAction:
    return _embedded_file("create_image", title, x, y, width, height, mime_type, data_url, size, metadata)


def create_pdf(
    *,
    title: str,
    x: float,
    y: float,
    width: float,
    height: float,
    mime_type: str | None = None,
    data_url: str | None = None,
    size: int | None = None,
    metadata: dict[str, Any] | None = None,
) -> CanvasAction:
    return _embedded_file("create_pdf", title, x, y, width, height, mime_type, data_url, size, metadata)


def create_markdown(
    *,
    title: str,
    x: float,
    y: float,
    width: float,
    height: float,
    mime_type: str | None = "text/markdown",
    data_url: str | None = None,
    size: int | None = None,
    metadata: dict[str, Any] | None = None,
) -> CanvasAction:
    return _embedded_file("create_markdown", title, x, y, width, height, mime_type, data_url, size, metadata)


def move_object(object_id: str, *, x: float, y: float) -> CanvasAction:
    return {"action": "move_object", "id": object_id, "x": x, "y": y}


def resize_object(object_id: str, *, width: float, height: float) -> CanvasAction:
    return {"action": "resize_object", "id": object_id, "width": width, "height": height}


def relabel_object(object_id: str, text: str) -> CanvasAction:
    return {"action": "relabel_object", "id": object_id, "text": text}


def delete_object(object_id: str) -> CanvasAction:
    return {"action": "delete_object", "id": object_id}


def action_batch(actions: list[CanvasAction]) -> dict[str, Any]:
    return {"schemaVersion": "pythios.canvas.actions.v1", "actions": actions}


def _connector(
    action: Literal["create_arrow", "create_line"],
    x: float,
    y: float,
    end_x: float,
    end_y: float,
    color: str | None,
    text: str | None,
    metadata: dict[str, Any] | None,
) -> CanvasAction:
    return _without_none(
        {
            "action": action,
            "x": x,
            "y": y,
            "endX": end_x,
            "endY": end_y,
            "color": color,
            "text": text,
            "metadata": metadata,
        }
    )


def _embedded_file(
    action: Literal["create_file", "create_image", "create_pdf", "create_markdown"],
    title: str,
    x: float,
    y: float,
    width: float,
    height: float,
    mime_type: str | None = None,
    data_url: str | None = None,
    size: int | None = None,
    metadata: dict[str, Any] | None = None,
) -> CanvasAction:
    return _without_none(
        {
            "action": action,
            "title": title,
            "x": x,
            "y": y,
            "width": width,
            "height": height,
            "mimeType": mime_type,
            "dataUrl": data_url,
            "size": size,
            "metadata": metadata,
        }
    )


def _without_none(data: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in data.items() if value is not None}
