"""Data schemas for intent classification."""

from enum import Enum
from typing import Dict, Any
from pydantic import BaseModel, Field


class Intent(str, Enum):
    """Supported intents."""
    OPEN_APP = "OPEN_APP"
    CLOSE_APP = "CLOSE_APP"
    SEARCH_WEB = "SEARCH_WEB"
    PLAY_MUSIC = "PLAY_MUSIC"
    STOP_MUSIC = "STOP_MUSIC"
    GET_TIME = "GET_TIME"
    GET_DATE = "GET_DATE"
    SYSTEM_INFO = "SYSTEM_INFO"
    GREETING = "GREETING"
    EXIT = "EXIT"
    PLAY_YOUTUBE = "PLAY_YOUTUBE"
    SEARCH_YOUTUBE = "SEARCH_YOUTUBE"
    UNKNOWN = "UNKNOWN"


class IntentResult(BaseModel):
    """Result of intent classification."""
    intent: Intent
    confidence: float = Field(ge=0.0, le=1.0)
    slots: Dict[str, Any] = Field(default_factory=dict)
    raw_text: str
    
    class Config:
        use_enum_values = False
