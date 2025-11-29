"""Voice management endpoints"""

from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime

from ..voice_library import VoiceLibraryManager
from .models import VoiceProfileResponse, VoiceListResponse, VoiceCreateRequest

router = APIRouter(prefix="/voices", tags=["Voices"])

# Initialize voice library manager (singleton-like)
voice_manager = VoiceLibraryManager()


@router.get("", response_model=VoiceListResponse)
async def list_voices():
    """
    List all voices in the library
    
    Returns a list of all available voice profiles with metadata.
    """
    try:
        voices = voice_manager.list_voices()
        return VoiceListResponse(
            voices=[
                VoiceProfileResponse(
                    voice_id=v.voice_id,
                    name=v.name,
                    description=v.description,
                    gender=v.gender,
                    source_media=v.source_media,
                    created_at=v.created_at,
                    metadata=v.metadata,
                )
                for v in voices
            ],
            count=len(voices),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list voices: {str(e)}",
        )


@router.get("/{voice_id}", response_model=VoiceProfileResponse)
async def get_voice(voice_id: str):
    """
    Get details of a specific voice
    
    Args:
        voice_id: The unique identifier of the voice
    
    Returns:
        Voice profile with all metadata
    """
    try:
        voice = voice_manager.get_voice(voice_id)
        if not voice:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Voice '{voice_id}' not found",
            )
        return VoiceProfileResponse(
            voice_id=voice.voice_id,
            name=voice.name,
            description=voice.description,
            gender=voice.gender,
            source_media=voice.source_media,
            created_at=voice.created_at,
            metadata=voice.metadata,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get voice: {str(e)}",
        )


@router.post("", response_model=VoiceProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_voice(request: VoiceCreateRequest):
    """
    Create a new voice profile
    
    Useful for manually adding voices to the library without extraction.
    For cloning from media, use POST /api/extract instead.
    
    Args:
        request: Voice creation request with name and optional metadata
    
    Returns:
        Created voice profile
    """
    try:
        voice = voice_manager.add_voice(
            name=request.name,
            description=request.description,
            gender=request.gender,
            metadata=request.metadata,
        )
        return VoiceProfileResponse(
            voice_id=voice.voice_id,
            name=voice.name,
            description=voice.description,
            gender=voice.gender,
            source_media=voice.source_media,
            created_at=voice.created_at,
            metadata=voice.metadata,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create voice: {str(e)}",
        )


@router.delete("/{voice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_voice(voice_id: str):
    """
    Delete a voice from the library
    
    Args:
        voice_id: The unique identifier of the voice to delete
    """
    try:
        success = voice_manager.remove_voice(voice_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Voice '{voice_id}' not found",
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete voice: {str(e)}",
        )
