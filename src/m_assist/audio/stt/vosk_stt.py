"""
vosk_stt.py — fast-path transcription with Vosk (offline, CPU, instant).

Vosk is a Kaldi-based recognizer. It's lightweight and quick but less
accurate than Whisper on hard audio — perfect for the first-pass
"fast path" in our two-tier design.
"""

import json
import numpy as np
from vosk import Model, KaldiRecognizer
from ...core.logger import get_logger

log = get_logger("stt.vosk")


class VoskSTT:
    def __init__(self, model_path: str, sample_rate: int):
        log.info("Loading Vosk model from %s", model_path)
        self._model = Model(model_path)
        self.sample_rate = sample_rate

    def transcribe(self, audio_int16: np.ndarray) -> str:
        """Transcribe a full int16 audio array to text."""
        rec = KaldiRecognizer(self._model, self.sample_rate)
        rec.SetWords(True)
        # Vosk wants raw bytes.
        rec.AcceptWaveform(audio_int16.tobytes())
        result = json.loads(rec.FinalResult())
        text = result.get("text", "").strip()
        log.info("Vosk result: %r", text)
        return text