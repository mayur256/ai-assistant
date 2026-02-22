"""Intent definitions and example phrases."""

from typing import List, Dict
from .schemas import Intent


# Intent patterns: keywords that trigger each intent
INTENT_PATTERNS: Dict[Intent, List[str]] = {
    Intent.OPEN_APP: [
        "open", "launch", "start", "run"
    ],
    Intent.CLOSE_APP: [
        "close", "quit", "exit", "kill", "stop"
    ],
    Intent.SEARCH_WEB: [
        "search", "google", "look up", "find"
    ],
    Intent.STOP_MUSIC: [
        "stop", "pause", "halt"
    ],
    Intent.GET_TIME: [
        "time", "what time", "current time"
    ],
    Intent.GET_DATE: [
        "date", "what date", "today", "current date"
    ],
    Intent.SYSTEM_INFO: [
        "system", "info", "status", "cpu", "memory", "disk"
    ],
    Intent.GREETING: [
        "hello", "hi", "hey", "greetings"
    ],
    Intent.EXIT: [
        "exit", "quit", "goodbye", "bye", "stop"
    ],
    Intent.PLAY_YOUTUBE: [
        "play", "youtube", "video", "song", "music"
    ],
    Intent.SEARCH_YOUTUBE: [
        "search", "youtube", "find", "video"
    ],
}


# Common app names for slot extraction
KNOWN_APPS = [
    "firefox", "chrome", "code", "terminal", "spotify",
    "slack", "discord", "vscode", "browser"
]
