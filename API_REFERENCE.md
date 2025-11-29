# IndexTTS Standalone - API Reference

## Quick Reference

### Emotion Parsing

```python
from indextts_app.emotion import (
    parse_emotion_tags,
    parse_emotion_tags_to_vectors,
    EmotionTagParser,
    EmotionSegment,
    text_to_emotion_vector
)

# Parse text with emotion tags
segments, plain_text = parse_emotion_tags(text)
segments, plain_text = parse_emotion_tags_to_vectors(text)

# Advanced parsing
parser = EmotionTagParser()
segments, plain_text = parser.parse(text)
vectors, plain_text = parser.parse_to_vectors(text)

# Utility functions
vector = text_to_emotion_vector(text, emotion_description="happy,calm")
merged = merge_emotion_vectors([vec1, vec2], weights=[0.6, 0.4])
normalized = normalize_emotion_vector(vector)
```

### Voice Library

```python
from indextts_app.voice_library import (
    VoiceLibraryManager,
    VoiceProfile,
    VoiceLibrary,
    VoiceExtractor,
    extract_audio_from_file
)

# Voice management
manager = VoiceLibraryManager(Path("./voices"))
voice = manager.add_voice_from_file(name, audio_path, **options)
voices = manager.list_voices()
voice = manager.get_voice(voice_id)
voice = manager.get_voice_by_name(name)
deleted = manager.delete_voice(voice_id)
updated = manager.update_voice(profile)

# Audio extraction
extractor = VoiceExtractor()
success = extractor.extract_audio(input_path, output_path, sample_rate=24000)
success = extractor.extract_audio_segment(input_path, output_path, start_time, duration)
info = extractor.get_audio_info(file_path)

# Convenience function
success, info = extract_audio_from_file(file_path, output_path, sample_rate=24000)
```

### Synthesis

```python
from indextts_app.utils import (
    TTSSynthesizer,
    SynthesisRequest,
    SynthesisResult
)

# Initialize
synth = TTSSynthesizer(config_path, model_dir, use_fp16=True)

# Create request
request = SynthesisRequest(
    text=text,
    voice_id=voice_id,
    emotion_vector=emotion_vec,
    emotion_text=emotion_desc,
    use_emotion_text=True,
    use_random=False,
    language="auto",
    output_format="wav"
)

# Synthesize
result = synth.synthesize(request, voice_audio_path, output_path=None)
result = synth.synthesize_with_emotions(text, voice_path, emotion_segments)

# Check result
if result.success:
    print(f"Output: {result.audio_path}")
else:
    print(f"Error: {result.error}")
```

### CLI

```bash
# Voice management
uv run -m indextts_app.cli voice add <name> <file> [options]
uv run -m indextts_app.cli voice list
uv run -m indextts_app.cli voice remove <voice_id>

# Audio extraction
uv run -m indextts_app.cli extract audio <input> <output> [options]

# Testing
uv run -m indextts_app.cli test speak <text> <voice_id> [options]

# Info
uv run -m indextts_app.cli info
```

---

## Complete API Reference

### `indextts_app.emotion` Module

#### `parse_emotion_tags(text: str) -> Tuple[List[EmotionSegment], str]`

Parse text with emotion tags.

**Args:**
- `text`: Text with emotion tags like `[Happy:80]text[Sad:50]more`

**Returns:**
- Tuple of (EmotionSegments list, plain text without tags)

**Example:**
```python
segments, plain = parse_emotion_tags("[Happy:80]Great [Sad:50]news")
# segments = [EmotionSegment(...), EmotionSegment(...)]
# plain = "Great news"
```

---

#### `parse_emotion_tags_to_vectors(text: str) -> Tuple[List[Tuple[str, List[float]]], str]`

Parse emotions and return emotion vectors.

**Args:**
- `text`: Text with emotion tags

**Returns:**
- Tuple of (list of (text_segment, emotion_vector), plain_text)

**Example:**
```python
vectors, plain = parse_emotion_tags_to_vectors("[Happy:80]Hello")
# vectors = [("Hello", [0.8, 0, 0, 0, 0, 0, 0, 0])]
```

---

#### `class EmotionSegment`

Represents a text segment with emotions.

**Attributes:**
- `text: str` - Text segment
- `start_char: int` - Start position in original text
- `end_char: int` - End position
- `emotions: Dict[str, float]` - Emotion name → intensity
- `to_emotion_vector() -> List[float]` - Convert to 8-element vector

---

#### `class EmotionTagParser`

Advanced parser with more control.

