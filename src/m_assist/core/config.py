"""
config.py — loads config.yaml into a dot-accessible object.

Why dot-access? Writing cfg.llm.gemini.model reads far better than
cfg["llm"]["gemini"]["model"], and it fails loudly (AttributeError)
if you typo a key, instead of silently returning None.
"""

from pathlib import Path
from types import SimpleNamespace
import yaml


def _to_namespace(obj):
    """Recursively turn dicts into SimpleNamespace for dot-access.

    Lists are walked too, so a list of dicts also becomes namespaces.
    Scalars (str, int, float, bool) are returned unchanged.
    """
    if isinstance(obj, dict):
        return SimpleNamespace(**{k: _to_namespace(v) for k, v in obj.items()})
    if isinstance(obj, list):
        return [_to_namespace(item) for item in obj]
    return obj


def load_config(path: str = "config.yaml") -> SimpleNamespace:
    """Read the YAML file and return a dot-accessible config object.

    Raises FileNotFoundError with a clear message if the file is missing,
    so a fresh clone fails in an obvious way rather than cryptically.
    """
    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(
            f"Config file not found at '{config_path.resolve()}'. "
            f"Make sure config.yaml is in the project root."
        )

    with config_path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f)

    return _to_namespace(raw)


# Convenience: a module-level singleton so other modules can just do
#   from m_assist.core.config import CONFIG
# without each one re-reading the file. Lazy so import never crashes.
_CONFIG_CACHE = None


def get_config(path: str = "config.yaml") -> SimpleNamespace:
    global _CONFIG_CACHE
    if _CONFIG_CACHE is None:
        _CONFIG_CACHE = load_config(path)
    return _CONFIG_CACHE
