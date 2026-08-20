from __future__ import annotations

import json
import os
import urllib.error
import urllib.request


class GitHubDispatchError(RuntimeError):
    """خطای ارسال رویداد اجرای Agent به GitHub."""


def dispatch_agent(repository: str, request: dict) -> None:
    """اجرای Workflow را با repository_dispatch فعال می‌کند.

    توکن فقط از محیط اجرا خوانده می‌شود و هرگز در Log چاپ نمی‌شود.
    """
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        raise GitHubDispatchError("GITHUB_TOKEN در محیط Manager تنظیم نشده است.")
    if not repository or "/" not in repository:
        raise GitHubDispatchError("نام Repository نامعتبر است.")
    required = ("request_id", "agent", "url", "execution_id")
    if any(not str(request.get(key, "")).strip() for key in required):
        raise GitHubDispatchError("اطلاعات اجرای Agent ناقص است.")

    payload = json.dumps(
        {"event_type": "execute-agent", "client_payload": request},
        ensure_ascii=False,
    ).encode("utf-8")
    api_request = urllib.request.Request(
        f"https://api.github.com/repos/{repository}/dispatches",
        data=payload,
        method="POST",
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            "Content-Type": "application/json",
            "User-Agent": "AI-Agent-Manager",
        },
    )
    try:
        with urllib.request.urlopen(api_request, timeout=20) as response:
            if response.status not in (200, 201, 204):
                raise GitHubDispatchError("GitHub اجرای Workflow را نپذیرفت.")
    except urllib.error.HTTPError as error:
        if error.code in (401, 403):
            raise GitHubDispatchError("توکن GitHub مجوز اجرای Workflow را ندارد.") from error
        raise GitHubDispatchError("ارسال رویداد به GitHub ناموفق بود.") from error
    except urllib.error.URLError as error:
        raise GitHubDispatchError("ارتباط با GitHub برقرار نشد.") from error
