import json
import os
from datetime import datetime

HISTORY_FILE = "history.json"


def load_history() -> list:
    if not os.path.exists(HISTORY_FILE):
        return []
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)


def save_to_history(user_input: str, app_type: str, response: str):
    history = load_history()
    entry = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "timestamp": datetime.now().strftime("%b %d, %Y – %H:%M"),
        "app_type": app_type,
        "idea": user_input[:120] + ("..." if len(user_input) > 120 else ""),
        "full_idea": user_input,
        "response": response,
        "mermaid": "",
        "chat_history": [],  # ← new
    }
    history.insert(0, entry)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def delete_entry(entry_id: str):
    history = load_history()
    history = [h for h in history if h["id"] != entry_id]
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def clear_history():
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)
