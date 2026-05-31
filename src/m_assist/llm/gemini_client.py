"""
gemini_client.py — Google AI Studio (Gemini 2.5 Flash, free tier).

Uses the google-genai SDK. The API key is read from the environment
variable named in config (never hardcoded, never in the repo).
"""

import os
from .base import LLMBackend
from ..core.logger import get_logger

log = get_logger("llm.gemini")


class GeminiClient(LLMBackend):
    name = "gemini"

    def __init__(self, cfg_gemini):
        self.model = cfg_gemini.model
        self.api_key = os.getenv(cfg_gemini.api_key_env)
        self._client = None
        if self.api_key:
            # Import inside __init__ so the package still imports
            # even if google-genai isn't installed yet.
            from google import genai
            self._client = genai.Client(api_key=self.api_key)

    def is_available(self) -> bool:
        return self._client is not None

    def generate(self, prompt: str) -> str:
        if self._client is None:
            raise RuntimeError("Gemini key missing — set GEMINI_API_KEY in .env")
        log.debug("Gemini generate via %s", self.model)
        resp = self._client.models.generate_content(
            model=self.model, contents=prompt
        )
        return (resp.text or "").strip()