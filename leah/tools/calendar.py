"""Google Calendar tools: list and create events."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from leah.tools import TOOL_DEFINITIONS, TOOL_REGISTRY, _services


def list_events(days_ahead: int = 7, max_results: int = 20) -> str:
    svc = _services.calendar
    now = datetime.now(timezone.utc)
    end = now + timedelta(days=days_ahead)
    result = svc.events().list(
        calendarId="primary",
        timeMin=now.isoformat(),
        timeMax=end.isoformat(),
        maxResults=max_results,
        singleEvents=True,
        orderBy="startTime",
    ).execute()
    events = result.get("items", [])
    if not events:
        return json.dumps({"events": [], "note": f"No events in the next {days_ahead} days."})

    out = []
    for e in events:
        start = e["start"].get("dateTime", e["start"].get("date", ""))
        end_time = e["end"].get("dateTime", e["end"].get("date", ""))
        out.append({
            "id": e["id"],
            "title": e.get("summary", "(no title)"),
            "start": start,
            "end": end_time,
            "location": e.get("location", ""),
            "description": e.get("description", ""),
        })
    return json.dumps({"events": out})


def create_event(
    title: str,
    start: str,
    end: str,
    description: str = "",
    location: str = "",
    timezone: str = "UTC",
) -> str:
    svc = _services.calendar
    body: dict = {
        "summary": title,
        "start": {"dateTime": start, "timeZone": timezone},
        "end": {"dateTime": end, "timeZone": timezone},
    }
    if description:
        body["description"] = description
    if location:
        body["location"] = location
    created = svc.events().insert(calendarId="primary", body=body).execute()
    return json.dumps({
        "created": True,
        "id": created["id"],
        "title": created.get("summary"),
        "link": created.get("htmlLink", ""),
    })


# ── Tool definitions ──────────────────────────────────────────────────────────

TOOL_DEFINITIONS += [
    {
        "name": "list_events",
        "description": "List upcoming Google Calendar events. Defaults to the next 7 days.",
        "input_schema": {
            "type": "object",
            "properties": {
                "days_ahead": {"type": "integer", "description": "How many days ahead to look (default 7)"},
                "max_results": {"type": "integer", "description": "Maximum number of events to return (default 20)"},
            },
        },
    },
    {
        "name": "create_event",
        "description": "Create a new event on Google Calendar.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Event title"},
                "start": {"type": "string", "description": "Start time in ISO 8601 format, e.g. 2024-06-15T09:00:00"},
                "end": {"type": "string", "description": "End time in ISO 8601 format"},
                "description": {"type": "string", "description": "Event description (optional)"},
                "location": {"type": "string", "description": "Event location (optional)"},
                "timezone": {"type": "string", "description": "IANA timezone name, e.g. America/New_York (default UTC)"},
            },
            "required": ["title", "start", "end"],
        },
    },
]

TOOL_REGISTRY.update({
    "list_events": list_events,
    "create_event": create_event,
})
