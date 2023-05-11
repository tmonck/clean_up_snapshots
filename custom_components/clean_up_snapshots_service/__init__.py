"""
Support for automating the deletion of snapshots.
"""
import logging
import os

import pytz
from dateutil.parser import parse
import asyncio
import aiohttp
import async_timeout
from urllib.parse import urlparse

from homeassistant.const import (CONF_HOST, CONF_TOKEN)
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'clean_up_snapshots_service'
ATTR_NAME = 'number_of_snapshots_to_keep'
DEFAULT_NUM = 0
BACKUPS_URL_PATH = 'backups'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Optional(ATTR_NAME, default=DEFAULT_NUM): int,
    }),
}, extra=vol.ALLOW_EXTRA)

async def async_setup(hass, config):
    conf = config[DOMAIN]
    supervisor_url = 'http://supervisor/'
    auth_token = os.getenv('SUPERVISOR_TOKEN')
    num_snapshots_to_keep = conf.get(ATTR_NAME, DEFAULT_NUM)
    headers = {'authorization': "Bearer {}".format(auth_token)}

    async def async_get_snapshots():
        _LOGGER.info('Calling get snapshots')
        async with aiohttp.ClientSession(raise_for_status=True) as session:
            try:
                with async_timeout.timeout(10):
                    resp = await session.get(supervisor_url + BACKUPS_URL_PATH, headers=headers)
                data = await resp.json()
                await session.close()
                return data['data']['backups']
            except aiohttp.ClientError:
                _LOGGER.error("Client error on calling get snapshots", exc_info=True)
                await session.close()
            except asyncio.TimeoutError:
                _LOGGER.error("Client timeout error on get snapshots", exc_info=True)
                await session.close()
            except Exception:
                _LOGGER.error("Unknown exception thrown", exc_info=True)
                await session.close()

    async def async_remove_snapshots(stale_snapshots):
        for snapshot in stale_snapshots:
            async with aiohttp.ClientSession(raise_for_status=True) as session:
                _LOGGER.info('Attempting to remove snapshot: slug=%s', snapshot['slug'])
                # call hassio API deletion
                try:
                    with async_timeout.timeout(10):
                        resp = await session.delete(supervisor_url + f"{BACKUPS_URL_PATH}/" + snapshot['slug'], headers=headers)
                    res = await resp.json()
                    if res['result'].lower() == "ok":
                        _LOGGER.info("Deleted snapshot %s", snapshot["slug"])
                        await session.close()
                        continue
                    else:
                        # log an error
                        _LOGGER.warning("Failed to delete snapshot %s: %s", snapshot["slug"], str(res.status_code))

                except aiohttp.ClientError:
                    _LOGGER.error("Client error on calling delete snapshot", exc_info=True)
                    await session.close()
                except asyncio.TimeoutError:
                    _LOGGER.error("Client timeout error on delete snapshot", exc_info=True)
                    await session.close()
                except Exception:
                    _LOGGER.error("Unknown exception thrown on calling delete snapshot", exc_info=True)
                    await session.close()

    async def async_handle_clean_up(call):
        # Allow the service call override the configuration.
        num_to_keep = call.data.get(ATTR_NAME, num_snapshots_to_keep)
        _LOGGER.info('Number of snapshots we are going to keep: %s', str(num_to_keep))

        if num_to_keep == 0:
            _LOGGER.info('Number of snapshots to keep was zero which is default so no snapshots will be removed')
            return

        snapshots = await async_get_snapshots()
        _LOGGER.info('Snapshots: %s', snapshots)

        # filter the snapshots
        if snapshots is not None:
            for snapshot in snapshots:
                d = parse(snapshot["date"])
                if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
                    _LOGGER.info("Naive DateTime found for snapshot %s, setting to UTC...", snapshot["slug"])
                    snapshot["date"] = d.replace(tzinfo=pytz.utc).isoformat()
            snapshots.sort(key=lambda item: parse(item["date"]), reverse=True)
            stale_snapshots = snapshots[num_to_keep:]
            _LOGGER.info('Stale Snapshots: {}'.format(stale_snapshots))
            await async_remove_snapshots(stale_snapshots)
        else:
            _LOGGER.info('No snapshots found.')

    hass.services.async_register(DOMAIN, 'clean_up', async_handle_clean_up)

    return True
