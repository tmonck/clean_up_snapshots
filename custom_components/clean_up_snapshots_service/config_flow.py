"""Adds config flow for clean_up_snapshots"""
import logging

from homeassistant import config_entries
import voluptuous as vol

from .const import CONF_ATTR_NAME, DOMAIN, DEFAULT_NUM

_LOGGER = logging.getLogger(__name__)


class CleanUpSnapshotsFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    def __init__(self):
        _LOGGER.debug("loading clean_up_snapshots confFlowHandler")
        self._errors = {}

    async def async_step_user(self, user_input=None):
        self._errors = {}

        if user_input is not None:
            return self.async_create_entry(title=DOMAIN, data=user_input)

        if self._async_current_entries():
            return self.async_abort(reason="single_instance")

        user_input = {}
        user_input[CONF_ATTR_NAME] = DEFAULT_NUM
        return await self._show_config_form(user_input)

    async def async_step_import(self, user_input=None):
        _LOGGER.info("Importing config entry form configuration.yaml")
        user_input.get(CONF_ATTR_NAME)

    async def _show_config_form(self, user_input):
        _LOGGER.debug("doing a thang")
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Optional(CONF_ATTR_NAME, default=user_input[DEFAULT_NUM]): int,
                }
            ),
            errors=self._errors,
        )
