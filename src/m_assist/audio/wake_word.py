"""
wake_word.py — listens for the wake word using openWakeWord.

openWakeWord is a fully local, open-source wake-word engine. No access
key, no online activation — it runs small ONNX models on-device.

We replaced Porcupine with it because Picovoice's signup blocks free
email providers. The public interface here (listen(on_wake)) is
unchanged, so nothing else in the project had to move.

The "hey jarvis" pretrained model expects 16kHz mono int16 audio, fed
in chunks of 1280 samples (80ms). It outputs a confidence score 0..1
per chunk; we fire when it crosses the configured threshold.
"""

import time
import numpy as np
from openwakeword.model import Model
import openwakeword
from .microphone import Microphone
from ..core.logger import get_logger

log = get_logger("audio.wake")

# openWakeWord processes audio in 80ms chunks at 16kHz = 1280 samples.
CHUNK_SAMPLES = 1280


class WakeWordListener:
    def __init__(self, cfg_audio):
        ww = cfg_audio.wake_word
        self.model_name = ww.model
        self.threshold = ww.threshold
        self.framework = ww.inference_framework
        self.cooldown = ww.trigger_cooldown_s
        self.channels = cfg_audio.channels
        self.device = cfg_audio.input_device
        self.sample_rate = cfg_audio.sample_rate   # 16000

        # First run downloads the pretrained models (~tens of MB), then cached.
        try:
            openwakeword.utils.download_models()
        except Exception as e:
            log.warning("Model download skipped/failed (may already be cached): %s", e)

        # Load just the one model we want, using ONNX (Windows-safe).
        self._model = Model(
            wakeword_models=[self.model_name],
            inference_framework=self.framework,
        )
        self._last_trigger = 0.0
        log.info("openWakeWord ready — model='%s', framework=%s, threshold=%.2f",
                 self.model_name, self.framework, self.threshold)

    def listen(self, on_wake):
        """Block and listen forever. Calls on_wake() when wake word detected.

        Ctrl+C to stop.
        """
        with Microphone(self.sample_rate, CHUNK_SAMPLES,
                        self.channels, self.device) as mic:
            log.info("Listening for '%s'... (Ctrl+C to stop)", self.model_name)
            try:
                while True:
                    frame = mic.read_frame()           # int16, length 1280
                    # predict() returns a dict: {model_name: score}
                    scores = self._model.predict(frame)
                    score = scores.get(self.model_name, 0.0)

                    if score >= self.threshold:
                        now = time.time()
                        # Cooldown stops one utterance firing many times.
                        if now - self._last_trigger >= self.cooldown:
                            self._last_trigger = now
                            log.info("Wake word detected! (score=%.2f)", score)
                            on_wake()
            except KeyboardInterrupt:
                log.info("Stopped listening.")

    def close(self):
        """Symmetry with the old interface; openWakeWord needs no explicit free."""
        pass