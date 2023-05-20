"""Common utils"""
import json

from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry, load_fixture
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker

import custom_components.clean_up_snapshots_service


async def setup_supervisor_integration(aioclient_mock: AiohttpClientMocker):
    """"""
    headers = {"authorization": "Bearer %s" % None}
    aioclient_mock.get(
        "http://supervisor/backups",
        json=json.loads(load_fixture("backups.json")),
        headers=headers,
    )
    aioclient_mock.delete("http://supervisor/backups/id", json={}, headers=headers)
