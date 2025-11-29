"""IndexTTS Home Assistant Integration - Config Flow

Handles configuration and setup of the IndexTTS integration through HA UI.
"""

import logging
from typing import Any, Dict, Optional

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import aiohttp

_LOGGER = logging.getLogger(__name__)

DOMAIN = "indextts"
CONF_API_URL = "api_url"
CONF_DEFAULT_VOICE = "default_voice"


class IndexTTSConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for IndexTTS."""
    
    VERSION = 1
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_POLL
    
    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: Dict[str, str] = {}
        
        if user_input is not None:
            # Validate the API connection
            try:
                api_url = user_input.get(CONF_API_URL, "").rstrip("/")
                
                # Test connection
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"{api_url}/health",
                        timeout=aiohttp.ClientTimeout(total=10),
                    ) as resp:
                        if resp.status == 200:
                            health = await resp.json()
                            _LOGGER.info(
                                f"Connected to IndexTTS API at {api_url}: "
                                f"{health.get('service')} v{health.get('version')}"
                            )
                        else:
                            errors["base"] = "invalid_auth"
            
            except asyncio.TimeoutError:
                errors["base"] = "timeout_connect"
            except aiohttp.ClientError as err:
                _LOGGER.error(f"Connection error: {err}")
                errors["base"] = "cannot_connect"
            except Exception as err:
                _LOGGER.error(f"Unexpected error: {err}")
                errors["base"] = "unknown"
            
            if not errors:
                # Save the configuration
                return self.async_create_entry(
                    title=f"IndexTTS ({user_input.get(CONF_DEFAULT_VOICE, 'default')})",
                    data=user_input,
                )
        
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_API_URL,
                        default="http://192.168.4.192:5150",
                    ): str,
                    vol.Optional(CONF_DEFAULT_VOICE, default="default"): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "example_url": "http://192.168.4.192:5150",
            },
        )


# For config schema validation
import asyncio

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                vol.Required(CONF_API_URL): cv.string,
                vol.Optional(CONF_DEFAULT_VOICE, default="default"): cv.string,
            }
        )
    },
    extra=vol.ALLOW_EXTRA,
)
