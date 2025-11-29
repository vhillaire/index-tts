"""
Audio extraction from media files

Extract audio from MP4, MP3, WAV, and other formats
"""

import subprocess
from pathlib import Path
from typing import Optional, Tuple


class VoiceExtractor:
    """Extract audio from various media formats"""
    
    SUPPORTED_FORMATS = {
        '.mp4', '.mkv', '.avi', '.mov', '.flv',  # Video
        '.mp3', '.m4a', '.aac', '.flac', '.wav', '.ogg'  # Audio
    }
    
    @staticmethod
    def get_audio_info(file_path: Path) -> Optional[dict]:
        """
        Get audio information using ffprobe
        
        Args:
            file_path: Path to media file
            
        Returns:
            Dict with duration, sample_rate, channels, etc.
        """
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-select_streams', 'a:0',
                '-show_entries', 'stream=duration,sample_rate,channels',
                '-of', 'default=noprint_wrappers=1:nokey=1:nokey=1',
                str(file_path)
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                return {
                    'duration': float(lines[0]) if lines[0] else 0.0,
                    'sample_rate': int(lines[1]) if len(lines) > 1 and lines[1] else 24000,
                    'channels': int(lines[2]) if len(lines) > 2 and lines[2] else 1,
                }
        except Exception:
            pass
        return None
    
    @staticmethod
    def extract_audio(
        input_path: Path,
        output_path: Path,
        sample_rate: int = 24000,
        channels: int = 1,
        start_time: Optional[float] = None,
        duration: Optional[float] = None
    ) -> bool:
        """
        Extract audio from media file
        
        Args:
            input_path: Input media file
            output_path: Output audio file (WAV format)
            sample_rate: Target sample rate in Hz
            channels: Number of audio channels
            start_time: Start time in seconds (optional)
            duration: Duration in seconds (optional)
            
        Returns:
            True if successful
        """
        cmd = [
            'ffmpeg',
            '-i', str(input_path),
            '-acodec', 'pcm_s16le',  # WAV codec
            '-ar', str(sample_rate),  # Sample rate
            '-ac', str(channels),  # Audio channels
            '-y',  # Overwrite output
            str(output_path)
        ]
        
        # Add time trimming if specified
        if start_time is not None or duration is not None:
            trim_cmd = ['ffmpeg', '-i', str(input_path)]
            if start_time is not None:
                trim_cmd.extend(['-ss', str(start_time)])
            if duration is not None:
                trim_cmd.extend(['-t', str(duration)])
            trim_cmd.extend([
                '-acodec', 'pcm_s16le',
                '-ar', str(sample_rate),
                '-ac', str(channels),
                '-y',
                str(output_path)
            ])
            cmd = trim_cmd
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                timeout=300,  # 5 minutes timeout
                check=False
            )
            return result.returncode == 0
        except subprocess.TimeoutExpired:
            return False
    
    @staticmethod
    def extract_audio_segment(
        input_path: Path,
        output_path: Path,
        start_time: float,
        duration: float,
        sample_rate: int = 24000
    ) -> bool:
        """
        Extract a segment from media file
        
        Args:
            input_path: Input media file
            output_path: Output audio file
            start_time: Start time in seconds
            duration: Duration in seconds
            sample_rate: Target sample rate
            
        Returns:
            True if successful
        """
        return VoiceExtractor.extract_audio(
            input_path,
            output_path,
            sample_rate=sample_rate,
            channels=1,
            start_time=start_time,
            duration=duration
        )


def extract_audio_from_file(
    file_path: Path,
    output_path: Path,
    sample_rate: int = 24000
) -> Tuple[bool, Optional[dict]]:
    """
    Extract audio from a media file (convenience function)
    
    Args:
        file_path: Input media file
        output_path: Output audio file
        sample_rate: Target sample rate
        
    Returns:
        Tuple of (success: bool, audio_info: dict)
    """
    extractor = VoiceExtractor()
    
    # Get audio info
    audio_info = extractor.get_audio_info(file_path)
    
    # Extract audio
    success = extractor.extract_audio(
        file_path,
        output_path,
        sample_rate=sample_rate
    )
    
    return success, audio_info
