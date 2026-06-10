"""
router_cli.py — Stage 5a test: type text, see how the router classifies it.
NO audio, NO LLM, NO actions — pure classification testing.

    python -m src.m_assist.router_cli
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from m_assist.core.config import load_config
from m_assist.core.logger import setup_logging, get_logger
from m_assist.routing.router import Router


def main():
    cfg = load_config(str(PROJECT_ROOT / "config.yaml"))
    setup_logging(cfg)
    router = Router(cfg.router)

    print("\nType an utterance to classify ('quit' to exit):\n")
    while True:
        text = input("test > ").strip()
        if text.lower() in {"quit", "exit"}:
            break
        if not text:
            continue
        d = router.route(text)
        print(f"  → type={d['type']}  command={d.get('command')}  "
              f"target={d.get('target')}  tier={d['tier']}  score={d.get('score'):.2f}\n")


if __name__ == "__main__":
    main()