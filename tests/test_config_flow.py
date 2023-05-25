"""Tests of config_flow.py"""
import asyncio

import pytest
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.clean_up_snapshots_service.const import CONF_ATTR_NAME, DOMAIN


@pytest.mark.asyncio
async def test_async_step_user_complete_flow(hass: HomeAssistant):
    # self._errors = {}

    # if user_input is not None:
    #     return self.async_create_entry(title=DOMAIN, data=user_input)

    # if self._async_current_entries():
    #     return self.async_abort(reason="single_instance")

    # user_input = {}
    # user_input[CONF_ATTR_NAME] = DEFAULT_NUM
    # return await self._show_config_form(user_input)
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    assert result is not None
    assert result["type"] == FlowResultType.FORM

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], user_input={CONF_ATTR_NAME: 3}
    )
    assert result["title"] == "clean_up_snapshots_service"
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert "data" in result
    assert result["data"][CONF_ATTR_NAME] == 3


@pytest.mark.asyncio
async def test_async_step_user_already_configured(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
):
    # self._errors = {}

    # if user_input is not None:
    #     return self.async_create_entry(title=DOMAIN, data=user_input)

    # if self._async_current_entries():
    #     return self.async_abort(reason="single_instance")

    # user_input = {}
    # user_input[CONF_ATTR_NAME] = DEFAULT_NUM
    # return await self._show_config_form(user_input)
    mock_config_entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    assert result is not None
    assert result["type"] == FlowResultType.ABORT


@pytest.mark.asyncio
async def test_async_step_import_calls_setup_user(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
):
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_IMPORT},
        data={CONF_ATTR_NAME: 5},
    )
    assert result is not None
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert "data" in result
    assert result["data"][CONF_ATTR_NAME] == 5


@pytest.mark.asyncio
async def test_async_step_import_returns_already_configured(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
):
    mock_config_entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_IMPORT},
        data={CONF_ATTR_NAME: 5},
    )
    assert result is not None
    assert result["type"] == FlowResultType.ABORT
    assert result["reason"] == "already_configured"
