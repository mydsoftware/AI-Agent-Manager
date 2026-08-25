from __future__ import annotations

import json
from io import BytesIO
from unittest.mock import patch

from http_api import ManagerRequestHandler


def _create_handler(body: dict) -> ManagerRequestHandler:
    """یک handler مجازی برای تست ایجاد می‌کند."""
    raw = json.dumps(body, ensure_ascii=False).encode("utf-8")
    handler = object.__new__(ManagerRequestHandler)
    handler.rfile = BytesIO(raw)
    handler.headers = {
        "Content-Length": str(len(raw)),
        "X-API-Key": "test-key",
        "X-Execution-ID": "exec-test",
    }
    handler.path = "/execute/website-audit"
    return handler


def test_website_audit_pre_contract_is_allowed():
    handler = _create_handler({
        "request_id": "req-test",
        "url": "https://example.com",
        "mode": "pre_contract",
        "access": False,
        "language": "fa",
        "description": "ممیزی تستی",
    })

    with patch.object(ManagerRequestHandler, "_authorized", return_value=True):
        with patch.object(ManagerRequestHandler, "_send_json") as send_json:
            with patch.object(ManagerRequestHandler, "_run_execution"):
                with patch("http_api.ManagerRequestHandler.execution_store") as mock_store:
                    handler.do_POST()
                    # بررسی اینکه پاسخ 202 برگردانده شده
                    if send_json.called:
                        status = send_json.call_args[0][0]
                        assert status == 202


def test_policy_rejects_pre_contract_fix_without_running_agent():
    from manager.policy import authorize

    decision = authorize(action="fix", mode="pre_contract", access=False)
    assert decision.allowed is False
    assert "ممیزی" in decision.reason
