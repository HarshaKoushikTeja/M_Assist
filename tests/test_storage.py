"""
test_storage.py — unit tests for conversation storage (slug + save).
Uses pytest's tmp_path so it never touches your real saved_conversations/.
"""

import sys
from pathlib import Path
from types import SimpleNamespace

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from m_assist.storage import ConversationStore


def _make_store(tmp_path):
    cfg = SimpleNamespace(save_enabled=True, save_dir=str(tmp_path / "saved"),
                          save_phrases=["save that"])
    return ConversationStore(cfg)


def test_slug_strips_punctuation(tmp_path):
    store = _make_store(tmp_path)
    assert store._slug("What's a HashMap? (in Java)") == "whats-a-hashmap-in-java"


def test_slug_handles_empty(tmp_path):
    store = _make_store(tmp_path)
    assert store._slug("???") == "turn"


def test_save_creates_file(tmp_path):
    store = _make_store(tmp_path)
    path = store.save_turn("what is a hashmap", "A hashmap is a data structure.")
    assert path is not None
    assert path.exists()
    content = path.read_text(encoding="utf-8")
    assert "what is a hashmap" in content
    assert "data structure" in content


def test_disabled_store_saves_nothing(tmp_path):
    cfg = SimpleNamespace(save_enabled=False, save_dir=str(tmp_path / "saved"),
                          save_phrases=["save that"])
    store = ConversationStore(cfg)
    assert store.save_turn("q", "a") is None