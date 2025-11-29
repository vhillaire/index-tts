"""IndexTTS REST API Service

Provides a FastAPI-based microservice for IndexTTS2 with emotion-tagged synthesis,
voice cloning, and voice library management.

Port: 5150
Base URL: http://localhost:5150

Main Endpoints:
- POST /api/voices/extract - Clone voice from media file
- GET/POST/DELETE /api/voices - Manage voice library
- POST /api/synthesize - Generate speech with emotion tags
- GET /health - Health check
- GET /docs - Interactive API documentation (Swagger UI)

Examples:
    # Clone voice from MP4
    curl -F "file=@video.mp4" http://localhost:5150/api/voices/extract

    # List voices
    curl http://localhost:5150/api/voices

    # Synthesize with emotion tags
    curl -X POST http://localhost:5150/api/synthesize \
      -H "Content-Type: application/json" \
      -d '{
        "voice_id": "my-voice",
        "text": "[Happy:80]Hello world[Calm:60]!"
      }'
"""

__version__ = "0.2.0"
