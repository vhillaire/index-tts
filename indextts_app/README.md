# IndexTTS Standalone Application

A comprehensive standalone application built on IndexTTS2 for voice cloning and emotion-based text-to-speech synthesis.

## Features

- **Voice Cloning**: Extract voice profiles from audio files or media (MP4, MP3, WAV, etc.)
- **Voice Library**: Manage and organize multiple voice profiles with metadata
- **Emotion Tags**: Control speech emotion using intuitive tag syntax: `[Happy:60,Calm:40]text[Angry:30]more text`
- **REST API**: Full API for integration with other applications
- **CLI Interface**: Command-line tools for testing and voice management
- **Flexible Output**: Multiple audio format support (WAV, MP3, OGG, M4A)

## Project Structure

```
indextts_app/
├── __init__.py
├── cli/                    # Command-line interface
│   └── __init__.py        # CLI commands for voice management and testing
├── emotion/                # Emotion tag parsing
│   ├── __init__.py
│   ├── parser.py          # Emotion tag parser
│   └── utils.py           # Emotion vector utilities
├── voice_library/          # Voice management
│   ├── __init__.py
│   ├── storage.py         # Voice profile storage and database
│   └── extractor.py       # Audio extraction from media files
├── utils/                  # Core utilities
│   ├── __init__.py
│   └── synthesizer.py     # TTS synthesis wrapper
└── api/                    # REST API (coming soon)
    └── __init__.py
```

## Installation

The application requires:
- Python 3.10+
- IndexTTS2 model weights
- FFmpeg for audio processing

### Setup

```bash
# Install dependencies
uv sync --all-extras

# Download model weights
uv tool install "huggingface-hub[cli,hf_xet]"
hf download IndexTeam/IndexTTS-2 --local-dir=checkpoints
```

## Quick Start

### Voice Library Management

```bash
# Add a voice from audio file
uv run -m indextts_app.cli voice add "My Voice" path/to/voice.wav --description "My custom voice"

# List all voices
uv run -m indextts_app.cli voice list

# Remove a voice
uv run -m indextts_app.cli voice remove <voice_id>
```

### Extract Audio from Media

```bash
# Extract from MP4
uv run -m indextts_app.cli extract audio input.mp4 output.wav --sample-rate 24000

# Extract a segment
uv run -m indextts_app.cli extract audio video.mp4 segment.wav \
  --start 10.5 --duration 5.0
```

### Test TTS Synthesis

```bash
# Simple synthesis
uv run -m indextts_app.cli test speak "Hello world!" <voice_id>

# With emotions
uv run -m indextts_app.cli test speak \
  "[Calm:60,Happy:40]Now I've been waiting patiently [Angry:30] \
   It's been 2 weeks [Angry:60,Hate:80] Now I want my money!" \
  <voice_id>
```

## Emotion Tag Syntax

Control speech emotion using emotion tags in square brackets. Multiple emotions can be specified with intensity values (0-100):

```
[Calm:60,Happy:40]Now I've been waiting [Angry:30] It's been 2 weeks!
```

Supported emotions:
- **happy** (0): Happy/joyful
- **angry** (1): Angry/frustrated
- **sad** (2): Sad/sorrowful
- **afraid/fear** (3): Afraid/fearful
- **disgusted/disgust** (4): Disgusted
- **melancholic/melancholy** (5): Melancholic/depressed
- **surprised/surprise** (6): Surprised/amazed
- **calm/peaceful** (7): Calm/peaceful

### Examples

```
[Happy:80]Great news! [Calm:70]Take your time. [Angry:90]This is unacceptable!
[Sad:100]I can't believe it's gone [Afraid:60] What if it happens again?
```

## Python API Usage

### Basic Synthesis

```python
from pathlib import Path
from indextts_app.voice_library import VoiceLibraryManager
from indextts_app.utils import TTSSynthesizer, SynthesisRequest
from indextts_app.emotion import parse_emotion_tags_to_vectors

# Load voice from library
manager = VoiceLibraryManager(Path("./voices"))
voice = manager.get_voice_by_name("My Voice")

# Initialize synthesizer
synthesizer = TTSSynthesizer(
    config_path=Path("./checkpoints/config.yaml"),
    model_dir=Path("./checkpoints"),
    use_fp16=True
)

# Parse emotion tags
segments, plain_text = parse_emotion_tags_to_vectors(
    "[Happy:60]Hello! [Calm:40]How are you?"
)

# Create synthesis request
request = SynthesisRequest(
    text="Hello! How are you?",
    voice_id=voice.id,
    emotion_vector=segments[0][1] if segments else None
)

# Synthesize
result = synthesizer.synthesize(request, Path(voice.audio_path))
if result.success:
    print(f"Generated: {result.audio_path}")
else:
    print(f"Error: {result.error}")
```

