"""Rule-based intent classifier with weighted scoring."""

from typing import Dict, Any
from .schemas import Intent, IntentResult
from .intents import INTENT_PATTERNS, KNOWN_APPS


def classify(text: str) -> IntentResult:
    """
    Classify intent using weighted rule-based scoring.
    
    Args:
        text: Input text to classify
        
    Returns:
        IntentResult with intent, confidence, and extracted slots
    """
    normalized = text.lower().strip()
    words = normalized.split()
    
    # Score each intent using weighted rules
    scores: Dict[Intent, float] = {}
    
    for intent in Intent:
        if intent == Intent.UNKNOWN:
            continue
            
        score = _score_intent(normalized, words, intent)
        if score > 0:
            scores[intent] = score
    
    # Get best intent
    if not scores:
        return IntentResult(
            intent=Intent.UNKNOWN,
            confidence=0.0,
            slots={},
            raw_text=text
        )
    
    best_intent = max(scores, key=scores.get)
    confidence = min(scores[best_intent], 1.0)
    
    # Return UNKNOWN if confidence too low
    if confidence < 0.4:
        return IntentResult(
            intent=Intent.UNKNOWN,
            confidence=confidence,
            slots={},
            raw_text=text
        )
    
    # Extract slots
    slots = _extract_slots(normalized, best_intent)
    
    return IntentResult(
        intent=best_intent,
        confidence=confidence,
        slots=slots,
        raw_text=text
    )


def _score_intent(text: str, words: list, intent: Intent) -> float:
    """
    Calculate weighted confidence score for specific intent.
    
    Args:
        text: Normalized input text
        words: Split words from text
        intent: Intent to score
        
    Returns:
        Confidence score (0.0-1.0+, normalized later)
    """
    score = 0.0
    
    # Base keyword matching
    keywords = INTENT_PATTERNS.get(intent, [])
    for keyword in keywords:
        if keyword in text:
            # Exact word match gets higher score
            if f" {keyword} " in f" {text} ":
                score += 0.3
            else:
                score += 0.1
    
    # Intent-specific weighted scoring
    if intent == Intent.OPEN_APP:
        # +0.5 if command starts with "open" or "launch"
        if words and words[0] in ["open", "launch"]:
            score += 0.5
        
        # +0.3 if known app name detected
        for app in KNOWN_APPS:
            if app in text:
                score += 0.3
                break
        
        # +0.2 if concise command (<=4 words)
        if len(words) <= 4:
            score += 0.2
    
    elif intent == Intent.CLOSE_APP:
        # Similar logic for close commands
        if words and words[0] in ["close", "quit", "exit", "kill"]:
            score += 0.4
        
        for app in KNOWN_APPS:
            if app in text:
                score += 0.3
                break
                
        if len(words) <= 4:
            score += 0.2
    
    elif intent == Intent.SEARCH_WEB:
        # Boost if starts with search terms
        if words and words[0] in ["search", "google", "find"]:
            score += 0.4
        
        # Boost if has "for" indicating query
        if " for " in text:
            score += 0.2
    
    elif intent in [Intent.GET_TIME, Intent.GET_DATE]:
        # Boost question patterns
        if text.startswith("what"):
            score += 0.3
        
        if "is" in text:
            score += 0.2
    
    elif intent in [Intent.STOP_MUSIC]:
        # Boost direct commands
        if words and words[0] in ["stop", "pause"]:
            score += 0.4
    
    elif intent == Intent.PLAY_YOUTUBE:
        # Boost if starts with play/start/put on
        if words and words[0] in ["play", "start", "put"]:
            score += 0.6
        
        # Boost if has enough content (2+ additional tokens)
        if len(words) >= 3:
            score += 0.3
        
        # Boost if contains "by" (artist indicator)
        if "by" in text:
            score += 0.2
    
    elif intent == Intent.SYSTEM_INFO:
        # Boost system-related queries
        if "system" in text or "status" in text:
            score += 0.4
        
        # Boost specific info requests
        if any(word in text for word in ["cpu", "memory", "disk", "info"]):
            score += 0.3
    
    elif intent == Intent.GREETING:
        # Boost if starts with greeting
        if words and words[0] in ["hello", "hi", "hey"]:
            score += 0.6
        
        # Boost short greetings (1-3 words)
        if len(words) <= 3:
            score += 0.3
    
    elif intent == Intent.EXIT:
        # Boost exit commands at start
        if words and words[0] in ["exit", "quit", "goodbye", "bye"]:
            score += 0.6
        
        # Boost if contains "stop" + assistant context
        if "stop" in text and any(word in text for word in ["listening", "assistant"]):
            score += 0.3
    
    return score


def _extract_slots(text: str, intent: Intent) -> Dict[str, Any]:
    """
    Extract slot values from text based on intent.
    
    Args:
        text: Normalized input text
        intent: Detected intent
        
    Returns:
        Dictionary of extracted slots
    """
    slots: Dict[str, Any] = {}
    
    # Extract app name for app-related intents
    if intent in (Intent.OPEN_APP, Intent.CLOSE_APP):
        for app in KNOWN_APPS:
            if app in text:
                slots["app_name"] = app
                break
    
    # Extract search query for web search
    if intent == Intent.SEARCH_WEB:
        # Remove trigger words to get query
        query = text
        for trigger in ["search", "google", "look up", "find", "for"]:
            query = query.replace(trigger, "")
        query = query.strip()
        if query:
            slots["query"] = query
    
    # Extract YouTube query
    if intent in (Intent.PLAY_YOUTUBE, Intent.SEARCH_YOUTUBE):
        # Remove trigger words to get clean query
        query = text
        trigger_words = [
            "play", "start", "put on", "search", "on youtube", "youtube", 
            "video", "please", "can you", "could you", "find", "for", "a"
        ]
        for trigger in trigger_words:
            query = query.replace(trigger, "")
        query = query.strip()
        if query:
            slots["query"] = query
    
    return slots
