"""
embedding_router.py — tier 2: fuzzy semantic matching.

Runs when rules don't fire. Embeds every intent example once at startup,
then for each utterance finds the nearest example by cosine similarity.
If the best match clears a confidence threshold, we use its intent type;
otherwise we default to QUESTION (safest — sends to the LLM).

Model: all-MiniLM-L6-v2 (~80MB, fast on CPU).
"""

import numpy as np
from .intents import INTENTS, QUESTION
from ..core.logger import get_logger

log = get_logger("routing.embed")


class EmbeddingRouter:
    def __init__(self, model_name: str, threshold: float):
        from sentence_transformers import SentenceTransformer
        log.info("Loading embedding model '%s'...", model_name)
        self._model = SentenceTransformer(model_name)
        self.threshold = threshold

        # Flatten all examples, remembering which intent each belongs to.
        self._example_texts = []
        self._example_meta = []   # parallel list of (type, command)
        for intent in INTENTS:
            for ex in intent["examples"]:
                self._example_texts.append(ex)
                self._example_meta.append((intent["type"], intent.get("command")))

        # Embed all examples ONCE (normalized so dot product = cosine sim).
        self._example_embeds = self._model.encode(
            self._example_texts, normalize_embeddings=True
        )
        log.info("Embedded %d example phrases across %d intents",
                 len(self._example_texts), len(INTENTS))

    def classify(self, text: str):
        """Return {type, command, score} for the nearest intent example."""
        query = self._model.encode([text], normalize_embeddings=True)[0]
        # Cosine similarity = dot product of normalized vectors.
        sims = self._example_embeds @ query
        best_idx = int(np.argmax(sims))
        best_score = float(sims[best_idx])
        best_type, best_command = self._example_meta[best_idx]

        log.info("Nearest: %r (score=%.2f) -> %s/%s",
                 self._example_texts[best_idx], best_score, best_type, best_command)

        if best_score < self.threshold:
            # Not confident enough — default to QUESTION (send to LLM).
            log.info("Below threshold %.2f — defaulting to QUESTION", self.threshold)
            return {"type": QUESTION, "command": None, "score": best_score}

        return {"type": best_type, "command": best_command, "score": best_score}