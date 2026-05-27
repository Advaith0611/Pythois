from app.models.schemas import GenerateRequest, GeneratedUI
from app.pipelines.local_generator import generate_local
from app.pipelines.spatial_parser import parse_spatial_intent
from app.pipelines.tool_switcher import choose_generator
from app.services.groq_client import generate_with_groq


def generate_interface(request: GenerateRequest) -> GeneratedUI:
    intent = parse_spatial_intent(request)

    if choose_generator(intent) == "groq":
        try:
            generated = generate_with_groq(intent)
            if generated:
                return generated
        except Exception:
            pass

    return generate_local(intent)
