# 🎬 Get Started Now - 5 Minute Quick Start

## Choose Your Path

### ⚡ Path 1: Just See It Work (2 minutes)

```bash
cd /home/voir/Projects/index-tts

# Test the emotion parser
PYTHONPATH="$PYTHONPATH:." uv run indextts_app/test_emotion.py
```

You'll see:
- ✅ Emotion tag parsing in action
- ✅ Vector conversion examples
- ✅ Complex emotion scenarios
- ✅ Edge case handling

### 📖 Path 2: Understand Everything (15 minutes)

1. **Read DELIVERY_SUMMARY.md** (5 min)
   ```bash
   cat DELIVERY_SUMMARY.md | head -100
   ```

2. **Read QUICK_REFERENCE.md** (3 min)
   ```bash
   cat QUICK_REFERENCE.md
   ```

3. **Try Python API** (7 min)
   ```python
   python3 << 'EOF'
   from indextts_app.emotion import parse_emotion_tags_to_vectors
   from pathlib import Path
   from indextts_app.voice_library import VoiceLibraryManager
   
   # Parse emotions
   text = "[Happy:80]Hello [Angry:30]Where have you been?"
   segments, plain = parse_emotion_tags_to_vectors(text)
   print(f"Parsed: {[(t.strip(), v) for t, v in segments]}")
   
   # Check voice library
   manager = VoiceLibraryManager(Path("./voices"))
   print(f"Voices: {[v.name for v in manager.list_voices()]}")
   EOF
   ```

### 🛠️ Path 3: Build Something (30 minutes)

```python
# script.py
from pathlib import Path
from indextts_app.voice_library import VoiceLibraryManager, VoiceExtractor
from indextts_app.emotion import parse_emotion_tags_to_vectors
from indextts_app.utils import TTSSynthesizer, SynthesisRequest

# 1. Extract voice from media (if you have a video)
# extractor = VoiceExtractor()
# extractor.extract_audio(Path("video.mp4"), Path("voice.wav"))

# 2. Add to library
manager = VoiceLibraryManager(Path("./voices"))
# voice = manager.add_voice_from_file("My Voice", Path("voice.wav"))

# 3. Use existing voice from examples
from indextts_app.voice_library import VoiceLibrary
lib = VoiceLibrary(Path("./voices/voices.db"))
voices = lib.list_voices()
if not voices:
    print("No voices yet. Add one first!")
else:
    voice = voices[0]
    print(f"Using: {voice.name}")

# 4. Parse emotions
text_with_emotions = "[Happy:60]Hello world [Calm:40] this is nice"
segments, plain = parse_emotion_tags_to_vectors(text_with_emotions)

# 5. Would synthesize here (needs model loaded)
# synth = TTSSynthesizer(Path("./checkpoints/config.yaml"), Path("./checkpoints"))
# request = SynthesisRequest(text=plain, voice_id=voice.id, emotion_vector=segments[0][1])
# result = synth.synthesize(request, Path(voice.audio_path))

print("✅ All systems ready!")
```

Run it:
```bash
PYTHONPATH="$PYTHONPATH:." uv run script.py
```

---

## 📚 What You Have

### Code (indextts_app/)
```
✅ emotion/        - Parse [Emotion:Intensity]text
✅ voice_library/  - Store voices in SQLite  
✅ utils/          - Wrap IndexTTS2 model
✅ cli/            - Command-line interface
```

### Docs (Root Level)
```
✅ DELIVERY_SUMMARY.md      - What you got
✅ QUICK_REFERENCE.md       - Quick lookup
✅ INDEXTTS_APP_SETUP.md   - Getting started
✅ API_REFERENCE.md         - All functions
✅ DOCS_INDEX.md            - Navigation
```

### Examples
```
✅ examples/indextts_app_example.py  - Full walkthrough
✅ indextts_app/test_emotion.py      - Test suite
```

---

## 🎯 Common Tasks

### Parse Text with Emotions

