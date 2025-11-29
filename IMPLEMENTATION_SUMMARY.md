# IndexTTS Standalone Application - Implementation Summary

## What Has Been Built

You now have a **complete standalone framework** for advanced text-to-speech with voice cloning and emotion control. This is a foundation that can be extended with REST API, web UI, and eventually integrated into Home Assistant.

### Core Components Implemented

#### 1. **Emotion Tag Parser** (`indextts_app/emotion/`)

Parses text with emotion tags and converts them to IndexTTS2 emotion vectors.

**Syntax:**
```
[Emotion:Intensity]text[Emotion:Intensity]more text
```

**Example:**
```python
from indextts_app.emotion import parse_emotion_tags_to_vectors

text = "[Calm:60,Happy:40]Now I've been waiting [Angry:30] It's been 2 weeks!"
segments, plain_text = parse_emotion_tags_to_vectors(text)

# segments = [
#   ("Now I've been waiting ", [0.4, 0, 0, 0, 0, 0, 0, 0.6]),
#   (" It's been 2 weeks!", [0, 0.3, 0, 0, 0, 0, 0, 0]),
# ]
```

**Supported Emotions:**
- happy (0), angry (1), sad (2), afraid (3)
- disgusted (4), melancholic (5), surprised (6), calm (7)

#### 2. **Voice Library Management** (`indextts_app/voice_library/`)

Store, manage, and organize voice profiles with metadata.

**Features:**
- SQLite database for persistent storage
- Voice profile metadata (name, language, tags, description)
- Voice listing, retrieval, update, delete operations
- Unique ID generation for each voice

**Example:**
```python
from indextts_app.voice_library import VoiceLibraryManager

manager = VoiceLibraryManager(Path("./voices"))

# Add voice
voice = manager.add_voice_from_file(
    name="My Voice",
    audio_path=Path("voice.wav"),
    language="en",
    tags=["female", "calm"]
)

# List voices
for v in manager.list_voices():
    print(f"{v.name}: {v.id}")
```

#### 3. **Audio Extraction** (`indextts_app/voice_library/extractor.py`)

Extract audio from media files (MP4, MP3, WAV, etc.) using FFmpeg.

**Features:**
- Support for video and audio formats
- Segment extraction (start_time, duration)
- Sample rate and channel configuration
- Audio information retrieval (duration, sample rate)

**Example:**
```python
from indextts_app.voice_library import VoiceExtractor

extractor = VoiceExtractor()

# Extract from video
success = extractor.extract_audio(
    Path("video.mp4"),
    Path("voice.wav"),
    sample_rate=24000
)

# Extract 5-second segment starting at 10 seconds
success = extractor.extract_audio_segment(
    Path("video.mp4"),
    Path("segment.wav"),
    start_time=10.0,
    duration=5.0
)
```

#### 4. **TTS Synthesizer Wrapper** (`indextts_app/utils/synthesizer.py`)

Wrapper around IndexTTS2 for easy synthesis with emotion vectors.

**Features:**
- Model initialization and management
- Synthesis request/result data structures
- Emotion vector integration
- Error handling and result validation

**Example:**
```python
from indextts_app.utils import TTSSynthesizer, SynthesisRequest

synthesizer = TTSSynthesizer(
    config_path=Path("./checkpoints/config.yaml"),
    model_dir=Path("./checkpoints")
)

request = SynthesisRequest(
    text="Hello world!",
    voice_id="my-voice",
    emotion_vector=[0.8, 0, 0, 0, 0, 0, 0, 0.2]
)

result = synthesizer.synthesize(request, Path("voice.wav"))
```

#### 5. **CLI Interface** (`indextts_app/cli/`)

Command-line interface for voice management and testing.

**Commands:**
```bash
# Voice management
voice add <name> <audio_file>          # Add voice to library
voice list                              # List all voices
voice remove <voice_id>                # Remove voice

# Audio extraction
extract audio <input> <output>         # Extract audio from media
extract audio <input> <output> \
  --start 10.0 --duration 5.0         # Extract segment

# Testing
test speak <text> <voice_id>           # Simple synthesis
test speak <text_with_emotions> <voice_id>  # With emotions
```

### Directory Structure

