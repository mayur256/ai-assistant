#!/usr/bin/env python3
"""Test PLAY_YOUTUBE intent classification."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from intelligence.hybrid_classifier import classify_hybrid


def test_play_youtube():
    """Test PLAY_YOUTUBE classification with various inputs."""
    
    test_cases = [
        "Play Believer by Imagine Dragons",
        "play despacito",
        "start a song",
        "put on music",
        "play bohemian rhapsody",
        "play some music",
    ]
    
    print("=" * 70)
    print("PLAY_YOUTUBE Intent Classification Test")
    print("=" * 70)
    print()
    
    for text in test_cases:
        result = classify_hybrid(text)
        intent_result = result["intent_result"]
        
        print(f"Input: \"{text}\"")
        print(f"  Rule Intent: {result['rule_intent']}")
        print(f"  Rule Confidence: {result['rule_confidence']:.3f}")
        
        if result['semantic_intent']:
            print(f"  Semantic Intent: {result['semantic_intent']}")
            print(f"  Semantic Similarity: {result['semantic_similarity']:.3f}")
        
        print(f"  Decision Source: {result['decision_source'].upper()}")
        print(f"  Final Intent: {intent_result.intent.value}")
        print(f"  Final Confidence: {intent_result.confidence:.3f}")
        print(f"  Extracted Query: {intent_result.slots.get('query', 'N/A')}")
        print()


if __name__ == "__main__":
    test_play_youtube()
