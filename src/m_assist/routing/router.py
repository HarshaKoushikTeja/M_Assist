"""
router.py — the two-tier router: rules first, embeddings second.

This is the single entry point the assistant calls. It returns a
decision dict the assistant acts on:
    {type, command, target, score, tier}
"""

from . import rule_router
from .embedding_router import EmbeddingRouter
from ..core.logger import get_logger

log = get_logger("routing.router")


class Router:
    def __init__(self, cfg_router):
        self.embedder = EmbeddingRouter(
            cfg_router.embedding_model, cfg_router.local_intent_threshold
        )

    def route(self, text: str) -> dict:
        # Tier 1: rules (fast, exact).
        rule_hit = rule_router.match(text)
        if rule_hit is not None:
            rule_hit["tier"] = "rules"
            rule_hit.setdefault("score", 1.0)
            rule_hit.setdefault("target", None)
            return rule_hit

        # Tier 2: embeddings (fuzzy).
        embed_hit = self.embedder.classify(text)
        embed_hit["tier"] = "embeddings"
        embed_hit.setdefault("target", None)
        return embed_hit