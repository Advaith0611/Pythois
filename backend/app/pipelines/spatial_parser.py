from app.models.schemas import GenerateRequest, SpatialShape


def _text(shape: SpatialShape) -> str:
    return (shape.text or "").strip()


def parse_spatial_intent(request: GenerateRequest) -> dict:
    shapes = sorted(request.shapes, key=lambda shape: (shape.y, shape.x))
    text_shapes = [shape for shape in shapes if shape.text]
    arrows = [shape for shape in shapes if shape.type == "arrow"]
    zones = [_zone_for_shape(shape) for shape in shapes]

    keywords = " ".join([request.prompt or "", *[_text(shape) for shape in text_shapes]]).lower()
    if any(word in keywords for word in ["workflow", "flow", "steps", "journey", "process"]):
        task = "workflow"
    elif any(word in keywords for word in ["table", "kanban", "tasks", "pipeline", "crm"]):
        task = "app"
    else:
        task = "dashboard"

    return {
        "prompt": request.prompt,
        "selected_only": request.selectedOnly,
        "task": task,
        "shape_count": len(shapes),
        "text": [_text(shape) for shape in text_shapes],
        "arrows": len(arrows),
        "zones": zones,
        "bounds": _bounds(shapes),
    }


def _zone_for_shape(shape: SpatialShape) -> dict:
    role = "panel"
    text = _text(shape).lower()
    if shape.type == "text":
        role = "label" if len(text) > 18 else "control"
    elif shape.type == "arrow":
        role = "connection"
    elif shape.w > shape.h * 2.6:
        role = "table"
    elif shape.h > shape.w * 1.4:
        role = "sidebar"
    elif "chart" in text or "graph" in text:
        role = "chart"

    return {
        "id": shape.id,
        "type": shape.type,
        "role": role,
        "text": shape.text,
        "x": shape.x,
        "y": shape.y,
        "w": shape.w,
        "h": shape.h,
    }


def _bounds(shapes: list[SpatialShape]) -> dict:
    if not shapes:
        return {"x": 0, "y": 0, "w": 0, "h": 0}

    min_x = min(shape.x for shape in shapes)
    min_y = min(shape.y for shape in shapes)
    max_x = max(shape.x + shape.w for shape in shapes)
    max_y = max(shape.y + shape.h for shape in shapes)
    return {"x": min_x, "y": min_y, "w": max_x - min_x, "h": max_y - min_y}
