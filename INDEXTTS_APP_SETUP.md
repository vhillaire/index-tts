# IndexTTS Standalone - Quick Setup Guide

## Overview

You now have a complete standalone IndexTTS application framework that includes:

✅ **Emotion Tag Parser** - Parse text with emotion tags like `[Happy:60,Calm:40]text[Angry:30]`  
✅ **Voice Library Management** - Store and manage voice profiles  
✅ **Audio Extraction** - Extract audio from MP4, MP3, and other media  
✅ **TTS Synthesizer** - Wrapper around IndexTTS2 for synthesis  
✅ **CLI Interface** - Command-line tools for testing and management  
✅ **Python API** - Full API for integration  

## Project Structure

```
indextts_app/
├── __init__.py                 # Main package
├── README.md                   # Full documentation
├── emotion/                    # Emotion tag parsing
│   ├── parser.py              # Core parser: parse_emotion_tags()
│   └── utils.py               # Emotion vector utilities
├── voice_library/              # Voice management
│   ├── storage.py             # VoiceLibrary, VoiceProfile
│   └── extractor.py           # VoiceExtractor for media files
├── utils/
│   └── synthesizer.py         # TTSSynthesizer wrapper
└── cli/
    └── __init__.py            # CLI commands
```

## Getting Started

### 1. Test Emotion Parser

```python
from indextts_app.emotion import parse_emotion_tags_to_vectors

text = "[Calm:60,Happy:40]Now I've been waiting [Angry:30] It's been 2 weeks!"
segments, plain_text = parse_emotion_tags_to_vectors(text)

# segments = [
#   ("Now I've been waiting ", [0.4, 0, 0, 0, 0, 0, 0, 0.6]),
#   (" It's been 2 weeks!", [0.3, 0, 0, 0, 0, 0, 0, 0]),
# ]
# plain_text = "Now I've been waiting  It's been 2 weeks!"
```

### 2. Manage Voices

```python
from pathlib import Path
from indextts_app.voice_library import VoiceLibraryManager

manager = VoiceLibraryManager(Path("./voices"))

# Add voice
voice = manager.add_voice_from_file(
    name="My Voice",
    audio_path=Path("voice.wav"),
    language="en"
)

# List voices
for v in manager.list_voices():
    print(f"{v.name} - {v.id}")

# Get voice
voice = manager.get_voice_by_name("My Voice")
```

### 3. Extract Audio

```python
from indextts_app.voice_library import VoiceExtractor
from pathlib import Path

extractor = VoiceExtractor()

# Extract from video
success = extractor.extract_audio(
    Path("video.mp4"),
    Path("voice.wav"),
    sample_rate=24000
)

# Extract segment (10-15 seconds)
success = extractor.extract_audio_segment(
    Path("video.mp4"),
    Path("segment.wav"),
    start_time=10.0,
    duration=5.0
)
```

### 4. Synthesize with Emotions

```python
from indextts_app.utils import TTSSynthesizer, SynthesisRequest
from pathlib import Path

# Initialize
synth = TTSSynthesizer(
    config_path=Path("./checkpoints/config.yaml"),
    model_dir=Path("./checkpoints")
)

# Create request
request = SynthesisRequest(
    text="Hello world!",
    voice_id="my-voice",
    emotion_vector=[0.8, 0, 0, 0, 0, 0, 0, 0.2]  # Happy + Calm
)

# Synthesize
result = synth.synthesize(request, Path("voice.wav"))
if result.success:
    print(f"Output: {result.audio_path}")
```

## Emotion Tag Syntax

### Basic Format
```
[Emotion:Intensity]text[Emotion:Intensity]more text
```

### Examples

```python
# Single emotion
"[Happy:80]Great news!"

# Multiple emotions per tag
"[Happy:60,Calm:40]Be patient"

# Complex example
"[Calm:70]Listen carefully. [Angry:90,Hate:80]This is unacceptable!"

# Overlapping emotions across text
"[Sad:100]It's gone [Afraid:60]and might not return [Calm:40]but we'll adapt"
```

