"""
recorder.py — records a spoken command after the wake word fires.

Strategy: keep reading mic frames until the user goes silent for
`silence_duration_s`, or we hit `max_seconds`. This "endpointing" means
the user doesn't have to press anything — they just stop talking.

Returns the full recording as one int16 numpy array, plus the average
RMS (loudness) so the transcriber can decide whether ambient noise
warrants the Whisper fallback.
"""

import time
import numpy as np
from .microphone import Microphone
from ..core.logger import get_logger

log = get_logger("audio.recorder")

CHUNK_SAMPLES = 1280   # 80ms @ 16kHz, same chunk size as wake word


class Recorder:
    def __init__(self, cfg_audio, cfg_record):
        self.sample_rate = cfg_audio.sample_rate
        self.channels = cfg_audio.channels
        self.device = cfg_audio.input_device
        self.max_seconds = cfg_record.max_seconds
        self.silence_rms = cfg_record.silence_rms
        self.silence_duration_s = cfg_record.silence_duration_s

    def record_command(self):
        """Record until silence (after speech) or max_seconds. Returns (audio_int16, avg_rms)."""
        frames = []
        rms_values = []
        silence_started = None
        has_spoken = False          # NEW: don't endpoint until real speech begins
        start = time.time()

        with Microphone(self.sample_rate, CHUNK_SAMPLES,
                        self.channels, self.device) as mic:
            log.info("Recording command... (speak now)")
            while True:
                frame = mic.read_frame()
                frames.append(frame)
                level = mic.rms_level(frame)
                rms_values.append(level)

                now = time.time()

                if level >= self.silence_rms:
                    has_spoken = True        # speech detected
                    silence_started = None   # reset silence tracking

                # Only start counting silence AFTER the user has spoken.
                elif has_spoken:
                    if silence_started is None:
                        silence_started = now
                    elif now - silence_started >= self.silence_duration_s:
                        log.info("Silence after speech — done recording.")
                        break

                # Hard cap regardless.
                if now - start >= self.max_seconds:
                    log.info("Max record time reached.")
                    break

        audio = np.concatenate(frames) if frames else np.array([], dtype=np.int16)
        avg_rms = float(np.mean(rms_values)) if rms_values else 0.0
        log.info("Captured %.1fs of audio (avg RMS %.3f)",
                 len(audio) / self.sample_rate, avg_rms)
        return audio, avg_rms