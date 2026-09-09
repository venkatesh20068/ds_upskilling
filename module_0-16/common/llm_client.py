"""Shared local client for talking to Ollama's REST API.

Used by the Ollama-backed samples across modules.
Requires Ollama running locally (https://ollama.com) with
`llama3.1` pulled (`ollama pull llama3.1`) for chat/generation, and
`all-MiniLM` pulled (`ollama pull all-minilm`) for embeddings.
"""

import json
import sys
import requests

sys.stdout.reconfigure(encoding="utf-8")  # llama3.1 output may include Unicode the console codepage can't render

OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.1"

EMBED_URL = "http://localhost:11434/api/embed"
EMBED_MODEL = "all-MiniLM"


def chat(
    messages: list[dict],
    temperature: float = 0.7,
    seed: int | None = None,
    json_mode: bool = False,
    num_predict: int | None = None,
    tools: list[dict] | None = None,
) -> dict:
    """Call Ollama and return the full response dict - includes
    Ollama's own token counts (prompt_eval_count, eval_count). Pass
    json_mode=True to constrain output to valid JSON (Ollama's JSON
    mode). num_predict caps the number of generated tokens (Ollama's
    equivalent of max_tokens/max_new_tokens). tools is a list of
    OpenAI-style function-tool definitions; if the model decides to
    call one, the response's message["tool_calls"] is populated
    instead of (or alongside) message["content"]."""
    options = {"temperature": temperature}
    if seed is not None:
        options["seed"] = seed
    if num_predict is not None:
        options["num_predict"] = num_predict

    payload = {"model": MODEL, "messages": messages, "stream": False, "options": options}
    if json_mode:
        payload["format"] = "json"
    if tools is not None:
        payload["tools"] = tools

    response = requests.post(OLLAMA_URL, json=payload, timeout=120)
    response.raise_for_status()
    return response.json()


def embed(texts: str | list[str]) -> list[list[float]]:
    """Embed one or more strings via Ollama's embedding endpoint.
    Always returns a list of vectors, one per input string (even for a
    single string input - index [0] to get that one vector). Vectors
    come back L2-normalized (unit length)."""
    payload_input = [texts] if isinstance(texts, str) else texts

    response = requests.post(
        EMBED_URL,
        json={"model": EMBED_MODEL, "input": payload_input},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["embeddings"]


def stream_chat(messages: list[dict]):
    """Call Ollama with streaming enabled; yields each content piece as
    it arrives (newline-delimited JSON, one chunk per line)."""
    with requests.post(
        OLLAMA_URL,
        json={"model": MODEL, "messages": messages, "stream": True},
        stream=True,
        timeout=120,
    ) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if not line:
                continue
            chunk = json.loads(line)
            piece = chunk.get("message", {}).get("content", "")
            if piece:
                yield piece
            if chunk.get("done"):
                break
