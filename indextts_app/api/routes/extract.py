"""Audio extraction endpoints"""

from fastapi import APIRouter, UploadFile, File, HTTPException, status, Form
from typing import Optional

from ..voice_library import VoiceExtractor, VoiceLibraryManager
from .models import ExtractRequest, ExtractResponse
import tempfile
from pathlib import Path

router = APIRouter(prefix="/extract", tags=["Extraction"])

extractor = VoiceExtractor()
voice_manager = VoiceLibraryManager()


@router.post("", response_model=ExtractResponse, status_code=status.HTTP_201_CREATED)
async def extract_voice(
    file: UploadFile = File(..., description="Media file (MP4, MP3, WAV, etc.)"),
    voice_name: str = Form(..., description="Name for the cloned voice"),
    start_time: Optional[float] = Form(None, description="Start time in seconds"),
    end_time: Optional[float] = Form(None, description="End time in seconds"),
    description: Optional[str] = Form(None, description="Voice description"),
):
    """
    Extract audio from media file and create a voice profile
    
    Supports MP4, MP3, WAV, and 50+ audio/video formats via FFmpeg.
    
    Args:
        file: Uploaded media file
        voice_name: Name for the cloned voice
        start_time: Optional start time for clip (seconds)
        end_time: Optional end time for clip (seconds)
        description: Optional description of the voice
    
    Returns:
        Extracted voice profile with metadata
    
    Raises:
        400: Invalid file format or parameters
        500: Extraction failed
    """
    try:
        # Create temporary file for upload
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = Path(tmp.name)
        
        # Extract audio
        try:
            audio_path = extractor.extract_audio_segment(
                tmp_path,
                start_time=start_time,
                end_time=end_time,
            )
            
            # Create voice profile
            voice = voice_manager.add_voice(
                name=voice_name,
                description=description or f"Extracted from {file.filename}",
                source_media=file.filename,
                metadata={
                    "extraction_start": start_time,
                    "extraction_end": end_time,
                    "source_format": Path(file.filename).suffix,
                },
            )
            
            # Get audio duration
            info = extractor.get_audio_info(audio_path)
            duration = float(info.get("duration", 0))
            
            return ExtractResponse(
                voice_id=voice.voice_id,
                name=voice.name,
                duration=duration,
                created_at=voice.created_at,
                message=f"Voice '{voice_name}' extracted successfully from {file.filename}",
            )
        finally:
            # Cleanup temp file
            if tmp_path.exists():
                tmp_path.unlink()
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Audio extraction failed: {str(e)}",
        )
