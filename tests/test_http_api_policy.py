from __future__ import annotations

import json
from unittest.mock import patch

from http_api import ManagerRequestHandler


def _request_body(handler, body: dict) -> None:
    raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
    handler.rfile.read = lambda length: raw
    handler.headers = {
        "Content-Length": str(len(raw)),
        "X-API-Key": "test-key",
        "X-Execution-ID": "exec-test",
    }


def test_website_audit_pre_contract_is_allowed():
    handler = object.__new__(ManagerRequestHandler)
    handler.path = "/execute/website-audit"
    _request_body(
        handler,
        {
            "request_id": "req-test",
            "url": "https://example.com",
            "mode": "pre_contract",
            "access": False,
            "language": "fa",
            "description": "ممیزی تستی",
        },
    )
    handler._authorized = lambda: True
    handler._send_json = lambda status, data: setattr(handler, "response", (status, data))
    handler.execution_store = object()
    handler.executor = object()

    with patch.object(ManagerRequestHandler, "_authorized", return_value=True):
        with patch.object(ManagerRequestHandler, "_send_json") as send_json:
            with patch.object(ManagerRequestHandler, "_run_execution"):
                with patch.object(ManagerRequestHandler.execution_store, "create", create=True):
                    pass


def test_policy_rejects_pre_contract_fix_without_running_agent():
    from manager.policy import authorize

    decision = authorize(action="fix", mode="pre_contract", access=False)
    assert decision.allowed is False
    assert "ممیزی" in decision.reason
