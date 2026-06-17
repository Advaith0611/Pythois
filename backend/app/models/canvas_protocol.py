from typing import Any, Literal

from pydantic import BaseModel, Field


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


class CanvasBounds(BaseModel):
    x: float
    y: float
    w: float
    h: float


class CanvasStyle(BaseModel):
    color: str | None = None
    fill: str | None = None
    stroke: str | None = None
    strokeWidth: float | None = None
    opacity: float | None = None
    dash: str | None = None
    font: str | None = None
    fontSize: float | None = None


class CanvasRelationship(BaseModel):
    type: Literal["parent", "child", "group", "binding", "embed"]
    objectId: str


class EmbeddedCanvasObject(BaseModel):
    id: str
    kind: Literal["image", "pdf", "file", "webpage"]
    x: float
    y: float
    w: float
    h: float
    title: str
    mimeType: str | None = None
    size: int | None = None
    dataUrl: str | None = None
    url: str | None = None
    createdAt: str
    metadata: dict[str, Any] | None = None


class CanvasObjectSnapshot(BaseModel):
    id: str
    source: CanvasObjectSource
    kind: CanvasObjectKind
    type: str
    bounds: CanvasBounds
    rotation: float | None = None
    layerIndex: int
    parentId: str | None = None
    groupId: str | None = None
    text: str | None = None
    url: str | None = None
    mimeType: str | None = None
    size: int | None = None
    title: str | None = None
    style: CanvasStyle = Field(default_factory=CanvasStyle)
    relationships: list[CanvasRelationship] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    raw: Any | None = None


class SceneGraphNode(BaseModel):
    id: str
    source: CanvasObjectSource
    kind: CanvasObjectKind
    parentId: str | None = None
    children: list["SceneGraphNode"] = Field(default_factory=list)
    bounds: CanvasBounds
    layerIndex: int
    relationships: list[CanvasRelationship] = Field(default_factory=list)


class SceneGraph(BaseModel):
    nodes: list[SceneGraphNode] = Field(default_factory=list)
    flat: list[SceneGraphNode] = Field(default_factory=list)


class CanvasViewport(BaseModel):
    x: float
    y: float
    z: float
    screenBounds: CanvasBounds


class CanvasState(BaseModel):
    schemaVersion: Literal["pythios.canvas.v1"] = "pythios.canvas.v1"
    capturedAt: str
    viewport: CanvasViewport
    objects: list[CanvasObjectSnapshot] = Field(default_factory=list)
    selectedObjectIds: list[str] = Field(default_factory=list)
    visibleObjectIds: list[str] = Field(default_factory=list)
    sceneGraph: SceneGraph
    embeddedObjects: list[EmbeddedCanvasObject] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class CanvasVisualContext(BaseModel):
    schemaVersion: Literal["pythios.canvas.visual.v1"] = "pythios.canvas.visual.v1"
    capturedAt: str
    format: Literal["image/png"]
    dataUrl: str
    width: int
    height: int
    viewportPageBounds: CanvasBounds
    notes: list[str] = Field(default_factory=list)


class CanvasPoint(BaseModel):
    x: float
    y: float


class CreateBoxAction(BaseModel):
    action: Literal["create_rectangle", "create_circle"]
    id: str | None = None
    x: float
    y: float
    width: float
    height: float
    fill: str | None = None
    color: str | None = None
    text: str | None = None
    metadata: dict[str, Any] | None = None


class CreateTextAction(BaseModel):
    action: Literal["create_text"]
    id: str | None = None
    x: float
    y: float
    width: float | None = None
    text: str
    color: str | None = None
    metadata: dict[str, Any] | None = None


class CreateConnectorAction(BaseModel):
    action: Literal["create_arrow", "create_line"]
    id: str | None = None
    x: float
    y: float
    endX: float
    endY: float
    color: str | None = None
    text: str | None = None
    metadata: dict[str, Any] | None = None


class CreatePathAction(BaseModel):
    action: Literal["create_polygon", "create_freehand"]
    id: str | None = None
    points: list[CanvasPoint]
    color: str | None = None
    fill: str | None = None
    strokeWidth: float | None = None
    metadata: dict[str, Any] | None = None


