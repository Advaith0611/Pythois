from datetime import UTC, datetime
from uuid import uuid4

from app.models.schemas import GeneratedComponent, GeneratedUI


def generate_local(intent: dict) -> GeneratedUI:
    zones = intent.get("zones", [])
    task = intent.get("task", "dashboard")
    prompt = (intent.get("prompt") or "").strip()
    text_title = next((zone.get("text") for zone in zones if zone.get("text")), None)
    components = [_component_from_zone(zone, index) for index, zone in enumerate(zones[:12])]

    if not components:
        components = _default_components()

    if task == "workflow":
        layout = "workflow"
        app_type = "workflow_builder"
    elif task == "app":
        layout = "app"
        app_type = "operations_workspace"
    else:
        layout = "dashboard"
        app_type = "analytics_dashboard"

    return GeneratedUI(
        id=str(uuid4()),
        app_type=app_type,
        title=prompt or text_title or "Spatial AI Workspace",
        summary=f"Generated from {intent.get('shape_count', 0)} canvas object(s) with structured spatial parsing.",
        theme="dark",
        layout=layout,
        generated_at=datetime.now(UTC).isoformat(),
        source="backend",
        components=components,
    )


def _component_from_zone(zone: dict, index: int) -> GeneratedComponent:
    role = zone.get("role")
    text = (zone.get("text") or "").strip()
    title = text or f"{role.title()} {index + 1}"

    if role == "table":
        return GeneratedComponent(
            id=zone["id"],
            type="table",
            title=title,
            columns=["Segment", "Owner", "Score"],
            rows=[
                {"Segment": "Acquisition", "Owner": "Growth", "Score": 82},
                {"Segment": "Activation", "Owner": "Product", "Score": 76},
                {"Segment": "Revenue", "Owner": "Sales", "Score": 69},
            ],
        )

    if role == "sidebar":
        return GeneratedComponent(
            id=zone["id"],
            type="list",
            title=title,
            items=["Overview", "Customers", "Reports", "Settings"],
            detail="Navigation converted from a tall canvas region.",
        )

    if role == "connection":
        return GeneratedComponent(
            id=zone["id"],
            type="workflow",
            title=title,
            items=["Input", "Route", "Generate", "Review"],
        )

    if role == "control":
        lowered = title.lower()
        return GeneratedComponent(
            id=zone["id"],
            type="input" if any(word in lowered for word in ["search", "filter", "input"]) else "button",
            title=title,
            label=title,
        )

    if role == "label":
        return GeneratedComponent(
            id=zone["id"],
            type="note",
            title=title,
            detail="Text annotation promoted into a contextual note.",
            items=["Interpret", "Render", "Refine"],
        )

    if role == "chart":
        return GeneratedComponent(
            id=zone["id"],
            type="chart",
            title=title,
            detail="Chart inferred from a labeled canvas region.",
        )

    if index % 5 == 0:
        return GeneratedComponent(
            id=zone["id"],
            type="metric",
            title=title,
            value=f"{84 + index}%",
            detail="Metric inferred from a compact region.",
        )

    return GeneratedComponent(
        id=zone["id"],
        type="chart",
        title=title,
        detail="Chart inferred from a rectangular canvas region.",
    )


def _default_components() -> list[GeneratedComponent]:
    return [
        GeneratedComponent(id="metric-1", type="metric", title="Intent Confidence", value="91%", detail="Local parser score"),
        GeneratedComponent(id="metric-2", type="metric", title="Generated Regions", value="4", detail="Starter layout"),
        GeneratedComponent(id="chart-1", type="chart", title="Workspace Activity", detail="Trend preview"),
        GeneratedComponent(
            id="table-1",
            type="table",
            title="Canvas Objects",
            columns=["Object", "Role", "State"],
            rows=[
                {"Object": "Rectangle", "Role": "Panel", "State": "Rendered"},
                {"Object": "Text", "Role": "Control", "State": "Interactive"},
                {"Object": "Arrow", "Role": "Flow", "State": "Connected"},
            ],
        ),
        GeneratedComponent(id="workflow-1", type="workflow", title="Generation Loop", items=["Draw", "Parse", "Generate", "Refine"]),
    ]
