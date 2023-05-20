"""conftest for clean up snapshots service"""
import pytest_asyncio

pytest_plugins = "pytest_homeassistant_custom_component"


@pytest_asyncio.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Creating doc string for linter"""
    yield
