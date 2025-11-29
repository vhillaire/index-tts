"""Emotion tag parsing and emotion vector generation"""

from .parser import (
    parse_emotion_tags,
    parse_emotion_tags_to_vectors,
    EmotionSegment,
    EmotionTagParser
)
from .utils import text_to_emotion_vector

__all__ = [
    "parse_emotion_tags",
    "parse_emotion_tags_to_vectors",
    "EmotionSegment",
    "EmotionTagParser",
    "text_to_emotion_vector"
]
