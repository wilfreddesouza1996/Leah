"""Gmail tools: list, read, search emails; create/edit/list drafts; delete emails."""

from __future__ import annotations

import base64
import json
from email.mime.text import MIMEText

from leah.tools import TOOL_DEFINITIONS, TOOL_REGISTRY, _services

# Bulk delete is only permitted for these Gmail categories
_BULK_ALLOWED = ("category:promotions", "category:updates", "category:social")


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


def _make_raw(to: str, subject: str, body: str) -> str:
    mime = MIMEText(body)
    mime["to"] = to
    mime["subject"] = subject
    return base64.urlsafe_b64encode(mime.as_bytes()).decode()


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


def create_draft(to: str, subject: str, body: str) -> str:
    svc = _services.gmail
    draft = svc.users().drafts().create(
        userId="me", body={"message": {"raw": _make_raw(to, subject, body)}}
    ).execute()
    return json.dumps({"created": True, "draft_id": draft["id"], "to": to, "subject": subject})


def list_drafts(max_results: int = 10) -> str:
    svc = _services.gmail
    result = svc.users().drafts().list(userId="me", maxResults=max_results).execute()
    drafts = result.get("drafts", [])
    if not drafts:
        return json.dumps({"drafts": [], "note": "No drafts found."})

    out = []
    for d in drafts:
        draft = svc.users().drafts().get(userId="me", id=d["id"], format="metadata").execute()
        msg = draft.get("message", {})
        headers = {h["name"]: h["value"] for h in msg.get("payload", {}).get("headers", [])}
        out.append({
            "draft_id": d["id"],
            "to": headers.get("To", ""),
            "subject": headers.get("Subject", "(no subject)"),
            "snippet": msg.get("snippet", ""),
        })
    return json.dumps({"drafts": out})


def edit_draft(draft_id: str, to: str, subject: str, body: str) -> str:
    svc = _services.gmail
    updated = svc.users().drafts().update(
        userId="me", id=draft_id,
        body={"message": {"raw": _make_raw(to, subject, body)}},
    ).execute()
    return json.dumps({"updated": True, "draft_id": updated["id"], "to": to, "subject": subject})


def delete_email(email_id: str) -> str:
    """Move a single email to Trash (recoverable)."""
    svc = _services.gmail
    svc.users().messages().trash(userId="me", id=email_id).execute()
    return json.dumps({"trashed": True, "email_id": email_id})


def reply_to_email(email_id: str, body: str) -> str:
    """Create a draft reply to an email. Does NOT send — user reviews and sends manually."""
    svc = _services.gmail
    msg = svc.users().messages().get(
        userId="me", id=email_id, format="metadata",
        metadataHeaders=["Subject", "From", "Message-ID", "References"],
    ).execute()

    subject = _header(msg, "Subject")
    from_addr = _header(msg, "From")
    message_id = _header(msg, "Message-ID")
    references = _header(msg, "References")
    thread_id = msg.get("threadId", "")

    if not subject.lower().startswith("re:"):
        subject = f"Re: {subject}"

    mime = MIMEText(body)
    mime["to"] = from_addr
    mime["subject"] = subject
    if message_id:
        mime["In-Reply-To"] = message_id
        mime["References"] = f"{references} {message_id}".strip() if references else message_id

    raw = base64.urlsafe_b64encode(mime.as_bytes()).decode()
    draft = svc.users().drafts().create(
        userId="me", body={"message": {"raw": raw, "threadId": thread_id}}
    ).execute()
    return json.dumps({"created": True, "draft_id": draft["id"], "to": from_addr, "subject": subject})


def mark_email_read(email_id: str) -> str:
    _services.gmail.users().messages().modify(
        userId="me", id=email_id, body={"removeLabelIds": ["UNREAD"]}
    ).execute()
    return json.dumps({"marked_read": True, "email_id": email_id})


def mark_email_unread(email_id: str) -> str:
    _services.gmail.users().messages().modify(
        userId="me", id=email_id, body={"addLabelIds": ["UNREAD"]}
    ).execute()
    return json.dumps({"marked_unread": True, "email_id": email_id})


def move_email(email_id: str, destination: str) -> str:
    """Move an email to a label/folder. destination can be INBOX, SPAM, STARRED, or a custom label name."""
    svc = _services.gmail
    system_labels = {"INBOX", "SPAM", "TRASH", "STARRED", "IMPORTANT"}
    dest_upper = destination.upper()

    if dest_upper in system_labels:
        label_ids = [dest_upper]
    else:
        all_labels = svc.users().labels().list(userId="me").execute().get("labels", [])
        match = next((l for l in all_labels if l["name"].lower() == destination.lower()), None)
        if not match:
            return json.dumps({"error": f"Label '{destination}' not found."})
        label_ids = [match["id"]]

    msg = svc.users().messages().get(userId="me", id=email_id, format="minimal").execute()
    current = msg.get("labelIds", [])
    remove = [l for l in ["INBOX", "SPAM", "TRASH"] if l in current and l not in label_ids]

    svc.users().messages().modify(
        userId="me", id=email_id,
        body={"addLabelIds": label_ids, "removeLabelIds": remove},
    ).execute()
    return json.dumps({"moved": True, "email_id": email_id, "destination": destination})


