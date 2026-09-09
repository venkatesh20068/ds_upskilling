"""Content moderation via Llama Guard 3 (`ollama pull llama-guard3`) - 
a genuine safety-tuned local model, used here instead of the OpenAI 
Moderation API or Perspective API (both cloud services). Passing just 
a user message moderates that input; passing `[user, assistant]` moderates 
the assistant's (last) turn - the same call handles both directions.

Confirmed directly against a running Ollama instance before relying on
it: a safe message returns "safe"; an unsafe one returns
"unsafe\\nS<category>" (e.g. "unsafe\\nS9" for weapons-making
instructions, "unsafe\\nS2" for a non-violent-crime suggestion aimed at
an assistant turn).
"""

import requests

GUARD_MODEL = "llama-guard3"
OLLAMA_URL = "http://localhost:11434/api/chat"

# Llama Guard 3's hazard taxonomy (only labeled for readability - the
# category codes themselves come straight from the model's own output).
CATEGORY_LABELS = {
    "S1": "Violent Crimes",
    "S2": "Non-Violent Crimes",
    "S3": "Sex-Related Crimes",
    "S4": "Child Sexual Exploitation",
    "S5": "Defamation",
    "S6": "Specialized Advice",
    "S7": "Privacy",
    "S8": "Intellectual Property",
    "S9": "Indiscriminate Weapons",
    "S10": "Hate",
    "S11": "Suicide & Self-Harm",
    "S12": "Sexual Content",
    "S13": "Elections",
    "S14": "Code Interpreter Abuse",
}


def moderate(messages: list[dict]) -> dict:
    """`messages` is a `[user]` or `[user, assistant]` list - Llama Guard
    evaluates whichever turn is last."""
    response = requests.post(
        OLLAMA_URL,
        json={"model": GUARD_MODEL, "messages": messages, "stream": False},
        timeout=120,
    )
    response.raise_for_status()
    content = response.json()["message"]["content"].strip()
    lines = content.splitlines()
    flagged = lines[0].strip().lower() == "unsafe"
    categories = [CATEGORY_LABELS.get(c.strip(), c.strip()) for c in lines[1:]]
    return {"flagged": flagged, "categories": categories, "raw": content}


def moderate_input(user_message: str) -> dict:
    return moderate([{"role": "user", "content": user_message}])


def moderate_output(user_message: str, assistant_message: str) -> dict:
    return moderate(
        [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message},
        ]
    )
