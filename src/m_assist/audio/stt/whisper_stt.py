"""
whisper_stt.py — fallback transcription with faster-whisper.

We use faster-whisper (CTranslate2 backend) rather than openai-whisper:
faster on NVIDIA, lower VRAM with int8, and no system FFmpeg needed.
This is the accurate-but-heavier path, used only when Vosk's output
looks unreliable.

Lazy-loaded: the model is only constructed on first use, so startup
stays fast and we don't hold VRAM until actually needed.
"""

import numpy as np
from ...core.logger import get_logger

log = get_logger("stt.whisper")


class WhisperSTT:
    def __init__(self, cfg_whisper, sample_rate: int):
        self.model_size = cfg_whisper.model
        self.device = cfg_whisper.device
        self.compute_type = cfg_whisper.compute_type
        self.sample_rate = sample_rate
        self._model = None   # lazy

    def _ensure_loaded(self):
        if self._model is None:
            from faster_whisper import WhisperModel
            log.info("Loading faster-whisper '%s' (device=%s, compute=%s)...",
                     self.model_size, self.device, self.compute_type)
            self._model = WhisperModel(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )

    def transcribe(self, audio_int16: np.ndarray) -> str:
        self._ensure_loaded()
        # faster-whisper wants float32 normalized to -1..1.
        audio_f32 = audio_int16.astype(np.float32) / 32768.0
        segments, info = self._model.transcribe(
            audio_f32, beam_size=5, language="en", vad_filter=True
        )
        # segments is a generator; join the pieces.
        text = " ".join(seg.text.strip() for seg in segments).strip()
        log.info("Whisper result: %r", text)
        return text