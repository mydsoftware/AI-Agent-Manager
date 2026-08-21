from __future__ import annotations

import json
from typing import Callable

from agents.wordpress_connection_http_api import WordPressConnectionHttpApi


class AgentHttpServerAdapter:
    """آداپتور مستقل برای اتصال Routeها به HTTP Server اصلی Agent Manager."""

    def __init__(self, connection_api: WordPressConnectionHttpApi | None = None) -> None:
        self.connection_api = connection_api or WordPressConnectionHttpApi()

    def handle(self, method: str, path: str, body: bytes = b"") -> tuple[int, dict[str, str], bytes]:
        if method.upper() == "POST" and path == "/api/wordpress/connection/check":
            try:
                payload = json.loads(body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                return 400, {"Content-Type": "application/json; charset=utf-8"}, json.dumps({"message": "JSON نامعتبر است."}, ensure_ascii=False).encode("utf-8")

            if not isinstance(payload, dict):
                return 400, {"Content-Type": "application/json; charset=utf-8"}, json.dumps({"message": "بدنه درخواست باید Object باشد."}, ensure_ascii=False).encode("utf-8")

            result = self.connection_api.post_check(payload)
            return result.status, {"Content-Type": "application/json; charset=utf-8"}, json.dumps(result.body, ensure_ascii=False).encode("utf-8")

        return 404, {"Content-Type": "application/json; charset=utf-8"}, json.dumps({"message": "Route پیدا نشد."}, ensure_ascii=False).encode("utf-8")
