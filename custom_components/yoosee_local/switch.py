"""Switch platform for Yoosee Local (Auto Tracking & White Light)."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_HOST, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Yoosee switches from config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    host = entry.data[CONF_HOST]

    entities = [
        YooseeTrackingSwitch(entry=entry, device_data=data, host=host),
        YooseeWhiteLightSwitch(entry=entry, device_data=data, host=host),
    ]

    async_add_entities(entities)


class YooseeTrackingSwitch(SwitchEntity):
    """Switch to toggle Auto Tracking."""

    def __init__(self, entry: ConfigEntry, device_data, host: str) -> None:
        self._entry = entry
        self._device_data = device_data
        self._host = host
        self._attr_name = f"{device_data.name} Rastreamento Automático"
        self._attr_unique_id = f"{entry.entry_id}_auto_tracking"
        self._attr_icon = "mdi:crosshairs-gps"

    @property
    def is_on(self) -> bool:
        """Return true if tracking is enabled."""
        return self._device_data.auto_tracking_on

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
        """Enable auto tracking."""
        _LOGGER.debug("Enabling auto tracking on %s", self._host)
        await self.hass.async_add_executor_job(
            self._device_data.client.set_auto_tracking, True
        )
        self._device_data.auto_tracking_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Disable auto tracking."""
        _LOGGER.debug("Disabling auto tracking on %s", self._host)
        await self.hass.async_add_executor_job(
            self._device_data.client.set_auto_tracking, False
        )
        self._device_data.auto_tracking_on = False
        self.async_write_ha_state()


class YooseeWhiteLightSwitch(SwitchEntity):
    """Switch to toggle White Light / Spotlight."""

    def __init__(self, entry: ConfigEntry, device_data, host: str) -> None:
        self._entry = entry
        self._device_data = device_data
        self._host = host
        self._attr_name = f"{device_data.name} Luz Branca"
        self._attr_unique_id = f"{entry.entry_id}_white_light"
        self._attr_icon = "mdi:flood-light"

    @property
    def is_on(self) -> bool:
        """Return true if white light is enabled."""
        return self._device_data.white_light_on

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
        """Turn on white light."""
        _LOGGER.debug("Turning ON white light on %s", self._host)
        await self.hass.async_add_executor_job(
            self._device_data.client.set_white_light, True
        )
        self._device_data.white_light_on = True
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off white light."""
        _LOGGER.debug("Turning OFF white light on %s", self._host)
        await self.hass.async_add_executor_job(
            self._device_data.client.set_white_light, False
        )
        self._device_data.white_light_on = False
        self.async_write_ha_state()
