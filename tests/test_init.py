"""Tests of __init__.py"""
import asyncio
import json
import os
from http import HTTPStatus
from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest
from dateutil.parser import parse
from homeassistant.components.hassio import HassioAPIError
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import load_fixture
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker
from yarl import URL

from custom_components.clean_up_snapshots_service import (
    CleanUpSnapshots,
    async_setup,
    async_setup_entry,
)
from custom_components.clean_up_snapshots_service.const import (
    BACKUPS_URL_PATH,
    CONF_ATTR_NAME,
    DOMAIN,
    SUPERVISOR_URL,
)
from tests.common import setup_supervisor_integration


@pytest.mark.asyncio
@pytest.mark.parametrize("config", [({}), ({DOMAIN: {}})])
async def test_async_setup_always_returns_true(hass: HomeAssistant, config):
    """Test the async setup call"""
    result = await async_setup(hass, config)
    assert result is True


@pytest.mark.asyncio
@pytest.mark.parametrize("return_value", [(True), (False)])
async def test_async_setup_entry(hass: HomeAssistant, return_value):
    is_hassio = MagicMock()
    is_hassio.return_value = return_value
    with patch("custom_components.clean_up_snapshots_service.is_hassio", is_hassio):
        entry = ConfigEntry(1, DOMAIN, "", {}, None, options={CONF_ATTR_NAME: 3})
        result = await async_setup_entry(hass, entry)
    assert result is return_value


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


@pytest.mark.asyncio
async def test_async_remove_snapshots_makes_api_call_for_stale_snapshots(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
):
    backups = json.loads(load_fixture("backups.json"))["data"]["backups"][0:3]
    backup_slugs = []
    for backup in backups:
        backup_slugs.append(backup["slug"])
    await setup_supervisor_integration(aioclient_mock, backup_slugs)
    thing = CleanUpSnapshots(hass, None)
    await thing.async_remove_snapshots(backups)
    # Assert we only call for the backups that are passed
    assert aioclient_mock.call_count == len(backups)
    # All the calls should be a delete verb.
    for mock_call in aioclient_mock.mock_calls:
        (method, _, _, _) = mock_call
        assert method == "DELETE"


@pytest.mark.asyncio
async def test_async_remove_snapshots_logs_warning_when_delete_fails(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, caplog
):
    headers = {"authorization": "Bearer %s" % None}
    backups = [json.loads(load_fixture("backups.json"))["data"]["backups"][0]]
    url = f"http://supervisor/backups/%s" % backups[0]["slug"]
    aioclient_mock.delete(
        url, json={"result": "failed"}, status=HTTPStatus.BAD_REQUEST, headers=headers
    )
    thing = CleanUpSnapshots(hass, None)
    await thing.async_remove_snapshots(backups)
    # Assert we only call for the backups that are passed
    assert aioclient_mock.call_count == len(backups)
    # All the calls should be a delete verb.
    for mock_call in aioclient_mock.mock_calls:
        (method, _, _, _) = mock_call
        assert method == "DELETE"

    for record in caplog.records:
        if record.levelname == "WARNING":
            assert f"Failed to delete snapshot %s" % backups[0]["slug"] in caplog.text


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error, error_message, log_message",
    [
        (
            asyncio.TimeoutError,
            "Client timeout on DELETE /backups",
            "timeout error on delete snapshot",
        ),
        (
            aiohttp.ClientError,
            "Client error on calling DELETE /backups",
            "Client error on calling delete snapshot",
        ),
        (
            Exception,
            "Unknown exception thrown when calling DELETE /backup",
            "Unknown exception throw",
        ),
    ],
)
async def test_async_remove_snapshots_logs_error_and_raises(
    hass: HomeAssistant,
    aioclient_mock: AiohttpClientMocker,
    caplog,
    error,
    error_message,
    log_message,
):
    headers = {"authorization": "Bearer %s" % None}
    backups = [json.loads(load_fixture("backups.json"))["data"]["backups"][0]]
    url = f"http://supervisor/backups/%s" % backups[0]["slug"]
    aioclient_mock.delete(
        url,
        json={"result": "failed"},
        exc=error,
        status=HTTPStatus.BAD_REQUEST,
        headers=headers,
    )
    thing = CleanUpSnapshots(hass, None)
    try:
        _ = await thing.async_remove_snapshots(backups)
    except HassioAPIError as err:
        assert err is not None
        assert error_message in str(err)
    assert aioclient_mock.call_count == 1
    (method, url, _, headers) = aioclient_mock.mock_calls[0]
    assert method == "DELETE"
    for record in caplog.records:
        if record.levelname == "ERROR":
            assert log_message in caplog.text


