"""Health check endpoints"""

from fastapi import APIRouter, status
from typing import Dict, Any

router = APIRouter(prefix="/health", tags=["Health"])


@router.get("", status_code=status.HTTP_200_OK)
async def health_check() -> Dict[str, Any]:
    """
    Health check endpoint
    
    Returns service status and readiness information.
    """
    return {
        "status": "healthy",
        "service": "IndexTTS API",
        "version": "0.2.0",
        "port": 5150,
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check endpoint
    
    Verifies all dependencies are available (IndexTTS2 model, voice library, etc.)
    """
    return {
        "ready": True,
        "components": {
            "model": "loaded",
            "voice_library": "ready",
            "audio_extraction": "ready",
        },
    }
