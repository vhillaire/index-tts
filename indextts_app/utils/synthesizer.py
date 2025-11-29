"""
TTS Synthesizer wrapper around IndexTTS2

Manages model initialization and synthesis requests
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple
from datetime import datetime
import tempfile


@dataclass
class SynthesisRequest:
    """Request for TTS synthesis"""
    text: str
    voice_id: str
    emotion_vector: Optional[List[float]] = None
    emotion_text: Optional[str] = None
    use_emotion_text: bool = False
    use_random: bool = False
    language: str = "auto"
    output_format: str = "wav"  # wav, mp3, ogg, m4a


@dataclass
class SynthesisResult:
    """Result of TTS synthesis"""
    success: bool
    audio_path: Optional[str] = None
    duration: Optional[float] = None
    sample_rate: int = 24000
    error: Optional[str] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


class TTSSynthesizer:
    """Wrapper around IndexTTS2 for synthesis"""
    
    def __init__(
        self,
        config_path: Path,
        model_dir: Path,
        use_fp16: bool = True,
        use_cuda_kernel: bool = True,
        use_deepspeed: bool = False
    ):
        """
        Initialize TTS synthesizer
        
        Args:
            config_path: Path to config.yaml
            model_dir: Directory containing model weights
            use_fp16: Use half-precision for faster inference
            use_cuda_kernel: Use CUDA kernels if available
            use_deepspeed: Use DeepSpeed for acceleration
        """
        self.config_path = Path(config_path)
        self.model_dir = Path(model_dir)
        self.use_fp16 = use_fp16
        self.use_cuda_kernel = use_cuda_kernel
        self.use_deepspeed = use_deepspeed
        self.model = None
        self._load_model()
    
    def _load_model(self):
        """Load IndexTTS2 model"""
        try:
            from indextts.infer_v2 import IndexTTS2
            self.model = IndexTTS2(
                cfg_path=str(self.config_path),
                model_dir=str(self.model_dir),
                use_fp16=self.use_fp16,
                use_cuda_kernel=self.use_cuda_kernel,
                use_deepspeed=self.use_deepspeed
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load IndexTTS2 model: {e}")
    
    def synthesize(
        self,
        request: SynthesisRequest,
        voice_audio_path: Path,
        output_path: Optional[Path] = None
    ) -> SynthesisResult:
        """
        Synthesize speech
        
        Args:
            request: Synthesis request
            voice_audio_path: Path to voice reference audio
            output_path: Where to save output (optional, creates temp file if not provided)
            
        Returns:
            SynthesisResult with success status and audio path
        """
        if self.model is None:
            return SynthesisResult(
                success=False,
                error="Model not loaded"
            )
        
        if output_path is None:
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(
                suffix=f".{request.output_format}",
                delete=False
            )
            output_path = Path(temp_file.name)
            temp_file.close()
        
        try:
            # Build synthesis kwargs
            kwargs = {
                'spk_audio_prompt': str(voice_audio_path),
                'text': request.text,
                'output_path': str(output_path),
                'verbose': False
            }
            
            # Add emotion parameters if provided
            if request.emotion_vector is not None:
                kwargs['emo_vector'] = request.emotion_vector
            
            if request.emotion_text is not None:
                kwargs['emo_text'] = request.emotion_text
                kwargs['use_emo_text'] = request.use_emotion_text
            
            if request.use_emotion_text:
                kwargs['use_emo_text'] = True
            
            kwargs['use_random'] = request.use_random
            
            # Perform inference
            self.model.infer(**kwargs)
            
            # Verify output file was created
            if not output_path.exists():
                return SynthesisResult(
                    success=False,
                    error="Output file not created"
                )
            
            return SynthesisResult(
                success=True,
                audio_path=str(output_path),
                sample_rate=24000  # IndexTTS2 default
            )
            
        except Exception as e:
            # Clean up temp file on error
            if output_path.exists():
                output_path.unlink()
            return SynthesisResult(
                success=False,
                error=str(e)
            )
    
    def synthesize_with_emotions(
        self,
        text: str,
        voice_audio_path: Path,
        emotion_segments: List[Tuple[str, List[float]]],
        output_path: Optional[Path] = None
    ) -> SynthesisResult:
        """
        Synthesize with multiple emotion segments
        
        Currently does simple stitching by using the first emotion for the whole text.
        In future, this could be enhanced to do segment-level synthesis and combining.
        
        Args:
            text: Full text to synthesize
            voice_audio_path: Voice reference audio
            emotion_segments: List of (text_segment, emotion_vector) tuples
            output_path: Output path
            
        Returns:
            SynthesisResult
        """
        if not emotion_segments:
            request = SynthesisRequest(
                text=text,
                voice_id="default"
            )
            return self.synthesize(request, voice_audio_path, output_path)
        
        # Use first emotion for now
        _, first_emotion = emotion_segments[0]
        request = SynthesisRequest(
            text=text,
            voice_id="default",
            emotion_vector=first_emotion
        )
        return self.synthesize(request, voice_audio_path, output_path)
