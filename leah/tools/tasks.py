"""Google Tasks tools: list, create, complete, and delete tasks."""

from __future__ import annotations

import json

from leah.tools import TOOL_DEFINITIONS, TOOL_REGISTRY, _services


def list_tasks(max_results: int = 20, show_completed: bool = False) -> str:
    svc = _services.tasks
    result = svc.tasks().list(
        tasklist="@default",
        maxResults=max_results,
        showCompleted=show_completed,
        showHidden=False,
    ).execute()
    tasks = result.get("items", [])
    if not tasks:
        return json.dumps({"tasks": [], "note": "No tasks found."})

    out = []
    for t in tasks:
        out.append({
            "id": t["id"],
            "title": t.get("title", "(untitled)"),
            "status": t.get("status", ""),
            "due": t.get("due", ""),
            "notes": t.get("notes", ""),
        })
    return json.dumps({"tasks": out})


def create_task(title: str, notes: str = "", due: str = "") -> str:
    svc = _services.tasks
    body: dict = {"title": title}
    if notes:
        body["notes"] = notes
    if due:
        body["due"] = due  # RFC 3339 format, e.g. 2024-06-15T00:00:00.000Z
    task = svc.tasks().insert(tasklist="@default", body=body).execute()
    return json.dumps({"created": True, "id": task["id"], "title": task.get("title")})


def complete_task(task_id: str) -> str:
    svc = _services.tasks
    updated = svc.tasks().patch(
        tasklist="@default", task=task_id, body={"status": "completed"}
    ).execute()
    return json.dumps({"completed": True, "id": updated["id"], "title": updated.get("title")})


def delete_task(task_id: str) -> str:
    svc = _services.tasks
    svc.tasks().delete(tasklist="@default", task=task_id).execute()
    return json.dumps({"deleted": True, "task_id": task_id})


# ── Tool definitions ──────────────────────────────────────────────────────────

TOOL_DEFINITIONS += [
    {
        "name": "list_tasks",
        "description": "List tasks from Google Tasks. Shows pending tasks by default.",
        "input_schema": {
            "type": "object",
            "properties": {
                "max_results": {"type": "integer", "description": "Number of tasks to return (default 20)"},
                "show_completed": {"type": "boolean", "description": "Include completed tasks (default false)"},
            },
        },
    },
    {
        "name": "create_task",
        "description": "Add a new task to Google Tasks.",
        "input_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Task title"},
                "notes": {"type": "string", "description": "Additional notes (optional)"},
                "due": {"type": "string", "description": "Due date in RFC 3339 format, e.g. 2024-06-15T00:00:00.000Z (optional)"},
            },
            "required": ["title"],
        },
    },
    {
        "name": "complete_task",
        "description": "Mark a task as completed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "Task ID from list_tasks"},
            },
            "required": ["task_id"],
        },
    },
    {
        "name": "delete_task",
        "description": "Delete a task permanently.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task_id": {"type": "string", "description": "Task ID from list_tasks"},
            },
            "required": ["task_id"],
        },
    },
]

TOOL_REGISTRY.update({
    "list_tasks": list_tasks,
    "create_task": create_task,
    "complete_task": complete_task,
    "delete_task": delete_task,
})
