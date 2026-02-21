"""Hybrid intent classifier combining rule-based and semantic approaches.

Architecture:
    Primary: Rule-based classifier (fast, deterministic)
    Fallback: Semantic matcher (handles paraphrasing, variations)
    
    Decision Flow:
        1. Run rule-based classifier
        2. If confidence >= 0.75 → Use rule result
        3. If confidence < 0.75 → Try semantic fallback
        4. If semantic similarity >= 0.80 → Use semantic result
        5. Otherwise → UNKNOWN
"""

import logging
from typing import Dict, Any
from .schemas import Intent, IntentResult
from . import classifier as rule_classifier
from .semantic_engine import semantic_match


def classify_hybrid(text: str) -> Dict[str, Any]:
    """
    Classify intent using hybrid approach (rule-based + semantic fallback).
    
    Strategy:
        - Rule-based is primary (fast, deterministic)
        - Semantic is fallback for low confidence cases
        - Semantic threshold: 0.80 (high similarity required)
    
    Args:
        text: Input text to classify
        
    Returns:
        Dictionary containing:
            - intent_result: Final IntentResult
            - rule_intent: Intent from rule classifier
            - rule_confidence: Confidence from rule classifier
            - semantic_intent: Intent from semantic matcher (if used)
            - semantic_similarity: Similarity score (if used)
            - decision_source: "rule" or "semantic"
    """
    # Step 1: Run rule-based classifier
    rule_result = rule_classifier.classify(text)
    
    result_data = {
        "rule_intent": rule_result.intent.value,
        "rule_confidence": rule_result.confidence,
        "semantic_intent": None,
        "semantic_similarity": None,
        "decision_source": "rule"
    }
    
    # Step 2: Check if rule confidence is high enough
    if rule_result.confidence >= 0.75:
        # High confidence - use rule result directly
        result_data["intent_result"] = rule_result
        logging.info(
            f"Hybrid Decision: RULE | "
            f"Rule: {rule_result.intent.value}({rule_result.confidence:.2f})"
        )
        return result_data
    
    # Step 3: Low confidence - try semantic fallback
    semantic_intent, semantic_similarity = semantic_match(text)
    
    result_data["semantic_intent"] = semantic_intent.value
    result_data["semantic_similarity"] = semantic_similarity
    
    # Step 4: Check semantic similarity threshold
    if semantic_similarity >= 0.83:
        # High semantic similarity - override with semantic result
        semantic_result = IntentResult(
            intent=semantic_intent,
            confidence=semantic_similarity,
            slots=rule_result.slots,  # Keep slots from rule classifier
            raw_text=text
        )
        result_data["intent_result"] = semantic_result
        result_data["decision_source"] = "semantic"
        
        logging.info(
            f"Hybrid Decision: SEMANTIC | "
            f"Rule: {rule_result.intent.value}({rule_result.confidence:.2f}) | "
            f"Semantic: {semantic_intent.value}({semantic_similarity:.2f})"
        )
        return result_data
    
    # Step 5: Both low confidence - return UNKNOWN
    unknown_result = IntentResult(
        intent=Intent.UNKNOWN,
        confidence=0.0,
        slots={},
        raw_text=text
    )
    result_data["intent_result"] = unknown_result
    result_data["decision_source"] = "none"
    
    logging.info(
        f"Hybrid Decision: UNKNOWN | "
        f"Rule: {rule_result.intent.value}({rule_result.confidence:.2f}) | "
        f"Semantic: {semantic_intent.value}({semantic_similarity:.2f})"
    )
    
    return result_data
