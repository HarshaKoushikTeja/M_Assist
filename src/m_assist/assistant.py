"""
assistant.py — the bridge that connects every stage into one loop.

Flow:
    wake word ("hey jarvis")
      -> record command (silence-endpointed)
      -> transcribe (Vosk fast path, Whisper fallback)
      -> LLM (Gemma local, or cloud per config)
      -> respond: PRINT full reply, SPEAK first paragraph
      -> back to listening

This class owns the wiring; each component still does its own job. That
separation is why we could build and test the pieces independently.
"""

from .core.logger import get_logger
from .audio.wake_word import WakeWordListener
from .audio.recorder import Recorder
from .audio.stt.transcriber import Transcriber
from .audio.tts import TTS
from .llm.client import LLMClient
from .storage import ConversationStore

import time

log = get_logger("assistant")


class Assistant:
    def __init__(self, cfg):
        self.cfg = cfg
        self.wake = WakeWordListener(cfg.audio)
        self.recorder = Recorder(cfg.audio, cfg.stt.record)
        self.transcriber = Transcriber(cfg.stt, cfg.audio.sample_rate)
        self.tts = TTS(cfg.tts)
        self.llm = LLMClient(cfg)
        self.speak_first_para_only = cfg.response.speak_first_paragraph_only
        self.name = cfg.assistant.name

        self.store = ConversationStore(cfg.conversation)
        self.save_phrases = [p.lower() for p in cfg.conversation.save_phrases]
        self.last_turn = None   # (question, answer) of the most recent exchange

    def _first_paragraph(self, text: str) -> str:
        """Return the first paragraph (text up to the first blank line).

        If there are no blank lines, fall back to the first sentence-ish
        chunk so we don't speak a huge wall of text.
        """
        text = text.strip()
        # Split on the first double-newline (paragraph break).
        para = text.split("\n\n", 1)[0].strip()
        return para

    def _handle_command(self, text: str):
        """Process one transcribed command end-to-end."""
        if not text.strip():
            log.info("Empty transcription — ignoring.")
            return

        print(f"\n🗣️  You said: {text}")

        # --- Local command: "save that" ---  (precursor to Stage 5 routing)
        if self._is_save_command(text):
            self._handle_save()
            return

        # --- Otherwise: normal LLM turn ---
        log.info("Sending to LLM: %r", text)
        reply = self.llm.generate(text)
        print(f"\n🤖 {self.name}: {reply}\n")

        # Remember this turn so "save that" can grab it next.
        self.last_turn = (text, reply)

        to_speak = self._first_paragraph(reply) if self.speak_first_para_only else reply
        self.tts.speak(to_speak)

    def _is_save_command(self, text: str) -> bool:
        """True if the user's utterance matches a save phrase."""
        cleaned = text.lower().strip().rstrip(".!?")
        return any(phrase in cleaned for phrase in self.save_phrases)

    def _handle_save(self):
        """Save the most recent turn, if there is one."""
        if self.last_turn is None:
            msg = "There's nothing to save yet."
            print(f"\n🤖 {self.name}: {msg}\n")
            self.tts.speak(msg)
            return
        question, answer = self.last_turn
        path = self.store.save_turn(question, answer)
        if path:
            msg = "Saved that for you."
        else:
            msg = "Saving is turned off right now."
        print(f"\n🤖 {self.name}: {msg}\n")
        self.tts.speak(msg)

    def run(self):
        """Start the continuous wake-word loop. Ctrl+C to stop."""
        log.info("=== %s is online. Say 'hey jarvis' to wake me. ===", self.name)
        print(f"\n{self.name} is listening. Say 'hey jarvis'...  (Ctrl+C to quit)\n")

        def on_wake():
            # Called by the wake-word listener when "hey jarvis" fires.
            print("\n🎙️  (listening for your command...)")
            recording, avg_rms = self.recorder.record_command()
            if recording.size == 0 or avg_rms < 0.005:
                log.info("No real speech captured (RMS %.3f) — ignoring.", avg_rms)
                return                      # was 'continue' — return exits the callback
            text = self.transcriber.transcribe(recording, avg_rms)
            self._handle_command(text)
            # Fix 4: settle delay so the speaker's tail/echo doesn't self-trigger
            # the wake word when listening resumes (laptop speakers -> mic feedback).
            time.sleep(self.cfg.response.post_speak_cooldown_s)
            print(f"\n{self.name} is listening. Say 'hey jarvis'...\n")

        try:
            self.wake.listen(on_wake)
        except KeyboardInterrupt:
            log.info("Shutting down.")
        finally:
            self.wake.close()