"""conftest for clean up snapshots service"""
import pytest_asyncio
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.clean_up_snapshots_service.const import (
    CONF_ATTR_NAME,
    DEFAULT_NUM,
    DOMAIN,
)

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest_asyncio.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Creating doc string for linter"""
    yield


@pytest_asyncio.fixture(autouse=True)
def mock_config_entry() -> MockConfigEntry:
    """Return the default mocked config entry"""
    return MockConfigEntry(title="", domain=DOMAIN, data={CONF_ATTR_NAME: 3})
