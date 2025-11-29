"""
Emotion tag parser for IndexTTS application

Parses text with emotion tags like:
[Calm:60,Happy:40]Now I've been waiting patiently [angry:30] It's been 2 weeks
[angry:60,hate:80] Now I want my $2 Mister!

Supports:
- Multiple emotions per segment
- Intensity values (0-100)
- Case-insensitive emotion names
- Overlapping emotion segments
"""

import re
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict


# Map emotion names to indices in emotion vector
# Order: [happy, angry, sad, afraid, disgusted, melancholic, surprised, calm]
EMOTION_MAP = {
    "happy": 0,
    "angry": 1,
    "sad": 2,
    "afraid": 3,
    "fear": 3,
    "disgusted": 4,
    "disgust": 4,
    "melancholic": 5,
    "melancholy": 5,
    "sad_melancholic": 5,
    "surprised": 6,
    "surprise": 6,
    "calm": 7,
    "peaceful": 7,
}


@dataclass
class EmotionSegment:
    """Represents a text segment with associated emotions"""
    text: str
    start_char: int
    end_char: int
    emotions: Dict[str, float]  # emotion_name -> intensity (0-100)
    
    def to_emotion_vector(self) -> List[float]:
        """Convert emotions to IndexTTS2 emotion vector format"""
        vector = [0.0] * 8  # 8 emotions
        for emotion_name, intensity in self.emotions.items():
            emotion_idx = EMOTION_MAP.get(emotion_name.lower())
            if emotion_idx is not None:
                # Normalize intensity to 0-1 range
                normalized = intensity / 100.0
                vector[emotion_idx] = max(vector[emotion_idx], normalized)
        return vector


class EmotionTagParser:
    """Parser for emotion-tagged text"""
    
    # Pattern to match [emotion:intensity,emotion:intensity]
    TAG_PATTERN = re.compile(r'\[([^\]]+)\]')
    
    @staticmethod
    def parse_tag(tag_content: str) -> Dict[str, float]:
        """
        Parse a single tag like 'Calm:60,Happy:40'
        
        Args:
            tag_content: The content inside [ ]
            
        Returns:
            Dictionary mapping emotion names to intensities
        """
        emotions = {}
        # Split by comma for multiple emotions
        for emotion_spec in tag_content.split(','):
            emotion_spec = emotion_spec.strip()
            if ':' in emotion_spec:
                emotion_name, intensity_str = emotion_spec.split(':', 1)
                emotion_name = emotion_name.strip()
                try:
                    intensity = float(intensity_str.strip())
                    # Clamp intensity to 0-100
                    intensity = max(0.0, min(100.0, intensity))
                    emotions[emotion_name.lower()] = intensity
                except ValueError:
                    # Skip malformed intensity values
                    pass
        return emotions
    
    @classmethod
    def parse(cls, text: str) -> Tuple[List[EmotionSegment], str]:
        """
        Parse text with emotion tags
        
        Args:
            text: Text with emotion tags like [Calm:60,Happy:40]Some text[angry:30]more text
            
        Returns:
            Tuple of (EmotionSegments, plain_text_without_tags)
        """
        segments = []
        plain_text = ""
        current_emotions = {}
        last_end = 0
        char_offset = 0  # Track character position in plain text
        
        # Find all tags and their positions
        for match in cls.TAG_PATTERN.finditer(text):
            tag_start = match.start()
            tag_end = match.end()
            tag_content = match.group(1)
            
            # Add text before this tag
            text_before = text[last_end:tag_start]
            if text_before:
                segment = EmotionSegment(
                    text=text_before,
                    start_char=char_offset,
                    end_char=char_offset + len(text_before),
                    emotions=current_emotions.copy()
                )
                segments.append(segment)
                plain_text += text_before
                char_offset += len(text_before)
            
            # Update current emotions
            new_emotions = cls.parse_tag(tag_content)
            current_emotions.update(new_emotions)
            
            last_end = tag_end
        
        # Add remaining text after last tag
        remaining_text = text[last_end:]
        if remaining_text:
            segment = EmotionSegment(
                text=remaining_text,
                start_char=char_offset,
                end_char=char_offset + len(remaining_text),
                emotions=current_emotions.copy()
            )
            segments.append(segment)
            plain_text += remaining_text
        
        # Filter out empty segments
        segments = [s for s in segments if s.text.strip()]
        
        return segments, plain_text
    
    @classmethod
    def parse_to_vectors(cls, text: str) -> Tuple[List[Tuple[str, List[float]]], str]:
        """
        Parse text and convert emotions to vectors
        
        Args:
            text: Text with emotion tags
            
        Returns:
            Tuple of (list of (text_segment, emotion_vector), plain_text)
        """
        segments, plain_text = cls.parse(text)
        vectors = [(seg.text, seg.to_emotion_vector()) for seg in segments]
        return vectors, plain_text


def parse_emotion_tags(text: str) -> Tuple[List[EmotionSegment], str]:
    """
    Convenience function to parse emotion tags in text
    
    Args:
        text: Text with emotion tags
        
    Returns:
        Tuple of (EmotionSegments, plain_text)
    """
    return EmotionTagParser.parse(text)


def parse_emotion_tags_to_vectors(text: str) -> Tuple[List[Tuple[str, List[float]]], str]:
    """
    Parse emotion tags and return text segments with emotion vectors
    
    Args:
        text: Text with emotion tags
        
    Returns:
        Tuple of (list of (text_segment, emotion_vector), plain_text)
    """
    return EmotionTagParser.parse_to_vectors(text)
