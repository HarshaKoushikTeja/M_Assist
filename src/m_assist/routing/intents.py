"""
intents.py — defines the intents M.Assist can recognize, plus example
phrases for each. The embedding router uses these examples as anchors:
it embeds them once at startup, then compares each utterance against them.

Three top-level intent TYPES drive response behaviour:
  - LOCAL_COMMAND : handled in code, short spoken reply (no LLM)
  - CHAT          : short LLM reply, spoken in full
  - QUESTION      : longer LLM reply, printed full / first paragraph spoken

Within LOCAL_COMMAND, a `command` field names the specific action so the
executor (Stage 5b) knows what to do.
"""

# Response-type constants (your "modes").
LOCAL_COMMAND = "local_command"
CHAT = "chat"
QUESTION = "question"

# Each intent: a type, an optional command name, and example phrases.
INTENTS = [
    # ---- Local commands (each maps to a concrete action in Stage 5b) ----
    {
        "type": LOCAL_COMMAND,
        "command": "save_conversation",
        "examples": ["save that", "save this", "remember that", "save the answer", "keep that"],
    },
    {
        "type": LOCAL_COMMAND,
        "command": "get_time",
        "examples": ["what time is it", "tell me the time", "current time", "what's the time"],
    },
    {
        "type": LOCAL_COMMAND,
        "command": "get_date",
        "examples": ["what's the date", "what day is it", "today's date", "what is the date today"],
    },
    {
        "type": LOCAL_COMMAND,
        "command": "screenshot",
        "examples": ["take a screenshot", "capture the screen", "screenshot", "grab a screen capture"],
    },
    {
        "type": LOCAL_COMMAND,
        "command": "open_app",
        "examples": ["open chrome", "launch notepad", "open the calculator", "start spotify", "open vs code"],
    },
    {
        "type": LOCAL_COMMAND,
        "command": "open_site",
        "examples": ["open youtube", "go to github", "open gmail", "take me to google", "open stack overflow"],
    },
    {
        "type": LOCAL_COMMAND,
        "command": "open_folder",
        "examples": ["open downloads", "open my documents folder", "open the desktop folder", "show my downloads"],
    },

    # ---- Chat (short, social, spoken in full) ----
    {
        "type": CHAT,
        "command": None,
        "examples": ["hi", "hello", "hey there", "how are you", "good morning", "thank you",
                     "tell me a joke", "what's up", "good night"],
    },

    # ---- Question (knowledge, longer, mostly printed) ----
    {
        "type": QUESTION,
        "command": None,
        "examples": [
            "what is a hashmap", "explain recursion", "how does photosynthesis work",
            "what is the capital of france", "who invented the telephone",
            "explain how neural networks learn", "what's the difference between tcp and udp",
            # added: more interrogative "what is X" / "define X" anchors
            "what is a binary tree", "what is X", "what does this mean", "define recursion",
            "what are the types of databases", "why is the sky blue", "when did world war 2 end",
            "where is the eiffel tower",
        ],
    },
]