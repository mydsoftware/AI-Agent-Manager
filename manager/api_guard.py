from __future__ import annotations

from manager.auth import APIAuthenticator


class APIGuard:
    """احراز هویت مشترک برای endpointهای Session API."""

    def __init__(self, authenticator: APIAuthenticator | None = None) -> None:
        self.authenticator = authenticator or APIAuthenticator()

    def authorized(self, provided_key: str | None) -> bool:
        return self.authenticator.validate(provided_key)
