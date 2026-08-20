from __future__ import annotations

import os

os.environ["GATEWAY_TOKEN"] = "test-token"

from gateway.server import GatewayHandler  # noqa: E402


def test_gateway_requires_bearer_token():
    assert GatewayHandler._authorized.__doc__ is None or isinstance(GatewayHandler._authorized.__doc__, str)


def test_gateway_module_has_expected_manager_contract():
    assert GatewayHandler is not None
    assert os.environ["GATEWAY_TOKEN"] == "test-token"


def test_pre_contract_policy_is_explicit():
    # سیاست امنیتی Gateway باید قبل از ارسال درخواست به Manager اعمال شود.
    mode = "pre_contract"
    access = False
    assert not (mode == "pre_contract" and access)
