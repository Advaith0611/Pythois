from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.models.schemas import GenerateRequest, GeneratedUI, HealthResponse
from app.pipelines.orchestrator import generate_interface

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="ok", ai="local-ready")


@router.post("/generate", response_model=GeneratedUI)
async def generate(request: GenerateRequest):
    return generate_interface(request)


@router.websocket("/ws/generate")
async def generate_ws(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            payload = await websocket.receive_json()
            request = GenerateRequest.model_validate(payload)
            result = generate_interface(request)
            await websocket.send_json(result.model_dump())
    except WebSocketDisconnect:
        return