class CreateFileAction(BaseModel):
    action: Literal["create_file", "create_image", "create_pdf", "create_markdown"]
    id: str | None = None
    x: float
    y: float
    width: float
    height: float
    title: str
    mimeType: str | None = None
    size: int | None = None
    dataUrl: str | None = None
    metadata: dict[str, Any] | None = None


class CreateWebpageAction(BaseModel):
    action: Literal["create_webpage"]
    id: str | None = None
    url: str
    x: float
    y: float
    width: float
    height: float
    title: str | None = None
    metadata: dict[str, Any] | None = None


class MoveObjectAction(BaseModel):
    action: Literal["move_object"]
    id: str
    x: float
    y: float


class ResizeObjectAction(BaseModel):
    action: Literal["resize_object"]
    id: str
    width: float
    height: float


class UpdateStyleAction(BaseModel):
    action: Literal["update_style"]
    id: str
    style: CanvasStyle


class RelabelObjectAction(BaseModel):
    action: Literal["relabel_object"]
    id: str
    text: str


class UpdateWebpageAction(BaseModel):
    action: Literal["update_webpage"]
    id: str
    url: str
    title: str | None = None


class UpdateMetadataAction(BaseModel):
    action: Literal["update_metadata"]
    id: str
    metadata: dict[str, Any]


class SingleObjectAction(BaseModel):
    action: Literal["delete_object", "duplicate_object", "bring_to_front", "send_to_back"]
    id: str


class GroupObjectsAction(BaseModel):
    action: Literal["group_objects"]
    ids: list[str]
    id: str | None = None


class UngroupObjectsAction(BaseModel):
    action: Literal["ungroup_objects"]
    ids: list[str]


class SelectObjectsAction(BaseModel):
    action: Literal["select_objects"]
    ids: list[str]


CanvasAction = (
    CreateBoxAction
    | CreateTextAction
    | CreateConnectorAction
    | CreatePathAction
    | CreateFileAction
    | CreateWebpageAction
    | MoveObjectAction
    | ResizeObjectAction
    | UpdateStyleAction
    | RelabelObjectAction
    | UpdateWebpageAction
    | UpdateMetadataAction
    | SingleObjectAction
    | GroupObjectsAction
    | UngroupObjectsAction
    | SelectObjectsAction
)


class CanvasActionBatch(BaseModel):
    schemaVersion: Literal["pythios.canvas.actions.v1"] = "pythios.canvas.actions.v1"
    actions: list[CanvasAction] = Field(default_factory=list)


class CanvasActionResult(BaseModel):
    action: str
    ok: bool
    objectIds: list[str] = Field(default_factory=list)
    error: str | None = None


class CanvasActionBatchResult(BaseModel):
    schemaVersion: Literal["pythios.canvas.actions.v1"] = "pythios.canvas.actions.v1"
    appliedAt: str | None = None
    results: list[CanvasActionResult] = Field(default_factory=list)


class CanvasProtocolResponse(BaseModel):
    stateSchema: str = "pythios.canvas.v1"
    visualSchema: str = "pythios.canvas.visual.v1"
    actionSchema: str = "pythios.canvas.actions.v1"
    readableStructures: list[str] = Field(
        default_factory=lambda: ["CanvasState", "SceneGraph", "SelectedObjects", "VisibleObjects"]
    )
    writableActions: list[str] = Field(
        default_factory=lambda: [
            "create_rectangle",
            "create_circle",
            "create_arrow",
            "create_line",
            "create_polygon",
            "create_text",
            "create_freehand",
            "create_image",
            "create_pdf",
            "create_markdown",
            "create_file",
            "create_webpage",
            "move_object",
            "resize_object",
            "update_style",
            "relabel_object",
            "update_webpage",
            "update_metadata",
            "group_objects",
            "ungroup_objects",
            "duplicate_object",
            "delete_object",
            "bring_to_front",
            "send_to_back",
            "select_objects",
        ]
    )
