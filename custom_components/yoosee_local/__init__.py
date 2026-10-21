"""The Yoosee Local integration."""
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .client import YooseeClient
from .const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    DEFAULT_PORT,
    DEFAULT_SOUND,
    DOMAIN,
    PLATFORMS,
)

_LOGGER = logging.getLogger(__name__)


class YooseeDeviceData:
    """Shared state and client for a Yoosee camera entry."""

    def __init__(self, client: YooseeClient, name: str):
        self.client = client
        self.name = name
        self.selected_sound: str = DEFAULT_SOUND
        self.white_light_on: bool = False
        self.auto_tracking_on: bool = False
        self.siren_on: bool = False


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Yoosee Local from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    host = entry.data[CONF_HOST]
    name = entry.data.get(CONF_NAME, f"Yoosee {host}")
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)

    client = YooseeClient(host=host, port=port)
    device_data = YooseeDeviceData(client=client, name=name)
    hass.data[DOMAIN][entry.entry_id] = device_data

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok
