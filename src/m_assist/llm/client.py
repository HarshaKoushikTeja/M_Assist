"""
client.py — the LLM orchestrator.

Responsibilities:
  - Build the right backend(s) from config.
  - For local backend: just call it.
  - For cloud: try primary (Gemini), and on rate-limit/error,
    SILENTLY fail over to fallback (Groq). User never sees the switch.
  - Enforce rate limits proactively via RateLimiter.
"""

from .base import LLMBackend
from .local_client import LocalClient
from .gemini_client import GeminiClient
from .groq_client import GroqClient
from .rate_limiter import RateLimiter
from ..core.logger import get_logger

log = get_logger("llm.client")


class LLMClient:
    def __init__(self, cfg):
        self.cfg = cfg
        self.backend_mode = cfg.llm.backend   # "local" | "gemini" | "groq" | "cloud"

        # Build backend instances we might need.
        self.local = LocalClient(cfg.llm.local)
        self.gemini = GeminiClient(cfg.llm.gemini)
        self.groq = GroqClient(cfg.llm.groq)

        # Rate limiters for the cloud backends.
        self.gemini_rl = RateLimiter(
            cfg.llm.gemini.rate_limit.requests_per_minute,
            cfg.llm.gemini.rate_limit.requests_per_day,
        )
        self.groq_rl = RateLimiter(
            cfg.llm.groq.rate_limit.requests_per_minute,
            cfg.llm.groq.rate_limit.requests_per_day,
        )

    def _try(self, backend: LLMBackend, limiter: RateLimiter, prompt: str):
        """Attempt one backend. Returns text on success, None on failure."""
        if limiter and not limiter.allow():
            log.warning("%s rate limit reached (%s) — failing over",
                        backend.name, limiter.status())
            return None
        try:
            result = backend.generate(prompt)
            if limiter:
                limiter.record()
            return result
        except Exception as e:
            log.warning("%s failed (%s) — failing over", backend.name, e)
            return None

    def generate(self, prompt: str) -> str:
        """Main entry. Routes to the configured backend with failover."""
        mode = self.backend_mode

        if mode == "local":
            return self.local.generate(prompt)   # let errors surface; no cloud fallback in pure-local

        if mode == "gemini":
            return self._try(self.gemini, self.gemini_rl, prompt) or "[all backends unavailable]"

        if mode == "groq":
            return self._try(self.groq, self.groq_rl, prompt) or "[all backends unavailable]"

        if mode == "cloud":
            # Primary -> fallback, silently.
            result = self._try(self.gemini, self.gemini_rl, prompt)
            if result is not None:
                return result
            result = self._try(self.groq, self.groq_rl, prompt)
            if result is not None:
                return result
            # Last resort: local, if Ollama is up.
            if self.local.is_available():
                log.warning("Both cloud backends down — falling back to local.")
                return self.local.generate(prompt)
            return "[all backends unavailable]"

        raise ValueError(f"Unknown llm.backend: {mode!r}")