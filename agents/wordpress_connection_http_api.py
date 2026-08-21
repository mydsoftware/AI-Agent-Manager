from __future__ import annotations

from dataclasses import dataclass
from agents.wordpress_connection import WordPressConnectionApi, WordPressConnectionConfig


@dataclass(frozen=True)
class ConnectionHttpResponse:
    status: int
    body: dict[str, object]


class WordPressConnectionHttpApi:
    """Endpoint منطقی Backend برای فرم اتصال WordPress."""

    def __init__(self, api: WordPressConnectionApi | None = None) -> None:
        self.api = api or WordPressConnectionApi()

    def post_check(self, payload: dict[str, object]) -> ConnectionHttpResponse:
        required = ("site_url", "username", "application_password", "agent_token")
        if any(not str(payload.get(key, "")).strip() for key in required):
            return ConnectionHttpResponse(400, {"message": "همه اطلاعات اتصال الزامی است."})

        config = WordPressConnectionConfig(
            site_url=str(payload["site_url"]).strip(),
            username=str(payload["username"]).strip(),
            application_password=str(payload["application_password"]),
            agent_token=str(payload["agent_token"]),
        )
        return ConnectionHttpResponse(200, self.api.check(config))
