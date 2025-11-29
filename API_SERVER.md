# IndexTTS REST API Server

Complete REST API microservice for IndexTTS2 with emotion-tagged speech synthesis, voice cloning, and library management.

**Port**: 5150  
**Base URL**: `http://localhost:5150`  
**API Documentation**: `http://localhost:5150/docs` (Interactive Swagger UI)

## Quick Start

### 1. Run Locally

```bash
# Install dependencies
pip install fastapi uvicorn python-multipart

# Run the server
PYTHONPATH="$PYTHONPATH:." python -m indextts_app.api.main
```

The server will start on `http://localhost:5150`

### 2. Run with Docker

```bash
# Build and run
docker-compose up --build

# Or just run the container
docker build -t indextts-api .
docker run -p 5150:5150 \
  -v $(pwd)/checkpoints:/app/checkpoints \
  -v $(pwd)/voices:/app/voices \
  --gpus all \
  indextts-api
```

### 3. Test Health

```bash
curl http://localhost:5150/health
```

Response:
```json
{
  "status": "healthy",
  "service": "IndexTTS API",
  "version": "0.2.0",
  "port": 5150
}
```

## API Endpoints

### Health & Status

#### `GET /health`
Service health check.

```bash
curl http://localhost:5150/health
```

#### `GET /health/ready`
Readiness check (all dependencies available).

```bash
curl http://localhost:5150/health/ready
```

---

### Voice Management

#### `GET /api/voices`
List all voices in the library.

```bash
curl http://localhost:5150/api/voices
```

Response:
```json
{
  "voices": [
    {
      "voice_id": "voice_abc123",
      "name": "John Doe",
      "description": "Deep, calm male voice",
      "gender": "male",
      "source_media": "recording.mp4",
      "created_at": "2025-11-29T10:30:00",
      "metadata": {"age": 35}
    }
  ],
  "count": 1
}
```

#### `GET /api/voices/{voice_id}`
Get details of a specific voice.

```bash
curl http://localhost:5150/api/voices/voice_abc123
```

#### `POST /api/voices`
Create a new voice profile (without extraction).

```bash
curl -X POST http://localhost:5150/api/voices \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Sarah",
    "description": "Friendly female voice",
    "gender": "female",
    "metadata": {"language": "en-US"}
  }'
```

#### `DELETE /api/voices/{voice_id}`
Delete a voice from the library.

```bash
curl -X DELETE http://localhost:5150/api/voices/voice_abc123
```

---

### Audio Extraction

#### `POST /api/extract`
Extract audio from media file and create a voice profile.

Supports: MP4, MP3, WAV, MKV, AVI, MOV, FLAC, OGG, and 50+ formats

```bash
curl -F "file=@video.mp4" \
  -F "voice_name=my_voice" \
  -F "description=Extracted from video" \
  http://localhost:5150/api/extract
```

With optional time range:
```bash
curl -F "file=@recording.mp4" \
  -F "voice_name=clip1" \
  -F "start_time=10.5" \
  -F "end_time=30.2" \
  http://localhost:5150/api/extract
```

Response:
```json
{
  "voice_id": "voice_xyz789",
  "name": "my_voice",
  "duration": 19.7,
  "created_at": "2025-11-29T10:30:00",
  "message": "Voice extracted successfully from video.mp4"
}
```

---

### Speech Synthesis

#### `POST /api/synthesize`
Synthesize speech with emotion tags.

Supported emotions: `happy`, `angry`, `sad`, `afraid`, `disgusted`, `melancholic`, `surprised`, `calm`

Intensity: 0-100

```bash
curl -X POST http://localhost:5150/api/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "voice_id": "voice_abc123",
    "text": "[Happy:80]Hello world![Calm:60] How are you?",
    "output_format": "wav",
    "speed": 1.0
  }'
```

Response:
```json
{
  "audio_file": "/audio/synthesis_12345.wav",
  "duration": 3.5,
  "format": "wav",
  "emotions_applied": {
    "happy": 80,
    "calm": 60
  },
  "message": "Synthesis completed successfully"
}
```

#### Emotion Tag Syntax

Use emotion tags to control the speech synthesis:

```
[Emotion:Intensity]text
```

**Examples**:
- `[Happy:100]I'm so excited!` - Very happy
- `[Angry:80]That's terrible!` - Quite angry
- `[Calm:50]Let's take it easy.` - Mildly calm
- Mixed: `[Happy:80]Great news![Calm:60] Everything is fine now.`

---

## Integration Examples

### Python Client

```python
import requests

API_URL = "http://localhost:5150"

# Extract voice from media
extract_response = requests.post(
    f"{API_URL}/api/extract",
    files={"file": open("video.mp4", "rb")},
    data={
        "voice_name": "my_voice",
        "description": "From my video"
    }
)
voice_id = extract_response.json()["voice_id"]

# Synthesize with emotions
synthesis_response = requests.post(
    f"{API_URL}/api/synthesize",
    json={
        "voice_id": voice_id,
        "text": "[Happy:80]Hello![Calm:60] Nice to meet you.",
        "output_format": "wav"
    }
)
audio_file = synthesis_response.json()["audio_file"]
print(f"Audio saved to: {audio_file}")

# List voices
voices = requests.get(f"{API_URL}/api/voices").json()
for voice in voices["voices"]:
    print(f"- {voice['name']} ({voice['voice_id']})")
```

