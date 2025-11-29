"""Speech synthesis endpoints"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import FileResponse
from typing import Dict

from ..utils import TTSSynthesizer
from ..emotion import parse_emotion_tags
from ..voice_library import VoiceLibraryManager
from .models import SynthesisRequest, SynthesisResponse
from pathlib import Path

router = APIRouter(prefix="/synthesize", tags=["Synthesis"])

synthesizer = TTSSynthesizer()
voice_manager = VoiceLibraryManager()


@router.post("", response_model=SynthesisResponse)
async def synthesize_speech(request: SynthesisRequest):
    """
    Synthesize speech with emotion-tagged text
    
    Supports emotion tags in the format: [Emotion:Intensity]text
    
    Supported emotions: happy, angry, sad, afraid, disgusted, melancholic, surprised, calm
    Intensity: 0-100
    
    Example:
        [Happy:80]Hello![Calm:60] How are you?
    
    Args:
        request: Synthesis request with voice_id, text, and optional parameters
    
    Returns:
        Generated audio file and metadata
    
    Raises:
        404: Voice not found
        400: Invalid emotion tags or parameters
        500: Synthesis failed
    """
    try:
        # Verify voice exists
        voice = voice_manager.get_voice(request.voice_id)
        if not voice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Voice '{request.voice_id}' not found",
            )
        
        # Parse emotion tags
        emotion_vector, text_clean = parse_emotion_tags(request.text)
        
        # Synthesize
        result = synthesizer.synthesize(
            voice_id=request.voice_id,
            text=text_clean,
            emotion_vector=emotion_vector,
            speed=request.speed,
        )
        
        # Convert emotion vector back to readable format
        emotions_applied = {}
        emotion_names = ["happy", "angry", "sad", "afraid", "disgusted", "melancholic", "surprised", "calm"]
        for i, name in enumerate(emotion_names):
            if i < len(result.emotion_vector) and result.emotion_vector[i] > 0:
                emotions_applied[name] = int(result.emotion_vector[i] * 100)
        
        return SynthesisResponse(
            audio_file=str(result.audio_path),
            duration=result.duration,
            format=request.output_format,
            emotions_applied=emotions_applied,
            message="Synthesis completed successfully",
        )
    
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid emotion tags: {str(e)}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Synthesis failed: {str(e)}",
        )


@router.get("/audio/{audio_id}")
async def get_audio(audio_id: str):
    """
    Download generated audio file
    
    Args:
        audio_id: Audio file identifier
    
    Returns:
        Audio file as binary stream
    """
    try:
        # Construct path (simplified - in production, use proper path resolution)
        audio_path = Path(f"./audio/{audio_id}")
        
        if not audio_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Audio file '{audio_id}' not found",
            )
        
        return FileResponse(
            path=audio_path,
            media_type="audio/wav",
            filename=audio_path.name,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve audio: {str(e)}",
        )
