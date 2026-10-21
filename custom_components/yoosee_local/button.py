"""Button platform for Yoosee Local PTZ control."""
from __future__ import annotations

import logging
from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_HOST, DOMAIN

_LOGGER = logging.getLogger(__name__)

PTZ_BUTTONS = [
    ("up", "Mover Cima", "mdi:arrow-up-bold"),
    ("down", "Mover Baixo", "mdi:arrow-down-bold"),
    ("left", "Mover Esquerda", "mdi:arrow-left-bold"),
    ("right", "Mover Direita", "mdi:arrow-right-bold"),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Yoosee PTZ buttons from config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    host = entry.data[CONF_HOST]

    entities = [
        YooseePTZButton(
            entry=entry,
            device_data=data,
            direction=direction,
            label=label,
            icon=icon,
            host=host,
        )
        for direction, label, icon in PTZ_BUTTONS
    ]

    async_add_entities(entities)


class YooseePTZButton(ButtonEntity):
    """Button entity to trigger a PTZ movement."""

    def __init__(
        self,
        entry: ConfigEntry,
        device_data,
        direction: str,
        label: str,
        icon: str,
        host: str,
    ) -> None:
        self._entry = entry
        self._device_data = device_data
        self._direction = direction
        self._attr_name = f"{device_data.name} {label}"
        self._attr_unique_id = f"{entry.entry_id}_ptz_{direction}"
        self._attr_icon = icon
        self._host = host

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

    async def async_press(self) -> None:
        """Handle button press."""
        _LOGGER.debug("Sending PTZ %s to %s", self._direction, self._host)
        success = await self.hass.async_add_executor_job(
            self._device_data.client.move, self._direction
        )
        if not success:
            _LOGGER.warning("PTZ %s failed on %s", self._direction, self._host)
