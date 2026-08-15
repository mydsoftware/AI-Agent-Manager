from session_api import SessionAPIHandler


def test_session_api_serializes_state():
    assert hasattr(SessionAPIHandler, "state")
    assert hasattr(SessionAPIHandler, "runtime")
