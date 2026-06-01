"""
storage.py — saves a single Q&A turn to its own Markdown file.

Triggered on demand when the user says "save that". Each turn becomes a
timestamped .md file in the configured directory, so they're easy to
browse, re-read, or open in any editor.
"""

import re
from datetime import datetime
from pathlib import Path
from .core.logger import get_logger

log = get_logger("storage")


class ConversationStore:
    def __init__(self, cfg_conv):
        self.enabled = cfg_conv.save_enabled
        self.save_dir = Path(cfg_conv.save_dir)
        if self.enabled:
            self.save_dir.mkdir(parents=True, exist_ok=True)

    def _slug(self, text: str, max_len: int = 40) -> str:
        """Make a filesystem-safe snippet from the question for the filename."""
        text = text.lower().strip()
        text = re.sub(r"[^a-z0-9\s-]", "", text)   # drop punctuation
        text = re.sub(r"\s+", "-", text)            # spaces -> hyphens
        return text[:max_len].strip("-") or "turn"

    def save_turn(self, question: str, answer: str) -> Path | None:
        """Write one Q&A turn to its own Markdown file. Returns the path."""
        if not self.enabled:
            log.info("Saving disabled in config.")
            return None

        now = datetime.now()
        # Timestamp prefix keeps files sorted chronologically and unique.
        fname = f"{now:%Y%m%d-%H%M%S}_{self._slug(question)}.md"
        path = self.save_dir / fname

        content = (
            f"# {question}\n\n"
            f"*Saved {now:%Y-%m-%d %H:%M:%S}*\n\n"
            f"---\n\n"
            f"{answer}\n"
        )
        path.write_text(content, encoding="utf-8")
        log.info("Saved turn to %s", path)
        return path