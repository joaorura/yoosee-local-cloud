"""Siren platform for Yoosee Local alarm triggering."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.siren import (
    ATTR_TONE,
    SirenEntity,
    SirenEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_HOST, DEFAULT_SOUND, DOMAIN, SOUND_OPTIONS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Yoosee siren entity from config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    host = entry.data[CONF_HOST]

    async_add_entities([YooseeSirenEntity(entry=entry, device_data=data, host=host)])


class YooseeSirenEntity(SirenEntity):
    """Siren entity to sound alarm on the camera speaker."""

    _attr_supported_features = (
        SirenEntityFeature.TURN_ON
        | SirenEntityFeature.TURN_OFF
        | SirenEntityFeature.TONES
    )
    _attr_available_tones = SOUND_OPTIONS

    def __init__(self, entry: ConfigEntry, device_data, host: str) -> None:
        self._entry = entry
        self._device_data = device_data
        self._host = host
        self._attr_name = f"{device_data.name} Alarme"
        self._attr_unique_id = f"{entry.entry_id}_siren"
        self._attr_icon = "mdi:bullhorn"

    @property
    def is_on(self) -> bool:
        """Return true if siren is sounding."""
        return self._device_data.siren_on

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=self._device_data.name,
            manufacturer="Yoosee / Gwelltimes",
            model="Anyka AK3918 Camera",
            configuration_url=f"http://{self._host}",
        )

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on siren and play sound."""
        tone = kwargs.get(ATTR_TONE) or self._device_data.selected_sound or DEFAULT_SOUND
        _LOGGER.debug("Triggering siren tone '%s' on %s", tone, self._host)

        await self.hass.async_add_executor_job(
            self._device_data.client.play_sound, tone
        )
        self._device_data.siren_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off siren."""
        _LOGGER.debug("Turning OFF siren on %s", self._host)
        await self.hass.async_add_executor_job(
            self._device_data.client.stop_sound
        )
        self._device_data.siren_on = False
        self.async_write_ha_state()