### Voice Management

```python
from pathlib import Path
from indextts_app.voice_library import VoiceLibraryManager

# Initialize manager
manager = VoiceLibraryManager(Path("./voices"))

# Add voice from file
profile = manager.add_voice_from_file(
    name="New Voice",
    audio_path=Path("voice.wav"),
    description="A custom voice",
    language="en",
    tags=["female", "calm"]
)

# List all voices
for voice in manager.list_voices():
    print(f"{voice.name} (ID: {voice.id}) - {voice.language}")

# Get specific voice
voice = manager.get_voice_by_name("New Voice")
print(f"Audio path: {voice.audio_path}")
```

### Emotion Parsing

```python
from indextts_app.emotion import parse_emotion_tags, parse_emotion_tags_to_vectors

# Parse with segments
segments, plain_text = parse_emotion_tags(
    "[Happy:80]Great! [Sad:60]But there's a problem."
)

for segment in segments:
    print(f"Text: {segment.text}")
    print(f"Emotions: {segment.emotions}")
    print(f"Vector: {segment.to_emotion_vector()}")

# Parse to vectors directly
vectors, plain_text = parse_emotion_tags_to_vectors(
    "[Calm:50]Hello [Angry:70]what do you want?"
)

for text_seg, emotion_vec in vectors:
    print(f"{text_seg} -> {emotion_vec}")
```

## Architecture

### Emotion System

The emotion system works by:

1. **Parsing**: Text with emotion tags `[Emotion:Intensity]` is parsed into segments
2. **Conversion**: Emotions are mapped to IndexTTS2's 8-dimensional emotion vector:
   - `[happy, angry, sad, afraid, disgusted, melancholic, surprised, calm]`
3. **Normalization**: Intensity values (0-100) are normalized to 0-1 range
4. **Application**: Emotion vector is passed to IndexTTS2 during synthesis

### Voice Library

Voices are stored in:
- **SQLite Database** (`voices.db`): Metadata for all voices
- **Audio Files**: Stored in voice directory
- **Profiles**: Include name, description, language, tags, metadata

### Synthesis Flow

```
Text with Emotion Tags
    ↓
Parse Emotion Tags → Segments with Emotion Vectors
    ↓
IndexTTS2 Model
    ├─ Voice Reference Audio
    ├─ Text
    └─ Emotion Vector
    ↓
Audio Output
```

## Next Steps

### Coming Soon
- REST API server with FastAPI
- Web UI for voice management and testing
- Advanced segment-level emotion synthesis
- Audio caching system
- Real-time streaming synthesis

### Planned Features
- Voice quality metrics
- Emotion intensity analysis
- Batch synthesis
- Audio effects (reverb, pitch shift, etc.)
- Multi-speaker synthesis
- Language auto-detection

## Troubleshooting

### FFmpeg not found
Install FFmpeg:
- **Linux**: `sudo apt-get install ffmpeg`
- **macOS**: `brew install ffmpeg`
- **Windows**: Download from https://ffmpeg.org/download.html

### CUDA errors
Ensure you have CUDA 12.8+ installed and PyTorch CUDA support:
```bash
uv run tools/gpu_check.py
```

### Model loading issues
Verify model weights are in the correct location:
```bash
ls -la checkpoints/
```

Should contain: `config.yaml`, model weights, and `pinyin.vocab`

## Development

### Running Tests

```bash
# Test emotion parser
python -m pytest indextts_app/emotion/test_parser.py

# Test voice library
python -m pytest indextts_app/voice_library/test_storage.py
```

### Code Structure

- **Modular Design**: Each component (emotion, voice, synthesis) is independent
- **Type Hints**: Full type annotations for IDE support
- **Error Handling**: Graceful error handling with descriptive messages
- **Logging**: Comprehensive logging for debugging

## Contributing

Contributions welcome! Areas for improvement:

- [ ] REST API implementation
- [ ] Web UI
- [ ] Advanced emotion blending
- [ ] Performance optimization
- [ ] Additional audio formats
- [ ] Voice quality metrics

## License

Same as IndexTTS2 - See LICENSE file

## References

- [IndexTTS2 Paper](https://arxiv.org/abs/2506.21619)
- [IndexTTS GitHub](https://github.com/index-tts/index-tts)
- [IndexTTS2 Demo](https://index-tts.github.io/index-tts2.github.io/)
