"""Common utils"""
import json
from http import HTTPStatus

from pytest_homeassistant_custom_component.common import load_fixture
from pytest_homeassistant_custom_component.test_util.aiohttp import AiohttpClientMocker


async def setup_supervisor_integration(
    aioclient_mock: AiohttpClientMocker, backup_slugs_to_delete=None
):
    """"""
    if backup_slugs_to_delete is None:
        backup_slugs_to_delete = []
    headers = {"authorization": "Bearer %s" % None}
    aioclient_mock.get(
        "http://supervisor/backups",
        json=json.loads(load_fixture("backups.json")),
        headers=headers,
    )
    for backup_slug in backup_slugs_to_delete:
        url = f"http://supervisor/backups/%s" % backup_slug
        aioclient_mock.delete(url, json={"result": "ok"}, headers=headers)