### Supported Emotions

| Emotion | Index | Usage |
|---------|-------|-------|
| happy | 0 | Joyful, excited |
| angry | 1 | Frustrated, upset |
| sad | 2 | Sorrowful, depressed |
| afraid / fear | 3 | Fearful, anxious |
| disgusted / disgust | 4 | Disgusted |
| melancholic / melancholy | 5 | Gloomy, depressed |
| surprised / surprise | 6 | Amazed, shocked |
| calm / peaceful | 7 | Peaceful, composed |

## Next: Build the REST API

To make this available as a service, you'll want to build a REST API server:

```python
# Example: FastAPI server structure

from fastapi import FastAPI, File, UploadFile
from indextts_app.voice_library import VoiceLibraryManager
from indextts_app.utils import TTSSynthesizer, SynthesisRequest
from indextts_app.emotion import parse_emotion_tags_to_vectors

app = FastAPI()

# Endpoints:
# POST /api/synthesize - Synthesize text with emotions
# POST /api/voices - Add voice
# GET /api/voices - List voices
# GET /api/voices/{id} - Get voice
# DELETE /api/voices/{id} - Delete voice
# POST /api/extract - Extract audio from file
```

## CLI Usage

```bash
# Add voice
uv run -m indextts_app.cli voice add "My Voice" voice.wav

# List voices
uv run -m indextts_app.cli voice list

# Extract audio
uv run -m indextts_app.cli extract audio video.mp4 voice.wav

# Test synthesis
uv run -m indextts_app.cli test speak "[Happy:80]Hello!" <voice-id>
```

## File Locations

- **Voice Library**: `./voices/` (configurable)
- **Database**: `./voices/voices.db` (SQLite)
- **Configuration**: `./checkpoints/config.yaml`
- **Model Weights**: `./checkpoints/`

## Key Classes

### Emotion System
- `EmotionTagParser` - Parse emotion tags
- `EmotionSegment` - Text segment with emotions
- `text_to_emotion_vector()` - Convert emotions to vector

### Voice Library
- `VoiceLibraryManager` - High-level voice management
- `VoiceLibrary` - SQLite database
- `VoiceProfile` - Voice metadata
- `VoiceExtractor` - Extract audio from media

### Synthesis
- `TTSSynthesizer` - Wrapper around IndexTTS2
- `SynthesisRequest` - Synthesis request data
- `SynthesisResult` - Synthesis result data

## Development Workflow

1. **Test Emotion Parser** - Verify tag parsing works
2. **Add Test Voices** - Build voice library
3. **Test Synthesis** - Verify TTS works
4. **Build REST API** - Create API server
5. **Add Web UI** - Create web interface
6. **Integration** - Home Assistant integration

## What's Next

The following tasks are in progress or planned:

- [ ] REST API Server (FastAPI)
- [ ] Web UI for voice management
- [ ] Advanced emotion blending for multi-emotion segments
- [ ] Audio caching system
- [ ] Real-time streaming synthesis
- [ ] Home Assistant integration

## Testing

Run the example script to verify everything works:

```bash
PYTHONPATH="$PYTHONPATH:." uv run examples/indextts_app_example.py
```

## Troubleshooting

### Import errors
If you see import errors, ensure you're running with `uv run`:
```bash
PYTHONPATH="$PYTHONPATH:." uv run examples/indextts_app_example.py
```

### FFmpeg not found
```bash
# Linux
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### CUDA errors
Check GPU setup:
```bash
uv run tools/gpu_check.py
```

## Documentation

Full documentation is available in:
- `indextts_app/README.md` - Complete API documentation
- `indextts_app/emotion/parser.py` - Emotion parser details
- `indextts_app/voice_library/storage.py` - Voice library details
- `examples/indextts_app_example.py` - Working examples

---

**Ready to build the REST API?** Let me know! 🚀
