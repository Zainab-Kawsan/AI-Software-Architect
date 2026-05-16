import os
import re

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from prompt import SYSTEM_PROMPT

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise EnvironmentError("GROQ_API_KEY is not set in your .env file.")

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)

REFINE_SYSTEM_PROMPT = """
You are a senior software architect helping a user refine their app architecture.

The user has already generated an architecture blueprint. They will ask you to:
- Modify specific sections (e.g. "switch the database to PostgreSQL")
- Add new components (e.g. "add a Redis cache layer")
- Explain decisions (e.g. "why did you choose REST over GraphQL?")
- Expand sections (e.g. "give me more detail on the API endpoints")

RULES:
1. If the user asks to change or improve the architecture, output the FULL updated blueprint
   using EXACTLY these section headers (same as the original):

## Project Overview
## Recommended Tech Stack
## Folder Structure
## Database Schema
## API Endpoints
## Development Roadmap
## Starter Backend Code

2. If the user asks a question or wants an explanation only, answer conversationally —
   do NOT reprint the full blueprint unless they ask for changes.

3. Keep the same professional, beginner-friendly tone as the original blueprint.
4. Be specific — reference actual tech choices from the current blueprint when explaining.
5. If only one section changes, still return the full blueprint with all sections intact.
"""


def build_chat_messages(
    original_blueprint: str,
    app_type: str,
    user_idea: str,
    chat_history: list[dict],
    new_message: str,
) -> list:
    """
    Build the full message list for the refinement LLM call.
    chat_history: list of {"role": "user"|"assistant", "content": str}
    """
    messages = [SystemMessage(content=REFINE_SYSTEM_PROMPT)]

    # Inject the original blueprint as the first assistant turn
    context = (
        f"App Type: {app_type}\n"
        f"Original Idea: {user_idea}\n\n"
        f"Current Blueprint:\n{original_blueprint}"
    )
    messages.append(HumanMessage(content=context))
    messages.append(
        AIMessage(
            content="I have your blueprint loaded. What would you like to refine or ask about?"
        )
    )

    # Replay conversation history
    for turn in chat_history:
        if turn["role"] == "user":
            messages.append(HumanMessage(content=turn["content"]))
        else:
            messages.append(AIMessage(content=turn["content"]))

    # Add the new user message
    messages.append(HumanMessage(content=new_message))
    return messages


def is_full_blueprint(text: str) -> bool:
    """Detect if the response contains a full updated blueprint."""
    required = [
        "## Project Overview",
        "## Recommended Tech Stack",
        "## Folder Structure",
    ]
    return all(section in text for section in required)


def refine_architecture(
    original_blueprint: str,
    app_type: str,
    user_idea: str,
    chat_history: list[dict],
    new_message: str,
) -> tuple[str, bool]:
    """
    Returns (response_text, is_blueprint_update).
    is_blueprint_update = True means the response is a new full blueprint.
    """
    try:
        messages = build_chat_messages(
            original_blueprint, app_type, user_idea, chat_history, new_message
        )
        response = llm.invoke(messages)
        content = response.content.strip()
        return content, is_full_blueprint(content)

    except Exception as e:
        return f"Error: {str(e)}", False
