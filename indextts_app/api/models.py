"""Request/Response models for the API"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# ==================== Voice Models ====================

class VoiceProfileResponse(BaseModel):
    """Voice profile response model"""
    voice_id: str = Field(..., description="Unique voice identifier")
    name: str = Field(..., description="Human-readable voice name")
    description: Optional[str] = Field(None, description="Voice description")
    gender: Optional[str] = Field(None, description="Voice gender (male/female/neutral)")
    source_media: Optional[str] = Field(None, description="Original media file")
    created_at: datetime = Field(..., description="Creation timestamp")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "voice_id": "voice_abc123",
                "name": "John Doe",
                "description": "Deep, calm male voice",
                "gender": "male",
                "source_media": "recording.mp4",
                "created_at": "2025-11-29T10:30:00",
                "metadata": {"age": 35, "accent": "neutral"}
            }
        }


class VoiceListResponse(BaseModel):
    """List of voices response"""
    voices: List[VoiceProfileResponse] = Field(..., description="List of voice profiles")
    count: int = Field(..., description="Total number of voices")


class VoiceCreateRequest(BaseModel):
    """Request to add a new voice"""
    name: str = Field(..., description="Voice name")
    description: Optional[str] = Field(None, description="Voice description")
    gender: Optional[str] = Field(None, description="Voice gender")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Sarah",
                "description": "Friendly female voice",
                "gender": "female",
                "metadata": {"language": "en-US"}
            }
        }


# ==================== Extraction Models ====================

class ExtractRequest(BaseModel):
    """Request to extract audio from media file"""
    voice_name: str = Field(..., description="Name for the cloned voice")
    start_time: Optional[float] = Field(None, description="Start time in seconds (optional)")
    end_time: Optional[float] = Field(None, description="End time in seconds (optional)")
    description: Optional[str] = Field(None, description="Voice description")

    class Config:
        json_schema_extra = {
            "example": {
                "voice_name": "clip_from_video",
                "start_time": 10.5,
                "end_time": 30.2,
                "description": "Extracted from presentation video"
            }
        }


class ExtractResponse(BaseModel):
    """Response from audio extraction"""
    voice_id: str = Field(..., description="ID of created voice")
    name: str = Field(..., description="Voice name")
    duration: float = Field(..., description="Duration of extracted audio in seconds")
    created_at: datetime = Field(..., description="Creation timestamp")
    message: str = Field(..., description="Status message")

    class Config:
        json_schema_extra = {
            "example": {
                "voice_id": "voice_xyz789",
                "name": "clip_from_video",
                "duration": 19.7,
                "created_at": "2025-11-29T10:30:00",
                "message": "Voice extracted successfully"
            }
        }


# ==================== Synthesis Models ====================

class SynthesisRequest(BaseModel):
    """Request to synthesize speech"""
    voice_id: str = Field(..., description="ID of voice to use")
    text: str = Field(..., description="Text to synthesize (can include emotion tags like [Happy:80]text)")
    output_format: Optional[str] = Field("wav", description="Output format (wav, mp3, ogg)")
    speed: Optional[float] = Field(1.0, description="Speech speed multiplier (0.5-2.0)")

    class Config:
        json_schema_extra = {
            "example": {
                "voice_id": "voice_abc123",
                "text": "[Happy:80]Hello world![Calm:60] How are you?",
                "output_format": "wav",
                "speed": 1.0
            }
        }


class SynthesisResponse(BaseModel):
    """Response from synthesis request"""
    audio_file: str = Field(..., description="Path or URL to generated audio")
    duration: float = Field(..., description="Duration in seconds")
    format: str = Field(..., description="Audio format")
    emotions_applied: Dict[str, int] = Field(..., description="Emotions and intensities applied")
    message: str = Field(..., description="Status message")

    class Config:
        json_schema_extra = {
            "example": {
                "audio_file": "/audio/synthesis_12345.wav",
                "duration": 3.5,
                "format": "wav",
                "emotions_applied": {"happy": 80, "calm": 60},
                "message": "Synthesis completed successfully"
            }
        }


# ==================== Error Models ====================

class ErrorResponse(BaseModel):
    """Standard error response"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    status_code: int = Field(..., description="HTTP status code")

    class Config:
        json_schema_extra = {
            "example": {
                "error": "Voice not found",
                "detail": "Voice with ID 'invalid_id' does not exist",
                "status_code": 404
            }
        }