**Methods:**
- `parse(text: str) -> Tuple[List[EmotionSegment], str]` - Parse text
- `parse_to_vectors(text: str) -> Tuple[List[Tuple[str, List[float]]], str]` - Parse and vectorize
- `parse_tag(tag_content: str) -> Dict[str, float]` - Parse single tag

---

#### `text_to_emotion_vector(text: str, emotion_description: str = "", default_intensity: float = 0.5) -> List[float]`

Convert emotion description to vector.

**Args:**
- `text`: Text (for context)
- `emotion_description`: "happy,calm" or "happy:0.8,calm:0.5"
- `default_intensity`: Default if no intensity specified

**Returns:**
- 8-element emotion vector

---

#### `merge_emotion_vectors(vectors: List[List[float]], weights: Optional[List[float]] = None) -> List[float]`

Merge multiple emotion vectors.

**Args:**
- `vectors`: List of emotion vectors
- `weights`: Optional weights (auto-normalized)

**Returns:**
- Merged emotion vector

---

#### `normalize_emotion_vector(vector: List[float]) -> List[float]`

Normalize vector so max value is 1.0.

---

### `indextts_app.voice_library` Module

#### `class VoiceProfile`

Voice metadata.

**Attributes:**
- `id: str` - Unique ID
- `name: str` - Display name
- `audio_path: str` - Path to audio file
- `created_at: str` - ISO timestamp
- `description: str` - Description
- `source_file: str` - Original source file
- `duration: float` - Audio duration in seconds
- `sample_rate: int` - Sample rate in Hz
- `language: str` - Language code
- `tags: List[str]` - Tag list
- `metadata: Dict[str, Any]` - Custom metadata

**Methods:**
- `to_dict() -> Dict[str, Any]` - Convert to dict

---

#### `class VoiceLibrary`

SQLite-based storage backend.

**Methods:**
- `add_voice(profile: VoiceProfile) -> bool` - Add voice
- `get_voice(voice_id: str) -> Optional[VoiceProfile]` - Get by ID
- `get_voice_by_name(name: str) -> Optional[VoiceProfile]` - Get by name
- `list_voices() -> List[VoiceProfile]` - List all
- `delete_voice(voice_id: str) -> bool` - Delete
- `update_voice(profile: VoiceProfile) -> bool` - Update

---

#### `class VoiceLibraryManager`

High-level manager (recommended for general use).

**Methods:**
- `__init__(voice_dir: Path, db_path: Optional[Path] = None)`
- `add_voice_from_file(name, audio_path, source_file="", description="", language="auto", tags=None, **metadata) -> Optional[VoiceProfile]`
- `get_voice(voice_id: str) -> Optional[VoiceProfile]`
- `get_voice_by_name(name: str) -> Optional[VoiceProfile]`
- `list_voices() -> List[VoiceProfile]`
- `delete_voice(voice_id: str) -> bool`
- `update_voice(profile: VoiceProfile) -> bool`
- `create_voice_id(name: str) -> str` - Generate unique ID

---

#### `class VoiceExtractor`

Audio extraction from media files.

**Static Methods:**
- `get_audio_info(file_path: Path) -> Optional[dict]` - Get duration, sample_rate, channels
- `extract_audio(input_path, output_path, sample_rate=24000, channels=1, start_time=None, duration=None) -> bool`
- `extract_audio_segment(input_path, output_path, start_time, duration, sample_rate=24000) -> bool`

**Attributes:**
- `SUPPORTED_FORMATS` - Set of supported file extensions

---

#### `extract_audio_from_file(file_path: Path, output_path: Path, sample_rate: int = 24000) -> Tuple[bool, Optional[dict]]`

Convenience function.

**Returns:**
- (success: bool, audio_info: dict)

---

### `indextts_app.utils` Module

#### `class SynthesisRequest`

Synthesis request parameters.

**Attributes:**
- `text: str` - Text to synthesize
- `voice_id: str` - Voice identifier
- `emotion_vector: Optional[List[float]]` - Emotion vector (8 elements)
- `emotion_text: Optional[str]` - Text-based emotion description
- `use_emotion_text: bool` - Use emotion_text flag
- `use_random: bool` - Add randomness to synthesis
- `language: str` - Language code
- `output_format: str` - Output format (wav, mp3, ogg, m4a)

---

#### `class SynthesisResult`

Synthesis result.

**Attributes:**
- `success: bool` - Whether synthesis succeeded
- `audio_path: Optional[str]` - Path to output audio
- `duration: Optional[float]` - Audio duration
- `sample_rate: int` - Sample rate
- `error: Optional[str]` - Error message if failed
- `timestamp: str` - ISO timestamp

