# 📋 Quick Reference Card

## 🚀 Get Started in 5 Minutes

### 1. Test Emotion Parser

```bash
PYTHONPATH="$PYTHONPATH:." uv run indextts_app/test_emotion.py
```

### 2. Add a Voice

```python
from indextts_app.voice_library import VoiceLibraryManager
from pathlib import Path

manager = VoiceLibraryManager(Path("./voices"))
voice = manager.add_voice_from_file("My Voice", Path("examples/voice_01.wav"))
print(f"Added: {voice.name} (ID: {voice.id})")
```

### 3. Parse Emotions

```python
from indextts_app.emotion import parse_emotion_tags_to_vectors

text = "[Happy:80]Hello [Angry:30] where were you?"
segments, plain = parse_emotion_tags_to_vectors(text)

for text_seg, emotion_vec in segments:
    print(f"Text: {text_seg} | Emotions: {emotion_vec}")
```

### 4. Synthesize

```python
from indextts_app.utils import TTSSynthesizer, SynthesisRequest
from pathlib import Path

synth = TTSSynthesizer(
    config_path=Path("./checkpoints/config.yaml"),
    model_dir=Path("./checkpoints")
)

request = SynthesisRequest(
    text="Hello world!",
    voice_id="my-voice",
    emotion_vector=[0.8, 0, 0, 0, 0, 0, 0, 0.2]
)

result = synth.synthesize(request, Path("voice.wav"))
```

---

## 📚 Documentation

| Document | Purpose | Link |
|----------|---------|------|
| Start Here | What you got | [DELIVERY_SUMMARY.md](./DELIVERY_SUMMARY.md) |
| Quick Start | Getting started | [INDEXTTS_APP_SETUP.md](./INDEXTTS_APP_SETUP.md) |
| Full Docs | All features | [indextts_app/README.md](./indextts_app/README.md) |
| API Ref | Function details | [API_REFERENCE.md](./API_REFERENCE.md) |
| Navigation | All docs | [DOCS_INDEX.md](./DOCS_INDEX.md) |

---

## 🎯 Emotion Emotions

| Emotion | Intensity | Example |
|---------|-----------|---------|
| happy | 0-100 | `[Happy:80]` |
| angry | 0-100 | `[Angry:90]` |
| sad | 0-100 | `[Sad:70]` |
| afraid | 0-100 | `[Afraid:60]` |
| disgusted | 0-100 | `[Disgusted:75]` |
| melancholic | 0-100 | `[Melancholic:50]` |
| surprised | 0-100 | `[Surprised:85]` |
| calm | 0-100 | `[Calm:40]` |

---

## 🛠️ CLI Commands

```bash
# Add voice
uv run -m indextts_app.cli voice add "Name" file.wav

# List voices
uv run -m indextts_app.cli voice list

# Remove voice
uv run -m indextts_app.cli voice remove <voice-id>

# Extract audio
uv run -m indextts_app.cli extract audio input.mp4 output.wav

# Test synthesis
uv run -m indextts_app.cli test speak "[Happy:80]Hello!" <voice-id>
```

---

## 💻 Core Classes

### Emotion
- `EmotionTagParser` - Parse `[Emotion:Intensity]text`
- `EmotionSegment` - Text + emotion pair

### Voice
- `VoiceLibraryManager` - Add/list/delete voices
- `VoiceExtractor` - Extract from media files

### Synthesis
- `TTSSynthesizer` - Create speech
- `SynthesisRequest` - Input parameters
- `SynthesisResult` - Output + status

---

## 🗂️ File Locations

| Item | Location |
|------|----------|
| Application | `indextts_app/` |
| Voice Library | `voices/` |
| Database | `voices/voices.db` |
| Config | `checkpoints/config.yaml` |
| Model | `checkpoints/` |

---

## 🔗 Emotion Vector Format

```python
[happy, angry, sad, afraid, disgusted, melancholic, surprised, calm]
[  0   ,  1   ,  2  ,   3   ,     4    ,     5    ,    6    ,   7  ]
```

**Values:** 0.0 (no emotion) → 1.0 (max emotion)

**Example:** `[0.8, 0, 0, 0, 0, 0, 0, 0.2]` = 80% happy, 20% calm

---

## ⚡ Common Operations

### Extract Voice from Video

```python
from indextts_app.voice_library import VoiceExtractor
from pathlib import Path

extractor = VoiceExtractor()
extractor.extract_audio(Path("video.mp4"), Path("voice.wav"))
```

### Get Voice by Name

```python
voice = manager.get_voice_by_name("My Voice")
```

### List All Voices

```python
for voice in manager.list_voices():
    print(f"{voice.name}: {voice.id}")
```

### Synthesize with Emotions

```python
request = SynthesisRequest(
    text="Hello!",
    voice_id=voice.id,
    emotion_vector=[0.7, 0.3, 0, 0, 0, 0, 0, 0]  # Happy + Angry
)
result = synth.synthesize(request, Path(voice.audio_path))
```

---

## 🐛 Troubleshooting

| Issue | Fix |
|-------|-----|
| FFmpeg not found | `sudo apt-get install ffmpeg` |
| Model not loading | `ls -la ./checkpoints/` |
| Import error | `PYTHONPATH="$PYTHONPATH:." uv run script.py` |
| CUDA error | `uv run tools/gpu_check.py` |

---

## 📖 Learn More

- Emotion syntax: [INDEXTTS_APP_SETUP.md](./INDEXTTS_APP_SETUP.md)
- All APIs: [API_REFERENCE.md](./API_REFERENCE.md)
- Examples: [examples/indextts_app_example.py](./examples/indextts_app_example.py)
- Tests: `PYTHONPATH="$PYTHONPATH:." uv run indextts_app/test_emotion.py`

---

## 🚀 What's Next

- [ ] REST API server
- [ ] Web UI
- [ ] Home Assistant integration
- [ ] Advanced features

---

## 📞 Need Help?

1. Check [DOCS_INDEX.md](./DOCS_INDEX.md) for navigation
2. See [API_REFERENCE.md](./API_REFERENCE.md) for troubleshooting
3. Run examples: `PYTHONPATH="$PYTHONPATH:." uv run examples/indextts_app_example.py`

---

**You're ready to go!** 🚀

Start with one of the 5-minute examples above.
