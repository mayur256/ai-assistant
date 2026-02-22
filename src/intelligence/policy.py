"""Policy layer for intent execution decisions."""

import logging
from pathlib import Path
from datetime import datetime
from .schemas import Intent, IntentResult


# Configure logging
def setup_logging(log_dir: Path) -> None:
    """
    Setup structured logging to file.
    
    Args:
        log_dir: Directory for log files
    """
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / "assistant.log"
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )


def get_action_description(intent_result: IntentResult) -> str:
    """
    Generate human-readable action description from intent.
    
    Args:
        intent_result: Classified intent result
        
    Returns:
        Human-readable action description
    """
    intent = intent_result.intent
    slots = intent_result.slots
    
    if intent == Intent.OPEN_APP:
        app = slots.get("app_name", "an application")
        return f"open {app}"
    elif intent == Intent.CLOSE_APP:
        app = slots.get("app_name", "an application")
        return f"close {app}"
    elif intent == Intent.SEARCH_WEB:
        query = slots.get("query", "something")
        return f"search for {query}"
    elif intent == Intent.STOP_MUSIC:
        return "stop music"
    elif intent == Intent.GET_TIME:
        return "tell you the time"
    elif intent == Intent.GET_DATE:
        return "tell you the date"
    elif intent == Intent.SYSTEM_INFO:
        return "show system information"
    elif intent == Intent.GREETING:
        return "greet you"
    elif intent == Intent.EXIT:
        return "exit"
    elif intent == Intent.PLAY_YOUTUBE:
        query = slots.get("query", "a video")
        return f"play {query} on YouTube"
    elif intent == Intent.SEARCH_YOUTUBE:
        query = slots.get("query", "something")
        return f"search YouTube for {query}"
    else:
        return "do something"


def decide_action(intent_result: IntentResult) -> tuple[str, bool]:
    """
    Policy layer: Decide whether to execute based on confidence.
    
    Decision thresholds:
    - UNKNOWN intent: Always reject, ask to repeat
    - confidence < 0.6: Too low, ask to repeat
    - 0.6 <= confidence < 0.75: Medium, ask confirmation
    - confidence >= 0.75: High, execute immediately
    
    Args:
        intent_result: Classified intent result
        
    Returns:
        Tuple of (response_text, should_execute)
    """
    # Log the intent classification
    logging.info(
        f"Intent: {intent_result.intent.value} | "
        f"Confidence: {intent_result.confidence:.2f} | "
        f"Transcript: {intent_result.raw_text}"
    )
    
    # Policy 1: UNKNOWN intent - always reject
    if intent_result.intent == Intent.UNKNOWN:
        return "I did not understand that. Could you repeat?", False
    
    # Policy 2: Low confidence - ask to repeat
    if intent_result.confidence < 0.6:
        return "I'm not sure what you said. Please repeat.", False
    
    # Policy 3: Medium confidence - ask confirmation
    if intent_result.confidence < 0.75:
        action = get_action_description(intent_result)
        return f"Did you want me to {action}?", False
    
    # Policy 4: High confidence - execute
    return f"Intent detected: {intent_result.intent.value}", True
