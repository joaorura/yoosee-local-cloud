"""Select platform for Yoosee Local alarm sound selection."""
from __future__ import annotations

import logging

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_HOST, DOMAIN, SOUND_OPTIONS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Yoosee alarm sound select from config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    host = entry.data[CONF_HOST]

    async_add_entities([YooseeAlarmSoundSelect(entry=entry, device_data=data, host=host)])


class YooseeAlarmSoundSelect(SelectEntity):
    """Select entity to choose alarm sound from library."""

    _attr_options = SOUND_OPTIONS

    def __init__(self, entry: ConfigEntry, device_data, host: str) -> None:
        self._entry = entry
        self._device_data = device_data
        self._host = host
        self._attr_name = f"{device_data.name} Som de Alarme"
        self._attr_unique_id = f"{entry.entry_id}_alarm_sound"
        self._attr_icon = "mdi:music-box-outline"

    @property
    def current_option(self) -> str:
        """Return the selected entity option."""
        return self._device_data.selected_sound

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

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        if option in SOUND_OPTIONS:
            _LOGGER.debug("Setting alarm sound on %s to %s", self._host, option)
            self._device_data.selected_sound = option
            self.async_write_ha_state()
        else:
            _LOGGER.warning("Invalid sound option: %s", option)
