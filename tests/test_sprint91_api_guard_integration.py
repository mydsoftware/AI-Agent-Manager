from manager.api_guard import APIGuard
from session_api import SessionAPIHandler


def test_session_api_uses_shared_guard():
    assert hasattr(SessionAPIHandler, "guard")
    assert isinstance(SessionAPIHandler.guard, APIGuard)
    assert callable(SessionAPIHandler.authorized)
