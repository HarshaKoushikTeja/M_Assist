"""
audio_cli.py — Stage 2 smoke test, two modes:

  List your audio devices (find your mic's index):
      python -m src.m_assist.audio_cli --list-devices

  Live mic level meter (sub-step 2a — proves capture works, NO wake word):
      python -m src.m_assist.audio_cli --meter

  Wake word listening (sub-step 2b — needs Porcupine key in .env):
      python -m src.m_assist.audio_cli --listen
"""

import sys
import argparse
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

from m_assist.core.config import load_config
from m_assist.core.logger import setup_logging, get_logger


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--list-devices", action="store_true")
    parser.add_argument("--meter", action="store_true")
    parser.add_argument("--listen", action="store_true")
    args = parser.parse_args()

    cfg = load_config(str(PROJECT_ROOT / "config.yaml"))
    setup_logging(cfg)
    log = get_logger("audio_cli")

    # --- List devices ---
    if args.list_devices:
        from m_assist.audio.microphone import list_devices
        print(list_devices())
        return

    # --- Mic level meter (2a) ---
    if args.meter:
        import time
        from m_assist.audio.microphone import Microphone
        # 512 samples @ 16kHz is fine for a meter too.
        frame_len = 512
        print("Speak into the mic — Ctrl+C to stop.\n")
        with Microphone(cfg.audio.sample_rate, frame_len,
                        cfg.audio.channels, cfg.audio.input_device) as mic:
            try:
                while True:
                    frame = mic.read_frame()
                    level = mic.rms_level(frame)
                    bar = "#" * int(level * 600)
                    print(f"\r[{bar:<60}] {level:.3f}", end="", flush=True)
                    time.sleep(0.01)
            except KeyboardInterrupt:
                print("\nStopped.")
        return

    # --- Wake word (2b) ---
    if args.listen:
        from m_assist.audio.wake_word import WakeWordListener
        listener = WakeWordListener(cfg.audio)

        def on_wake():
            print(f"\n🎙️  '{listener.model_name}' detected! (this is where we'd start recording a command)\n")

        try:
            listener.listen(on_wake)
        finally:
            listener.close()
        return

    parser.print_help()


if __name__ == "__main__":
    main()