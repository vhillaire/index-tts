"""Command-line interface for IndexTTS application"""

import click
from pathlib import Path
from typing import Optional


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """IndexTTS Standalone - Voice Cloning & Emotion-based TTS"""
    pass


@cli.group()
def voice():
    """Voice library management"""
    pass


@voice.command('add')
@click.argument('name')
@click.argument('audio_file', type=click.Path(exists=True))
@click.option('--description', '-d', help='Voice description')
@click.option('--language', '-l', default='auto', help='Language')
@click.option('--tags', '-t', multiple=True, help='Tags for the voice')
@click.option('--voice-dir', type=click.Path(), default='./voices', help='Voice library directory')
def add_voice(name, audio_file, description, language, tags, voice_dir):
    """Add a voice to the library"""
    from indextts_app.voice_library import VoiceLibraryManager
    
    manager = VoiceLibraryManager(Path(voice_dir))
    profile = manager.add_voice_from_file(
        name=name,
        audio_path=Path(audio_file),
        description=description,
        language=language,
        tags=list(tags) if tags else []
    )
    
    if profile:
        click.echo(f"✓ Voice added: {profile.name} (ID: {profile.id})")
    else:
        click.echo(f"✗ Failed to add voice (name may already exist)")


@voice.command('list')
@click.option('--voice-dir', type=click.Path(), default='./voices', help='Voice library directory')
def list_voices(voice_dir):
    """List all voices in the library"""
    from indextts_app.voice_library import VoiceLibraryManager
    
    manager = VoiceLibraryManager(Path(voice_dir))
    voices = manager.list_voices()
    
    if not voices:
        click.echo("No voices found in library")
        return
    
    click.echo(f"\n{'ID':<12} {'Name':<20} {'Language':<10} {'Created':<20}")
    click.echo("-" * 62)
    for voice in voices:
        click.echo(f"{voice.id:<12} {voice.name:<20} {voice.language:<10} {voice.created_at[:19]}")


@voice.command('remove')
@click.argument('voice_id')
@click.option('--voice-dir', type=click.Path(), default='./voices', help='Voice library directory')
@click.confirmation_option(prompt='Are you sure?')
def remove_voice(voice_id, voice_dir):
    """Remove a voice from the library"""
    from indextts_app.voice_library import VoiceLibraryManager
    
    manager = VoiceLibraryManager(Path(voice_dir))
    if manager.delete_voice(voice_id):
        click.echo(f"✓ Voice removed: {voice_id}")
    else:
        click.echo(f"✗ Voice not found: {voice_id}")


@cli.group()
def extract():
    """Extract audio from media files"""
    pass


@extract.command('audio')
@click.argument('input_file', type=click.Path(exists=True))
@click.argument('output_file', type=click.Path())
@click.option('--sample-rate', '-r', type=int, default=24000, help='Sample rate in Hz')
@click.option('--start', type=float, help='Start time in seconds')
@click.option('--duration', type=float, help='Duration in seconds')
def extract_audio(input_file, output_file, sample_rate, start, duration):
    """Extract audio from media file (MP4, MP3, etc.)"""
    from indextts_app.voice_library import VoiceExtractor
    
    extractor = VoiceExtractor()
    success = extractor.extract_audio(
        Path(input_file),
        Path(output_file),
        sample_rate=sample_rate,
        start_time=start,
        duration=duration
    )
    
    if success:
        click.echo(f"✓ Audio extracted to {output_file}")
    else:
        click.echo(f"✗ Failed to extract audio")


@cli.group()
def test():
    """Test TTS synthesis"""
    pass


@test.command('speak')
@click.argument('text')
@click.argument('voice_id')
@click.option('--emotion', '-e', help='Emotion tags like [Happy:50,Calm:30]text[Angry:70]more')
@click.option('--output', '-o', type=click.Path(), help='Output audio file')
@click.option('--config', type=click.Path(), default='./checkpoints/config.yaml', help='Config path')
@click.option('--model-dir', type=click.Path(), default='./checkpoints', help='Model directory')
@click.option('--voice-dir', type=click.Path(), default='./voices', help='Voice library directory')
@click.option('--fp16', is_flag=True, default=True, help='Use FP16 precision')
def test_speak(text, voice_id, emotion, output, config, model_dir, voice_dir, fp16):
    """Test TTS synthesis with emotion tags"""
    from indextts_app.voice_library import VoiceLibraryManager
    from indextts_app.utils import TTSSynthesizer, SynthesisRequest
    from indextts_app.emotion import parse_emotion_tags_to_vectors
    
    # Get voice from library
    manager = VoiceLibraryManager(Path(voice_dir))
    voice = manager.get_voice(voice_id)
    
    if not voice:
        click.echo(f"✗ Voice not found: {voice_id}")
        return
    
    # Initialize synthesizer
    try:
        synthesizer = TTSSynthesizer(
            config_path=Path(config),
            model_dir=Path(model_dir),
            use_fp16=fp16
        )
    except Exception as e:
        click.echo(f"✗ Failed to load model: {e}")
        return
    
    # Parse emotions if provided
    emotion_vector = None
    if emotion:
        segments, plain_text = parse_emotion_tags_to_vectors(emotion)
        if segments:
            _, emotion_vector = segments[0]
            text = plain_text
    
    # Create synthesis request
    request = SynthesisRequest(
        text=text,
        voice_id=voice_id,
        emotion_vector=emotion_vector
    )
    
    # Synthesize
    click.echo("Synthesizing...")
    result = synthesizer.synthesize(
        request,
        Path(voice.audio_path),
        Path(output) if output else None
    )
    
    if result.success:
        click.echo(f"✓ Synthesis complete: {result.audio_path}")
    else:
        click.echo(f"✗ Synthesis failed: {result.error}")


@cli.command()
def info():
    """Show application information"""
    from indextts_app import __version__
    
    click.echo(f"""
IndexTTS Standalone v{__version__}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Advanced Text-to-Speech with Voice Cloning & Emotion Control

Features:
  • Voice cloning from audio files
  • Voice library management
  • Emotion-based speech synthesis
  • Audio extraction from MP4, MP3, etc.
  • Emotion tag syntax: [Happy:60,Calm:40]text[Angry:30]more text

Commands:
  voice add       Add voice to library
  voice list      List all voices
  voice remove    Remove voice from library
  
  extract audio   Extract audio from media files
  
  test speak      Test TTS synthesis

Use 'indexttts COMMAND --help' for more information.
""")


if __name__ == '__main__':
    cli()
