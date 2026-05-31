"""
logger.py — central logging setup.

One configured logger, reused everywhere via get_logger(__name__).
Writes to console (for live dev) and a rotating file (so logs/ never
balloons). Level and destinations come from config.yaml.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


_CONFIGURED = False


def setup_logging(cfg) -> None:
    """Configure the root 'm_assist' logger once, from config.

    Safe to call multiple times — guarded so handlers aren't duplicated
    (a classic bug that makes every log line print 2-3 times).
    """
    global _CONFIGURED
    if _CONFIGURED:
        return

    level = getattr(logging, cfg.logging.level.upper(), logging.INFO)

    logger = logging.getLogger("m_assist")
    logger.setLevel(level)

    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    # Console handler
    if cfg.logging.console:
        console = logging.StreamHandler()
        console.setFormatter(fmt)
        logger.addHandler(console)

    # Rotating file handler — make sure the logs/ dir exists first
    log_path = Path(cfg.logging.file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        log_path, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    _CONFIGURED = True


def get_logger(name: str) -> logging.Logger:
    """Return a child logger under the 'm_assist' namespace.

    Use as: log = get_logger(__name__)
    Children inherit the handlers/level set up in setup_logging().
    """
    return logging.getLogger(f"m_assist.{name}")
