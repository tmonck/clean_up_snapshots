"""Adds config flow for clean_up_snapshots"""
import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_ATTR_NAME, DEFAULT_NUM, DOMAIN

_LOGGER = logging.getLogger(__name__)


def _get_schema(config_entry: config_entries.ConfigEntry | None = None) -> vol.Schema:
    if config_entry is not None:
        num_to_keep_from_data = config_entry.data.get(CONF_ATTR_NAME, DEFAULT_NUM)
        _LOGGER.info("num_to_keep_from_data %d" % num_to_keep_from_data)
        return vol.Schema(
            {
                vol.Optional(
                    CONF_ATTR_NAME,
                    default=config_entry.data.get(CONF_ATTR_NAME, DEFAULT_NUM),
                ): int,
            }
        )
    return vol.Schema(
        {
            vol.Optional(CONF_ATTR_NAME, default=DEFAULT_NUM): int,
        }
    )


class CleanUpBackupsFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle config flow for CleanUpSnapshotsService"""

    VERSION = 1

    def __init__(self):
        self._errors = {}

    async def async_step_user(self, user_input=None):
        self._errors = {}

        if user_input is not None:
            return self.async_create_entry(title=DOMAIN, data=user_input)

        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        user_input = {}
        user_input[CONF_ATTR_NAME] = DEFAULT_NUM
        return await self._show_config_form()

    async def async_step_import(self, user_input):
        """import step of config flow"""
        _LOGGER.info("Importing config entry form configuration.yaml")
        _LOGGER.info(user_input)
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        return self.async_create_entry(title=DOMAIN, data=user_input)

    async def _show_config_form(self):
        return self.async_show_form(
            step_id="user",
            data_schema=_get_schema(None),
            errors=self._errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return CleanUpBackupsOptionsFlowHandler(config_entry)


class CleanUpBackupsOptionsFlowHandler(config_entries.OptionsFlow):
    """OptionsFlowHandler for Clean Up Backups Service"""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry
        self._errors: dict[str, Any] = {}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=_get_schema(self._config_entry),
            errors=self._errors,
        )
