"""
llm_cli.py — Stage 1 smoke test.

Type a prompt, get a reply from the configured backend.
    python -m src.m_assist.llm_cli

With config llm.backend: "local", you need Ollama running + gemma3:4b pulled.
Switch to "cloud" once you've put keys in .env.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")   # load keys BEFORE building clients

from m_assist.core.config import load_config
from m_assist.core.logger import setup_logging, get_logger
from m_assist.llm.client import LLMClient


def main() -> None:
    cfg = load_config(str(PROJECT_ROOT / "config.yaml"))
    setup_logging(cfg)
    log = get_logger("llm_cli")

    client = LLMClient(cfg)
    log.info("Backend mode: %s", cfg.llm.backend)
    print("Type a prompt (or 'quit'):\n")

    while True:
        try:
            prompt = input("you > ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if prompt.lower() in {"quit", "exit"}:
            break
        if not prompt:
            continue
        reply = client.generate(prompt)
        print(f"\n{cfg.assistant.name} > {reply}\n")


if __name__ == "__main__":
    main()