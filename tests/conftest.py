"""Shared test fixtures."""

import pytest
from unittest.mock import MagicMock

import leah.tools as tools_module


@pytest.fixture(autouse=True)
def mock_services():
    """Replace all Google API services with MagicMocks for every test."""
    original = {
        "gmail": tools_module._services.gmail,
        "calendar": tools_module._services.calendar,
        "drive": tools_module._services.drive,
        "docs": tools_module._services.docs,
        "tasks": tools_module._services.tasks,
    }
    tools_module._services.gmail = MagicMock()
    tools_module._services.calendar = MagicMock()
    tools_module._services.drive = MagicMock()
    tools_module._services.docs = MagicMock()
    tools_module._services.tasks = MagicMock()

    yield tools_module._services

    # Restore originals
    for key, val in original.items():
        setattr(tools_module._services, key, val)
