"""Tool registry: aggregates all Claude tool definitions and service injection."""

from __future__ import annotations

from typing import Callable


class Services:
    """Holds authenticated API service clients. Populated by initialize_services()."""

    gmail = None
    calendar = None
    drive = None
    docs = None
    tasks = None


_services = Services()

# Tool definitions sent to Claude API — populated as tools are implemented
TOOL_DEFINITIONS: list[dict] = []

# Maps tool name -> handler function — populated as tools are implemented
TOOL_REGISTRY: dict[str, Callable] = {}


def initialize_services(settings) -> None:
    """Authenticate with Google and populate _services. Called once at startup."""
    from leah.auth.google import (
        build_calendar_service,
        build_docs_service,
        build_drive_service,
        build_gmail_service,
        build_tasks_service,
        get_google_credentials,
    )

    creds = get_google_credentials(settings)
    _services.gmail = build_gmail_service(creds)
    _services.calendar = build_calendar_service(creds)
    _services.drive = build_drive_service(creds)
    _services.docs = build_docs_service(creds)
    _services.tasks = build_tasks_service(creds)

    # Import tool modules so they register themselves
    import leah.tools.gmail  # noqa: F401
    import leah.tools.calendar  # noqa: F401


def execute_tool(name: str, tool_input: dict) -> str:
    """Dispatch a tool call from Claude to the registered handler."""
    handler = TOOL_REGISTRY.get(name)
    if handler is None:
        return f"Error: unknown tool '{name}'"
    try:
        return handler(**tool_input)
    except Exception as e:
        return f"Error running {name}: {e}"