```
indextts_app/
├── __init__.py                      # Package initialization
├── README.md                        # Full documentation
├── test_emotion.py                  # Emotion parser tests
│
├── emotion/                         # Emotion system
│   ├── __init__.py
│   ├── parser.py                    # EmotionTagParser, parse_emotion_tags()
│   └── utils.py                     # Utility functions
│
├── voice_library/                   # Voice management
│   ├── __init__.py
│   ├── storage.py                   # VoiceLibrary, VoiceProfile, VoiceLibraryManager
│   └── extractor.py                 # VoiceExtractor for audio extraction
│
├── utils/                           # Core utilities
│   ├── __init__.py
│   └── synthesizer.py               # TTSSynthesizer, SynthesisRequest, SynthesisResult
│
└── cli/
    └── __init__.py                  # Click CLI commands
```

### Key Classes

#### Emotion System
- **`EmotionTagParser`** - Main parser class
- **`EmotionSegment`** - Text segment with emotions
- **`parse_emotion_tags(text)`** - Parse emotion tags, returns segments
- **`parse_emotion_tags_to_vectors(text)`** - Parse and return emotion vectors

#### Voice Library
- **`VoiceLibraryManager`** - High-level voice management
- **`VoiceLibrary`** - SQLite database interface
- **`VoiceProfile`** - Voice metadata dataclass
- **`VoiceExtractor`** - Audio extraction utility

#### Synthesis
- **`TTSSynthesizer`** - Wrapper around IndexTTS2
- **`SynthesisRequest`** - Request data
- **`SynthesisResult`** - Result data with success/error info

## Usage Examples

### Example 1: Parse Emotions

```python
from indextts_app.emotion import parse_emotion_tags

text = "[Happy:80]Great! [Sad:60]But it's complicated."
segments, plain_text = parse_emotion_tags(text)

for segment in segments:
    print(f"Text: {segment.text}")
    print(f"Emotions: {segment.emotions}")  # {'happy': 80.0, 'sad': 60.0}
    print(f"Vector: {segment.to_emotion_vector()}")
```

### Example 2: Manage Voices

```python
from pathlib import Path
from indextts_app.voice_library import VoiceLibraryManager

manager = VoiceLibraryManager(Path("./voices"))

# Add from examples
voice = manager.add_voice_from_file(
    name="Example Voice",
    audio_path=Path("examples/voice_01.wav"),
    description="Voice from examples",
    language="en"
)

# List and retrieve
all_voices = manager.list_voices()
voice = manager.get_voice_by_name("Example Voice")
print(f"Voice audio path: {voice.audio_path}")
```

### Example 3: Extract Audio

```python
from pathlib import Path
from indextts_app.voice_library import VoiceExtractor

extractor = VoiceExtractor()

# Extract from MP4
success = extractor.extract_audio(
    Path("examples/video.mp4"),
    Path("extracted_voice.wav"),
    sample_rate=24000
)
```

### Example 4: Synthesize

```python
from pathlib import Path
from indextts_app.utils import TTSSynthesizer, SynthesisRequest

# Initialize
synth = TTSSynthesizer(
    config_path=Path("./checkpoints/config.yaml"),
    model_dir=Path("./checkpoints")
)

# Create request with emotion
request = SynthesisRequest(
    text="Hello, this is a test",
    voice_id="test-voice",
    emotion_vector=[0.7, 0, 0, 0, 0, 0, 0, 0.3]  # Happy + Calm
)

# Synthesize
result = synth.synthesize(request, Path("voice.wav"))
if result.success:
    print(f"Generated: {result.audio_path}")
```

### Example 5: Full Workflow

```python
from pathlib import Path
from indextts_app.voice_library import VoiceLibraryManager, VoiceExtractor
from indextts_app.emotion import parse_emotion_tags_to_vectors
from indextts_app.utils import TTSSynthesizer, SynthesisRequest

# 1. Extract voice from video
extractor = VoiceExtractor()
extractor.extract_audio(Path("video.mp4"), Path("voice.wav"))

# 2. Add to library
manager = VoiceLibraryManager(Path("./voices"))
voice = manager.add_voice_from_file(
    name="Extracted Voice",
    audio_path=Path("voice.wav")
)

# 3. Parse emotions from text
text = "[Calm:60,Happy:40]Good morning [Angry:30] It's raining again!"
segments, plain_text = parse_emotion_tags_to_vectors(text)

# 4. Synthesize with emotions
synth = TTSSynthesizer(
    config_path=Path("./checkpoints/config.yaml"),
    model_dir=Path("./checkpoints")
)

request = SynthesisRequest(
    text=plain_text,
    voice_id=voice.id,
    emotion_vector=segments[0][1] if segments else None
)

result = synth.synthesize(request, Path(voice.audio_path))
```

