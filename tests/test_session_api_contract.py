from session_api import SessionAPIHandler


def test_session_api_exposes_runtime_contract():
    assert hasattr(SessionAPIHandler, "runtime")
    assert callable(SessionAPIHandler.state)
    assert callable(SessionAPIHandler.body)
    assert callable(SessionAPIHandler.send_json)


def test_session_api_default_port_is_stable():
    import session_api

    assert session_api.run_server.__defaults__ == ("127.0.0.1", 8081)
