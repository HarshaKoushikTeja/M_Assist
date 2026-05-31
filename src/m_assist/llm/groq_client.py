"""
groq_client.py — Groq (free tier, very fast inference).

Uses the groq SDK. Same pattern as Gemini: key from env, lazy import.
"""

import os
from .base import LLMBackend
from ..core.logger import get_logger

log = get_logger("llm.groq")


class GroqClient(LLMBackend):
    name = "groq"

    def __init__(self, cfg_groq):
        self.model = cfg_groq.model
        self.api_key = os.getenv(cfg_groq.api_key_env)
        self._client = None
        if self.api_key:
            from groq import Groq
            self._client = Groq(api_key=self.api_key)

    def is_available(self) -> bool:
        return self._client is not None

    def generate(self, prompt: str) -> str:
        if self._client is None:
            raise RuntimeError("Groq key missing — set GROQ_API_KEY in .env")
        log.debug("Groq generate via %s", self.model)
        resp = self._client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
        )
        return resp.choices[0].message.content.strip()