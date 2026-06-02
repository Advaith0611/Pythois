from canvas_protocol import *


def run(
    canvas_state,
    visual_context=None,
    prompt=None,
    request=None,
):
    actions = [
        create_text(
    x=130,
    y=130,
    width=700,
    text="PYTHIOS",
    ),

    create_text(
    x=130,
    y=180,
    width=700,
    text="SEE • UNDERSTAND • FORESEE",
    ),

    create_text(
            x=130,
            y=240,
            width=650,
            text=(
                "AI features are currently under development.\n\n"
                "Soon Pythios will be able to:\n"
                "• Understand drawings and diagrams\n"
                "• Generate interfaces from sketches\n"
                "• Create and edit shapes automatically\n"
                "• Analyze uploaded files and images\n"
                "• Generate markdown and PDF documents\n"
                "• Create interactive webpage embeds\n"
                "• Transform visual ideas into working applications\n\n"
                "For now, this is a preview of the upcoming AI capabilities."
            ),
            color="black",
        ),
    ]
    return action_batch(actions)