"""Google Calendar tools: list, create, edit, delete events; find free slots."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

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


def edit_event(
    event_id: str,
    title: str = None,
    start: str = None,
    end: str = None,
    description: str = None,
    location: str = None,
    timezone: str = None,
) -> str:
    svc = _services.calendar
    patch: dict = {}
    if title is not None:
        patch["summary"] = title
    if start is not None:
        patch["start"] = {"dateTime": start, "timeZone": timezone or "UTC"}
    if end is not None:
        patch["end"] = {"dateTime": end, "timeZone": timezone or "UTC"}
    if description is not None:
        patch["description"] = description
    if location is not None:
        patch["location"] = location
    updated = svc.events().patch(calendarId="primary", eventId=event_id, body=patch).execute()
    return json.dumps({
        "updated": True,
        "id": updated["id"],
        "title": updated.get("summary"),
        "start": updated["start"].get("dateTime", updated["start"].get("date")),
        "end": updated["end"].get("dateTime", updated["end"].get("date")),
    })


def delete_event(event_id: str) -> str:
    svc = _services.calendar
    svc.events().delete(calendarId="primary", eventId=event_id).execute()
    return json.dumps({"deleted": True, "event_id": event_id})


def find_free_slots(
    date: str,
    duration_minutes: int,
    timezone: str = "UTC",
    work_start: str = "09:00",
    work_end: str = "17:00",
) -> str:
    """Find free time slots on a given date within working hours."""
    tz = ZoneInfo(timezone)
    day = datetime.fromisoformat(date)

    ws_h, ws_m = map(int, work_start.split(":"))
    we_h, we_m = map(int, work_end.split(":"))
    day_start = datetime(day.year, day.month, day.day, ws_h, ws_m, tzinfo=tz)
    day_end = datetime(day.year, day.month, day.day, we_h, we_m, tzinfo=tz)

    svc = _services.calendar
    result = svc.events().list(
        calendarId="primary",
        timeMin=day_start.isoformat(),
        timeMax=day_end.isoformat(),
        singleEvents=True,
        orderBy="startTime",
    ).execute()

    busy = []
    for e in result.get("items", []):
        s = e["start"].get("dateTime")
        en = e["end"].get("dateTime")
        if s and en:
            busy.append((
                datetime.fromisoformat(s).astimezone(tz),
                datetime.fromisoformat(en).astimezone(tz),
            ))

    duration = timedelta(minutes=duration_minutes)
    free = []
    cursor = day_start

    for busy_start, busy_end in busy:
        while cursor + duration <= busy_start:
            free.append({
                "start": cursor.strftime("%-I:%M %p"),
                "end": (cursor + duration).strftime("%-I:%M %p"),
            })
            cursor += duration
        cursor = max(cursor, busy_end)

    while cursor + duration <= day_end:
        free.append({
            "start": cursor.strftime("%-I:%M %p"),
            "end": (cursor + duration).strftime("%-I:%M %p"),
        })
        cursor += duration

    return json.dumps({
        "date": date,
        "duration_minutes": duration_minutes,
        "timezone": timezone,
        "working_hours": f"{work_start}–{work_end}",
        "free_slots": free,
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
                "timezone": {"type": "string", "description": "IANA timezone name, e.g. America/Kolkata (default UTC)"},
            },
            "required": ["title", "start", "end"],
        },
    },
    {
        "name": "edit_event",
        "description": "Edit an existing calendar event. Only provide the fields you want to change.",
        "input_schema": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "Event ID from list_events"},
                "title": {"type": "string", "description": "New event title (optional)"},
                "start": {"type": "string", "description": "New start time in ISO 8601 format (optional)"},
                "end": {"type": "string", "description": "New end time in ISO 8601 format (optional)"},
                "description": {"type": "string", "description": "New description (optional)"},
                "location": {"type": "string", "description": "New location (optional)"},
                "timezone": {"type": "string", "description": "IANA timezone name (optional)"},
            },
            "required": ["event_id"],
        },
    },
    {
        "name": "delete_event",
        "description": "Delete a calendar event permanently.",
        "input_schema": {
            "type": "object",
            "properties": {
                "event_id": {"type": "string", "description": "Event ID from list_events"},
            },
            "required": ["event_id"],
        },
    },
    {
        "name": "find_free_slots",
        "description": "Find available time slots on a given date within working hours.",
        "input_schema": {
            "type": "object",
            "properties": {
                "date": {"type": "string", "description": "Date in YYYY-MM-DD format"},
                "duration_minutes": {"type": "integer", "description": "Required slot duration in minutes"},
                "timezone": {"type": "string", "description": "IANA timezone name, e.g. Asia/Kolkata"},
                "work_start": {"type": "string", "description": "Working hours start in HH:MM format (default 09:00)"},
                "work_end": {"type": "string", "description": "Working hours end in HH:MM format (default 17:00)"},
            },
            "required": ["date", "duration_minutes"],
        },
    },
]

TOOL_REGISTRY.update({
    "list_events": list_events,
    "create_event": create_event,
    "edit_event": edit_event,
    "delete_event": delete_event,
    "find_free_slots": find_free_slots,
})
