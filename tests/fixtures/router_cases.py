"""
router_cases.py — labeled evaluation set for the intent router.

Each case: (utterance, expected_type). This doubles as a regression
test (catches misclassifications when we tune thresholds/examples) and
as a reported accuracy benchmark.

Includes deliberately hard cases: paraphrases that rules won't catch,
and adversarial utterances that LOOK like commands but are questions.
"""

from m_assist.routing.intents import LOCAL_COMMAND, CHAT, QUESTION

ROUTER_CASES = [
    # ---- Local commands: direct ----
    ("save that", LOCAL_COMMAND),
    ("save this", LOCAL_COMMAND),
    ("what time is it", LOCAL_COMMAND),
    ("what's the date", LOCAL_COMMAND),
    ("take a screenshot", LOCAL_COMMAND),
    ("open chrome", LOCAL_COMMAND),
    ("open youtube", LOCAL_COMMAND),
    ("open downloads", LOCAL_COMMAND),

    # ---- Local commands: paraphrased (embedding tier should catch) ----
    ("can you remember this answer", LOCAL_COMMAND),
    ("tell me the current time please", LOCAL_COMMAND),
    ("could you capture the screen", LOCAL_COMMAND),
    ("launch the calculator", LOCAL_COMMAND),

    # ---- Chat: social / short ----
    ("hi", CHAT),
    ("hello there", CHAT),
    ("how are you", CHAT),
    ("good morning", CHAT),
    ("thank you", CHAT),
    ("tell me a joke", CHAT),

    # ---- Questions: clear knowledge queries ----
    ("what is a hashmap", QUESTION),
    ("what is a binary tree", QUESTION),
    ("explain recursion", QUESTION),
    ("how does photosynthesis work", QUESTION),
    ("what is the capital of france", QUESTION),
    ("what is the difference between tcp and udp", QUESTION),
    ("who invented the telephone", QUESTION),

    # ---- Adversarial: look command-ish, are actually questions ----
    ("what is a clock in cpu", QUESTION),       # contains "clock"/"time"-ish
    ("what is pytorch", QUESTION),
    ("what is the weather", QUESTION),          # not a command in our scope
    ("why is the sky blue", QUESTION),
]