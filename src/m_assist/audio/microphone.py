"""
microphone.py — captures audio from the mic using sounddevice.

We chose sounddevice over PyAudio because it's far more stable on
Windows (handles WASAPI/sample-rate conversion cleanly, fewer install
headaches with PortAudio).

This module is intentionally dumb: it just yields raw int16 audio
frames. Wake word, STT, etc. consume those frames downstream.
"""

import sounddevice as sd
import numpy as np
from ..core.logger import get_logger

log = get_logger("audio.mic")


def list_devices() -> str:
    """Return a human-readable list of audio devices.

    Use this to find the integer index of your mic if the default
    device isn't the one you want (common on laptops with multiple
    inputs — built-in array mic vs headset).
    """
    return str(sd.query_devices())


class Microphone:
    """Streams mic audio as fixed-size int16 frames.

    frame_length is dictated by the consumer (Porcupine needs exactly
    512 samples per frame at 16kHz). We open a RawInputStream and read
    that many samples at a time.
    """

    def __init__(self, sample_rate: int, frame_length: int,
                 channels: int = 1, device=None):
        self.sample_rate = sample_rate
        self.frame_length = frame_length
        self.channels = channels
        self.device = device
        self._stream = None

    def __enter__(self):
        # RawInputStream gives us raw bytes we convert to int16.
        self._stream = sd.RawInputStream(
            samplerate=self.sample_rate,
            blocksize=self.frame_length,
            dtype="int16",
            channels=self.channels,
            device=self.device,
        )
        self._stream.start()
        log.info("Mic stream open @ %d Hz, frame=%d", self.sample_rate, self.frame_length)
        return self

    def __exit__(self, *exc):
        if self._stream:
            self._stream.stop()
            self._stream.close()
            log.info("Mic stream closed")

    def read_frame(self) -> np.ndarray:
        """Read one frame of audio. Returns an int16 numpy array.

        The second return value from stream.read is an 'overflowed'
        flag — True if we weren't reading fast enough and dropped audio.
        We log it because dropped frames hurt wake-word accuracy.
        """
        data, overflowed = self._stream.read(self.frame_length)
        if overflowed:
            log.warning("Audio input overflow — frame(s) dropped")
        return np.frombuffer(data, dtype=np.int16)

    def rms_level(self, frame: np.ndarray) -> float:
        """Root-mean-square loudness of a frame, normalized to ~0..1.

        Useful for a mic-level meter and later for the STT fallback
        trigger (high ambient noise -> prefer Whisper).
        """
        if frame.size == 0:
            return 0.0
        # int16 range is -32768..32767; divide to normalize.
        return float(np.sqrt(np.mean((frame.astype(np.float32) / 32768.0) ** 2)))