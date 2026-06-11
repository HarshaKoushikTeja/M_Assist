"""
test_rate_limiter.py — unit tests for the sliding-window rate limiter.

No model loading, no network — pure logic, runs in milliseconds. This is
the kind of fast deterministic test CI loves.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from m_assist.llm.rate_limiter import RateLimiter


def test_allows_under_limit():
    rl = RateLimiter(requests_per_minute=3, requests_per_day=100)
    assert rl.allow() is True
    rl.record()
    assert rl.allow() is True


def test_blocks_at_minute_limit():
    rl = RateLimiter(requests_per_minute=2, requests_per_day=100)
    rl.record()
    rl.record()
    # Two recorded, limit is two -> next should be blocked.
    assert rl.allow() is False


def test_blocks_at_day_limit():
    rl = RateLimiter(requests_per_minute=100, requests_per_day=2)
    rl.record()
    rl.record()
    assert rl.allow() is False


def test_status_string():
    rl = RateLimiter(requests_per_minute=5, requests_per_day=50)
    rl.record()
    status = rl.status()
    assert "1/5" in status and "1/50" in status