## Testing

Run the included test script to verify everything works:

```bash
cd /home/voir/Projects/index-tts

# Test emotion parser
PYTHONPATH="$PYTHONPATH:." uv run indextts_app/test_emotion.py

# Run examples (if model is loaded)
PYTHONPATH="$PYTHONPATH:." uv run examples/indextts_app_example.py
```

## Next Steps

### Phase 2: REST API Server
Build a FastAPI server to expose the functionality via HTTP:

```python
# Example endpoints
POST /api/synthesize           # Synthesize with emotions
POST /api/voices               # Add voice
GET /api/voices                # List voices
GET /api/voices/{id}           # Get voice
DELETE /api/voices/{id}        # Delete voice
POST /api/extract              # Extract audio from file
```

### Phase 3: Web UI
Build a simple web interface (could extend existing webui.py):
- Voice library browser
- Voice cloning uploader
- Emotion tag editor
- Synthesis player
- Real-time preview

### Phase 4: Home Assistant Integration
Create Home Assistant integration package:
- TTS platform implementation
- Voice and emotion options
- Service endpoints
- Configuration flow

## Files Modified/Created

### New Files
- `indextts_app/` - Main application package
- `indextts_app/__init__.py` - Package initialization
- `indextts_app/README.md` - Full documentation
- `indextts_app/test_emotion.py` - Emotion parser tests
- `indextts_app/emotion/` - Emotion system module
- `indextts_app/voice_library/` - Voice management module
- `indextts_app/utils/` - Utilities module
- `indextts_app/cli/` - CLI interface
- `indextts_app/api/` - REST API (stub)
- `INDEXTTS_APP_SETUP.md` - Quick setup guide
- `examples/indextts_app_example.py` - Usage examples

### Unchanged
- Core IndexTTS2 code remains untouched
- All existing functionality preserved

## Configuration

Default locations:
- **Voice Library**: `./voices/`
- **Database**: `./voices/voices.db`
- **Model Config**: `./checkpoints/config.yaml`
- **Model Weights**: `./checkpoints/`

All configurable when initializing managers/synthesizers.

## Dependencies

Required packages (already in pyproject.toml):
- torch
- torchaudio
- transformers
- click (for CLI)
- (FastAPI, uvicorn - for REST API when built)

Additional system requirements:
- FFmpeg (for audio extraction)
- CUDA 12.8+ (for GPU acceleration)

## Quality & Style

- ✅ Full type hints for IDE support
- ✅ Comprehensive docstrings
- ✅ Error handling with meaningful messages
- ✅ Modular design - each component independent
- ✅ Examples for each major component
- ✅ Tests for critical functionality

## Performance Considerations

- **Voice Library**: SQLite queries are fast for typical use (< 1000 voices)
- **Emotion Parsing**: O(n) where n is text length, very efficient
- **Audio Extraction**: Depends on FFmpeg, typically 1-2x realtime
- **Synthesis**: Depends on IndexTTS2, typically 1-5x realtime

## Known Limitations

1. **Emotion Segments**: Currently uses first emotion for whole text. Future: segment-level synthesis
2. **Voice Conversion**: No built-in voice conversion. Uses reference voice directly
3. **Batch Processing**: Currently single synthesis at a time. Future: batching support
4. **Streaming**: No streaming API yet. Future: streaming synthesis

## Future Enhancements

- [ ] REST API with FastAPI
- [ ] WebUI for voice management
- [ ] Emotion blending across segments
- [ ] Voice quality metrics
- [ ] Audio caching system
- [ ] Real-time streaming
- [ ] Batch processing
- [ ] Home Assistant integration
- [ ] Voice conversion/transformation
- [ ] Multi-speaker synthesis

---

**You're all set!** The framework is ready for:
1. Testing emotion parsing with your custom text
2. Building the REST API
3. Creating the web interface
4. Integrating with Home Assistant

Would you like me to proceed with building the REST API next? 🚀
