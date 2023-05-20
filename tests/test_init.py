"""Tests of __init__.py"""
import asyncio
import logging

import aiohttp
import pytest
from homeassistant.components.hassio import HassioAPIError
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker
from yarl import URL

from custom_components.clean_up_snapshots_service import CleanUpSnapshots
from custom_components.clean_up_snapshots_service.const import (
    BACKUPS_URL_PATH,
    SUPERVISOR_URL,
)
from tests.common import setup_supervisor_integration

pytest_plugins = ("pytest_asyncio",)


@pytest.mark.asyncio
async def test_async_setup_entry():
    """Test the async setup entry call"""
    # # check for supervisor
    # if not is_hassio(hass):
    #     _LOGGER.error("You must be running Supervisor for this integraion to work.")
    #     return False

    # options = {num_snapshots_to_keep: entry.options.get(CONF_ATTR_NAME, DEFAULT_NUM)}
    # cleanup_snapshots = CleanUpSnapshots(hass, options)

    # hass.services.async_register(
    #     DOMAIN, "clean_up", cleanup_snapshots.async_handle_clean_up
    # )


@pytest.mark.asyncio
async def test_async_get_snapshots(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
):
    """Test the async setup entry call"""
    await setup_supervisor_integration(aioclient_mock)
    thing = CleanUpSnapshots(hass, None)
    _ = await thing.async_get_snapshots()
    assert aioclient_mock.call_count == 1
    (method, url, _, headers) = aioclient_mock.mock_calls[0]
    assert method == "GET"
    assert url == URL(f"%s%s" % (SUPERVISOR_URL, BACKUPS_URL_PATH))


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error, error_message, log_message",
    [
        (
            asyncio.TimeoutError,
            "Client timeout on GET /backups",
            "timeout error on get snapshots",
        ),
        (
            aiohttp.ClientError,
            "Client error on calling GET /backups",
            "Client error on calling get snapshots",
        ),
        (
            Exception,
            "Unknown exception thrown when calling GET /backup",
            "Unknown exception throw",
        ),
    ],
)
async def test_async_get_snapshots_logs_timeout_error_and_raises(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    caplog,
    error,
    error_message,
    log_message,
):
    headers = {"authorization": "Bearer %s" % None}
    aioclient_mock.get(
        "http://supervisor/backups",
        exc=error,
        headers=headers,
    )
    thing = CleanUpSnapshots(hass, None)
    try:
        _ = await thing.async_get_snapshots()
    except HassioAPIError as err:
        assert err is not None
        assert error_message in str(err)
    assert aioclient_mock.call_count == 1
    (method, url, _, headers) = aioclient_mock.mock_calls[0]
    assert method == "GET"
    assert url == URL(f"%s%s" % (SUPERVISOR_URL, BACKUPS_URL_PATH))
    for record in caplog.records:
        if record.levelname == "ERROR":
            assert log_message in caplog.text


# @pytest.mark.asyncio
# async def test_async_get_snapshots_logs_timeout_error_and_raises(
#     hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, caplog
# ):
#     headers = {"authorization": "Bearer %s" % None}
#     aioclient_mock.get(
#         "http://supervisor/backups",
#         exc=asyncio.TimeoutError,
#         headers=headers,
#     )
#     thing = CleanUpSnapshots(hass, None)
#     try:
#         _ = await thing.async_get_snapshots()
#     except HassioAPIError as err:
#         assert err is not None
#         assert "Client timeout on GET /backups" == str(err)
#     assert aioclient_mock.call_count == 1
#     (method, url, _, headers) = aioclient_mock.mock_calls[0]
#     assert method == "GET"
#     assert url == URL(f"%s%s" % (SUPERVISOR_URL, BACKUPS_URL_PATH))
#     for record in caplog.records:
#         if record.levelname == "ERROR":
#             assert "timeout error on get snapshots" in caplog.text
