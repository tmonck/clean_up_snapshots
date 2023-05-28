"""
Support for automating the deletion of snapshots.
"""
import asyncio
import logging
import os

import aiohttp
import async_timeout
import homeassistant.helpers.config_validation as cv
import pytz
import voluptuous as vol
from dateutil.parser import parse
from dateutil.tz import tzutc
from homeassistant.components.hassio import HassioAPIError, is_hassio
from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.typing import ConfigType

from .const import BACKUPS_URL_PATH, CONF_ATTR_NAME, DEFAULT_NUM, DOMAIN, SUPERVISOR_URL

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = vol.Schema(
    vol.All(
        cv.deprecated(DOMAIN),
        {
            DOMAIN: vol.Schema(
                {
                    vol.Optional(CONF_ATTR_NAME, default=DEFAULT_NUM): int,
                }
            ),
        },
    ),
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass: HomeAssistant, config: ConfigType):
    if DOMAIN in config:
        conf = config.get(DOMAIN, {})
        num_to_keep = conf.get(CONF_ATTR_NAME, DEFAULT_NUM)
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": SOURCE_IMPORT},
                data={CONF_ATTR_NAME: num_to_keep},
            )
        )
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    # check for supervisor
    if not is_hassio(hass):
        _LOGGER.error("You must be running Supervisor for this integration to work.")
        return False

    options = {CONF_ATTR_NAME: entry.data.get(CONF_ATTR_NAME, DEFAULT_NUM)}

    cleanup_snapshots = CleanUpSnapshots(hass, options)

    hass.services.async_register(
        DOMAIN, "clean_up", cleanup_snapshots.async_handle_clean_up
    )

    return True


class CleanUpSnapshots:
    def __init__(self, hass, options):
        self._hass = hass
        self._options = options
        self._headers = {"authorization": "Bearer %s" % os.getenv("SUPERVISOR_TOKEN")}
        self._client_session = aiohttp_client.async_get_clientsession(hass)

    async def async_get_snapshots(self):
        _LOGGER.info("Calling get snapshots")
        try:
            with async_timeout.timeout(10):
                resp = await self._client_session.get(
                    SUPERVISOR_URL + BACKUPS_URL_PATH, headers=self._headers
                )
            data = await resp.json()
            return data["data"]["backups"]
        except aiohttp.ClientError as err:
            _LOGGER.error("Client error on calling GET /backups", exc_info=True)
            raise HassioAPIError("Client error on calling GET /backups %s" % err)
        except asyncio.TimeoutError:
            _LOGGER.error("Client timeout error on GET /backups", exc_info=True)
            raise HassioAPIError("Client timeout on GET /backups")
        except Exception as err:
            _LOGGER.error(
                "Unknown exception thrown when calling GET /backups", exc_info=True
            )
            raise HassioAPIError(
                "Unknown exception thrown when calling GET /backups %s" % err
            )

    async def async_remove_snapshots(self, stale_snapshots):
        for snapshot in stale_snapshots:
            _LOGGER.info("Attempting to remove snapshot: slug=%s", snapshot["slug"])

            # call hassio API deletion
            try:
                with async_timeout.timeout(10):
                    resp = await self._client_session.delete(
                        SUPERVISOR_URL + f"{BACKUPS_URL_PATH}/" + snapshot["slug"],
                        headers=self._headers,
                    )
                res = await resp.json()
                if res["result"].lower() == "ok":
                    _LOGGER.info("Deleted snapshot %s", snapshot["slug"])
                    continue
                else:
                    _LOGGER.warning(
                        "Failed to delete snapshot %s: %s",
                        snapshot["slug"],
                        str(resp.status),
                    )

            except aiohttp.ClientError as err:
                _LOGGER.error("Client error on calling DELETE /backups", exc_info=True)
                raise HassioAPIError(
                    "Client error on calling DELETE /backups/%s %s"
                    % (snapshot["slug"], err)
                )
            except asyncio.TimeoutError:
                _LOGGER.error("Client timeout error on DELETE /backups", exc_info=True)
                raise HassioAPIError(
                    "Client timeout on DELETE /backups/%s" % snapshot["slug"]
                )
            except Exception as err:
                _LOGGER.error(
                    "Unknown exception thrown when calling DELETE /backups/%s"
                    % snapshot["slug"],
                    exc_info=True,
                )
                raise HassioAPIError(
                    "Unknown exception thrown when calling DELETE /backups/%s %s"
                    % (snapshot["slug"], err)
                )

    async def async_handle_clean_up(self, call):
        # Allow the service call override the configuration.
        num_to_keep = call.data.get(
            CONF_ATTR_NAME, self._options.get(CONF_ATTR_NAME, DEFAULT_NUM)
        )
        _LOGGER.info("Number of snapshots we are going to keep: %s", str(num_to_keep))

        if num_to_keep == 0:
            _LOGGER.info(
                "Number of snapshots to keep was zero which is default so no snapshots will be removed"
            )
            return

        snapshots = await self.async_get_snapshots()
        _LOGGER.debug("Snapshots: %s", snapshots)

        # filter the snapshots
        if snapshots is not None:
            if len(snapshots) <= num_to_keep:
                _LOGGER.info("Backup count below the desired count %d" % num_to_keep)
                return
            for snapshot in snapshots:
                d = parse(snapshot["date"], ignoretz=False)
                if d.tzinfo is None or d.tzinfo is not tzutc():
                    _LOGGER.info(
                        "Naive DateTime found for snapshot %s, setting to UTC...",
                        snapshot["slug"],
                    )
                    snapshot["date"] = d.replace(tzinfo=pytz.utc).isoformat()
            snapshots.sort(key=lambda item: parse(item["date"]), reverse=True)
            stale_snapshots = snapshots[num_to_keep:]
            _LOGGER.debug("Stale Snapshots: %s" % stale_snapshots)
            await self.async_remove_snapshots(stale_snapshots)
        else:
            _LOGGER.info("No snapshots found.")
