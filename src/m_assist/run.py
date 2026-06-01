"""
run.py — M.Assist entry point.

    python -m src.m_assist.run

Loads config + env, builds the Assistant, starts the voice loop.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")   # load any API keys before building clients

from m_assist.core.config import load_config
from m_assist.core.logger import setup_logging
from m_assist.assistant import Assistant


def main():
    cfg = load_config(str(PROJECT_ROOT / "config.yaml"))
    setup_logging(cfg)
    assistant = Assistant(cfg)
    assistant.run()


if __name__ == "__main__":
    main()