import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage

from prompt import SYSTEM_PROMPT

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise EnvironmentError("GROQ_API_KEY is not set in your .env file.")

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key)


def generate_architecture(user_input: str, app_type: str) -> str:
    try:
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(
                content=(
                    f"Application Type: {app_type}\n\n"
                    f"User Idea:\n{user_input}\n\n"
                    f"Tailor the tech stack, folder structure, and recommendations "
                    f"specifically for a {app_type}."
                )
            ),
        ]
        response = llm.invoke(messages)
        return response.content

    except Exception as e:
        return f"Error: {str(e)}"