### JavaScript/Node.js Client

```javascript
const API_URL = "http://localhost:5150";

// Synthesize speech
async function speak(voiceId, text) {
  const response = await fetch(`${API_URL}/api/synthesize`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      voice_id: voiceId,
      text: text,
      output_format: "wav"
    })
  });
  
  const result = await response.json();
  console.log(`Audio file: ${result.audio_file}`);
  return result;
}

// List voices
async function listVoices() {
  const response = await fetch(`${API_URL}/api/voices`);
  const data = await response.json();
  
  for (const voice of data.voices) {
    console.log(`- ${voice.name} (${voice.voice_id})`);
  }
}

// Usage
await speak("voice_abc123", "[Happy:80]Hello world!");
await listVoices();
```

### Trivok Integration

In Trivok's coder brain, use terminal commands to call IndexTTS:

```bash
# Extract voice
curl -F "file=@recording.mp4" \
  -F "voice_name=my_voice" \
  http://localhost:5150/api/extract

# Synthesize
curl -X POST http://localhost:5150/api/synthesize \
  -H "Content-Type: application/json" \
  -d '{
    "voice_id": "voice_abc123",
    "text": "[Happy:80]Hello from Trivok!"
  }'
```

### Home Assistant Integration

Example automation using IndexTTS:

```yaml
automation:
  - alias: "Speak with emotion"
    trigger:
      platform: state
      entity_id: sensor.something
    action:
      service: shell_command.speak_with_emotion
      data:
        text: "[Happy:80]Hello![Calm:60] Everything is ready."

shell_command:
  speak_with_emotion: |
    curl -X POST http://localhost:5150/api/synthesize \
      -H "Content-Type: application/json" \
      -d '{
        "voice_id": "home_voice",
        "text": "{{ text }}"
      }' | jq -r .audio_file
```

---

## API Response Format

All successful responses follow this pattern:

```json
{
  "data": { /* response-specific data */ },
  "status": "success",
  "timestamp": "2025-11-29T10:30:00Z"
}
```

Error responses:

```json
{
  "error": "Error message",
  "detail": "Detailed error information",
  "status_code": 400
}
```

---

## Configuration

### Environment Variables

```bash
# Server configuration
PORT=5150                           # API port
HOST=0.0.0.0                        # Bind address
RELOAD=true                         # Auto-reload on file changes (dev only)

# Model configuration
CUDA_VISIBLE_DEVICES=0              # GPU device(s) to use
INDEX_TTS_MODEL_PATH=./checkpoints  # Model weights location

# Voice library
VOICE_LIBRARY_PATH=./voices         # Voice profiles directory
AUDIO_OUTPUT_PATH=./audio           # Generated audio output directory
```

### Requirements

See `requirements.txt`:
```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
torch==2.1.0
torchaudio==2.1.0
```

---

## Troubleshooting

**Connection refused**
```bash
# Check if server is running
curl http://localhost:5150/health

# If not, start it
python -m indextts_app.api.main
```

**GPU not detected**
```bash
# Check GPU availability
nvidia-smi

# Set GPU device
export CUDA_VISIBLE_DEVICES=0
python -m indextts_app.api.main
```

**Model not found**
```bash
# Ensure checkpoints are downloaded
ls -la checkpoints/

# If missing, run
hf download IndexTeam/IndexTTS-2 --local-dir=checkpoints
```

**Audio extraction fails**
```bash
# Ensure FFmpeg is installed
which ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
choco install ffmpeg
```

---

## Performance Tips

- **GPU acceleration**: IndexTTS2 runs on GPU by default. For CPU-only, set `CUDA_VISIBLE_DEVICES=""` before starting
- **Batch processing**: Send multiple synthesis requests to take advantage of GPU throughput
- **Audio format**: WAV is fastest; MP3 requires encoding overhead
- **Model caching**: First request loads model into memory; subsequent requests are much faster

---

## Deployment

### Production Checklist

- [ ] Set `RELOAD=false` in environment
- [ ] Use production ASGI server: `gunicorn` or `uvicorn` with multiple workers
- [ ] Add authentication/authorization
- [ ] Set up monitoring and logging
- [ ] Use reverse proxy (nginx) for load balancing
- [ ] Configure CORS for your frontend domains
- [ ] Use HTTPS with valid certificates
- [ ] Set resource limits (CPU, memory, GPU)

### Example Production Deployment

```bash
# With Gunicorn (multiple workers)
gunicorn indextts_app.api.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:5150 \
  --access-logfile - \
  --error-logfile - \
  --log-level info
```

---

## License

MIT - See LICENSE file

