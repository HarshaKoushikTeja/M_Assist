"""
rule_router.py — tier 1: fast, exact/keyword rules.

Runs FIRST. If an utterance clearly matches a rule (e.g. starts with
"open " or exactly contains "save that"), we classify it instantly
without touching embeddings. Rules are cheap and deterministic — ideal
for unambiguous commands.

Returns a match dict {type, command} or None if no rule fires (then the
embedding tier takes over).
"""

import re
from .intents import LOCAL_COMMAND
from ..core.logger import get_logger

log = get_logger("routing.rules")

# Patterns that map directly to a local command, checked in order.
# Each is (compiled regex, command name).
_RULES = [
    (re.compile(r"\b(save|keep|remember)\s+(that|this|the answer|it)\b"), "save_conversation"),
    (re.compile(r"\b(what(?:'s| is)?\s+the\s+time|what time is it|current time)\b"), "get_time"),
    (re.compile(r"\b(what(?:'s| is)?\s+(?:the\s+)?date|what day is it|today's date)\b"), "get_date"),
    (re.compile(r"\b(take a |capture (?:the )?)?screenshot\b|capture the screen"), "screenshot"),
    (re.compile(r"^\s*(open|launch|start)\s+the\s+(.+?)\s+folder\b"), "open_folder"),
    (re.compile(r"^\s*(open|launch|start|go to)\s+(.+)$"), "_open_ambiguous"),
]


def match(text: str):
    """Return {type, command, target} if a rule fires, else None.

    'target' is the captured object of an open command (e.g. 'chrome',
    'youtube') — Stage 5b's executor resolves it against the allowlist
    to decide whether it's an app, site, or folder.
    """
    t = text.lower().strip()

    for pattern, command in _RULES:
        m = pattern.search(t)
        if not m:
            continue

        if command == "open_folder":
            target = m.group(2).strip()
            log.info("Rule matched open_folder: %r", target)
            return {"type": LOCAL_COMMAND, "command": "open_folder", "target": target}

        if command == "_open_ambiguous":
            # "open X" — we don't yet know if X is an app/site/folder.
            # Defer resolution to the executor's allowlist (Stage 5b).
            target = m.group(2).strip()
            log.info("Rule matched open (ambiguous): %r", target)
            return {"type": LOCAL_COMMAND, "command": "open", "target": target}

        log.info("Rule matched command: %s", command)
        return {"type": LOCAL_COMMAND, "command": command, "target": None}

    return None