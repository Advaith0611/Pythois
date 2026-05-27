"""Shared spatial AI orchestration notes.

The runnable API lives in backend/app/pipelines. This module exists as the
project-level extension point described in the scaffold: future model routers,
analyzers, renderers, and tool selectors can be promoted here when they need to
be shared by more than the FastAPI backend.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ToolDecision:
    task: str
    generator: str
    reason: str


def route_task(task: str, shape_count: int) -> ToolDecision:
    if task in {"dashboard", "app", "workflow"} and shape_count > 0:
        return ToolDecision(task=task, generator="local_or_groq", reason="Structured UI generation")
    return ToolDecision(task=task, generator="local", reason="No external model required")
