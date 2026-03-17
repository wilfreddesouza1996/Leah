"""Gmail tools: list, read, search, and send emails."""

from __future__ import annotations

import base64
import json
from email.mime.text import MIMEText

from leah.tools import TOOL_DEFINITIONS, TOOL_REGISTRY, _services


def _header(msg, name: str) -> str:
    headers = msg.get("payload", {}).get("headers", [])
    return next((h["value"] for h in headers if h["name"].lower() == name.lower()), "")


def _body_text(payload: dict) -> str:
    """Extract plain-text body from a message payload."""
    mime = payload.get("mimeType", "")
    if mime == "text/plain":
        data = payload.get("body", {}).get("data", "")
        return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace") if data else ""
    for part in payload.get("parts", []):
        text = _body_text(part)
        if text:
            return text
    return ""


# ── Tool handlers ─────────────────────────────────────────────────────────────

def list_emails(max_results: int = 15, query: str = "") -> str:
    svc = _services.gmail
    params = {"userId": "me", "maxResults": max_results}
    if query:
        params["q"] = query
    result = svc.users().messages().list(**params).execute()
    messages = result.get("messages", [])
    if not messages:
        return json.dumps({"emails": [], "note": "No messages found."})

    emails = []
    for m in messages:
        msg = svc.users().messages().get(
            userId="me", id=m["id"], format="metadata",
            metadataHeaders=["Subject", "From", "Date"],
        ).execute()
        emails.append({
            "id": m["id"],
            "subject": _header(msg, "Subject") or "(no subject)",
            "from": _header(msg, "From"),
            "date": _header(msg, "Date"),
            "snippet": msg.get("snippet", ""),
        })
    return json.dumps({"emails": emails})


def read_email(email_id: str) -> str:
    svc = _services.gmail
    msg = svc.users().messages().get(userId="me", id=email_id, format="full").execute()
    return json.dumps({
        "id": email_id,
        "subject": _header(msg, "Subject") or "(no subject)",
        "from": _header(msg, "From"),
        "date": _header(msg, "Date"),
        "body": _body_text(msg.get("payload", {})) or "(no plain-text body)",
    })


def search_emails(query: str, max_results: int = 10) -> str:
    return list_emails(max_results=max_results, query=query)


def send_email(to: str, subject: str, body: str) -> str:
    svc = _services.gmail
    mime = MIMEText(body)
    mime["to"] = to
    mime["subject"] = subject
    raw = base64.urlsafe_b64encode(mime.as_bytes()).decode()
    sent = svc.users().messages().send(userId="me", body={"raw": raw}).execute()
    return json.dumps({"sent": True, "id": sent["id"]})


# ── Tool definitions ──────────────────────────────────────────────────────────

TOOL_DEFINITIONS += [
    {
        "name": "list_emails",
        "description": (
            "List recent emails from Gmail. Returns subject, sender, date, and a short snippet. "
            "Use the optional query parameter for Gmail search syntax (e.g. 'is:unread', 'from:alice@example.com')."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "max_results": {"type": "integer", "description": "Number of emails to return (default 15)"},
                "query": {"type": "string", "description": "Gmail search query (optional)"},
            },
        },
    },
    {
        "name": "read_email",
        "description": "Read the full body of a specific email by its ID.",
        "input_schema": {
            "type": "object",
            "properties": {
                "email_id": {"type": "string", "description": "The email ID from list_emails"},
            },
            "required": ["email_id"],
        },
    },
    {
        "name": "search_emails",
        "description": "Search Gmail using a query string (Gmail search syntax). Returns matching emails.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Gmail search query, e.g. 'from:boss@hospital.org subject:schedule'"},
                "max_results": {"type": "integer", "description": "Number of results to return (default 10)"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "send_email",
        "description": "Send an email from the user's Gmail account.",
        "input_schema": {
            "type": "object",
            "properties": {
                "to": {"type": "string", "description": "Recipient email address"},
                "subject": {"type": "string", "description": "Email subject line"},
                "body": {"type": "string", "description": "Plain-text email body"},
            },
            "required": ["to", "subject", "body"],
        },
    },
]

TOOL_REGISTRY.update({
    "list_emails": list_emails,
    "read_email": read_email,
    "search_emails": search_emails,
    "send_email": send_email,
})
