import os

from manager.auth import APIAuthenticator


def test_api_auth_uses_constant_time_comparison(monkeypatch):
    monkeypatch.setenv("AI_AGENT_MANAGER_API_KEY", "secret-key")
    auth = APIAuthenticator()

    assert auth.enabled is True
    assert auth.validate("secret-key") is True
    assert auth.validate("wrong-key") is False
    assert auth.validate(None) is False


def test_api_key_is_not_exposed_by_authenticator():
    auth = APIAuthenticator()
    assert not hasattr(auth, "get_api_key")
