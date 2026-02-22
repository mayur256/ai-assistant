"""Semantic intent matching using sentence embeddings.

Architecture:
    This module provides semantic similarity-based intent classification
    as an alternative/complement to rule-based keyword matching.
    
    Flow:
        1. Canonical phrases defined per intent
        2. Embeddings precomputed at initialization
        3. User input embedded at runtime
        4. Cosine similarity computed against all canonical phrases
        5. Best match returned with similarity score
    
    Benefits:
        - Handles paraphrasing and variations
        - More robust to typos and word order
        - Complements rule-based classifier
"""

from typing import Dict, List, Tuple
import numpy as np
from sentence_transformers import SentenceTransformer
from .schemas import Intent


# Canonical phrases per intent
# These represent typical ways users express each intent
CANONICAL_PHRASES: Dict[Intent, List[str]] = {
    Intent.OPEN_APP: [
        "open firefox",
        "launch chrome",
        "start the browser",
        "run terminal",
        "open code editor"
    ],
    Intent.CLOSE_APP: [
        "close firefox",
        "quit chrome",
        "exit the browser",
        "kill terminal",
        "stop the application"
    ],
    Intent.SEARCH_WEB: [
        "search for python documentation",
        "google machine learning",
        "look up weather forecast",
        "find information about linux"
    ],
    Intent.STOP_MUSIC: [
        "stop the music",
        "pause playback",
        "halt audio",
        "stop playing"
    ],
    Intent.GET_TIME: [
        "what time is it",
        "tell me the current time",
        "what's the time",
        "current time please"
    ],
    Intent.GET_DATE: [
        "what's today's date",
        "tell me the date",
        "what day is it",
        "current date please"
    ],
    Intent.SYSTEM_INFO: [
        "show system information",
        "what's the cpu usage",
        "check memory status",
        "display system stats"
    ],
    Intent.GREETING: [
        "hello",
        "hi there",
        "hey assistant",
        "good morning"
    ],
    Intent.EXIT: [
        "goodbye",
        "exit now",
        "quit assistant",
        "stop listening",
        "bye"
    ],
    Intent.PLAY_YOUTUBE: [
        "play despacito on youtube",
        "youtube play never gonna give you up",
        "play bohemian rhapsody video",
        "watch gangnam style on youtube",
        "play a song",
        "play music",
        "play believer by imagine dragons",
        "start a song",
        "put on music",
        "play a video",
        "search youtube and play",
        "play song on youtube"
    ],
    Intent.SEARCH_YOUTUBE: [
        "search youtube for python tutorials",
        "find videos about machine learning",
        "search for cooking videos on youtube",
        "look up travel vlogs on youtube"
    ],
}


class SemanticEngine:
    """Semantic intent matcher using sentence embeddings."""
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize semantic engine with embedding model.
        
        Args:
            model_name: SentenceTransformer model name
                       (all-MiniLM-L6-v2 is lightweight ~80MB)
        """
        print(f"→ Loading semantic model: {model_name}")
        self.model = SentenceTransformer(model_name)
        
        # Precompute embeddings for canonical phrases
        self.intent_embeddings: Dict[Intent, np.ndarray] = {}
        self._precompute_embeddings()
        print("✓ Semantic engine initialized")
    
    def _precompute_embeddings(self) -> None:
        """Precompute embeddings for all canonical phrases."""

        for intent, phrases in CANONICAL_PHRASES.items():
            # Encode all phrases for this intent
            embeddings = self.model.encode(phrases, convert_to_numpy=True)
            # Store average embedding for the intent - storing a gemotric center of the intent's phrase cluster
            # better than storing all individual phrase embeddings and comparing against them at runtime
            self.intent_embeddings[intent] = np.mean(embeddings, axis=0)
    
    def semantic_match(self, text: str) -> Tuple[Intent, float]:
        """
        Match input text to intent using semantic similarity.
        
        Args:
            text: Input text to classify
            
        Returns:
            Tuple of (best_intent, similarity_score)
            similarity_score is cosine similarity in range [0, 1]
        """
        # Encode input text
        input_embedding = self.model.encode(text, convert_to_numpy=True)
        
        # Compute cosine similarity with each intent
        similarities: Dict[Intent, float] = {}
        
        for intent, intent_embedding in self.intent_embeddings.items():
            # Cosine similarity = dot product of normalized vectors
            similarity = self._cosine_similarity(input_embedding, intent_embedding)
            similarities[intent] = similarity
        
        # Get best match
        best_intent = max(similarities, key=similarities.get)
        best_score = similarities[best_intent]
        
        return best_intent, best_score
    
    @staticmethod
    def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
        """
        Compute cosine similarity between two vectors.
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Cosine similarity in range [-1, 1], normalized to [0, 1]
        """
        # Normalize vectors
        vec1_norm = vec1 / np.linalg.norm(vec1)
        vec2_norm = vec2 / np.linalg.norm(vec2)
        
        # Compute dot product
        similarity = np.dot(vec1_norm, vec2_norm)
        
        # Normalize to [0, 1] range
        return (similarity + 1) / 2


# Module-level instance (lazy initialization)
_semantic_engine: SemanticEngine | None = None


def get_semantic_engine() -> SemanticEngine:
    """
    Get or create semantic engine instance (singleton pattern).
    
    Returns:
        Initialized SemanticEngine instance
    """
    global _semantic_engine
    if _semantic_engine is None:
        _semantic_engine = SemanticEngine()
    return _semantic_engine


def semantic_match(text: str) -> Tuple[Intent, float]:
    """
    Convenience function for semantic intent matching.
    
    Args:
        text: Input text to classify
        
    Returns:
        Tuple of (intent, similarity_score)
    """
    engine = get_semantic_engine()
    return engine.semantic_match(text)
