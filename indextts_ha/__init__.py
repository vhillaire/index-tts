"""IndexTTS Home Assistant Integration - Main Entry Point

This integration registers IndexTTS as a TTS service for Home Assistant.
It connects to an IndexTTS REST API running on a separate machine.

Installation:
1. Copy this directory to: ~/.homeassistant/custom_components/indextts/
2. Restart Home Assistant
3. Add through Settings > Devices & Services > Create Integration
4. Configure API URL (e.g., http://192.168.4.192:5150)

Usage:
- TTS service: tts.indextts_speak
- Options: voice (voice_id), emotion (emotion:intensity)

Example automation:
  service: tts.indextts_speak
  data:
    message: "[Happy:80]Welcome home!"
    entity_id: media_player.living_room_speaker
    cache: true
"""

import logging
from typing import Final

_LOGGER = logging.getLogger(__name__)

DOMAIN: Final = "indextts"
VERSION: Final = "0.1.0"


async def async_setup(hass, config):
    """Set up the IndexTTS integration (legacy setup)."""
    _LOGGER.debug("IndexTTS integration initializing")
    return True
