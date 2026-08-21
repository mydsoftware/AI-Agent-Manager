from __future__ import annotations

import json
from agents.wordpress_connection_http_api import WordPressConnectionHttpApi


def handle_wordpress_connection_check(body: bytes, api: WordPressConnectionHttpApi | None = None) -> tuple[int, dict[str, object]]:
    """هندلر مستقل Route برای اتصال UI به Backend بدون وابستگی به Framework خاص."""
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return 400, {"message": "بدنه درخواست JSON معتبر نیست."}

    if not isinstance(payload, dict):
        return 400, {"message": "بدنه درخواست باید یک شیء JSON باشد."}

    response = (api or WordPressConnectionHttpApi()).post_check(payload)
    return response.status, response.body
