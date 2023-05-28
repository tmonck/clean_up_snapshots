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
    mock_config_entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN,
        context={"source": config_entries.SOURCE_USER},
    )
    assert result is not None
    assert result["type"] == FlowResultType.ABORT


@pytest.mark.asyncio
async def test_async_step_import_creates_entry(hass: HomeAssistant):
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


@pytest.mark.asyncio
async def test_optionsflow(
    hass: HomeAssistant,
):
    entry_data = {CONF_ATTR_NAME: 3}
    entry = MockConfigEntry(domain=DOMAIN, data=entry_data)
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)
    assert result["type"] == "form"
    assert result["step_id"] == "init"

    update_data = {CONF_ATTR_NAME: 5}
    result = await hass.config_entries.options.async_init(
        entry.entry_id, data=update_data
    )

    assert result["type"] == "create_entry"
    assert result["data"] == update_data
