"""
cli.py — Stage 0 smoke test.

Run this to confirm the foundation works:
    python -m src.m_assist.cli
(or from the project root: python src/m_assist/cli.py after path setup)

It does three things:
  1. Loads config.yaml into a dot-accessible object
  2. Initializes logging (console + rotating file)
  3. Prints the resolved settings so you can SEE the wiring is correct

No audio, no LLM calls yet — just proves the skeleton holds together.
"""

import sys
from pathlib import Path

# Make the package importable whether run as module or script.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from m_assist.core.config import load_config
from m_assist.core.logger import setup_logging, get_logger


def main() -> None:
    # 1. Load config
    cfg = load_config(str(PROJECT_ROOT / "config.yaml"))

    # 2. Set up logging
    setup_logging(cfg)
    log = get_logger("cli")

    # 3. Report what we loaded — proves dot-access + config wiring
    log.info("=== %s — Stage 0 smoke test ===", cfg.assistant.name)
    log.info("Wake word        : %s", cfg.assistant.wake_word)
    log.info("LLM backend      : %s", cfg.llm.backend)
    log.info("  local model    : %s (%s)", cfg.llm.local.model, cfg.llm.local.provider)
    log.info("  cloud primary  : %s -> %s", cfg.llm.gemini.model, cfg.llm.groq.model)
    log.info("STT              : %s -> %s (fallback)", cfg.stt.primary, cfg.stt.fallback)
    log.info("Router embed     : %s", cfg.router.embedding_model)
    log.info("Cache enabled    : %s (sim>%.2f)", cfg.cache.enabled, cfg.cache.similarity_threshold)
    log.info("Audio library    : %s @ %d Hz", cfg.audio.library, cfg.audio.sample_rate)
    log.info("=== Stage 0 OK — foundation is wired correctly. ===")


if __name__ == "__main__":
    main()