mock_get_snapshots = AsyncMock()
backups = json.loads(load_fixture("backups.json"))["data"]["backups"]
mock_get_snapshots.return_value = backups


@pytest.mark.asyncio
@patch.object(CleanUpSnapshots, "async_get_snapshots", mock_get_snapshots)
async def test_async_handle_clean_up_call(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
):
    backups = json.loads(load_fixture("backups.json"))["data"]["backups"]
    backups.sort(key=lambda item: parse(item["date"]), reverse=True)
    backup_slugs = []
    for backup in backups[3:]:
        backup_slugs.append(backup["slug"])
    await setup_supervisor_integration(aioclient_mock, backup_slugs)
    thing = CleanUpSnapshots(hass, None)
    call = ServiceCall(DOMAIN, "clean_up", {"number_of_snapshots_to_keep": 3})
    await thing.async_handle_clean_up(call)
    assert aioclient_mock.call_count == len(backup_slugs)


mock_get_snapshots = AsyncMock()
mock_get_snapshots.return_value = None


@pytest.mark.asyncio
@patch.object(CleanUpSnapshots, "async_get_snapshots", mock_get_snapshots)
async def test_async_handle_clean_up_call_only_logs_once(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, caplog
):
    thing = CleanUpSnapshots(hass, None)
    call = ServiceCall(DOMAIN, "clean_up", {"number_of_snapshots_to_keep": 0})
    await thing.async_handle_clean_up(call)
    assert aioclient_mock.call_count == 0
    assert mock_get_snapshots.call_count == 0
    for record in caplog.records:
        if record.levelname == "INFO":
            assert (
                "Number of snapshots to keep was zero which is default so no snapshots will be removed"
                in caplog.text
            )


@pytest.mark.asyncio
@patch.object(CleanUpSnapshots, "async_get_snapshots", mock_get_snapshots)
async def test_async_handle_clean_up_call_only_logs(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker, caplog
):
    thing = CleanUpSnapshots(hass, None)
    call = ServiceCall(DOMAIN, "clean_up", {"number_of_snapshots_to_keep": 3})
    await thing.async_handle_clean_up(call)
    assert aioclient_mock.call_count == 0
    for record in caplog.records:
        if record.levelname == "INFO":
            assert "No snapshots found." in caplog.text


mock_get_snapshots = AsyncMock()
backups = json.loads(load_fixture("invalid_date_backups.json"))["data"]["backups"]
mock_get_snapshots.return_value = backups


@pytest.mark.asyncio
async def test_async_handle_clean_up_call_adjusts_date_if_tz_missing(
    hass: HomeAssistant, aioclient_mock: AiohttpClientMocker
):
    mock_get_snapshots = AsyncMock()
    backups = json.loads(load_fixture("invalid_date_backups.json"))["data"]["backups"]
    mock_get_snapshots.return_value = backups
    backups.sort(key=lambda item: parse(item["date"], ignoretz=True), reverse=True)
    backup_slugs = []
    for backup in backups:
        backup_slugs.append(backup["slug"])
    await setup_supervisor_integration(aioclient_mock, backup_slugs)
    with patch.object(CleanUpSnapshots, "async_get_snapshots", mock_get_snapshots):
        thing = CleanUpSnapshots(hass, None)
        call = ServiceCall(DOMAIN, "clean_up", {"number_of_snapshots_to_keep": 1})
        await thing.async_handle_clean_up(call)
    assert aioclient_mock.call_count == 2
    assert mock_get_snapshots.call_count == 1
