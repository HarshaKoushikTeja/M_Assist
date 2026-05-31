"""
base.py — the interface every LLM backend implements.

This is an Abstract Base Class (ABC). It can't be instantiated directly;
it just defines the shape every backend must have. If a subclass forgets
to implement generate(), Python raises an error at instantiation — a bug
caught early instead of at runtime.
"""

from abc import ABC, abstractmethod


class LLMBackend(ABC):
    """Common contract for all LLM backends (local or cloud)."""

    name: str = "base"

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Take a user prompt, return the model's text response.

        Must raise on failure (don't swallow errors here) — the
        orchestrator needs to SEE failures to trigger failover.
        """
        raise NotImplementedError

    def is_available(self) -> bool:
        """Optional quick health check. Default: assume available.

        Cloud backends can override to check the key exists; local
        can override to ping the Ollama server.
        """
        return True