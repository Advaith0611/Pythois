from typing import Literal

from pydantic import BaseModel, Field


class SpatialShape(BaseModel):
    id: str
    type: str
    x: float = 0
    y: float = 0
    w: float = 120
    h: float = 72
    text: str | None = None
    geo: str | None = None
    color: str | None = None


class GenerateRequest(BaseModel):
    shapes: list[SpatialShape] = Field(default_factory=list)
    prompt: str | None = None
    selectedOnly: bool = False


class GeneratedComponent(BaseModel):
    id: str
    type: Literal[
        "metric",
        "chart",
        "table",
        "button",
        "input",
        "list",
        "kanban",
        "timeline",
        "workflow",
        "note",
    ]
    title: str
    label: str | None = None
    value: str | None = None
    detail: str | None = None
    items: list[str] | None = None
    columns: list[str] | None = None
    rows: list[dict[str, str | int | float]] | None = None
    accent: str | None = None


class GeneratedUI(BaseModel):
    id: str
    app_type: str
    title: str
    summary: str
    theme: Literal["light", "dark"] = "dark"
    layout: Literal["dashboard", "app", "workflow", "wireframe"] = "dashboard"
    generated_at: str
    source: Literal["backend", "local"] = "backend"
    components: list[GeneratedComponent]


class HealthResponse(BaseModel):
    status: str
    ai: str
