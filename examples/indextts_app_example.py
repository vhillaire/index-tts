"""
Example usage of IndexTTS Standalone application

Demonstrates voice library management, emotion parsing, and synthesis
"""

from pathlib import Path
from indextts_app.voice_library import VoiceLibraryManager, VoiceExtractor
from indextts_app.emotion import parse_emotion_tags_to_vectors
from indextts_app.utils import TTSSynthesizer, SynthesisRequest


def example_voice_extraction():
    """Example: Extract audio from media file"""
    print("=" * 60)
    print("EXAMPLE 1: Extract Voice from Media")
    print("=" * 60)
    
    extractor = VoiceExtractor()
    
    # Check if we have a sample file
    sample_video = Path("examples/video.mp4")
    if sample_video.exists():
        print(f"Extracting audio from {sample_video}...")
        
        success = extractor.extract_audio(
            input_path=sample_video,
            output_path=Path("extracted_voice.wav"),
            sample_rate=24000
        )
        
        if success:
            print("✓ Audio extracted successfully!")
        else:
            print("✗ Failed to extract audio")
    else:
        print(f"Note: {sample_video} not found. Provide a video file to test extraction.")
    
    print()


def example_voice_management():
    """Example: Manage voice library"""
    print("=" * 60)
    print("EXAMPLE 2: Voice Library Management")
    print("=" * 60)
    
    manager = VoiceLibraryManager(Path("./voices"))
    
    # Check if we have example voices
    example_voice = Path("examples/voice_01.wav")
    if example_voice.exists():
        print(f"Adding voice from {example_voice}...")
        
        profile = manager.add_voice_from_file(
            name="Example Voice",
            audio_path=example_voice,
            description="An example voice for testing",
            language="en",
            tags=["example", "test"]
        )
        
        if profile:
            print(f"✓ Voice added! ID: {profile.id}")
    
    # List all voices
    voices = manager.list_voices()
    if voices:
        print(f"\nAvailable voices ({len(voices)}):")
        for voice in voices:
            print(f"  - {voice.name} (ID: {voice.id[:8]}...) - {voice.language}")
    else:
        print("\nNo voices in library yet.")
    
    print()


def example_emotion_parsing():
    """Example: Parse emotion tags"""
    print("=" * 60)
    print("EXAMPLE 3: Emotion Tag Parsing")
    print("=" * 60)
    
    # Example text with emotion tags
    text_with_emotions = """
    [Calm:60,Happy:40]Now I've been waiting patiently [Angry:30] \
    It's been 2 weeks [Angry:60,Hate:80] Now I want my $2 Mister!
    """
    
    print("Input text:")
    print(text_with_emotions)
    
    # Parse emotion tags
    segments, plain_text = parse_emotion_tags_to_vectors(text_with_emotions)
    
    print("\nParsed segments:")
    emotions_map = {
        0: "happy", 1: "angry", 2: "sad", 3: "afraid",
        4: "disgusted", 5: "melancholic", 6: "surprised", 7: "calm"
    }
    
    for i, (text_seg, emotion_vec) in enumerate(segments):
        print(f"\nSegment {i+1}:")
        print(f"  Text: {text_seg.strip()}")
        print(f"  Emotions: {[f'{emotions_map[j]}={v:.2f}' for j, v in enumerate(emotion_vec) if v > 0]}")
    
    print(f"\nPlain text (without tags):\n{plain_text}")
    print()


def example_synthesis():
    """Example: Test synthesis (requires model)"""
    print("=" * 60)
    print("EXAMPLE 4: Text-to-Speech Synthesis")
    print("=" * 60)
    
    config_path = Path("./checkpoints/config.yaml")
    model_dir = Path("./checkpoints")
    
    if not config_path.exists():
        print("⚠ Model config not found at ./checkpoints/config.yaml")
        print("Download the model first:")
        print("  uv tool install 'huggingface-hub[cli,hf_xet]'")
        print("  hf download IndexTeam/IndexTTS-2 --local-dir=checkpoints")
        return
    
    print("Initializing TTS model...")
    try:
        synthesizer = TTSSynthesizer(
            config_path=config_path,
            model_dir=model_dir,
            use_fp16=True
        )
        print("✓ Model loaded!")
    except Exception as e:
        print(f"✗ Failed to load model: {e}")
        return
    
    # Get voice from library
    manager = VoiceLibraryManager(Path("./voices"))
    voices = manager.list_voices()
    
    if not voices:
        print("⚠ No voices in library. Add a voice first using Example 2.")
        return
    
    voice = voices[0]
    print(f"Using voice: {voice.name}")
    
    # Create synthesis request with emotions
    text = "Hello! How are you today?"
    request = SynthesisRequest(
        text=text,
        voice_id=voice.id,
        emotion_vector=[0.7, 0, 0, 0, 0, 0, 0, 0.3]  # Happy + Calm
    )
    
    print(f"Synthesizing: '{text}'")
    print("Emotions: Happy (0.7) + Calm (0.3)")
    
    try:
        result = synthesizer.synthesize(
            request,
            Path(voice.audio_path),
            Path("example_output.wav")
        )
        
        if result.success:
            print(f"✓ Synthesis complete!")
            print(f"  Output: {result.audio_path}")
        else:
            print(f"✗ Synthesis failed: {result.error}")
    except Exception as e:
        print(f"✗ Error during synthesis: {e}")
    
    print()


def main():
    """Run all examples"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  IndexTTS Standalone Application - Examples".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print()
    
    try:
        # Example 1: Voice Extraction
        example_voice_extraction()
        
        # Example 2: Voice Management
        example_voice_management()
        
        # Example 3: Emotion Parsing
        example_emotion_parsing()
        
        # Example 4: Synthesis
        example_synthesis()
        
        print("=" * 60)
        print("Examples completed!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