def bulk_delete_emails(query: str) -> str:
    """Permanently delete emails matching a query. Restricted to Promotions, Updates, and Social only."""
    query_lower = query.lower().strip()
    if not any(cat in query_lower for cat in _BULK_ALLOWED):
        return json.dumps({
            "error": "Bulk delete is only allowed for category:promotions, category:updates, or category:social."
        })

    svc = _services.gmail
    all_ids = []
    page_token = None
    while True:
        params = {"userId": "me", "q": query, "maxResults": 500}
        if page_token:
            params["pageToken"] = page_token
        result = svc.users().messages().list(**params).execute()
        batch = result.get("messages", [])
        all_ids.extend(m["id"] for m in batch)
        page_token = result.get("nextPageToken")
        if not page_token:
            break

    if not all_ids:
        return json.dumps({"deleted": 0, "note": "No messages found matching that query."})

    # batchDelete accepts up to 1000 ids at a time
    for i in range(0, len(all_ids), 1000):
        svc.users().messages().batchDelete(
            userId="me", body={"ids": all_ids[i:i + 1000]}
        ).execute()

    return json.dumps({"deleted": len(all_ids), "query": query})


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
                "query": {"type": "string", "description": "Gmail search query"},
                "max_results": {"type": "integer", "description": "Number of results to return (default 10)"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "create_draft",
        "description": "Create a new draft email. Does NOT send it — the user reviews and sends manually.",
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
    {
        "name": "list_drafts",
        "description": "List existing email drafts. Returns draft ID, recipient, subject, and snippet.",
        "input_schema": {
            "type": "object",
            "properties": {
                "max_results": {"type": "integer", "description": "Number of drafts to return (default 10)"},
            },
        },
    },
    {
        "name": "edit_draft",
        "description": "Edit an existing draft. Replaces the current content with the new values provided.",
        "input_schema": {
            "type": "object",
            "properties": {
                "draft_id": {"type": "string", "description": "The draft ID from list_drafts"},
                "to": {"type": "string", "description": "Recipient email address"},
                "subject": {"type": "string", "description": "Email subject line"},
                "body": {"type": "string", "description": "Plain-text email body"},
            },
            "required": ["draft_id", "to", "subject", "body"],
        },
    },
    {
        "name": "reply_to_email",
        "description": "Create a draft reply to an email. Does NOT send it — the user reviews and sends manually.",
        "input_schema": {
            "type": "object",
            "properties": {
                "email_id": {"type": "string", "description": "ID of the email to reply to"},
                "body": {"type": "string", "description": "Plain-text reply body"},
            },
            "required": ["email_id", "body"],
        },
    },
    {
        "name": "mark_email_read",
        "description": "Mark an email as read.",
        "input_schema": {
            "type": "object",
            "properties": {
                "email_id": {"type": "string", "description": "The email ID to mark as read"},
            },
            "required": ["email_id"],
        },
    },
    {
        "name": "mark_email_unread",
        "description": "Mark an email as unread.",
        "input_schema": {
            "type": "object",
            "properties": {
                "email_id": {"type": "string", "description": "The email ID to mark as unread"},
            },
            "required": ["email_id"],
        },
    },
    {
        "name": "move_email",
        "description": "Move an email to a different label or folder (e.g. STARRED, IMPORTANT, or a custom label name).",
        "input_schema": {
            "type": "object",
            "properties": {
                "email_id": {"type": "string", "description": "The email ID to move"},
                "destination": {"type": "string", "description": "Label name or system label: INBOX, SPAM, TRASH, STARRED, IMPORTANT, or a custom label"},
            },
            "required": ["email_id", "destination"],
        },
    },
    {
        "name": "delete_email",
        "description": (
            "Move a single email to Trash (recoverable). "
            "IMPORTANT: Only call this after confirming the subject and first few lines with the user."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "email_id": {"type": "string", "description": "The email ID to trash"},
            },
            "required": ["email_id"],
        },
    },
    {
        "name": "bulk_delete_emails",
        "description": (
            "Permanently delete all emails matching a Gmail query. "
            "ONLY allowed for category:promotions, category:updates, or category:social. "
            "Will be rejected for any other query."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Must include category:promotions, category:updates, or category:social",
                },
            },
            "required": ["query"],
        },
    },
]

TOOL_REGISTRY.update({
    "list_emails": list_emails,
    "read_email": read_email,
    "search_emails": search_emails,
    "create_draft": create_draft,
    "list_drafts": list_drafts,
    "edit_draft": edit_draft,
    "reply_to_email": reply_to_email,
    "mark_email_read": mark_email_read,
    "mark_email_unread": mark_email_unread,
    "move_email": move_email,
    "delete_email": delete_email,
    "bulk_delete_emails": bulk_delete_emails,
})
