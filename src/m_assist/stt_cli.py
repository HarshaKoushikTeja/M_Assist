"""
stt_cli.py — Stage 3a smoke test: record + transcribe, NO wake word, NO LLM.

    python -m src.m_assist.stt_cli

Press Enter, speak a sentence, go quiet. It records, runs the two-tier
transcriber, and prints the text. Proves STT works before we bridge it.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from m_assist.core.config import load_config
from m_assist.core.logger import setup_logging, get_logger
from m_assist.audio.recorder import Recorder
from m_assist.audio.stt.transcriber import Transcriber


def main():
    cfg = load_config(str(PROJECT_ROOT / "config.yaml"))
    setup_logging(cfg)
    log = get_logger("stt_cli")

    recorder = Recorder(cfg.audio, cfg.stt.record)
    transcriber = Transcriber(cfg.stt, cfg.audio.sample_rate)

    print("\nPress Enter, then speak. Go quiet when done. ('quit' to exit)\n")
    while True:
        cmd = input("[Enter to record] > ").strip().lower()
        if cmd in {"quit", "exit"}:
            break
        audio, avg_rms = recorder.record_command()
        if audio.size == 0:
            print("No audio captured.\n")
            continue
        text = transcriber.transcribe(audio, avg_rms)
        print(f"\n📝 Transcribed: {text!r}\n")


if __name__ == "__main__":
    main()