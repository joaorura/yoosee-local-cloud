"""Config flow for Yoosee Local integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .client import YooseeClient
from .const import CONF_HOST, CONF_NAME, CONF_PORT, DEFAULT_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_NAME, default="Camera"): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
    }
)


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Yoosee Local."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            name = user_input.get(CONF_NAME, f"Yoosee {host}").strip()
            port = user_input.get(CONF_PORT, DEFAULT_PORT)

            await self.async_set_unique_id(host)
            self._abort_if_unique_id_configured()

            client = YooseeClient(host=host, port=port)
            connected = await self.hass.async_add_executor_job(client.test_connection)

            if not connected:
                _LOGGER.warning("Could not reach Yoosee camera at %s:%s, saving anyway", host, port)

            return self.async_create_entry(
                title=name,
                data={
                    CONF_HOST: host,
                    CONF_NAME: name,
                    CONF_PORT: port,
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
