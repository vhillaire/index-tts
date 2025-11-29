"""Utility functions for emotion handling"""

from typing import List, Dict, Optional

from .parser import EmotionTagParser, EMOTION_MAP


def text_to_emotion_vector(
    text: str,
    emotion_description: str = "",
    default_intensity: float = 0.5
) -> List[float]:
    """
    Convert emotion description to emotion vector
    
    This is a helper for when you want to manually specify emotions
    without using the tag syntax.
    
    Args:
        text: The text (for context, currently unused)
        emotion_description: Comma-separated emotions like "happy,calm"
        default_intensity: Default intensity if not specified (0-1)
        
    Returns:
        8-element emotion vector for IndexTTS2
    """
    
    vector = [0.0] * 8
    
    if not emotion_description:
        return vector
    
    # Simple case: no intensities specified
    if ':' not in emotion_description:
        emotions = [e.strip().lower() for e in emotion_description.split(',')]
        for emotion in emotions:
            emotion_idx = EMOTION_MAP.get(emotion)
            if emotion_idx is not None:
                vector[emotion_idx] = default_intensity
    else:
        # Parse with intensities: happy:0.8,calm:0.5
        tag_content = emotion_description.replace(':', ':').replace('%', '')
        emotions = EmotionTagParser.parse_tag(tag_content)
        for emotion_name, intensity in emotions.items():
            emotion_idx = EMOTION_MAP.get(emotion_name.lower())
            if emotion_idx is not None:
                vector[emotion_idx] = min(1.0, intensity / 100.0)
    
    return vector


def merge_emotion_vectors(
    vectors: List[List[float]],
    weights: Optional[List[float]] = None
) -> List[float]:
    """
    Merge multiple emotion vectors with optional weights
    
    Args:
        vectors: List of emotion vectors
        weights: Optional weights for each vector (will be normalized)
        
    Returns:
        Merged emotion vector
    """
    if not vectors:
        return [0.0] * 8
    
    if weights is None:
        weights = [1.0] * len(vectors)
    else:
        # Normalize weights
        total = sum(weights)
        weights = [w / total for w in weights]
    
    merged = [0.0] * 8
    for vector, weight in zip(vectors, weights):
        for i, emotion_val in enumerate(vector):
            merged[i] += emotion_val * weight
    
    # Ensure values don't exceed 1.0
    merged = [min(1.0, val) for val in merged]
    
    return merged


def normalize_emotion_vector(vector: List[float]) -> List[float]:
    """
    Normalize emotion vector so max value is 1.0
    
    Args:
        vector: Emotion vector
        
    Returns:
        Normalized vector
    """
    max_val = max(vector) if vector else 1.0
    if max_val == 0.0:
        return vector
    return [v / max_val for v in vector]
