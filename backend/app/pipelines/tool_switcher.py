from app.services.ollama_client import ollama_reason


def choose_generator(intent: dict) -> str:
    prompt = (
        "Choose the best generation system for this task. Return only GROQ or LOCAL.\n"
        f"Task: {intent.get('task')}\n"
        f"Shapes: {intent.get('shape_count')}\n"
    )
    decision = ollama_reason(prompt)
    if decision and "GROQ" in decision.upper():
        return "groq"
    return "local"
