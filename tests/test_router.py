"""
test_router.py — router accuracy benchmark + regression guard.

Loads the router once (embedding model load is slow), runs every labeled
case, and:
  - asserts overall accuracy stays above a floor (regression guard)
  - prints a per-category breakdown and any misclassifications

Run with:  pytest tests/test_router.py -v -s
The -s flag shows the printed accuracy report.
"""

import sys
from pathlib import Path
import pytest

# Make src importable.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from m_assist.core.config import load_config
from m_assist.routing.router import Router
from tests.fixtures.router_cases import ROUTER_CASES

# Accuracy floor — the test fails if the router drops below this.
ACCURACY_FLOOR = 0.90   # regression guard — set below current 100% to allow adding hard cases


@pytest.fixture(scope="module")
def router():
    """Build the router once for all tests (embedding load is expensive)."""
    cfg = load_config(str(PROJECT_ROOT / "config.yaml"))
    return Router(cfg.router)


def test_router_accuracy(router):
    """Run the full labeled set and assert accuracy above the floor."""
    correct = 0
    misses = []

    for utterance, expected in ROUTER_CASES:
        result = router.route(utterance)
        got = result["type"]
        if got == expected:
            correct += 1
        else:
            misses.append((utterance, expected, got, result.get("score")))

    total = len(ROUTER_CASES)
    accuracy = correct / total

    # Report (visible with pytest -s).
    print(f"\n{'='*55}")
    print(f"ROUTER ACCURACY: {correct}/{total} = {accuracy:.1%}")
    print(f"{'='*55}")
    if misses:
        print("Misclassifications:")
        for utt, exp, got, score in misses:
            score_str = f"{score:.2f}" if score is not None else "n/a"
            print(f"  {utt!r}: expected {exp}, got {got} (score {score_str})")
    else:
        print("No misclassifications. 🎯")
    print()

    assert accuracy >= ACCURACY_FLOOR, (
        f"Router accuracy {accuracy:.1%} fell below floor {ACCURACY_FLOOR:.0%}"
    )


@pytest.mark.parametrize("utterance,expected", ROUTER_CASES)
def test_individual_cases(router, utterance, expected):
    """Each case as its own test — pinpoints exactly which utterance breaks."""
    result = router.route(utterance)
    assert result["type"] == expected, (
        f"{utterance!r}: expected {expected}, got {result['type']} "
        f"(tier={result.get('tier')}, score={result.get('score')})"
    )