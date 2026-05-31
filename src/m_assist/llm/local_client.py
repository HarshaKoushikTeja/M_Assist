"""
local_client.py — local inference via Ollama (Gemma 3 4B).

Requires Ollama running locally and the model pulled:
    ollama pull gemma3:4b
Ollama exposes an HTTP API on localhost:11434 by default.
"""

import requests
from .base import LLMBackend
from ..core.logger import get_logger

log = get_logger("llm.local")


class LocalClient(LLMBackend):
    name = "local"

    def __init__(self, cfg_local):
        self.model = cfg_local.model
        self.host = cfg_local.host.rstrip("/")

    def is_available(self) -> bool:
        """Ping Ollama's /api/tags to confirm the server is up."""
        try:
            r = requests.get(f"{self.host}/api/tags", timeout=2)
            return r.status_code == 200
        except requests.RequestException:
            return False

    def generate(self, prompt: str) -> str:
        url = f"{self.host}/api/generate"
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        log.debug("Local generate via %s", self.model)
        r = requests.post(url, json=payload, timeout=120)
        r.raise_for_status()           # raises on HTTP error -> failover sees it
        data = r.json()
        return data.get("response", "").strip()