---

#### `class TTSSynthesizer`

IndexTTS2 wrapper.

**Methods:**
- `__init__(config_path, model_dir, use_fp16=True, use_cuda_kernel=True, use_deepspeed=False)`
- `synthesize(request: SynthesisRequest, voice_audio_path: Path, output_path: Optional[Path] = None) -> SynthesisResult`
- `synthesize_with_emotions(text, voice_audio_path, emotion_segments, output_path=None) -> SynthesisResult`

---

## Emotion Vector Format

8-element list representing:
```
[happy, angry, sad, afraid, disgusted, melancholic, surprised, calm]
```

**Values:** 0.0 (no emotion) to 1.0 (maximum)

**Example:**
```python
[0.8, 0, 0, 0, 0, 0, 0, 0.2]  # 80% happy, 20% calm
[1.0, 0.5, 0, 0, 0, 0, 0, 0]  # 100% happy, 50% angry (mixed)
```

---

## Data Structures

### VoiceProfile

```python
@dataclass
class VoiceProfile:
    id: str
    name: str
    audio_path: str
    created_at: str
    description: str = ""
    source_file: str = ""
    duration: float = 0.0
    sample_rate: int = 24000
    language: str = "auto"
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
```

### EmotionSegment

```python
@dataclass
class EmotionSegment:
    text: str
    start_char: int
    end_char: int
    emotions: Dict[str, float]
```

---

## Common Patterns

### Get or Create Voice

```python
manager = VoiceLibraryManager(Path("./voices"))
voice = manager.get_voice_by_name("My Voice")
if not voice:
    voice = manager.add_voice_from_file(
        "My Voice",
        Path("voice.wav")
    )
```

### Synthesize with Dynamic Emotions

```python
text = "[Happy:80]Great news! [Sad:60]But no money."
segments, plain_text = parse_emotion_tags_to_vectors(text)

for text_seg, emotion_vec in segments:
    request = SynthesisRequest(
        text=text_seg,
        voice_id=voice.id,
        emotion_vector=emotion_vec
    )
    result = synth.synthesize(request, Path(voice.audio_path))
```

### Batch Extract and Add Voices

```python
manager = VoiceLibraryManager(Path("./voices"))
extractor = VoiceExtractor()

for mp4_file in Path("./videos").glob("*.mp4"):
    # Extract audio
    success = extractor.extract_audio(
        mp4_file,
        Path(f"temp_{mp4_file.stem}.wav")
    )
    
    if success:
        # Add to library
        manager.add_voice_from_file(
            name=mp4_file.stem,
            audio_path=Path(f"temp_{mp4_file.stem}.wav"),
            source_file=str(mp4_file)
        )
```

---

## Error Handling

```python
from pathlib import Path
from indextts_app.voice_library import VoiceLibraryManager

manager = VoiceLibraryManager(Path("./voices"))

# Safe voice retrieval
voice = manager.get_voice_by_name("My Voice")
if not voice:
    print("Voice not found")
    # Create new voice...
else:
    print(f"Using voice: {voice.name}")

# Safe synthesis
result = synth.synthesize(request, Path(voice.audio_path))
if result.success:
    print(f"Success: {result.audio_path}")
else:
    print(f"Error: {result.error}")
```

---

## Performance Tips

1. **Emotion Parsing**: Cache parsed emotions if using same text multiple times
2. **Voice Library**: Load once, reuse VoiceLibraryManager instance
3. **Synthesis**: Use FP16 for faster GPU inference
4. **Audio Extraction**: Extract once, store in library
5. **Batch Operations**: Process multiple items without recreating managers

---

## Troubleshooting

### Import Errors
Ensure running with `uv run` to use correct environment:
```bash
PYTHONPATH="$PYTHONPATH:." uv run script.py
```

### FFmpeg Not Found
```bash
# Linux
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg
```

### Model Not Loading
Check model files exist:
```bash
ls -la ./checkpoints/
# Should contain: config.yaml, model weights, pinyin.vocab
```

### CUDA Errors
Check GPU setup:
```bash
uv run tools/gpu_check.py
```

---

## Version Info

- **IndexTTS App**: 0.1.0
- **Requires**: Python 3.10+
- **Dependencies**: torch, torchaudio, transformers, click
- **Optional**: FastAPI, uvicorn (for API)

---

For more detailed examples, see:
- `indextts_app/README.md` - Full documentation
- `examples/indextts_app_example.py` - Working examples
- `indextts_app/test_emotion.py` - Test cases
