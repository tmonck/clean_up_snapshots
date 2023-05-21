"""Adds config flow for clean_up_snapshots"""
import logging

import voluptuous as vol
from homeassistant import config_entries

from .const import CONF_ATTR_NAME, DEFAULT_NUM, DOMAIN

_LOGGER = logging.getLogger(__name__)


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
        return await self._show_config_form(user_input)

    async def async_step_import(self, user_input=None):
        _LOGGER.info("Importing config entry form configuration.yaml")
        return await self.async_step_user(user_input)

    async def _show_config_form(self, user_input):
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_ATTR_NAME, default=user_input[CONF_ATTR_NAME]
                    ): int,
                }
            ),
            errors=self._errors,
        )
