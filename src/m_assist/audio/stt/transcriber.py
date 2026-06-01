"""
transcriber.py — two-tier STT orchestrator.

Logic:
  1. Always try Vosk first (fast).
  2. Decide if Vosk's result is "good enough":
       - has at least `min_words` words, AND
       - the recording wasn't too noisy (avg RMS below threshold)
  3. If not good enough, fall back to Whisper (accurate).

This is the same proactive-fallback philosophy as the LLM client:
cheap path first, escalate only when signals say we should.
"""

from .vosk_stt import VoskSTT
from .whisper_stt import WhisperSTT
from ...core.logger import get_logger

log = get_logger("stt.transcriber")


class Transcriber:
    def __init__(self, cfg_stt, sample_rate: int):
        self.vosk = VoskSTT(cfg_stt.vosk_model_path, sample_rate)
        self.whisper = WhisperSTT(cfg_stt.whisper, sample_rate)
        self.min_words = cfg_stt.fallback_triggers.min_words
        self.noise_threshold = cfg_stt.fallback_triggers.rms_noise_threshold

    def _vosk_good_enough(self, text: str, avg_rms: float) -> bool:
        word_count = len(text.split())
        if word_count < self.min_words:
            log.info("Vosk too short (%d words) — will try Whisper", word_count)
            return False
        if avg_rms > self.noise_threshold:
            log.info("Recording noisy (RMS %.3f) — will try Whisper", avg_rms)
            return False
        return True

    def transcribe(self, audio_int16, avg_rms: float) -> str:
        """Two-tier transcription. Returns best-effort text."""
        vosk_text = self.vosk.transcribe(audio_int16)

        if self._vosk_good_enough(vosk_text, avg_rms):
            log.info("Using Vosk result (fast path).")
            return vosk_text

        # Fallback
        log.info("Falling back to Whisper.")
        whisper_text = self.whisper.transcribe(audio_int16)
        # If Whisper somehow returns empty, fall back to whatever Vosk had.
        return whisper_text or vosk_text