```python
from indextts_app.emotion import parse_emotion_tags_to_vectors

text = "[Calm:70]Listen carefully [Angry:90] This is unacceptable!"
segments, plain_text = parse_emotion_tags_to_vectors(text)

for segment_text, emotion_vec in segments:
    print(f"'{segment_text.strip()}' -> {emotion_vec}")
```

### Add Voice to Library

```python
from indextts_app.voice_library import VoiceLibraryManager
from pathlib import Path

manager = VoiceLibraryManager(Path("./voices"))
voice = manager.add_voice_from_file(
    name="My Voice",
    audio_path=Path("voice.wav"),
    language="en",
    tags=["natural", "calm"]
)
print(f"✅ Added: {voice.name} (ID: {voice.id})")
```

### Extract Audio from Video

```python
from indextts_app.voice_library import VoiceExtractor
from pathlib import Path

extractor = VoiceExtractor()
success = extractor.extract_audio(
    Path("video.mp4"),
    Path("extracted_voice.wav"),
    sample_rate=24000
)
print("✅ Extracted!" if success else "✗ Failed")
```

### List All Voices

```python
manager = VoiceLibraryManager(Path("./voices"))
for voice in manager.list_voices():
    print(f"- {voice.name} ({voice.language})")
```

---

## 💡 Key Concepts

### Emotion Tags
```
[Emotion:Intensity]text
```
- 8 emotions: happy, angry, sad, afraid, disgusted, melancholic, surprised, calm
- Intensity: 0-100
- Example: `[Happy:80]Great! [Sad:50]But sad too.`

### Emotion Vectors
```python
[happy, angry, sad, afraid, disgusted, melancholic, surprised, calm]
[0.8  , 0    , 0   , 0     , 0        , 0          , 0        , 0.2  ]
```
- 8 values (0.0 to 1.0)
- Used by IndexTTS2 directly

### Voice Profile
```python
VoiceProfile(
    id="abc123",
    name="My Voice",
    audio_path="/path/to/voice.wav",
    language="en",
    tags=["natural", "calm"],
    duration=5.2,
    sample_rate=24000
)
```

---

## 🔧 CLI Commands

```bash
# Add voice
uv run -m indextts_app.cli voice add "My Voice" voice.wav

# List voices
uv run -m indextts_app.cli voice list

# Remove voice
uv run -m indextts_app.cli voice remove <voice-id>

# Extract audio from video
uv run -m indextts_app.cli extract audio video.mp4 voice.wav

# Extract 5-second segment
uv run -m indextts_app.cli extract audio video.mp4 segment.wav \
  --start 10.0 --duration 5.0

# Test synthesis (requires model)
uv run -m indextts_app.cli test speak "[Happy:80]Hello!" <voice-id>
```

---

## 📞 Need Help?

### Find Documentation
- Navigation: [DOCS_INDEX.md](./DOCS_INDEX.md)
- Quick lookup: [QUICK_REFERENCE.md](./QUICK_REFERENCE.md)
- API details: [API_REFERENCE.md](./API_REFERENCE.md)

### Troubleshoot
- FFmpeg: `sudo apt-get install ffmpeg`
- CUDA: `uv run tools/gpu_check.py`
- Import: `PYTHONPATH="$PYTHONPATH:." uv run script.py`

### See Examples
- Run tests: `PYTHONPATH="$PYTHONPATH:." uv run indextts_app/test_emotion.py`
- Full examples: `PYTHONPATH="$PYTHONPATH:." uv run examples/indextts_app_example.py`

---

## ✅ Next Steps

1. **Try Path 1** (2 min) - Run the test
2. **Read Path 2** (15 min) - Understand it
3. **Build Path 3** (30 min) - Make something
4. **Read docs** - Deep dive into features
5. **Build REST API** - Next phase

---

## 🎉 You're Ready!

Pick any path above and get started. Everything is ready to use! 🚀

**Questions?** See [DOCS_INDEX.md](./DOCS_INDEX.md) for navigation.

**Want to build REST API next?** See [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) → "Next Steps"

---

**Happy coding!** 💻✨
