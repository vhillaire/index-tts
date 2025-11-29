"""IndexTTS Home Assistant Integration

TTS service for Home Assistant that connects to IndexTTS REST API running on
a separate machine (e.g., 192.168.4.192:5150).

Features:
- Emotion-tagged speech synthesis
- Voice cloning from media files
- Voice library management
- Audio caching
- Integration with HA automations
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from pathlib import Path
import aiohttp

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_VOICE_ID
from homeassistant.components.tts import PLATFORM_SCHEMA, Provider, TtsAudioType
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

DOMAIN = "indextts"
CONF_API_URL = "api_url"
CONF_DEFAULT_VOICE = "default_voice"
CONF_CACHE_DIR = "cache_dir"

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_API_URL): cv.string,
        vol.Optional(CONF_DEFAULT_VOICE, default="default"): cv.string,
        vol.Optional(CONF_CACHE_DIR, default="tts_cache"): cv.string,
    }
)


async def async_get_engine(
    hass: HomeAssistant, config: dict, discovery_info: dict
) -> Optional["IndexTTSProvider"]:
    """Set up IndexTTS TTS component."""
    _LOGGER.debug("Setting up IndexTTS TTS")
    
    api_url = config.get(CONF_API_URL, "http://localhost:5150")
    default_voice = config.get(CONF_DEFAULT_VOICE, "default")
    cache_dir = config.get(CONF_CACHE_DIR, "tts_cache")
    
    # Ensure cache directory exists
    cache_path = Path(hass.config.path(cache_dir))
    cache_path.mkdir(parents=True, exist_ok=True)
    
    return IndexTTSProvider(hass, api_url, default_voice, cache_path)


class IndexTTSProvider(Provider):
    """IndexTTS TTS service provider for Home Assistant."""
    
    def __init__(
        self,
        hass: HomeAssistant,
        api_url: str,
        default_voice: str,
        cache_path: Path,
    ):
        """Initialize the TTS provider."""
        self.hass = hass
        self.api_url = api_url.rstrip("/")
        self.default_voice = default_voice
        self.cache_path = cache_path
        self.name = "IndexTTS"
        self._voices = {}
        self._session: Optional[aiohttp.ClientSession] = None
    
    @property
    def supported_languages(self) -> list[str]:
        """Return list of supported languages."""
        return ["en"]
    
    @property
    def supported_options(self) -> list[str]:
        """Return list of supported options."""
        return ["voice", "emotion"]
    
    async def async_get_supported_voices(self, language: str) -> list[dict]:
        """Return list of available voices."""
        if not self._voices:
            await self._fetch_voices()
        
        return [
            {
                "voice_id": voice["voice_id"],
                "name": voice["name"],
                "gender": voice.get("gender", "neutral"),
            }
            for voice in self._voices.values()
        ]
    
    async def _fetch_voices(self) -> None:
        """Fetch available voices from IndexTTS API."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.api_url}/api/voices",
                    timeout=aiohttp.ClientTimeout(total=10),
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        self._voices = {
                            v["voice_id"]: v for v in data.get("voices", [])
                        }
                        _LOGGER.debug(f"Fetched {len(self._voices)} voices from API")
                    else:
                        _LOGGER.error(f"Failed to fetch voices: {resp.status}")
        except Exception as err:
            _LOGGER.error(f"Error fetching voices: {err}")
    
    async def async_get_tts_audio(
        self,
        message: str,
        language: str,
        options: dict[str, Any],
    ) -> tuple[TtsAudioType, str]:
        """Convert text to speech and return audio file path."""
        
        # Get voice ID from options or use default
        voice_id = options.get("voice", self.default_voice)
        
        # Get emotion tags (if any) from options
        emotion = options.get("emotion", "")
        
        # Build text with emotion tags if provided
        if emotion:
            # Convert emotion option to tag format
            # emotion format: "emotion_name:intensity" e.g., "happy:80"
            text = f"[{emotion.title()}]{message}"
        else:
            text = message
        
        # Create cache key
        cache_key = self._get_cache_key(voice_id, text)
        cache_file = self.cache_path / f"{cache_key}.wav"
        
        # Return cached audio if available
        if cache_file.exists():
            _LOGGER.debug(f"Using cached audio: {cache_key}")
            return (TtsAudioType.WAV, str(cache_file))
        
        # Synthesize new audio
        try:
            audio_data = await self._synthesize(voice_id, text)
            
            # Save to cache
            cache_file.write_bytes(audio_data)
            _LOGGER.debug(f"Cached new audio: {cache_key}")
            
            return (TtsAudioType.WAV, str(cache_file))
        
        except Exception as err:
            _LOGGER.error(f"Synthesis failed: {err}")
            raise
    
    async def _synthesize(self, voice_id: str, text: str) -> bytes:
        """Call IndexTTS API to synthesize speech."""
        async with aiohttp.ClientSession() as session:
            payload = {
                "voice_id": voice_id,
                "text": text,
                "output_format": "wav",
            }
            
            try:
                async with session.post(
                    f"{self.api_url}/api/synthesize",
                    json=payload,
                    timeout=aiohttp.ClientTimeout(total=60),
                ) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        audio_file = result.get("audio_file")
                        
                        # Download audio from API
                        async with session.get(
                            f"{self.api_url}{audio_file}",
                            timeout=aiohttp.ClientTimeout(total=30),
                        ) as audio_resp:
                            if audio_resp.status == 200:
                                return await audio_resp.read()
                        
                        raise Exception(f"Failed to download audio: {audio_resp.status}")
                    else:
                        error_detail = await resp.text()
                        raise Exception(f"API error {resp.status}: {error_detail}")
            
            except asyncio.TimeoutError:
                raise Exception("Synthesis timeout - API took too long to respond")
    
    def _get_cache_key(self, voice_id: str, text: str) -> str:
        """Generate cache key for audio."""
        import hashlib
        
        key_str = f"{voice_id}:{text}"
        return hashlib.md5(key_str.encode()).hexdigest()


# For backward compatibility with older HA versions
async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the IndexTTS integration."""
    _LOGGER.debug("IndexTTS integration loading")
    return True
