#!/usr/bin/env python3
"""Test script for semantic intent matching."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from intelligence.semantic_engine import semantic_match


def test_semantic_engine():
    """Test semantic engine with various inputs."""
    
    test_cases = [
        "launch firefox browser",
        "can you open chrome",
        "close the terminal",
        "search for python tutorials",
        "what time is it now",
        "hello there",
        "goodbye assistant",
        "play some music please",
        "show me system info"
    ]
    
    print("=" * 60)
    print("Semantic Engine Test")
    print("=" * 60)
    print()
    
    for text in test_cases:
        intent, score = semantic_match(text)
        print(f"Input: {text}")
        print(f"  → Intent: {intent.value}")
        print(f"  → Similarity: {score:.3f}")
        print()


if __name__ == "__main__":
    test_semantic_engine()
