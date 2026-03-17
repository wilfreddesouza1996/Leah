"""Google OAuth2 authentication and service factory."""

from __future__ import annotations

from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = [
    # Gmail
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.compose",
    # Calendar
    "https://www.googleapis.com/auth/calendar",
    # Tasks
    "https://www.googleapis.com/auth/tasks",
    # Drive (files created/opened by this app only)
    "https://www.googleapis.com/auth/drive.file",
    # Docs
    "https://www.googleapis.com/auth/documents",
]


def get_google_credentials(settings) -> Credentials:
    """Load cached token or run interactive OAuth2 browser flow.

    On first run, opens a browser tab for the user to authorize Leah.
    On subsequent runs, loads the cached token and refreshes it if expired.
    """
    token_path = Path(settings.google_token_file)
    creds_path = Path(settings.google_credentials_file)

    creds: Credentials | None = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(str(token_path), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not creds_path.exists():
                raise FileNotFoundError(
                    f"Google credentials file not found: {creds_path}\n"
                    "Download it from Google Cloud Console:\n"
                    "  APIs & Services → Credentials → OAuth 2.0 Client ID → Download JSON\n"
                    f"Then save it as: {creds_path}"
                )
            flow = InstalledAppFlow.from_client_secrets_file(str(creds_path), SCOPES)
            creds = flow.run_local_server(port=0)

        token_path.parent.mkdir(parents=True, exist_ok=True)
        token_path.write_text(creds.to_json())

    return creds


def build_gmail_service(creds: Credentials):
    return build("gmail", "v1", credentials=creds)


def build_calendar_service(creds: Credentials):
    return build("calendar", "v3", credentials=creds)


def build_drive_service(creds: Credentials):
    return build("drive", "v3", credentials=creds)


def build_docs_service(creds: Credentials):
    return build("docs", "v1", credentials=creds)


def build_tasks_service(creds: Credentials):
    return build("tasks", "v1", credentials=creds)
