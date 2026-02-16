"""Rule-based intent classifier."""

from typing import Dict, Any
from .schemas import Intent, IntentResult
from .intents import INTENT_PATTERNS, KNOWN_APPS


def classify(text: str) -> IntentResult:
    """
    Classify intent using rule-based keyword matching.
    
    Args:
        text: Input text to classify
        
    Returns:
        IntentResult with intent, confidence, and extracted slots
    """
    normalized = text.lower().strip()
    
    # Score each intent
    scores: Dict[Intent, float] = {}
    
    for intent, keywords in INTENT_PATTERNS.items():
        score = 0.0
        matched_keywords = 0
        
        for keyword in keywords:
            if keyword in normalized:
                matched_keywords += 1
                # Exact word match gets higher score
                if f" {keyword} " in f" {normalized} ":
                    score += 1.0
                else:
                    score += 0.5
        
        if matched_keywords > 0:
            scores[intent] = score / len(keywords)
    
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
    
    # Extract slots
    slots = _extract_slots(normalized, best_intent)
    
    return IntentResult(
        intent=best_intent,
        confidence=confidence,
        slots=slots,
        raw_text=text
    )


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
    
    return slots
