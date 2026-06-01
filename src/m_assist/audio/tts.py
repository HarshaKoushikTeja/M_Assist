"""
tts.py — text-to-speech via pyttsx3 (offline, uses Windows SAPI5).

We speak only the FIRST PARAGRAPH of a reply (see Assistant), so short
answers ("Hello, sir") are spoken fully while long explanations get a
spoken summary with the full text on screen.

pyttsx3 wraps the OS speech engine — no model download, no VRAM. The
voice is functional rather than natural; Piper is the future upgrade.
"""

from ..core.logger import get_logger

log = get_logger("audio.tts")


class TTS:
    def __init__(self, cfg_tts):
        self.enabled = cfg_tts.enabled
        self.rate = cfg_tts.rate
        self.volume = cfg_tts.volume
        self.voice_index = cfg_tts.voice_index
        self._engine = None
        if self.enabled:
            self._init_engine()

    def _init_engine(self):
        import pyttsx3
        self._engine = pyttsx3.init()
        self._engine.setProperty("rate", self.rate)
        self._engine.setProperty("volume", self.volume)
        if self.voice_index is not None:
            voices = self._engine.getProperty("voices")
            if 0 <= self.voice_index < len(voices):
                self._engine.setProperty("voice", voices[self.voice_index].id)
        log.info("TTS ready (rate=%d, volume=%.1f)", self.rate, self.volume)

    def list_voices(self):
        """Print available system voices so you can pick a voice_index."""
        if self._engine is None:
            self._init_engine()
        for i, v in enumerate(self._engine.getProperty("voices")):
            print(f"[{i}] {v.name}  ({v.id})")

    def speak(self, text: str):
        """Speak the given text and block until done."""
        if not self.enabled or not text.strip():
            return
        try:
            self._engine.say(text)
            self._engine.runAndWait()
        except RuntimeError as e:
            # runAndWait can complain if called while already running;
            # re-init and retry once rather than crashing the whole loop.
            log.warning("TTS runtime issue (%s) — reinitializing engine", e)
            self._init_engine()
            self._engine.say(text)
            self._engine.runAndWait()