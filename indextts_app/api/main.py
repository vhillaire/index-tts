"""Main entry point for IndexTTS REST API service

Run with:
    uvicorn indextts_app.api.main:app --host 0.0.0.0 --port 5150 --reload

Or with Python:
    python -m indextts_app.api.main

API Documentation:
    http://localhost:5150/docs (Swagger UI)
    http://localhost:5150/redoc (ReDoc)
"""

import uvicorn
from .app import app


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=5150,
        log_level="info",
        reload=True,  # Set to False in production
    )
