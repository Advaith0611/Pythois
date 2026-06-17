from groq import Groq
from dotenv import load_dotenv

load_dotenv()
client = Groq()


def get_project_plan(file):
    with open(file, "r") as project_file:
        return project_file.read()


def research(plan):
    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "system", 
                "content": """You are a senior research agent for an autonomous software builder.

Your job is to read the project plan, use browser_search only when research is actually needed, and return the information an implementation agent needs to build the project correctly.

Behavior:
- Do the research yourself. Do not output a list of tools to call.
- Use as few searches as possible. Prefer one broad, high-value search over many narrow searches.
- Prioritize official documentation, stable library docs, maintained examples, and current best practices.
- Avoid researching obvious or already-known basics unless the project depends on current APIs, package names, or version-specific behavior.
- If the project can be built safely from general engineering knowledge, use browser_search only for the highest-risk/current details.
- Do not browse for every TODO item. Group related questions into a small number of research passes.
- Prefer practical build decisions over long explanation.

For each project, determine:
- the recommended implementation stack
- the key libraries/APIs to use
- the exact docs or references the builder should rely on
- important implementation constraints and edge cases
- any risks, compatibility issues, or things to avoid
- a focused build order for the implementation agent
- complete enough that a coding agent can start implementation without doing another broad research pass."""
            },
            {
                "role": "user", 
                "content": plan
            }
        ],
        model="openai/gpt-oss-20b",
        temperature=1,
        max_completion_tokens=2048,
        top_p=1,
        stream=False,
        stop=None,
        tool_choice="required",
        tools=[
            {
                "type": "browser_search"
            }
        ]
    )
    print(chat_completion.choices[0].message.content)

if __name__ == "__main__":
    project_plan = get_project_plan("example_project_plan.pdf")
    research(project_plan)
